import json
from pathlib import Path
import unittest
import test_work_cli as fixtures
cli = fixtures.WORK_CLI


class WorkflowCliTest(unittest.TestCase):
    setUp = fixtures.WorkCliTest.setUp
    tearDown = fixtures.WorkCliTest.tearDown
    invoke = fixtures.WorkCliTest.invoke
    new_work = fixtures.WorkCliTest.new_work
    prepare_preview = fixtures.WorkCliTest.prepare_preview
    update_frontmatter = staticmethod(fixtures.WorkCliTest.update_frontmatter)

    def test_disabled_gates_progress_exact_draft_and_keep_script_content(self):
        identity, work = self.new_work()
        draft = self.prepare_preview(work)
        variant = work / 'variants/main'
        script = cli.input_path(variant, 'SCRIPT.md')
        self.update_frontmatter(script, approval='pending')
        self.update_frontmatter(variant / 'ANIMATION_PLAN.md', status='draft')
        before = cli.document_body(script)
        config = self.root / 'workflow.json'
        config.write_text(json.dumps({'human_confirmation': {'script': False, 'plan': False, 'draft': False}}))
        self.invoke('workflow', 'put', '--layer', 'work', '--file', str(config))
        preview = self.invoke('preview', 'register', str(draft))
        state = cli.read_json(variant / 'variant.yaml')
        self.assertEqual(preview, state['accepted_preview'])
        self.assertEqual(before, cli.document_body(script))
        self.assertEqual(state['script_revision'], state['accepted_script_revision'])
        config.write_text(json.dumps({'human_confirmation': {'script': False}}))
        error = self.invoke('workflow', 'put', '--layer', 'variant', '--file', str(config), expected=2)
        self.assertIn('Shared Script',error)
        files = json.loads(self.invoke('workflow','stage','plan'))['files']
        self.assertTrue(files)
        self.assertFalse(any('writing' in path for path in files))

    def test_advance_binds_exact_bytes_and_does_not_edit_script_or_plan(self):
        identity, work = self.new_work()
        self.prepare_preview(work)
        variant = work / 'variants/main'
        for stage, target in [('script', cli.input_path(variant, 'SCRIPT.md')),
                              ('plan', variant / 'ANIMATION_PLAN.md')]:
            before = target.read_bytes()
            digest = cli.file_sha256(target)
            result = json.loads(self.invoke('workflow', 'advance', stage, '--sha256', digest))
            self.assertEqual('advanced', result['status'])
            self.assertEqual('unchanged', json.loads(self.invoke('workflow', 'advance', stage, '--sha256', digest))['status'])
            self.assertEqual(before, target.read_bytes())
            state = cli.read_json(variant / 'variant.yaml')
            self.assertTrue(cli.confirmed_input(variant, state, stage))
            target.write_bytes(before + b'\nChanged input\n')
            self.assertFalse(cli.confirmed_input(variant, state, stage))
            self.assertIn('Input changed', self.invoke('workflow', 'advance', stage, '--sha256', digest, expected=2))


if __name__ == '__main__': unittest.main()
