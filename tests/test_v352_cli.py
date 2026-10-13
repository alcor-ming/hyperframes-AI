"""v352 CLI behavior with isolated synthetic icon and diagnostic fixtures."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

import test_work_cli as fixture
import test_visual_diagnostics_cli as diagnostics

CLI = fixture.WORK_CLI


def call(case, *args, expected=0):
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        status = CLI.main(list(args), root=case.root)
    case.assertEqual(expected, status, stderr.getvalue())
    return stdout.getvalue().strip() or stderr.getvalue().strip()


class V352CliTests(unittest.TestCase):
    setUp = fixture.WorkCliTest.setUp
    tearDown = fixture.WorkCliTest.tearDown

    def icons(self):
        external = tempfile.TemporaryDirectory()
        self.addCleanup(external.cleanup)
        base = Path(external.name)
        package, source, store = base / "npm", base / "cards/kit/assets/lucide-static", base / "store"
        (package / "icons").mkdir(parents=True)
        (package / "package.json").write_text(json.dumps({"name": "lucide-static", "version": "1.45.0", "license": "ISC"}))
        (package / "LICENSE").write_text("Synthetic ISC fixture")
        (package / "icons/fixture.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M2 3 L4 5"/></svg>')
        (package / "icon-metadata.json").write_text(json.dumps({"fixture": {"aliases": ["sample"], "tags": ["synthetic"]}}))
        import asset_store
        config = asset_store.configure_asset_store(self.root, store)
        import designs
        configuration = asset_store._config_path(self.root)
        data = json.loads(configuration.read_text()); data['design_root'] = str(base / 'cards')
        configuration.write_text(json.dumps(data))
        designs.new('kit', kind='material', root=self.root)
        result = json.loads(call(self, "icons", "import", "--from", str(package), "--source", str(source), "--json"))
        self.assertFalse(result["accepted"])
        self.assertFalse((store / "packages").exists())
        return base, store

    def test_icon_cli_import_search_use_and_interface(self):
        base, store = self.icons()
        for query in ("fixture", "sample", "synthetic"):
            row = json.loads(call(self, "icons", "search", query, "--json"))[0]
            self.assertEqual("lucide:fixture@1.45.0", row["ref"])
            self.assertEqual("kit/lucide-static", row["asset_ref"])
        card = json.loads(call(self, "component", "interface", "kit/lucide-static", "--json"))
        self.assertEqual("kit/lucide-static", card["component_ref"])
        self.assertIn("parameters", card["interface"])
        self.assertNotIn("M2 3", json.dumps(card))
        project = base / "sources/project"
        project.mkdir(parents=True)
        (project / "index.html").write_text('<img src="assets/fixture.svg">')
        import asset_store
        asset_store.register_source(store, base / "sources")
        import component_harness as components
        package = base / 'frozen'
        import asset_contract
        asset_contract.freeze_source(base / 'cards/kit/assets/lucide-static', package, card_ref='kit/lucide-static')
        components.install_component(package, project, {"schema_version": 3, "component_ref": "kit/lucide-static@v1",
                                     "usage": {"role": "icon-set", "required": True}})
        result = json.loads(call(self, "icons", "use", row["ref"], "--project", str(project), "--output", "assets/fixture.svg", "--json"))
        self.assertEqual("assets/fixture.svg", result["path"])
        svg = (project / result["path"]).read_text()
        self.assertIn('data-icon="lucide:fixture@1.45.0"', svg)
        self.assertIn("--appearance-colors-text", svg)
        self.assertIn("M2 3 L4 5", svg)
        message = call(self, "icons", "use", "lucide:missing@1.45.0", "--project", str(project), "--output", "assets/missing.svg", expected=2)
        self.assertIn("outside installed closure", message)

    def test_catalog_view_preserves_exact_targets_without_report(self):
        self.icons()
        full = json.loads(call(self, "component", "list", "--json"))
        summary = json.loads(call(self, "component", "list"))
        self.assertNotIn("report_path", summary)
        self.assertEqual(len(full['assets']), summary['total'])
        self.assertIn('--json', summary['full_result'])
        for row in summary['assets']:
            original = next(item for item in full['assets'] if item['path'] == row['path'])
            self.assertEqual(original['detail'], row['detail'])
            self.assertEqual(original['asset_type'], row['asset_type'])

    def test_existing_component_interface_has_parameters_and_example(self):
        source = fixture.REPO / 'tests/fixtures/components/capability-convergence/16x9/v1'
        card = json.loads(call(self, 'component', 'interface', str(source), '--candidate', '--json'))['interface']
        self.assertIn('slots', card)
        self.assertIn('slots', card['example'])
        self.assertNotIn('gsap.timeline', json.dumps(card))


class V352DiagnosticSummaryTests(unittest.TestCase):
    setUp = diagnostics.VisualDiagnosticsCliTests.setUp
    tearDown = fixture.WorkCliTest.tearDown
    invoke = fixture.WorkCliTest.invoke
    new_work = fixture.WorkCliTest.new_work
    update_frontmatter = staticmethod(fixture.WorkCliTest.update_frontmatter)
    bind = diagnostics.VisualDiagnosticsCliTests.bind

    def test_diagnosis_summary_saves_complete_report_without_changing_plan(self):
        self.update_frontmatter(self.plan, plan_format="3.5.2")
        self.sampled['samples'][0]['unverified'] = ['SVG image provenance could not be sampled: #unavailable']
        before = self.plan.read_bytes()
        arguments = ("--work", self.work_id, "--variant", "main", "preview", "diagnose", "current",
                     "--hyperframes-cli", str(self.cli), "--browser", str(self.root / "unused-browser"))
        full = json.loads(call(self, *arguments, "--json"))
        self.assertEqual([{'reason': 'icon_provenance_unverified', 'time': 0, 'target': '#unavailable'}],
                         full['icons']['unverified'])
        summary = json.loads(call(self, *arguments))
        report = json.loads(Path(summary["report_path"]).read_text())
        for key in ("status", "target", "d1", "rhythm", "icons", "samples"):
            self.assertEqual(full[key], report[key])
        self.assertNotIn("samples", summary["summary"])
        self.assertEqual(before, self.plan.read_bytes())


if __name__ == "__main__":
    unittest.main()
