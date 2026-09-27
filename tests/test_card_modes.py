"""New creation rejects retired modes; frozen history remains byte-stable."""
from contextlib import redirect_stderr
import io
import json
from pathlib import Path
import unittest

import test_work_appearance as fixture
import appearance

cli = fixture.cli


class CardModeTest(unittest.TestCase):
    setUp = fixture.WorkAppearanceTest.setUp
    asset = fixture.WorkAppearanceTest.asset
    invoke = fixture.WorkAppearanceTest.invoke

    def test_defaults_captions_ratios_and_snapshot_helpers(self):
        identity = self.invoke('new', 'Card', '--workflow', 'hyperframes_video', '--account', 'a')
        work, _ = cli.locate_work(self.root, identity)
        main = work / 'variants/main'
        state = cli.read_json(main / 'variant.yaml')
        self.assertEqual('card', state['mode'])
        self.assertFalse(state['appearance_lock']['selection']['captions'])
        self.invoke('variant', 'add', 'portrait', '--account', 'a', '--ratio', '9:16', '--captions', 'on')
        portrait = work / 'variants/portrait'
        state = cli.read_json(portrait / 'variant.yaml')
        self.assertEqual(('card', '9:16'), (state['mode'], state['ratio']))
        self.assertTrue(state['appearance_lock']['selection']['captions'])
        project = portrait / 'project'
        config = cli.read_json(project / 'project-config.json')
        for name in ('cues', 'captions', 'figures', 'scene-binding', 'rolls', 'card-component'):
            self.assertTrue((project / f'runtime/{name}.js').is_file())
            self.assertIn(f'runtime/{name}.js', config['snapshot_dependencies'])
        for ratio in ('4:3', '1:1', '3:4', '4:5'):
            with self.subTest(ratio=ratio), self.assertRaisesRegex(appearance.AppearanceError, '16:9 and 9:16'):
                appearance.resolve(self.root, self.account, {'ratio': ratio})
        before = self.invoke('current')
        with self.assertRaisesRegex(appearance.AppearanceError, '16:9 and 9:16'):
            self.invoke('variant', 'add', 'invalid', '--account', 'a', '--ratio', '4:3')
        self.assertEqual(before, self.invoke('current'))
        self.assertFalse((work / 'variants/invalid').exists())
        cli.account_service(self.root).put('account', 'plain', {'name': 'No asset selections'})
        with self.assertRaisesRegex(cli.HarnessError, 'exact Theme and Background'):
            cli.account_service(self.root).put('account', 'unfrozen-captions', {'name': 'No assets', 'captions': True})
        for ratio in ('4:3', 'source'):
            with self.subTest(plain_ratio=ratio), self.assertRaises(cli.HarnessError):
                self.invoke('variant', 'add', 'plain-invalid', '--account', 'plain', '--ratio', ratio)
        choices = self.base / 'square.json'
        choices.write_text(json.dumps({'ratio': 'source', 'width': 1200, 'height': 1200}))
        with self.assertRaisesRegex(appearance.AppearanceError, '16:9 and 9:16'):
            self.invoke('variant', 'add', 'square', '--account', 'a', '--appearance-file', str(choices))

    def test_retired_cli_modes_and_config_cannot_be_overridden(self):
        identity = self.invoke('new', 'Card', '--workflow', 'hyperframes_video', '--account', 'a')
        work, _ = cli.locate_work(self.root, identity)
        before = (work / 'variants/main/variant.yaml').read_bytes()
        for mode in appearance.LEGACY_MODES:
            for argv in (('new', 'Bad', '--workflow', 'hyperframes_video', '--mode', mode), ('variant', 'add', 'bad', '--mode', mode)):
                error = io.StringIO()
                with redirect_stderr(error), self.assertRaises(SystemExit):
                    cli.build_parser().parse_args(argv)
                self.assertIn('card', error.getvalue())
                self.assertIn('invalid choice', error.getvalue())
            for kind, name in (('account', 'a'), ('series', 'fixture')):
                service = cli.account_service(self.root)
                path = service.directory / kind / f'{name}.json'
                original = path.read_bytes()
                record = cli.read_json(path)
                cli.write_json(path, {**record, 'mode': mode})
                try:
                    for command in (('new', 'Bad', '--workflow', 'hyperframes_video'), ('variant', 'add', 'bad')):
                        with self.subTest(kind=kind, mode=mode, command=command), self.assertRaisesRegex(appearance.AppearanceError, 'update settings to card'):
                            self.invoke(*command, '--account', 'a', '--mode', 'card')
                    self.assertEqual(before, (work / 'variants/main/variant.yaml').read_bytes())
                    appearance.verify(work / 'variants/main/project', cli.read_json(work / 'variants/main/variant.yaml')['appearance_lock'])
                finally:
                    path.write_bytes(original)
        for mode in appearance.LEGACY_MODES:
            with self.assertRaisesRegex(appearance.AppearanceError, 'update settings to card'):
                appearance.resolve(self.root, {**self.account, 'mode': mode}, {'mode': 'card'})

    def test_prechange_frozen_locks_validate_without_rehash_or_rewrite(self):
        path = Path(__file__).parent / 'fixtures/card-legacy-locks.json'
        content = path.read_bytes()
        for lock in json.loads(content)['locks']:
            before = json.dumps(lock)
            appearance._check_lock(lock)
            self.assertEqual(before, json.dumps(lock))
            self.assertFalse(lock['selection'].get('captions', False))
        self.assertEqual(content, path.read_bytes())


if __name__ == '__main__':
    unittest.main()
