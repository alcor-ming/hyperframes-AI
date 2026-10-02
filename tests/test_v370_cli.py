"""Real lifecycle functions with isolated files; mock only Studio transport/sampling."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import unittest
from unittest import mock

from PIL import Image
import test_visual_plan as legacy_fixture
from test_work_cli import WORK_CLI as cli
from test_v370 import plan
import critic
import lines


class V370CliTest(unittest.TestCase):
    run_cli = legacy_fixture.VisualPlanTest.run_cli
    update = legacy_fixture.VisualPlanTest.update

    def setUp(self):
        legacy_fixture.VisualPlanTest.setUp(self)
        state = cli.read_json(self.variant / 'variant.yaml')
        state['line'] = lines.bind({'mode': 'card'})
        cli.write_variant(self.variant, state)
        metadata = {**cli.plan_metadata(self.variant, state), 'status': 'draft'}
        self.plan_path = self.variant / 'ANIMATION_PLAN.md'
        self.plan_path.write_text('---\n' + json.dumps(metadata) + '\n---\n' + plan().split('---\n', 2)[2])
        self.cli_path = self.root / 'cli.js'
        self.cli_path.write_text('// isolated transport identity')
        self.scope = ('--work', self.variant.parent.parent.name, '--variant', 'main')
        def start(executable, project, port, **kwargs):
            return {'port': 3101, 'studioUrl': f'http://127.0.0.1:3101/#project/{project.name}', 'pid': 123}
        self.addCleanup(mock.patch.stopall)
        mock.patch.object(cli.studio_preview, 'start', side_effect=start).start()
        mock.patch.object(cli.studio_preview, 'context', return_value={}).start()

    def call(self, *args):
        with redirect_stdout(io.StringIO()) as output:
            self.run_cli(*self.scope, *args, '--json')
        return output.getvalue().strip()

    def test_settings_cli_precedence_and_creation_binding(self):
        self.assertEqual({'id': 'card', 'version': 1}, cli.read_json(self.variant / 'variant.yaml')['line'])
        self.call('settings', 'set', '--layer', 'user', 'direction_approval', 'true')
        self.call('settings', 'set', 'direction_approval', 'false')
        values = json.loads(self.call('settings', 'show'))['values']
        self.assertEqual({'value':False, 'source':'variant'}, values['direction_approval'])
        self.call('settings', 'unset', 'direction_approval')
        self.assertEqual('user', json.loads(self.call('settings', 'show'))['values']['direction_approval']['source'])
        for key, value in [('direction_approval', '1'), ('unknown','true'), ('critic.model','text-only')]:
            with self.assertRaises(cli.HarnessError):
                self.call('settings', 'set', key, value)

    def test_direction_toggle_accepts_only_exact_draft_and_plan(self):
        draft = self.call('preview', 'register')
        preview = self.variant / 'previews' / draft
        frozen = (preview / 'ANIMATION_PLAN.md').read_bytes()
        self.call('preview', 'open', draft, '--hyperframes-cli', str(self.cli_path), '--no-open')
        self.call('settings', 'set', 'direction_approval', 'true')
        with self.assertRaisesRegex(cli.HarnessError, 'not approved'):
            self.call('preview', 'accept', draft)
        self.call('settings', 'set', 'direction_approval', 'false')
        content = self.plan_path.read_bytes()
        self.plan_path.write_bytes(content + b'changed direction')
        with self.assertRaisesRegex(cli.HarnessError, 'inputs changed'):
            self.call('preview', 'accept', draft)
        self.plan_path.write_bytes(content)
        self.call('preview', 'accept', draft)
        state = cli.read_json(self.variant / 'variant.yaml')
        self.assertFalse(state['draft_acceptance']['direction_approval'])
        self.assertEqual('approved', cli.read_frontmatter(self.plan_path)['status'])
        self.assertEqual(frozen, (preview / 'ANIMATION_PLAN.md').read_bytes())
        cli.assert_preview_ready(self.variant, state)
        self.assertFalse(list(self.variant.rglob('*.mp4')))
        self.assertFalse(list(self.variant.rglob('*.webm')))

    def sampled(self, request, *args):
        destination = Path(request['evidence_dir'])
        destination.mkdir(parents=True)
        samples = []
        for time in (0, .5, 1, 1.5, 1.8, 1.9, 2 - 1/60, 2, 2.1, 2.2, 2.4, 3, 3.5):
            name = f'{time:.6f}.png'
            Image.new('RGB', (32, 18), 'white').save(destination / name)
            samples.append({'time':round(time,6), 'ready':True, 'texts':[], 'rhythm_candidates':[], 'carry':[], 'screenshot':name})
        return {'samples':samples, 'timeline':[], 'unverified':[], 'boundaries':[0,2]}

    def test_imported_draft_rechecks_reenabled_direction_approval(self):
        movie = self.root / 'imported.mp4'
        movie.write_bytes(b'synthetic import fixture, not a rendered video')
        draft = self.call('preview', 'register', str(movie))
        self.call('settings', 'set', 'direction_approval', 'true')
        with self.assertRaisesRegex(cli.HarnessError, 'not approved'):
            self.call('preview', 'accept', draft)
        self.assertIsNone(cli.read_json(self.variant / 'variant.yaml')['accepted_preview'])

    def test_two_rounds_off_mode_and_previous_issue_coverage(self):
        mock.patch.object(cli.visual_diagnostics, 'probe', side_effect=self.sampled).start()
        self.call('settings', 'set', 'critic.provider', 'codex-subagent')
        one = json.loads(self.call('critic','round','--hyperframes-cli',str(self.cli_path),'--browser','/usr/bin/google-chrome'))
        package = Path(one['package'])
        self.assertTrue((package/'PROMPT.md').is_file())
        self.assertTrue((package/'contact-sheet.png').is_file())
        pairs = json.loads((package/'boundary-pairs.json').read_text())
        self.assertEqual('sampled', pairs[0]['status'])
        self.assertEqual(6, len(json.loads((package/'strips.json').read_text())[1]['frames']))
        ledger_path = self.variant/'critic/ledger.json'
        ledger = cli.read_json(ledger_path)
        entry = ledger['rounds'][0]
        verdict = {key:entry[key] for key in ('round','draft_id','snapshot_sha256')}
        verdict.update(new_issues=[{'id':'Q1','description':'sample visual issue'}], previous=[])
        file = self.root/'verdict.json'; cli.write_json(file,verdict)
        self.call('critic','record','--file',str(file))
        limited = json.loads(self.call('critic','round','--automatic','--hyperframes-cli',str(self.cli_path),'--browser','/usr/bin/google-chrome'))
        self.assertEqual('round_limit',limited['status'])
        self.call('settings','set','critic.provider','off')
        two = json.loads(self.call('critic','round','--hyperframes-cli',str(self.cli_path),'--browser','/usr/bin/google-chrome'))
        self.assertFalse((Path(two['package'])/'PROMPT.md').exists())
        entry = cli.read_json(ledger_path)['rounds'][1]
        verdict = {key:entry[key] for key in ('round','draft_id','snapshot_sha256')}
        verdict.update(new_issues=[],previous=[]);cli.write_json(file,verdict)
        with self.assertRaisesRegex(cli.HarnessError,'every previous'):
            self.call('critic','record','--file',str(file))
        verdict['previous']=[{'id':'Q1','status':'FIXED','detail':'frame evidence'}];cli.write_json(file,verdict)
        self.call('critic','record','--file',str(file))
        ledger=cli.read_json(ledger_path)
        self.assertEqual(2,len(ledger['rounds']))
        self.assertEqual([],critic.pending_issues(ledger['rounds']))
        self.assertIsNone(cli.read_json(self.variant/'variant.yaml')['accepted_preview'])
        self.assertEqual('draft',cli.read_frontmatter(self.plan_path)['status'])
        self.assertFalse(list(self.variant.rglob('*.mp4')))


if __name__ == '__main__':
    unittest.main()
