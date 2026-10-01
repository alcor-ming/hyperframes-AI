import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.studio'))
import explainer
import math_audio
import math_chain
import review_bundle
from work_requests import RequestError


class MathDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.cli = self.root / 'upstream/dist/cli.js'
        self.cli.parent.mkdir(parents=True)
        self.cli.write_text('// fixture', encoding='utf-8')
        self.package = self.cli.parent.parent / 'package.json'
        self.package.write_text('{"version":"0.8.27"}', encoding='utf-8')
        self.browser = self.root / 'browser'
        self.browser.write_bytes(b'fixture')
        self.audio = self.root / 'formal.MP3'
        self.audio.write_bytes(b'formal audio fixture')
        self.env = patch.dict(os.environ, {'HYPERFRAMES_BROWSER_PATH': str(self.browser)})
        self.env.start()
        self.addCleanup(self.env.stop)

    def upstream(self, data=None, code=0):
        if data is None:
            data = {'version': 1, 'audio': 'audio.mp3', 'beats': [{'time': t} for t in [0, .5, 1, 1.5, 2]]}

        def run(command, **options):
            self.assertEqual([str(self.cli), 'beats'], command[1:3])
            self.assertEqual('--json', command[-1])
            self.assertEqual('1', options['env']['HYPERFRAMES_NO_TELEMETRY'])
            self.assertEqual('1', options['env']['DO_NOT_TRACK'])
            project = Path(command[3])
            self.assertEqual(self.audio.read_bytes(), (project / 'audio.mp3').read_bytes())
            self.assertIn('data-timeline-role="music"', (project / 'index.html').read_text())
            (project / 'beats').mkdir()
            (project / 'beats/audio.mp3.json').write_text(json.dumps(data), encoding='utf-8')
            return SimpleNamespace(returncode=code, stderr='fixture failure' if code else '', stdout='')

        return patch('math_audio.subprocess.run', side_effect=run)

    def test_pinned_extraction_and_explicit_meter(self):
        with self.upstream() as run:
            grid = math_audio.extract(self.audio, self.cli, 3, 1)
        self.assertEqual(hashlib.sha256(self.audio.read_bytes()).hexdigest(), grid['audio_sha256'])
        self.assertEqual(.5, math_chain.find_beat(grid, 1, 1))
        self.assertEqual(2, math_chain.find_beat(grid, 2, 1))
        self.assertEqual(1, run.call_count)
        self.assertEqual(b'formal audio fixture', self.audio.read_bytes())
        for meter, downbeat in [(None, 0), (4, None), (0, 0), (4, -1)]:
            with self.subTest(meter=meter, downbeat=downbeat), self.upstream(), self.assertRaises(ValueError):
                math_audio.extract(self.audio, self.cli, meter, downbeat)

    def test_no_browser_download_or_version_upgrade(self):
        with patch('math_audio.subprocess.run') as run:
            with patch.dict(os.environ, {'HYPERFRAMES_BROWSER_PATH': ''}), self.assertRaisesRegex(ValueError, 'browser'):
                math_audio.extract(self.audio, self.cli, 4, 0)
            self.package.write_text('{"version":"0.8.28"}', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, '0.8.27'):
                math_audio.extract(self.audio, self.cli, 4, 0)
            run.assert_not_called()

    def test_audio_change_during_extraction_is_rejected(self):
        with self.upstream() as run:
            original = run.side_effect
            def changed(*args, **kwargs):
                result = original(*args, **kwargs)
                self.audio.write_bytes(b'changed formal audio')
                return result
            run.side_effect = changed
            with self.assertRaisesRegex(ValueError, 'Audio changed'):
                math_audio.extract(self.audio, self.cli, 4, 0)

    def test_upstream_failure_empty_or_invalid_schema(self):
        base = {'version': 1, 'audio': 'audio.mp3', 'beats': [{'time': 0}]}
        for data in [{**base, 'beats': []}, {**base, 'version': 2}, {**base, 'version': True},
                     {**base, 'audio': 'other.mp3'}, {**base, 'beats': None}, {**base, 'beats': [{}]}, []]:
            with self.subTest(data=data), self.upstream(data), self.assertRaises(ValueError):
                math_audio.extract(self.audio, self.cli, 4, 0)
        with self.upstream(code=1), self.assertRaisesRegex(ValueError, 'Pinned beat extraction failed'):
            math_audio.extract(self.audio, self.cli, 4, 0)

    def review_fixture(self):
        store = self.root / 'store'
        work = store / 'works/active/sample'
        variant = work / 'variants/main'
        files = {'variants/main/ANIMATION_PLAN.md': b'## S01\n',
                 'variants/main/project/scenes/s01.html': b'<main>math</main>',
                 'shots/one.png': b'\x89PNG\r\n\x1a\n', 'contact.png': b'contact', 'private.txt': b'undeclared'}
        cues = explainer.build_cues('a', b'{"characters":[{"char":"a","start":0,"end":1}]}')
        cues['beat_grid'] = math_chain.make_beat_grid([0, 1, 2], 'a' * 64, 3, 0)
        files['variants/main/project/runtime/cues.json'] = json.dumps(cues).encode()
        for name, content in files.items():
            path = work / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        manifest = dict(scenes=['variants/main/project/scenes/s01.html'],
                        screenshots=[dict(time=1.25, path='shots/one.png')], contact_sheet='contact.png')
        return store, work, variant, manifest, files

    def test_review_declared_evidence_only_and_no_overwrite(self):
        store, work, variant, manifest, files = self.review_fixture()
        target = review_bundle.build(store, work, variant, 'review-1', manifest)
        self.assertEqual(store / 'review/review-1', target)
        expected = set(files) - {'private.txt'}
        actual = {p.relative_to(target / 'evidence').as_posix() for p in (target / 'evidence').rglob('*') if p.is_file()}
        self.assertEqual(expected, actual)
        data = json.loads((target / 'manifest.json').read_text())
        self.assertEqual(manifest, data['declaration'])
        self.assertEqual({n: hashlib.sha256(files[n]).hexdigest() for n in expected}, data['files'])
        self.assertIn('| 严重度 | 证据 | 问题 | 建议 |', (target / 'REVIEW.md').read_text())
        self.assertIn('【图】【码】【未实现】', (target / 'REVIEW.md').read_text())
        with self.assertRaisesRegex(RequestError, 'already exists'):
            review_bundle.build(store, work, variant, 'review-1', manifest)
        self.assertEqual(files['variants/main/ANIMATION_PLAN.md'], (target / 'evidence/variants/main/ANIMATION_PLAN.md').read_bytes())

    def test_review_rejects_input_escape_links_and_output_links(self):
        store, work, variant, manifest, _ = self.review_fixture()
        outside = self.root / 'outside.html'
        outside.write_text('outside', encoding='utf-8')
        (work / 'linked.html').symlink_to(outside)
        os.link(outside, work / 'hard.html')
        (work / 'linked-dir').symlink_to(variant / 'project/scenes', target_is_directory=True)
        for name in ['../outside.html', str(outside), 'linked.html', 'hard.html', 'linked-dir/s01.html']:
            changed = {**manifest, 'scenes': [name]}
            with self.subTest(name=name), self.assertRaises(RequestError):
                review_bundle.build(store, work, variant, 'rejected', changed)
            self.assertFalse((store / 'review/rejected').exists())
        destination = self.root / 'outside-review'
        destination.mkdir()
        (store / 'review').symlink_to(destination, target_is_directory=True)
        with self.assertRaises(RequestError):
            review_bundle.build(store, work, variant, 'rejected', manifest)
        self.assertEqual([], list(destination.iterdir()))

    def test_review_invalid_declarations_or_missing_grid(self):
        store, work, variant, manifest, _ = self.review_fixture()
        invalid = [{**manifest, 'undeclared': 'private.txt'}, {**manifest, 'scenes': []}]
        for time in [-1, True, float('nan'), float('inf'), '1']:
            invalid.append({**manifest, 'screenshots': [dict(time=time, path='shots/one.png')]})
        invalid += [{**manifest, 'screenshots': [dict(time=1, path='shots/one.jpg')]},
                    {**manifest, 'screenshots': [dict(time=1, path='shots/one.png', extra=True)]}]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises((ValueError, RequestError)):
                review_bundle.build(store, work, variant, 'rejected', value)
        cue_file = variant / 'project/runtime/cues.json'
        cues = json.loads(cue_file.read_text())
        del cues['beat_grid']
        cue_file.write_text(json.dumps(cues), encoding='utf-8')
        with self.assertRaisesRegex(RequestError, 'beat grid'):
            review_bundle.build(store, work, variant, 'rejected', manifest)
        self.assertFalse((store / 'review/rejected').exists())


if __name__ == '__main__':
    unittest.main()
