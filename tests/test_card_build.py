"""Synthetic Plan-to-project checks; browser geometry is tested separately."""

import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / '.studio'))
import asset_store as STORE
import card_build as BUILD
import card_kit_assets as ASSETS
import component_harness as COMPONENT
import icon_sets as ICONS
from visual_plan import VisualPlanError


HEADER = '---\n{"plan_format":"3.5.2"}\n---\n## S01\n'
BODY = 'preset: F01\narea: full\ntitle: Heading @hello\n- Row @row\nnote: Note @note\nexit: exit'
PLAN = HEADER + '```card C1 · P001\n' + BODY + '\n```\n'


class CardBuildTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.project = self.root / 'project'
        self.project.mkdir()
        self.index = self.project / 'index.html'
        self.index.write_text('<html><body><section id="S01" data-start="0" data-duration="10">'
                              '<p id="handwritten">Keep me</p></section></body></html>', encoding='utf-8')
        source = self.root / 'source'
        ASSETS.export_card_kit(REPO, source)
        store = self.root / 'store'
        candidate = STORE.pack_source(store, source)
        acceptance = STORE.accept_component(store, candidate['component_ref'], candidate['package_sha256'],
                                            'Synthetic card build fixture only', runtime_root=REPO)
        COMPONENT.install_component(store / 'packages/card-kit/v1', self.project, {
            'schema_version': 3, 'component_ref': candidate['component_ref'], 'scene': 'S01',
            'usage': {'role': 'subject', 'required': True}}, acceptance=acceptance)
        runtime = self.project / 'runtime'
        runtime.mkdir()
        spoken = 'hello row note exit'
        cues = {'schema_version': 1, 'text': spoken, 'characters': [
            {'char': char, 'start': index / 3, 'end': (index + 1) / 3, 'aligned': True}
            for index, char in enumerate(spoken)], 'speech_intervals': [[0, len(spoken) / 3]]}
        (runtime / 'cues.json').write_text(json.dumps(cues), encoding='utf-8')
        geometry = patch.object(BUILD, 'check_geometry')
        self.geometry = geometry.start()
        self.addCleanup(geometry.stop)

    def snapshot(self):
        return {path.relative_to(self.project).as_posix(): path.read_bytes()
                for path in self.project.rglob('*') if path.is_file()}

    def build(self, plan=PLAN, **kwargs):
        return BUILD.build(self.project, plan, REPO, '16:9', **kwargs)

    def test_repeated_build_preserves_handwriting_and_removal_only_clears_generated_block(self):
        report = self.build()
        self.assertEqual(1, report['cards'])
        first = self.snapshot()
        self.build()
        self.assertEqual(first, self.snapshot())
        edited = self.index.read_text().replace('Keep me', 'Hand-edited outside generated content')
        self.index.write_text(edited, encoding='utf-8')
        self.build()
        self.assertIn('Hand-edited outside generated content', self.index.read_text())
        before = self.snapshot()
        report = self.build(HEADER + 'No cards in this Scene.\n')
        self.assertEqual(0, report['cards'])
        after = self.snapshot()
        self.assertNotIn(BUILD.START, self.index.read_text())
        self.assertIn('Hand-edited outside generated content', self.index.read_text())
        for name, data in before.items():
            if name not in {'index.html', BUILD.MANIFEST, 'project-config.json'}:
                self.assertEqual(data, after[name], name)

    def test_hand_edit_inside_generated_block_is_not_overwritten(self):
        self.build()
        self.index.write_text(self.index.read_text().replace(BUILD.START, BUILD.START + '\nmanual edit'), encoding='utf-8')
        before = self.snapshot()
        with self.assertRaisesRegex(VisualPlanError, 'content changed'):
            self.build()
        self.assertEqual(before, self.snapshot())

    def test_content_cannot_break_out_of_json_script(self):
        payload = '</script><script>alert(42)</script>'
        self.build(PLAN.replace('Heading', payload))
        html = self.index.read_text()
        self.assertNotIn(payload, html)
        match = re.search(r'<script type="application/json" data-hf-card-plan>(.*?)</script>', html, re.S)
        self.assertIsNotNone(match)
        data = json.loads(match[1])
        self.assertEqual(payload, data['scenes'][0]['cards'][0]['title']['text'])

    def test_invalid_cue_capacity_and_closure_fail_without_writes(self):
        cases = [PLAN.replace('@row', '@missing'),
                 PLAN.replace('- Row @row', '\n'.join(['- Row @row'] * 7)),
                 PLAN.replace('Heading @hello', 'Heading @hello [missing:icon@1]'),
                 PLAN.replace('Heading @hello', 'Heading @hello [custom:../outside.svg]')]
        for plan in cases:
            with self.subTest(plan=plan):
                before = self.snapshot()
                with self.assertRaises((VisualPlanError, COMPONENT.ComponentError)):
                    self.build(plan)
                self.assertEqual(before, self.snapshot())
        self.geometry.assert_not_called()

    def test_geometry_preflight_failure_does_not_write_project_or_plan(self):
        plan_path = self.root / 'ANIMATION_PLAN.md'
        plan_path.write_text(PLAN, encoding='utf-8')
        before = self.snapshot()
        self.geometry.side_effect = VisualPlanError('synthetic browser overflow')
        with self.assertRaisesRegex(VisualPlanError, 'browser overflow'):
            self.build(extra_files={plan_path: PLAN.replace('Heading', 'Changed').encode('utf-8')})
        self.assertEqual(before, self.snapshot())
        self.assertEqual(PLAN, plan_path.read_text())

    def test_plan_changed_during_prepare_is_preserved(self):
        plan_path = self.root / 'ANIMATION_PLAN.md'
        plan_path.write_text(PLAN, encoding='utf-8')
        concurrent = PLAN.replace('Heading', 'External edit')
        before = self.snapshot()
        prepare = BUILD.prepare

        def preparing(*args, **kwargs):
            result = prepare(*args, **kwargs)
            plan_path.write_text(concurrent, encoding='utf-8')
            return result

        with patch.object(BUILD, 'prepare', side_effect=preparing):
            with self.assertRaisesRegex(VisualPlanError, 'changed concurrently'):
                self.build(extra_files={plan_path: PLAN.replace('Heading', 'Studio edit').encode('utf-8')},
                           expected_before={plan_path: PLAN.encode('utf-8')})
        self.assertEqual(concurrent, plan_path.read_text())
        self.assertEqual(before, self.snapshot())

    def test_html_and_cues_changed_during_prepare_are_preserved(self):
        prepare = BUILD.prepare
        for relative in ('index.html', 'runtime/cues.json'):
            with self.subTest(relative=relative):
                path = self.project / relative
                original = path.read_bytes()
                concurrent = original + b'\n'
                before = self.snapshot()

                def preparing(*args, **kwargs):
                    result = prepare(*args, **kwargs)
                    path.write_bytes(concurrent)
                    return result

                with patch.object(BUILD, 'prepare', side_effect=preparing):
                    with self.assertRaisesRegex(VisualPlanError, 'changed concurrently'):
                        self.build()
                self.assertEqual({**before, relative: concurrent}, self.snapshot())
                path.write_bytes(original)

    def test_replace_only_target_card_and_commit_plan_with_build(self):
        other = '\nProse to preserve.\n```card C2 · P002\n' + BODY + '\n```\nTail.\n'
        original = PLAN + other
        changed = BUILD.replace_card(original, 'C1', BODY.replace('Heading', 'Changed'))
        self.assertEqual(original.replace('title: Heading', 'title: Changed', 1), changed)
        self.assertEqual(['C1', 'C2'], [row['id'] for row in BUILD.card_bodies(changed)])
        for identity, body in [('absent', BODY), ('C1', 'preset: BAD'),
                               ('C1', BODY + '\n```\n'), ('C1', 'x' * 65537)]:
            with self.subTest(identity=identity, body=body[:60]), self.assertRaises(VisualPlanError):
                BUILD.replace_card(original, identity, body)
        plan_path = self.root / 'ANIMATION_PLAN.md'
        plan_path.write_text(original, encoding='utf-8')
        self.build(changed, extra_files={plan_path: changed.encode('utf-8')})
        self.assertEqual(changed, plan_path.read_text())
        self.assertIn('Changed', self.index.read_text())

    def test_generated_verification_tracks_intent_and_real_inputs_not_plan_status(self):
        svg = self.project / 'figure.svg'
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0L20 20"/></svg>', encoding='utf-8')
        plan = PLAN.replace('Heading @hello', 'Heading @hello [custom:figure.svg]')
        self.build(plan)
        BUILD.verify_generated(self.project, plan)
        metadata_only = plan.replace('"plan_format":"3.5.2"', '"plan_format":"3.5.2","status":"approved"')
        BUILD.verify_generated(self.project, metadata_only)
        with self.assertRaisesRegex(VisualPlanError, 'differ from Plan'):
            BUILD.verify_generated(self.project, plan.replace('Heading', 'Changed'))
        for path in (self.index, self.project / 'runtime/cues.json', svg):
            with self.subTest(path=path):
                original = path.read_bytes()
                changed = (original.replace(BUILD.START.encode(), (BUILD.START + '\nmanual edit').encode())
                           if path == self.index else original + b'\n')
                path.write_bytes(changed)
                with self.assertRaisesRegex(VisualPlanError, 'changed'):
                    BUILD.verify_generated(self.project, plan)
                path.write_bytes(original)
        dependencies = json.loads((self.project / 'project-config.json').read_text())['snapshot_dependencies']
        self.assertIn(BUILD.MANIFEST, dependencies)

    def test_svg_replacement_and_removal_clear_only_owned_dependencies(self):
        for name in ('a.svg', 'b.svg', 'manual.svg'):
            (self.project / name).write_text('<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0L20 20"/></svg>', encoding='utf-8')
        config = self.project / 'project-config.json'
        config.write_text(json.dumps({'snapshot_dependencies': ['manual.svg'], 'custom_setting': 'preserved'}), encoding='utf-8')
        self.build(PLAN.replace('Heading @hello', 'Heading @hello [custom:a.svg]'))
        self.assertIn('a.svg', json.loads(config.read_text())['snapshot_dependencies'])
        self.build(PLAN.replace('Heading @hello', 'Heading @hello [custom:b.svg]'))
        data = json.loads(config.read_text())
        self.assertNotIn('a.svg', data['snapshot_dependencies'])
        self.assertIn('b.svg', data['snapshot_dependencies'])
        self.assertIn('manual.svg', data['snapshot_dependencies'])
        self.build(HEADER + 'No cards.\n')
        data = json.loads(config.read_text())
        self.assertNotIn('b.svg', data['snapshot_dependencies'])
        self.assertIn('manual.svg', data['snapshot_dependencies'])
        self.assertEqual('preserved', data['custom_setting'])
        self.assertTrue(all((self.project / name).exists() for name in ('a.svg', 'b.svg', 'manual.svg')))

    def test_unowned_generated_markers_are_not_overwritten(self):
        self.index.write_text(self.index.read_text().replace('</body>', BUILD.START + '\nowned elsewhere\n' + BUILD.END + '</body>'), encoding='utf-8')
        before = self.snapshot()
        with self.assertRaisesRegex(VisualPlanError, 'Unowned card markers'):
            self.build()
        self.assertEqual(before, self.snapshot())

    def test_removed_last_card_and_changed_scene_clock_require_rebuild(self):
        self.build()
        with self.assertRaisesRegex(VisualPlanError, 'differ from Plan'):
            BUILD.verify_generated(self.project, HEADER + 'No cards.\n')
        original = self.index.read_text()
        for old, new in [('data-start="0"', 'data-start="1"'),
                         ('data-duration="10"', 'data-duration="11"')]:
            with self.subTest(new=new):
                self.index.write_text(original.replace(old, new))
                with self.assertRaisesRegex(VisualPlanError, 'timing/source changed'):
                    BUILD.verify_generated(self.project, PLAN)
        self.index.write_text(original)
        BUILD.verify_generated(self.project, PLAN)
        self.build(HEADER + 'No cards.\n')
        BUILD.verify_generated(self.project, HEADER + 'No cards.\n')

    def test_installed_icon_set_projects_namespace_and_safe_theme_attributes(self):
        package = self.root / 'synthetic-lucide'
        (package / 'icons').mkdir(parents=True)
        (package / 'package.json').write_text(json.dumps({'name': 'lucide-static', 'version': '1.45.0', 'license': 'ISC'}), encoding='utf-8')
        (package / 'LICENSE').write_text('Synthetic test fixture, no downloaded third-party content.', encoding='utf-8')
        (package / 'icons/fixture.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M4 4L20 20"/></svg>', encoding='utf-8')
        source = self.root / 'icon-source'
        ICONS.import_lucide(package, source)
        store = self.root / 'store'
        candidate = STORE.pack_source(store, source)
        acceptance = STORE.accept_component(store, candidate['component_ref'], candidate['package_sha256'],
                                            'Synthetic icon set acceptance only', runtime_root=REPO)
        COMPONENT.install_component(store / 'packages/lucide-static/v1', self.project, {
            'schema_version': 3, 'component_ref': candidate['component_ref'],
            'usage': {'role': 'icon-set', 'required': True}}, acceptance=acceptance)
        reference = 'lucide:fixture@1.45.0'
        plan = PLAN.replace('Heading @hello', f'Heading @hello [{reference}]')
        self.build(plan)
        html = self.index.read_text()
        payload = json.loads(re.search(r'<script type="application/json" data-hf-card-plan>(.*?)</script>', html, re.S)[1])
        serialized = payload['svg'][reference]
        self.assertTrue(serialized.startswith('<svg '))
        svg = ET.fromstring(serialized)
        self.assertEqual('{http://www.w3.org/2000/svg}svg', svg.tag)
        self.assertNotIn('style', svg.attrib)
        self.assertEqual(reference, svg.attrib['data-icon'])
        self.assertRegex(svg.attrib['data-icon-sha256'], r'^[a-f0-9]{64}$')
        self.assertEqual('currentColor', svg.attrib['stroke'])
        self.assertEqual('var(--appearance-lines-icon-width,2)', svg.attrib['stroke-width'])
        self.assertEqual('var(--appearance-colors-text)', svg.attrib['color'])
        BUILD.verify_generated(self.project, plan)


if __name__ == '__main__':
    unittest.main()
