"""Isolated math package installation, transactional build and real glyph checks."""

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / '.studio'))
import asset_store as STORE
import appearance
import component_harness as COMPONENT
import math_build as BUILD
import math_kit_assets as ASSETS
from storage import snapshot_files
from visual_plan import VisualPlanError

FONT = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
HEADER = '---\n{"plan_format":"3.5.2","series_binding":{"spec":"math-rap"}}\n---\n## S01\n'


class MathBuildTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.project = self.root / 'project'
        self.project.mkdir()
        (self.project / 'DESIGN.md').write_text('Synthetic math fixture only.\n')
        self.index = self.project / 'index.html'
        self.index.write_text('<html><body><section id="S01" data-start="0" data-duration="10" '
                              'style="position:relative;width:1920px;height:1080px">'
                              '<p>Keep me</p></section></body></html>', encoding='utf-8')
        source = self.root / 'source'
        ASSETS.export_math_kit(REPO, source)
        store = self.root / 'store'
        candidate = STORE.pack_source(store, source)
        acceptance = STORE.accept_component(store, candidate['component_ref'], candidate['package_sha256'],
                                            'Synthetic math build fixture only', runtime_root=REPO)
        runtime = self.project / 'runtime'
        runtime.mkdir()
        selections = {'mode': 'explainer', 'motion': {}}
        for kind, payload in (('theme', {'tokens': {'colors': {'text': '#111111', 'accent': '#116655'}}}),
                              ('background', {'renderer': 'solid', 'parameters': {'color': '#ffffff'}})):
            source = self.root / ('source-' + kind)
            source.mkdir()
            (source / 'asset.json').write_text(json.dumps({
                'schema_version': 2, 'id': 'fixture-' + kind, 'kind': kind, 'version': 1,
                'contract_version': 1, 'parameters': {}, 'compatibility': {}, 'entry': 'entry.json'}))
            (source / 'entry.json').write_text(json.dumps(payload))
            candidate = STORE.pack_source(store, source)
            STORE.accept_component(store, candidate['component_ref'], candidate['package_sha256'],
                                   'Synthetic math appearance fixture only', runtime_root=REPO)
            selections[kind] = {'ref': candidate['component_ref'], 'kind': kind,
                                'package_sha256': candidate['package_sha256']}
        with patch.object(STORE, 'resolve_asset_closure',
                          side_effect=lambda root, refs: STORE._accepted_closure(store, refs, runtime_root=root)):
            lock = appearance.resolve(REPO, selections)
            appearance.materialize(REPO, self.project, lock)
        COMPONENT.install_component(store / 'packages/math-kit/v1', self.project, {
            'schema_version': 3, 'component_ref': 'math-kit@v1', 'scene': 'S01',
            'usage': {'role': 'subject', 'required': True}}, acceptance=acceptance)
        cues = {'schema_version': 1, 'text': 'ab', 'characters': [
            {'char': char, 'start': i + 1, 'end': i + 1.5, 'aligned': True} for i, char in enumerate('ab')],
            'speech_intervals': [[1, 2.5]]}
        (runtime / 'cues.json').write_text(json.dumps(cues), encoding='utf-8')
        self.font = self.project / 'font.ttf'
        self.font.write_bytes(FONT.read_bytes() if FONT.is_file() else b'synthetic-font')
        self.intent = {'units': [{'id': 'x', 'symbol': 'x', 'graphic': 'square'}],
                       'symbols': {'x': 'square'}, 'invariants': ['identity'],
                       'zero_basics': [{'relation': 'unknown', 'action': 'square'}],
                       'cues': [{'cue': 'a', 'keep': [], 'reveal': ['x'], 'remove': []}]}
        self.math = {'font': {'path': 'font.ttf', 'sha256': BUILD.digest(self.font.read_bytes()), 'characters': 'x'},
                     'items': [{'id': 'x', 'kind': 'unknown', 'box': [100, 100, 180, 180], 'label': 'x'}]}
        self.geometry_patch = patch.object(BUILD, 'check_geometry')
        self.geometry = self.geometry_patch.start()
        self.addCleanup(self.geometry_patch.stop)

    def plan(self):
        return HEADER + '```math-plan\n' + json.dumps(self.intent) + '\n```\n```math\n' + json.dumps(self.math) + '\n```\n'

    def build(self, plan=None, **kwargs):
        return BUILD.build(self.project, self.plan() if plan is None else plan, REPO, '16:9', **kwargs)

    def snapshot(self):
        return {path.relative_to(self.project).as_posix(): path.read_bytes()
                for path in self.project.rglob('*') if path.is_file()}

    def test_idempotence_handwriting_and_removal(self):
        self.assertEqual(1, self.build()['items'])
        before = self.snapshot()
        self.build()
        self.assertEqual(before, self.snapshot())
        self.index.write_text(self.index.read_text().replace('Keep me', 'Hand edited'))
        self.build()
        BUILD.verify_generated(self.project, self.plan())
        removed = self.plan().split('```math\n')[0]
        self.build(removed)
        self.assertNotIn(BUILD.START, self.index.read_text())
        self.assertIn('Hand edited', self.index.read_text())
        BUILD.verify_generated(self.project, removed)

    def test_generated_content_and_unowned_markers_are_protected(self):
        self.build()
        self.index.write_text(self.index.read_text().replace(BUILD.START, BUILD.START + '\nmanual edit'))
        before = self.snapshot()
        with self.assertRaisesRegex(VisualPlanError, 'content changed'):
            self.build()
        self.assertEqual(before, self.snapshot())

    def test_input_and_plan_changes_require_rebuild(self):
        self.build()
        BUILD.verify_generated(self.project, self.plan().replace('"plan_format":', '"status":"approved","plan_format":'))
        with self.assertRaisesRegex(VisualPlanError, 'differs from Plan'):
            BUILD.verify_generated(self.project, HEADER + 'No math.\n')
        manifest = json.loads((self.project / BUILD.MANIFEST).read_text())
        self.assertIn('runtime/math-project.js', manifest['inputs'])
        self.assertIn('font.ttf', manifest['inputs'])
        for relative in manifest['inputs']:
            path = self.project / relative
            original = path.read_bytes()
            path.write_bytes(original + b'\n')
            with self.subTest(relative=relative), self.assertRaisesRegex(VisualPlanError, 'input changed'):
                BUILD.verify_generated(self.project, self.plan())
            path.write_bytes(original)
        closure = snapshot_files(self.project)
        self.assertIn('font.ttf', closure)
        self.assertIn('runtime/math-project.js', closure)
        for name in manifest['inputs']:
            self.assertIn(name, closure)

    def test_cue_order_range_and_font_hash_fail_without_writes(self):
        for cue in ('missing', {'time': 20}):
            self.intent['cues'][0]['cue'] = cue
            before = self.snapshot()
            with self.assertRaises(ValueError):
                self.build()
            self.assertEqual(before, self.snapshot())
        self.intent['cues'][0]['cue'] = 'a'
        self.intent['cues'].append({'cue': 'a', 'keep': ['x'], 'reveal': [], 'remove': []})
        with self.assertRaisesRegex(VisualPlanError, 'increase strictly'):
            self.build()
        self.intent['cues'].pop()
        self.math['font']['sha256'] = '0' * 64
        with self.assertRaisesRegex(VisualPlanError, 'font hash'):
            self.build()
        self.geometry.assert_not_called()

    def test_removed_font_dependency_rejected_before_snapshot(self):
        self.build()
        config = self.project / 'project-config.json'
        data = json.loads(config.read_text())
        data['snapshot_dependencies'].remove('font.ttf')
        config.write_text(json.dumps(data))
        self.assertNotIn('font.ttf', snapshot_files(self.project))
        with self.assertRaisesRegex(VisualPlanError, 'outside the snapshot closure'):
            BUILD.verify_generated(self.project, self.plan())

    def test_browser_failure_and_concurrent_edits_do_not_write(self):
        before = self.snapshot()
        self.geometry.side_effect = VisualPlanError('synthetic font fallback')
        with self.assertRaisesRegex(VisualPlanError, 'font fallback'):
            self.build()
        self.assertEqual(before, self.snapshot())
        self.geometry.side_effect = lambda *args: self.font.write_bytes(b'concurrent edit')
        with self.assertRaisesRegex(VisualPlanError, 'changed concurrently'):
            self.build()
        self.assertEqual({**before, 'font.ttf': b'concurrent edit'}, self.snapshot())

    def test_scene_binding_must_cover_target(self):
        plan = self.plan().replace('S01', 'S02')
        self.index.write_text(self.index.read_text().replace('S01', 'S02'))
        before = self.snapshot()
        with self.assertRaisesRegex(VisualPlanError, 'binding does not cover'):
            self.build(plan)
        self.assertEqual(before, self.snapshot())

    def test_font_escape_and_symlink_are_rejected(self):
        for relative in ('../outside.ttf', '/tmp/outside.ttf', 'font.ttf?remote'):
            self.math['font']['path'] = relative
            before = self.snapshot()
            with self.subTest(relative=relative), self.assertRaises(ValueError):
                self.build()
            self.assertEqual(before, self.snapshot())
        self.math['font']['path'] = 'font.ttf'
        original = self.font.read_bytes()
        outside = self.root / 'outside.ttf'
        outside.write_bytes(original)
        self.font.unlink()
        self.font.symlink_to(outside)
        with self.assertRaises(ValueError):
            self.build()
        self.assertEqual(original, outside.read_bytes())

    def test_failed_atomic_write_restores_prior_project(self):
        before = self.snapshot()
        replace = BUILD.os.replace
        calls = 0

        def failing(source, target):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('synthetic disk failure')
            return replace(source, target)

        with patch.object(BUILD.os, 'replace', side_effect=failing):
            with self.assertRaisesRegex(OSError, 'disk failure'):
                self.build()
        self.assertEqual(before, self.snapshot())

    @unittest.skipUnless(FONT.is_file(), 'Local DejaVu font unavailable')
    def test_real_browser_frozen_font_and_missing_chinese_glyph(self):
        self.geometry_patch.stop()
        browser = os.environ.get('HYPERFRAMES_BROWSER_PATH') or os.environ.get('CHROME_PATH') or '/usr/bin/google-chrome'
        self.math['font']['characters'] = 'x = 2'
        self.math['items'][0]['label'] = 'x = 2'
        self.build(browser=browser)
        before = self.snapshot()
        self.math['font']['characters'] = 'x = 2中'
        with self.assertRaisesRegex(VisualPlanError, 'missing glyphs|fallback font'):
            self.build(browser=browser)
        self.assertEqual(before, self.snapshot())
        self.math['font']['characters'] = 'x'
        self.math['items'][0] = {'id': 'x', 'kind': 'edge', 'box': [100, 100, 180, 180],
                                 'from': [100, 10], 'to': [300, 10], 'length': 100,
                                 'label': 'x', 'duration': 1}
        with self.assertRaisesRegex(VisualPlanError, 'geometry outside Scene frame'):
            self.build(browser=browser)
        self.assertEqual(before, self.snapshot())


if __name__ == '__main__':
    unittest.main()
