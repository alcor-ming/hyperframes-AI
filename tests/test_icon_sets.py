"""Only synthetic SVG paths: no third-party icon payloads in the checkout."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".studio"))
import asset_contract as ASSET
import asset_store as STORE
import component_harness as COMPONENT
import icon_sets as ICONS
from work_requests import RequestError


class IconSetTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.npm = self.root / "npm"
        (self.npm / "icons").mkdir(parents=True)
        (self.npm / "package.json").write_text(json.dumps({"name": "lucide-static", "version": "1.45.0", "license": "ISC"}))
        (self.npm / "LICENSE").write_text("Synthetic fixture ISC license text")
        (self.npm / "icons/test-shape.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M1 2 L3 4"/></svg>')
        (self.npm / "icon-metadata.json").write_text(json.dumps({"test-shape": {"aliases": ["sample"], "tags": ["fixture"]}}))
        self.source = self.root / "source"
        self.project = self.root / "project"
        self.project.mkdir()
        (self.project / "index.html").write_text('<img src="assets/test.svg">')
        self.store = self.root / "store"

    def install(self):
        ICONS.import_lucide(self.npm, self.source)
        candidate = STORE.pack_source(self.store, self.source)
        acceptance = STORE.accept_component(self.store, candidate["component_ref"], candidate["package_sha256"],
                                            "Synthetic fixture", runtime_root=self.root)
        package = self.store / "packages/lucide-static/v1"
        COMPONENT.install_component(package, self.project,
            {"schema_version": 3, "component_ref": candidate["component_ref"],
             "usage": {"role": "icon-set", "required": True}}, acceptance=acceptance)
        return ICONS.project_packages(self.project)

    def test_import_pack_accept_search_install_use_and_closure(self):
        packages = self.install()
        self.assertEqual(1, len(packages))
        for query in ("test-shape", "sample", "fixture"):
            rows = ICONS.search_icons(packages, query)
            self.assertEqual("lucide:test-shape@1.45.0", rows[0]["ref"])
            self.assertEqual("lucide-static@v1", rows[0]["asset_ref"])
        row = ICONS.use_icon(packages, "lucide:test-shape@1.45.0", self.project, "assets/test.svg")
        svg = (self.project / row["path"]).read_text()
        self.assertIn("currentColor", svg)
        self.assertIn("var(--appearance-colors-text)", svg)
        self.assertEqual("M1 2 L3 4", next(node for node in ET.fromstring(svg) if node.tag.endswith("path")).get("d"))
        from visual_plan import validate_dependencies
        self.assertIn("assets/test.svg", validate_dependencies(self.project))
        self.assertEqual([], ICONS.audit_icons([{"svg": svg, "width": 24, "height": 24}], packages))
        self.assertEqual("icon_source_mismatch", ICONS.audit_icons([{"svg": svg.replace("M1 2", "M9 9")}], packages)[0]["code"])
        COMPONENT.verify_installation(self.project)
        with self.assertRaisesRegex(COMPONENT.ComponentError, "outside installed"):
            ICONS.use_icon([self.store / "packages/lucide-static/v1"], row["ref"], self.project, "assets/other.svg")

    def test_idempotence_conflict_invalid_svg_and_links(self):
        ICONS.import_lucide(self.npm, self.source)
        ICONS.import_lucide(self.npm, self.source)
        self.assertFalse((self.source / "HASHES.json").exists())
        manifest = json.loads((self.source / 'asset.json').read_text())
        declaration = json.loads((self.source / 'icons.json').read_text())
        with self.assertRaisesRegex(COMPONENT.ComponentError, 'cannot be overridden'):
            ASSET.validate_declaration(declaration, {**manifest, 'parameters': {'version': {}}}, self.source)
        path = self.npm / "icons/test-shape.svg"
        original = path.read_text()
        path.write_text(original.replace("M1 2", "M9 9"))
        with self.assertRaisesRegex(COMPONENT.ComponentError, "different content"):
            ICONS.import_lucide(self.npm, self.source)
        path.write_text('<svg><script/></svg>')
        with self.assertRaisesRegex(COMPONENT.ComponentError, "SVG"):
            ICONS.import_lucide(self.npm, self.root / "bad")
        path.unlink()
        path.symlink_to(self.source / "icons/test-shape.svg")
        with self.assertRaisesRegex(COMPONENT.ComponentError, "links"):
            ICONS.import_lucide(self.npm, self.root / "linked")

    def test_search_metadata_keeps_literal_operator_tags(self):
        symbols = ['->', '->|', '<', '<-', '<-|', '<>', '>', '{', '|->', '|<-', '}']
        (self.npm / 'icon-metadata.json').write_text(json.dumps({
            'test-shape': {'aliases': symbols, 'tags': symbols}}))
        packages = self.install()
        for symbol in symbols:
            with self.subTest(symbol=symbol):
                row = ICONS.search_icons(packages, symbol)[0]
                self.assertEqual(symbols, row['aliases'])
                self.assertEqual(symbols, row['tags'])

    def test_search_metadata_still_rejects_executable_payloads(self):
        ICONS.import_lucide(self.npm, self.source)
        metadata = json.loads((self.source / 'asset.json').read_text())
        declaration = json.loads((self.source / 'icons.json').read_text())
        for field in ('aliases', 'tags'):
            for payload in ('<script>alert(1)</script>', 'javascript:alert(1)',
                            'url(https://example.invalid/payload)', 'expression(alert(1))',
                            '{alert(1)}', 'x;alert(1)', '${alert(1)}'):
                with self.subTest(field=field, payload=payload):
                    declaration['icons'][0][field] = [payload]
                    with self.assertRaisesRegex(COMPONENT.ComponentError, 'Executable expressions'):
                        ASSET.validate_declaration(declaration, metadata, self.source)
                declaration['icons'][0][field] = []
        for symbol in ('<-', '->', '{', '}'):
            with self.subTest(parameter=symbol), self.assertRaisesRegex(COMPONENT.ComponentError, 'Executable expressions'):
                ASSET.validate_parameter(symbol, {'type': 'string', 'default': symbol})

    def test_editor_ids_do_not_change_icon_geometry(self):
        packages = self.install()
        ICONS.use_icon(packages, 'lucide:test-shape@1.45.0', self.project, 'assets/test.svg')
        root = ET.fromstring((self.project / 'assets/test.svg').read_text())
        root.set('data-hf-id', 'studio-root')
        path = next(iter(root))
        path.set('data-hf-id', 'studio-path')
        record = {'svg': ET.tostring(root, encoding='unicode'), 'target': '#original'}
        self.assertEqual([], ICONS.audit_icons([record], packages))
        for node, attribute, changed in ((path, 'd', 'M2 2 L3 4'),
                                         (path, 'transform', 'translate(1 0)'),
                                         (root, 'transform', 'scale(2)'),
                                         (path, 'data-hf-id-other', 'not-editor-metadata')):
            original = node.get(attribute)
            node.set(attribute, changed)
            with self.subTest(attribute=attribute):
                issue = ICONS.audit_icons([{'svg': ET.tostring(root, encoding='unicode')}], packages)
                self.assertEqual('icon_source_mismatch', issue[0]['code'])
            if original is None:
                del node.attrib[attribute]
            else:
                node.set(attribute, original)

    def test_missing_outside_and_audit_exemptions(self):
        with self.assertRaisesRegex(COMPONENT.ComponentError, "not installed"):
            ICONS.validate_svg_reference("lucide:test-shape@1.45.0", self.project)
        packages = self.install()
        with self.assertRaisesRegex(COMPONENT.ComponentError, "outside installed closure"):
            ICONS.validate_svg_reference("lucide:missing@1.45.0", self.project)
        svg = '<svg><path d="M0 0 L1 1"/></svg>'
        records = [{"svg": svg, "width": 24, "height": 24, "target": "small"},
                   {"svg": svg, "width": 24, "height": 24, "schematic": True},
                   {"svg": svg, "width": 500, "height": 500}]
        issues = ICONS.audit_icons(records, packages)
        self.assertEqual(["small"], [issue["target"] for issue in issues])
        (self.project / "custom.svg").write_text(svg)
        self.assertTrue(ICONS.validate_svg_reference("custom:custom.svg", self.project)["custom"])
        with self.assertRaises(COMPONENT.ComponentError):
            ICONS.validate_svg_reference("custom:../npm/icons/test-shape.svg", self.project)
        for body in ('<script/>', '<use href="https://example.invalid/icon.svg"/>', '<path onload="run()"/>'):
            (self.project / "custom.svg").write_text(f'<svg>{body}</svg>')
            with self.assertRaises(COMPONENT.ComponentError):
                ICONS.validate_svg_reference("custom:custom.svg", self.project)
        outside = self.root / "outside"
        outside.mkdir()
        (self.project / "linked").symlink_to(outside, target_is_directory=True)
        with self.assertRaises((COMPONENT.ComponentError, RequestError)):
            ICONS.use_icon(packages, "lucide:test-shape@1.45.0", self.project, "linked/icon.svg")
        self.assertFalse((outside / "icon.svg").exists())
        with self.assertRaisesRegex(COMPONENT.ComponentError, "separate"):
            ICONS.import_lucide(self.npm, self.npm / "nested")


if __name__ == "__main__":
    unittest.main()
