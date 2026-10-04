import test_root_deploy as fixtures
from unittest import mock


class RetirementTests(fixtures.RootDeploymentTests):
    def test_modified_retired_skill_is_preserved_outside_discovery_and_rollback(self):
        old = self.package('old')
        skill = '.agents/skills/retired/SKILL.md'
        self.add_files(old, {skill: 'original', 'runtime/python/retired.whl': 'old dependency'})
        fixtures.deploy.deploy(old, self.root, self.config)
        (self.root / skill).write_bytes(b'my custom instructions')
        new = self.package('new')
        result = fixtures.deploy.deploy(new, self.root, None)
        self.assertFalse((self.root / skill).exists())
        self.assertFalse((self.root / 'runtime/python/retired.whl').exists())
        record = result['retired_preserved'][0]
        self.assertEqual(skill, record['original'])
        self.assertFalse(record['preserved'].startswith('.agents/'))
        self.assertEqual(b'my custom instructions', (self.root / record['preserved']).read_bytes())
        restored = fixtures.deploy.recover(self.root, rollback=True)
        self.assertEqual('restored_with_local_modifications', restored['integrity'])
        self.assertEqual([skill], restored['restored_modified_files'])
        with self.assertRaisesRegex(ValueError, 'Locally modified managed file'):
            fixtures.deploy.verify_root(self.root)
        self.assertEqual(b'my custom instructions', (self.root / skill).read_bytes())
        self.assertTrue((self.root / 'runtime/python/retired.whl').is_file())
        self.assertFalse((self.root / record['preserved']).exists())

    def test_preservation_write_failure_restores_original_bytes(self):
        old = self.package('old')
        skill = '.agents/skills/retired/SKILL.md'
        self.add_files(old, {skill: 'original'})
        fixtures.deploy.deploy(old, self.root, self.config)
        (self.root / skill).write_bytes(b'custom')
        new = self.package('new')
        replace = fixtures.deploy.replace_file
        def fail(source, destination, data=None):
            if destination.suffix == '.bin':
                raise OSError('preservation disk failure')
            return replace(source, destination, data)
        with mock.patch.object(fixtures.deploy, 'replace_file', side_effect=fail):
            with self.assertRaisesRegex(OSError, 'preservation disk failure'):
                fixtures.deploy.deploy(new, self.root, None)
        self.assertEqual(b'custom', (self.root / skill).read_bytes())
        self.assertEqual('old', (self.root / 'work.cmd').read_text())
        self.assertFalse((self.root / fixtures.deploy.PENDING).exists())



for name in fixtures.RootDeploymentTests.__dict__:
    if name.startswith('test_'):
        setattr(RetirementTests, name, None)
