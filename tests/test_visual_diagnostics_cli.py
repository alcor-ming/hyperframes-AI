"""Exercise diagnostic CLI boundaries against isolated Work fixtures, without video export."""

import json
import shutil
import unittest
from unittest import mock

import test_work_cli as fixture


CLI = fixture.WORK_CLI
COPY = "先明确目标用户真正需要解决的问题，再选择证据完整且能够清楚说明关系的内容，最后安排画面。"


class VisualDiagnosticsCliTests(unittest.TestCase):
    invoke = fixture.WorkCliTest.invoke
    new_work = fixture.WorkCliTest.new_work
    update_frontmatter = staticmethod(fixture.WorkCliTest.update_frontmatter)
    tearDown = fixture.WorkCliTest.tearDown

    def setUp(self):
        fixture.WorkCliTest.setUp(self)
        self.work_id, self.work = self.new_work()
        self.variant = self.work / "variants" / "main"
        self.project = self.variant / "project"
        self.plan = self.variant / "ANIMATION_PLAN.md"
        self.plan.write_text(
            '---\n{"status":"approved","revision":1,"script_revision":1,"research_revision":1}\n---\n'
            '| 原 Scene ID | 使用信息 ID |\n|---|---|\n| S01 | I01 |\n'
            '| 信息 ID / 来源 | 实际表达 |\n|---|---|\n'
            '| I01 · SCRIPT.md#P001 | 先明确用户的问题 |\n', encoding="utf-8")
        self.script = CLI.input_path(self.variant, "SCRIPT.md")
        self.script.write_text('---\n{"revision":1,"approval":"approved"}\n---\n'
                               '<!-- P001 -->\n' + COPY + '\n', encoding="utf-8")
        self.update_frontmatter(CLI.input_path(self.variant, "RESEARCH.md"), status="ready")
        (self.project / "index.html").write_text(
            '<section id="S01" data-start="0" data-duration="4">' + COPY + '</section>', encoding="utf-8")
        (self.project / "compositions").mkdir(exist_ok=True)
        (self.project / "DESIGN.md").write_text("# Isolated diagnostic fixture\n", encoding="utf-8")
        (self.project / "project-config.json").write_text("{}\n", encoding="utf-8")
        self.cli = self.root / "hyperframes-cli.js"
        self.cli.write_text("// Identity-only fixture; never executed.\n", encoding="utf-8")
        self.bind("current", self.project)
        self.sampled = {"samples": [{"time": 0, "ready": True, "texts": [
            {"scene": "S01", "info": "I01", "text": COPY, "selector": "#S01"}]}],
            "motion": [], "timeline": [], "unverified": []}
        context = mock.patch.object(CLI.studio_preview, "context", return_value={})
        probe = mock.patch.object(CLI.visual_diagnostics, "probe", return_value=self.sampled)
        self.context = context.start()
        self.probe = probe.start()
        self.addCleanup(context.stop)
        self.addCleanup(probe.stop)

    def bind(self, target, project):
        CLI.write_json(CLI.studio_record(self.variant, target), {
            "work": self.work_id, "variant": "main", "target": target,
            "project": str(project), "kind": "executable", "port": 8123,
            "url": f"http://127.0.0.1:8123/#project/{project.name}", "cli_sha256": CLI.file_sha256(self.cli),
            "review_directory": project.parent.name,
        })

    def diagnose(self, target="current", *options, expected=0):
        return self.invoke("--work", self.work_id, "--variant", "main", "preview", "diagnose", target,
                           "--hyperframes-cli", str(self.cli), "--browser", str(self.root / "unused-browser"),
                           *options, expected=expected)

    def freeze(self, *options):
        target = self.invoke("--work", self.work_id, "--variant", "main", "preview", "register", *options)
        frozen = self.variant / "previews" / target
        review = self.variant / ".runtime" / "studio-review-fixture" / target
        shutil.copytree(frozen / "source-snapshot", review)
        self.bind(target, review)
        return frozen, review

    def files(self):
        return {str(path.relative_to(self.root)): path.read_bytes()
                for path in self.root.rglob("*") if path.is_file()}

    def test_explicit_work_and_variant_are_required_even_with_current_pointers(self):
        for selection in ((), ("--work", self.work_id), ("--variant", "main")):
            with self.subTest(selection=selection):
                message = self.invoke(*selection, "preview", "diagnose", "current", expected=2)
                self.assertIn("require explicit --work and --variant", message)
        self.probe.assert_not_called()
        self.context.assert_not_called()

    def test_invalid_parameters_fail_before_sampling(self):
        for option, value in (("--minimum", "0"), ("--similarity", "nan"), ("--step", "2"),
                              ("--window", "-1"), ("--pixel-delta", "256"),
                              ("--area-ratio", "1"), ("--width", "159"), ("--timeout-ms", "99")):
            with self.subTest(option=option):
                self.assertIn("Invalid diagnostic parameters", self.diagnose("current", option, value, expected=2))
        self.probe.assert_not_called()
        self.context.assert_not_called()

    def test_current_reports_findings_without_writing_any_fixture_file(self):
        before = self.files()
        report = json.loads(self.diagnose())
        self.assertEqual(before, self.files())
        self.assertEqual("diagnostic_only", report["status"])
        self.assertEqual("current", report["target"])
        self.assertEqual(CLI.preview_input_hashes(self.variant), report["input_sha256"])
        self.assertIn("suspected_copy", [item["kind"] for item in report["d1"]["findings"]])
        self.assertEqual([], report["cross_version_differences"])

    def test_screen_plan_empty_ready_scene_is_missing_without_writes(self):
        self.plan.write_text(
            '---\n{"status":"approved","revision":1,"script_revision":1,"research_revision":1}\n---\n'
            '| Scene | 信息 ID |\n|---|---|\n| S01 | I01 |\n'
            '### I01\n**来源：** SCRIPT.md#P001\n```screen\n先明确用户的问题\n```\n', encoding="utf-8")
        self.sampled['samples'][0]['texts'] = []
        before = self.files()
        report = json.loads(self.diagnose())
        self.assertEqual(before, self.files())
        self.assertEqual([('S01', 'I01', 'plan_information_missing')],
                         [(item['scene'], item['info'], item['kind']) for item in report['d1']['findings']])

    def test_current_input_or_project_changes_during_probe_mark_result_stale(self):
        for path in (self.plan, self.project / "index.html"):
            with self.subTest(path=path.name):
                def change_during_probe(*args):
                    path.write_text(path.read_text(encoding="utf-8") + "\n<!-- changed -->\n", encoding="utf-8")
                    return self.sampled
                self.probe.side_effect = change_during_probe
                report = json.loads(self.diagnose())
                self.assertEqual("stale", report["status"])
                self.assertIn("inputs_changed_during_diagnosis", [item["reason"] for item in report["unverified"]])

    def test_registered_draft_uses_frozen_inputs_and_lists_current_plan_difference(self):
        frozen, _ = self.freeze()
        self.plan.write_text(self.plan.read_text(encoding="utf-8").replace("先明确用户的问题", COPY), encoding="utf-8")
        before = self.files()
        report = json.loads(self.diagnose("draft-v001"))
        self.assertEqual(before, self.files())
        self.assertEqual("diagnostic_only", report["status"])
        self.assertEqual(CLI.preview_input_hashes(frozen), report["input_sha256"])
        self.assertEqual(["ANIMATION_PLAN.md"], report["cross_version_differences"])
        differences = [item for item in report["d1"]["findings"] if item["kind"] == "plan_implementation_difference"]
        self.assertEqual("先明确用户的问题", differences[0]["planned"])

    def test_modified_review_copy_is_rejected_before_sampling(self):
        _, review = self.freeze()
        (review / "index.html").write_text("changed review", encoding="utf-8")
        self.assertIn("Studio review copy changed", self.diagnose("draft-v001", expected=2))
        self.probe.assert_not_called()

    def test_scene_plan_uses_frozen_inputs_and_excludes_other_scene_information(self):
        self.plan.write_text(self.plan.read_text(encoding="utf-8")
                             .replace('| S01 | I01 |', '| S01 | I01 |\n| S02 | I01 I02 |')
                             + '| I02 · SCRIPT.md#P001 | 其他场景的完整结论 |\n', encoding="utf-8")
        frozen, _ = self.freeze("--purpose", "plan", "--scope", "scene", "--scene", "S01")
        for name in CLI.PREVIEW_DOCUMENTS:
            path = CLI.input_path(self.variant, name)
            path.write_text(path.read_text(encoding="utf-8") + '\nCurrent-only change\n', encoding="utf-8")
        for actual, kind in (([], 'plan_information_missing'),
                             ([{"scene": "S01", "info": "I01", "text": "用户", "selector": "#S01"}],
                              'plan_information_truncated')):
            with self.subTest(kind=kind):
                self.sampled['samples'][0]['texts'] = actual
                before = self.files()
                report = json.loads(self.diagnose("plan-v001"))
                self.assertEqual(before, self.files())
                self.assertEqual("diagnostic_only", report['status'])
                self.assertEqual(CLI.preview_input_hashes(frozen), report['input_sha256'])
                self.assertCountEqual(CLI.PREVIEW_DOCUMENTS, report['cross_version_differences'])
                self.assertEqual([('S01', 'I01', kind)],
                                 [(hit['scene'], hit['info'], hit['kind']) for hit in report['d1']['findings']])
                self.assertEqual('先明确用户的问题', report['d1']['findings'][0]['planned'])
                self.assertFalse(any(hit.get('scene') == 'S02' or hit.get('info') == 'I02'
                                     for hit in report['d1']['unverified']))
                self.assertEqual([{'scene': 'S02', 'information_ids': ['I01', 'I02'],
                                   'reason': 'outside_reference_scope'}], report['d1']['out_of_scope'])
                self.assertEqual(['S01'], [scene['id'] for scene in self.probe.call_args.args[0]['scenes']])

    def test_full_executable_plan_can_be_diagnosed(self):
        self.freeze("--purpose", "plan")
        report = json.loads(self.diagnose("plan-v001"))
        self.assertEqual("diagnostic_only", report['status'])

    def test_registered_reference_plan_is_rejected_even_with_executable_studio_record(self):
        self.freeze("--purpose", "plan", "--kind", "reference")
        self.assertIn("executable", self.diagnose("plan-v001", expected=2))
        self.probe.assert_not_called()
        self.context.assert_not_called()

    def test_url_cannot_select_a_different_project_or_port(self):
        path = CLI.studio_record(self.variant, 'current')
        record = CLI.read_json(path)
        for url in ('http://127.0.0.1:8124/#project/project', 'http://127.0.0.1:8123/#project/other'):
            CLI.write_json(path, {**record, 'url': url})
            self.assertIn('Diagnostic URL does not match', self.diagnose(expected=2))
        self.probe.assert_not_called()

    def test_sampling_failure_and_unready_sample_remain_unverified_not_pass(self):
        for samples, reason in (([{"time": 0, "ready": False, "texts": []}], "media_seek_timeout"),
                                ([], "studio_sampling_unavailable")):
            with self.subTest(reason=reason):
                self.probe.return_value = {"samples": samples, "unverified": [{"reason": reason}]}
                report = json.loads(self.diagnose())
                self.assertEqual("diagnostic_only", report["status"])
                self.assertEqual(0, report["d1"]["observed_groups"])
                self.assertIn(reason, [item["reason"] for item in report["unverified"]])
                self.assertIn("plan_information_not_observed", [item["reason"] for item in report["d1"]["unverified"]])
                self.assertNotIn("pass", json.dumps(report).lower())

    def test_invalid_confirmed_exceptions_are_rejected_before_sampling(self):
        exceptions = self.root / "exceptions.json"
        valid = {"scene": "S01", "text": COPY, "source": "SCRIPT.md#P001", "reason": "Confirmed quote"}
        invalid = ["{", "{}", json.dumps([{**valid, "reason": ""}]),
                   json.dumps([{**valid, "scene": "S99"}]), json.dumps([{**valid, "text": "not in source"}])]
        for content in invalid:
            with self.subTest(content=content):
                exceptions.write_text(content, encoding="utf-8")
                message = self.diagnose("current", "--exceptions", str(exceptions), expected=2)
                self.assertTrue("Exception" in message or "exceptions" in message, message)
        self.probe.assert_not_called()
        self.context.assert_not_called()


if __name__ == "__main__":
    unittest.main()
