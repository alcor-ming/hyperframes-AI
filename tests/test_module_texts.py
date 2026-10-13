"""Text ownership, font closure and explicit human confirmation regressions."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import test_appearance_resolver as fixture
import appearance
import designs
import module_texts


def inventory():
    return {'schema_version': 1, 'complete': True, 'items': [{'id':'title', 'text':'增长 30%',
        'scene':'S01', 'asset':'sample', 'start':0, 'end':2, 'kind':'independent',
        'embedded':True, 'text_type':'title', 'ownership_allowed':True, 'font_coverage':True}]}


class TextTests(unittest.TestCase):
    def test_plain_module_cannot_skip_inventory(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            (project / 'COMPONENT_LOCK.json').write_text(json.dumps({'components':[{'asset_kind':'module'}]}))
            self.assertTrue(module_texts.needs_inventory(project))

    def test_each_scene_requires_explicit_confirmation(self):
        value = inventory()
        value['items'].append({**value['items'][0], 'scene':'S02'})
        for choices in ([], ['S01'], ['S01', 'S02', 'S03']):
            with self.assertRaisesRegex(ValueError, 'per Scene'):
                module_texts.confirmation(value, choices)
        self.assertEqual(['S01', 'S02'], [row['scene'] for row in module_texts.confirmation(value, ['S02','S01'])])
        with self.assertRaisesRegex(ValueError, 'per Scene'):
            module_texts.confirmation(value, ['S01','S02'], automatic=True)

    def test_missing_glyphs_and_undeclared_ownership_cannot_accept(self):
        for field, message in [('font_coverage','font closure'), ('ownership_allowed','declaration')]:
            value = inventory(); value['items'][0][field] = False
            with self.assertRaisesRegex(ValueError, message):
                module_texts.confirmation(value, ['S01'])

    def test_diagnostics_delegate_layout_and_include_numeric_review(self):
        value = inventory(); value['items'][0]['ownership_allowed'] = False
        result = module_texts.diagnostics(value['items'])
        self.assertEqual('undeclared', result['layout'][0]['status'])
        self.assertNotIn('passed', result['layout'][0])
        self.assertEqual({'numeric_fact_review','undeclared_embedded_text'}, {row['kind'] for row in result['findings']})
        self.assertEqual(2, result['reading'][0]['seconds'])
        self.assertIsNone(result['reading'][0]['verdict'])


class CardFontTests(unittest.TestCase):
    setUp = fixture.AppearanceResolverTest.setUp
    ref = fixture.AppearanceResolverTest.ref

    def test_fonts_are_frozen_installed_and_verified_without_theme(self):
        card_dir = self.root / 'font-card'; card_dir.mkdir()
        (card_dir / 'font.ttf').write_bytes(b'synthetic font closure')
        (card_dir / 'LICENSE').write_text('Synthetic fixture license')
        card = {'id':'font-card','fonts':[{'family':'Fixture', 'path':'font.ttf', 'license':'LICENSE'}]}
        fonts = designs.font_manifest(card, card_dir)
        with patch('asset_store.resolve_asset_closure', return_value=[]), patch.object(designs, 'card_path', return_value=card_dir):
            lock = appearance.resolve(self.root, {}, {'capabilities':designs.legacy_capabilities('showcase'), 'card_fonts':fonts})
            project = self.root / 'project'; project.mkdir()
            appearance.materialize(self.root, project, lock)
            appearance.verify(project, lock)
            source = project / fonts['fonts'][0]['path']
            self.assertEqual(b'synthetic font closure', source.read_bytes())
            source.write_bytes(b'changed')
            with self.assertRaisesRegex(appearance.AppearanceError, 'font differs'):
                appearance.verify(project, lock)
        card['fonts'][0]['path'] = '../outside.ttf'
        with self.assertRaises(designs.DesignError):
            designs.font_manifest(card, card_dir)
