"""Content CLI acceptance against isolated lifecycle and synthetic exports only."""
import copy
import json
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch

import test_v370_cli as fixtures
from test_work_cli import WORK_CLI as cli
from test_v372_adapter import exports, workbook
import content_retro as content
import visual_memory as memory


class ContentTest(unittest.TestCase):
    run_cli = fixtures.V370CliTest.run_cli
    call = fixtures.V370CliTest.call
    update = fixtures.V370CliTest.update

    def setUp(self):
        fixtures.V370CliTest.setUp(self)
        self.draft = self.call('preview', 'register')
        self.movie = self.root / 'published.mp4'
        self.movie.write_bytes(b'synthetic fixture; never rendered')
        self.files = self.root / 'exports'; self.files.mkdir()
        exports(self.files)
        patch.object(content, 'duration', return_value=13).start()
        self.table = self.root / 'timings.json'
        self.table.write_text(json.dumps([{'scene':'S01','anchor':'P001','start':0,'end':13,
            'characters':[{'char':'开','start':1,'end':1.5},{'char':'场','start':3,'end':3.5}]}]))

    def link(self, target='pub1', *extra, variables=None, source=None):
        return json.loads(self.call('content', 'link', target, *(source or ('--draft', self.draft)),
            '--file', str(self.movie), '--platform', 'douyin', '--title', '合成主题', '--cover-text', '封面',
            '--published-at', '2026-10-01T00:00:00+08:00', '--ratio', '9:16',
            *(variables if variables is not None else ('--no-variable',)), *extra))

    def imported(self, target='pub1', stage='long-tail'):
        return json.loads(self.call('content', 'import', target, '--dir', str(self.files), '--cutoff', '2026-10-02',
                                   *(('--stage', stage) if stage else ())))

    def tree(self, directory):
        return {str(p.relative_to(directory)): memory.digest(p) for p in directory.rglob('*') if p.is_file()}

    def test_link_draft_final_account_experiments_and_history(self):
        state = cli.read_json(self.variant / 'variant.yaml'); state['account'] = None
        cli.write_variant(self.variant, state)
        before = self.tree(self.variant)
        with self.assertRaisesRegex(cli.HarnessError, 'account'):
            self.link()
        first = self.link('pub1', '--account', 'test-account')
        self.assertEqual('test-account', first['account'])
        self.assertEqual(before['variant.yaml'], memory.digest(self.variant/'variant.yaml'))
        for variable in [(), ('--variable','错=值'), ('--variable','其他=值')]:
            with self.assertRaises(cli.HarnessError):
                self.link('invalid','--account','test-account',variables=variable)
        second = self.link('pub1','--account','test-account',variables=('--variable','其他:节奏=更快'))
        self.assertEqual('无', second['history'][0]['previous']['variables'][0]['variable'])
        self.assertTrue(second['history'][0]['changed_at'])
        final = self.variant/'final'; final.mkdir(exist_ok=True)
        shutil.copyfile(self.movie, final/'final.mp4')
        cli.write_json(final/'manifest.json', {'final_sha256':memory.digest(self.movie),'source_preview':self.draft})
        linked = self.link('final','--account','test-account',source=('--final',))
        self.assertEqual('Final',linked['source']['type'])
        self.assertEqual(memory.digest(self.movie),linked['file_sha256'])
        (final/'final.mp4').write_bytes(b'changed')
        with self.assertRaisesRegex(cli.HarnessError,'Final hash'):
            self.link('bad','--account','test-account',source=('--final',))
        with self.assertRaises(cli.HarnessError):
            self.link('bad','--account','test-account',source=('--draft','draft-v999'))

    def test_source_tampering_and_explicit_scope(self):
        with self.assertRaisesRegex(cli.HarnessError,'explicit'):
            self.run_cli('content','check','pub1')
        source = self.variant/'previews'/self.draft/'source-snapshot/compositions/S01.html'
        source.write_text('<p>tampered</p>')
        with self.assertRaises(cli.HarnessError):
            self.link()

    def test_import_copies_hashes_stages_duration_and_retention(self):
        self.link()
        first, second = self.imported(stage='early'), self.imported(stage=None)
        self.assertNotEqual(first['id'],second['id'])
        self.assertEqual('unmarked',second['stage'])
        self.assertEqual(1,first['days_after_publication'])
        directory = self.variant/'retro/content/pub1/imports'
        for meta in (first,second):
            for item in meta['files']:
                target = directory/meta['id']/item['path']
                original = self.files/item['original_name']
                self.assertEqual(original.read_bytes(),target.read_bytes())
                self.assertNotEqual(original.stat().st_ino,target.stat().st_ino)
                self.assertFalse(target.is_symlink())
        workbook(self.files/'内容吸引力.xlsx', {'指标数据':[['平均播放时长'],['21秒']],
            '进度分析':[['时间','跳过率','回看率'],['00:00-00:20','1%','2%']]})
        before = self.tree(directory)
        with self.assertRaisesRegex(cli.HarnessError,'duration'):
            self.imported()
        self.assertEqual(before,self.tree(directory))

    def test_alignment_open_refresh_comparison_and_check(self):
        self.link('control'); self.imported('control')
        self.link('pub1','--timings',str(self.table),variables=('--variable','开头写法=先问问题','--compare','control'))
        imported = self.imported()
        result = json.loads(self.call('content','open','pub1'))
        self.assertEqual('开',result['analysis']['opening']['text_0_2'])
        self.assertEqual('场',result['analysis']['opening']['text_2_5'])
        self.assertEqual(8,result['analysis']['segments'][0]['overlaps'][0]['seconds'])
        self.assertEqual(imported['normalized_sha256'],result['import_sha256'])
        path = Path(result['path'])
        self.assertIn('| 指标 | pub1 | control |',path.read_text())
        path.write_text(path.read_text()+'\n手填保留\n')
        self.imported(stage='early')
        self.call('content','open','pub1')
        self.assertIn('手填保留',path.read_text())
        self.assertEqual([],json.loads(self.call('content','check','pub1'))['findings'])
        text = path.read_text().replace('| | | | |','| 低完播 | S01 | 错误层 | Script 开头与衔接 |')
        path.write_text(text)
        found = json.loads(self.call('content','check','pub1'))['findings']
        self.assertTrue(any('非法归因层' in f for f in found))
        self.assertTrue(any('card' in f for f in found))
        self.assertEqual(1,len(json.loads(self.call('content','open','pub1'))['traffic_changes']))

    def test_timing_validation_section_map_priority_and_unaligned(self):
        self.link('unaligned');self.imported('unaligned')
        result=json.loads(self.call('content','open','unaligned'))
        self.assertEqual('未对齐',result['analysis']['alignment'])
        self.assertEqual(2,len(result['analysis']['segments']))
        bad=json.loads(self.table.read_text());bad[0]['anchor']='P999'
        self.table.write_text(json.dumps(bad))
        with self.assertRaisesRegex(cli.HarnessError,'Anchor'):
            self.link('bad','--timings',str(self.table))
        # A section_map frozen as an explicit project dependency follows the real snapshot path.
        project_map=self.project/'section_map.json'
        bad[0]['anchor']='P001'
        project_map.write_text(json.dumps({'sections':bad}))
        cli.write_json(self.project/'project-config.json', {'snapshot_dependencies':['section_map.json']})
        self.draft=self.call('preview','register')
        linked=self.link('mapped')
        self.assertEqual('source-snapshot/section_map.json',linked['timing_source'])
        self.imported('mapped')
        result=json.loads(self.call('content','open','mapped'))
        self.assertEqual('开',result['analysis']['opening']['text_0_2'])

    def test_summary_groups_latest_long_tail_exclusions_and_readonly(self):
        for n in range(5):
            target=f'pub{n}'
            self.link(target,variables=('--variable','第一画面=实物'))
            self.imported(target)
        latest=self.imported('pub0')
        self.imported('pub0',stage='early'); self.imported('pub0',stage=None)
        self.link('excluded');self.imported('excluded',stage=None)
        state=cli.read_json(self.variant/'variant.yaml');state['account']=None
        cli.write_variant(self.variant,state)
        for n in range(4):
            self.link(f'other{n}','--account','other');self.imported(f'other{n}')
        with patch.object(content,'duration',return_value=90):
            self.link('longer','--account','other')
        # The independent time series must agree with the longer publication.
        workbook(self.files/'内容吸引力.xlsx', {'指标数据':[['平均播放时长','2s 跳出率','5s 完播率'],['21秒','60%','30%']],
            '进度分析':[['时间','跳过率','回看率'],['00:00-01:30','1%','2%']]})
        self.imported('longer')
        before=self.tree(self.root/'works')
        result=json.loads(self.call('content','summary'))
        self.assertEqual(before,self.tree(self.root/'works'))
        self.assertEqual([5,4,1],sorted((g['count'] for g in result['groups']),reverse=True))
        self.assertTrue(all(('deviations' in g)==(g['count']>=5) for g in result['groups']))
        self.assertEqual(latest['id'],next(p for p in result['publications'] if p['publication']=='pub0')['import'])
        self.assertEqual(.6,next(p for p in result['publications'] if p['publication']=='pub0')['metrics']['bounce_2s'])
        self.assertEqual(3,len(result['excluded_imports']))
        self.assertEqual(5,len([r for r in result['experiments'] if r['variable']=='第一画面']))
        self.assertEqual(10,len(result['topics']))
        self.assertTrue(Path(result['path']).is_file())
        visual=json.loads(self.call('retro','summary'))
        self.assertEqual([],visual['defects'])

    def test_comparison_across_works_and_ambiguous_ids(self):
        original_variant, original_scope = self.variant, self.scope
        other_work = self.variant.parent.parent.with_name('work-other')
        shutil.copytree(self.variant.parent.parent, other_work)
        self.variant = other_work/'variants/main'
        self.scope = ('--work',other_work.name,'--variant','main')
        self.link('control');self.imported('control')
        self.variant,self.scope = original_variant,original_scope
        self.link('subject',variables=('--variable','开头写法=更直接','--compare','control'))
        self.imported('subject')
        self.assertIn('| 指标 | subject | control |',Path(json.loads(self.call('content','open','subject'))['path']).read_text())
        self.link('control')
        with self.assertRaisesRegex(cli.HarnessError,'ambiguous'):
            self.link('ambiguous',variables=('--variable','开头写法=更短','--compare','control'))
        self.link('qualified',variables=('--variable','开头写法=更短','--compare','work-other/main/control'))

    def test_import_binding_rejects_copy_but_accepts_variable_history(self):
        self.link('a');self.imported('a')
        self.link('a',variables=('--variable','第一画面=修改1'))
        self.imported('a')
        self.link('a',variables=('--variable','第一画面=修改2'))
        self.assertTrue(json.loads(self.call('content','open','a'))['import_id'])
        self.link('b')
        shutil.copytree(self.variant/'retro/content/a/imports',self.variant/'retro/content/b/imports')
        with self.assertRaisesRegex(cli.HarnessError,'another publication'):
            self.call('content','open','b')
        with self.assertRaisesRegex(cli.HarnessError,'another publication'):
            self.call('content','summary')

    def test_package_excludes_content_summary_and_line_rules(self):
        import root_deploy
        from test_release_cli import RELEASE
        with self.assertRaisesRegex(ValueError, 'user/runtime content'):
            root_deploy.managed({'content-summary/summary.json': 'a' * 64})
        self.assertFalse(RELEASE.public_source('content-summary/summary.json'))
        self.assertFalse(RELEASE.public_source('.studio/content-summary/summary.json'))
        text = (Path(cli.__file__).parent/'templates/CONTENT_RETRO.template.md').read_text()
        text = text.replace('| | | | |', '| 信号 | S01 | 开头 | Script 开头与衔接 |')
        self.assertEqual([],content.check_text(text,'showcase/pdoom'))
        self.assertEqual([],content.check_text(text,'explainer'))
        self.assertTrue(content.check_text(text,'explainer/math-rap'))
        self.assertTrue(content.check_text('## 找问题\n## 找优秀','card'))

    def test_reject_symlinks_and_normalized_tampering(self):
        self.link(); meta=self.imported()
        target=self.variant/'retro/content/pub1/imports'/meta['id']/'normalized.json'
        target.write_text('{}')
        with self.assertRaisesRegex(cli.HarnessError,'changed'):
            self.call('content','open','pub1')
        outside=self.root/'outside';outside.mkdir()
        (self.variant/'retro/content/link').symlink_to(outside,target_is_directory=True)
        with self.assertRaises(cli.HarnessError):
            self.link('link')
        self.assertEqual([],list(outside.iterdir()))


if __name__ == '__main__':
    unittest.main()
