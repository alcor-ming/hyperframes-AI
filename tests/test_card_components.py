from html import escape
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.studio'))
import component_harness as component


class CardComponentsTest(unittest.TestCase):
    def test_all_families_have_two_layered_ratios_and_legacy_hashes_match(self):
        families = sorted((ROOT / '.studio/components').glob('*/16x9/v1'))
        self.assertEqual(len(families), 20)
        for old in families:
            # Existing metadata may predate today's validator; its frozen bytes remain authoritative.
            component._validate_hashes(old, ratio_contract=True)
            legacy = old.parent.parent / '4x3/v1'
            if legacy.exists():
                component._validate_hashes(legacy, ratio_contract=True)
            for ratio in ('16x9', '9x16'):
                path = old.parent.parent / ratio / 'v2'
                release = component.validate_component_release(path, allow_unapproved=True)
                self.assertEqual(release['metadata']['layers'], ['stage', 'text'])
                self.assertEqual(release['ratio'], ratio)
                self.assertNotEqual(release['package_sha256'], component.package_sha256(old))

    def test_install_verify_conflict_and_legacy_coexistence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / 'project'
            project.mkdir()
            mounts = []
            for ratio, version, scene in [('16x9', 1, 'old'), ('16x9', 2, 'wide'), ('9x16', 2, 'tall')]:
                source = ROOT / '.studio/components/cover-title-core' / ratio / f'v{version}'
                candidate = root / f'{ratio}-{version}'
                shutil.copytree(source, candidate)
                metadata = candidate / 'COMPONENT.md'
                metadata.write_text(metadata.read_text().replace('migration-ready', 'library-approved'))
                component.write_hashes(candidate)
                release = component.validate_component_release(candidate)
                width, height = (1920, 1080) if ratio == '16x9' else (1080, 1920)
                binding = dict(schema_version=2, component_ref=release['component_ref'], scene=scene,
                               slots=release['fixture']['slots'], surfaces=release['fixture'].get('surfaces', {}),
                               placement=dict(width=width, height=height), assets={},
                               timing=dict(offset=0, time_scale=1, hero_hold=0, handoff_hold=0))
                installed = component.install_component(candidate, project, binding)
                component.install_component(candidate, project, binding)
                prefix = 'data-card' if version == 2 else 'data-composition'
                attributes = {'data-component-ref': release['component_ref'],
                              'data-component-binding': f'component-bindings/{scene}.cover-title-core.json',
                              f'{prefix}-id': release['component_id'],
                              f'{prefix}-source' if version == 2 else f'{prefix}-src': f"{installed['component']['vendor_path']}/component.html",
                              'data-variable-values': json.dumps(component._binding_variable_values(binding)),
                              'data-start': '0', 'data-width': str(width), 'data-height': str(height)}
                for layer in (['stage', 'text'] if version == 2 else [None]):
                    attrs = {**attributes, **({'data-card-layer': layer, 'data-hf-layer': layer} if layer else {})}
                    mounts.append('<div ' + ' '.join(f'{key}="{escape(value, quote=True)}"' for key, value in attrs.items()) + '></div>')
            index = project / 'index.html'
            original = '\n'.join(mounts)
            index.write_text(original)
            verified = component.verify_installation(project)
            self.assertEqual(len(verified['components']), 3)
            for changed in (original.replace('data-hf-layer="text"', 'data-hf-layer="stage"', 1),
                            original.replace('data-card-source=', 'data-composition-src=', 1),
                            original.replace('data-card-id="cover-title-core"', 'data-card-id="wrong"', 1),
                            original.replace('data-card-layer="text"', 'data-card-layer="stage"', 1),
                            original.replace('data-component-ref="cover-title-core/9x16@v2"', 'data-component-ref="missing@v2"', 1)):
                index.write_text(changed)
                with self.assertRaises(component.ComponentError):
                    component.verify_installation(project)
            index.write_text(original)
            before = (project / 'COMPONENT_LOCK.json').read_bytes()
            with (candidate / 'component.html').open('a') as handle:
                handle.write('\n<!-- changed same version -->\n')
            component.write_hashes(candidate)
            with self.assertRaisesRegex(component.ComponentError, 'Existing vendor copy differs'):
                component.install_component(candidate, project, binding)
            self.assertEqual(before, (project / 'COMPONENT_LOCK.json').read_bytes())

    def test_forbidden_or_mismatching_layer_declarations_fail(self):
        source = ROOT / '.studio/components/cover-title-core/9x16/v2'
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / 'package'
            shutil.copytree(source, target)
            path = target / 'COMPONENT.md'
            path.write_text(path.read_text().replace('"stage",', '"background",'))
            component.write_hashes(target)
            with self.assertRaisesRegex(component.ComponentError, 'layers must be'):
                component.validate_component_release(target, allow_unapproved=True)
            shutil.copyfile(source / 'COMPONENT.md', path)
            for layer in ('background', 'captions'):
                html = target / 'component.html'
                html.write_text((source / 'component.html').read_text().replace('</template>', f'<div data-hf-layer="{layer}"></div></template>'))
                component.write_hashes(target)
                with self.assertRaisesRegex(component.ComponentError, 'cannot own background or captions'):
                    component.validate_component_release(target, allow_unapproved=True)


if __name__ == '__main__':
    unittest.main()
