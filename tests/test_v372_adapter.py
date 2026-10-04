"""Offline XLSX fixtures: no platform exports or network access."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from xml.sax.saxutils import escape
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".studio"))
from content_adapters import ApiAdapter, normalize


def workbook(path, sheets):
    """Write synthetic shared/inline/numeric/sparse cells and nonstandard targets."""
    shared = []
    with ZipFile(path, "w") as archive:
        sheet_nodes, rels = [], []
        for number, (name, rows) in enumerate(sheets.items(), 1):
            sheet_nodes.append(f'<sheet name="{escape(name)}" sheetId="{number}" r:id="id{number}"/>')
            rels.append(f'<Relationship Id="id{number}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/export{number + 10}.xml"/>')
            xml_rows = []
            for ri, row in enumerate(rows, 1):
                cells = []
                for ci, value in enumerate(row):
                    if value is None:
                        continue
                    reference = f'{chr(65 + ci)}{ri}'
                    if isinstance(value, (int, float)):
                        cell = f'<c r="{reference}" s="1"><v>{value}</v></c>'
                    elif ci % 2:
                        cell = f'<c r="{reference}" t="inlineStr"><is><t>{escape(value)}</t></is></c>'
                    else:
                        shared.append(value)
                        cell = f'<c r="{reference}" t="s"><v>{len(shared)-1}</v></c>'
                    cells.append(cell)
                xml_rows.append(f'<row r="{ri}">{"".join(cells)}</row>')
            archive.writestr(f'xl/worksheets/export{number + 10}.xml', '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>' + ''.join(xml_rows) + '</sheetData></worksheet>')
        archive.writestr('xl/workbook.xml', '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>' + ''.join(sheet_nodes) + '</sheets></workbook>')
        archive.writestr('xl/_rels/workbook.xml.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + ''.join(rels) + '</Relationships>')
        archive.writestr('xl/sharedStrings.xml', '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">' + ''.join(f'<si><t>{escape(v)}</t></si>' for v in shared) + '</sst>')
        archive.writestr('xl/styles.xml', '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><cellXfs count="2"><xf numFmtId="0"/><xf numFmtId="10"/></cellXfs></styleSheet>')
    return path


def exports(root):
    return [
        workbook(root / '内容吸引力.xlsx', {
            '指标数据': [['封面点击率', '平均播放时长', '完播率', '2s 跳出率', '平均播放占比', '5s 完播率', '新增指标'], ['10%', '21秒', .2, '60%', '35%', '30%', '保留原文']],
            '进度分析': [['时间', '跳过率', '回看率'], ['00:00-00:08', '2%', None], ['00:08-00:13', '.5%', '4%']]}),
        workbook(root / '参与度.xlsx', {
            '指标数据': [['指标', '数值'], ['点赞率', '5%'], ['评论率', '1%'], ['分享率', '2%'], ['收藏率', '3%'], ['弹幕量', 4]],
            '弹幕': [['时间', '当前作品', '同类作品'], ['00:00-00:08', 3, 10], ['00:08-00:13', 1, 12]]}),
        workbook(root / '观众.xlsx', {
            '指标数据': [['涨粉量', '涨粉率', '脱粉量', '脱粉率', '不感兴趣量', '不感兴趣率'], [8, '.8%', 2, '.2%', 1, '.1%']],
            '涨粉量-累计-每天趋势数据': [['日期', '涨粉量', '抖音', '抖音精选'], ['2026-10-01', 3, 2, 1], ['2026-10-02', 5, 4, 1]]}),
        workbook(root / '全量指标.xlsx', {'数据': [['日期', '总播放量', '2 秒跳出率', '平均播放时长'], ['2026-10-01', 400, '90%', '10.50s'], ['2026-10-02', 600, '80%', '11秒']]}),
        workbook(root / '来源.xlsx', {'抖音': [['来源', '来源占比', '对比7日'], ['推荐', '90%', '-2%'], ['个人主页', '10%', '2%']]})]


class AdapterTest(unittest.TestCase):
    def test_five_exports_all_sheets_and_nulls(self):
        with tempfile.TemporaryDirectory() as temporary:
            files = exports(Path(temporary))
            with patch('socket.socket', side_effect=AssertionError('network forbidden')):
                data = normalize(files, cutoff_date='2026-10-02', imported_at='2026-10-03T00:00:00Z')
                with self.assertRaisesRegex(NotImplementedError, '未实现'):
                    ApiAdapter().normalize()
            self.assertEqual(data['plays'], 1000)
            self.assertEqual(data['datasets'], ['attraction', 'audience', 'daily_plays', 'engagement', 'traffic'])
            self.assertEqual(data['points']['bounce_2s'], .6)
            self.assertEqual(data['points']['average_watch_seconds'], 21)
            self.assertEqual(data['points']['completion_rate'], .2)
            self.assertEqual(data['daily'][0]['average_watch_seconds'], 10.5)
            self.assertEqual(data['daily'][0]['followers'], 3)
            self.assertEqual(data['segments'][1]['end'], 13)
            self.assertEqual(data['segments'][0]['danmaku'], 3)
            self.assertEqual(data['segments'][0]['peer_danmaku'], 10)
            self.assertIsNone(data['segments'][0]['rewatch_rate'])
            self.assertTrue(any('rewatch_rate' in item for item in data['warnings']))
            self.assertEqual(data['unknown_columns'][0]['values'], ['保留原文'])
            search = next(row for row in data['traffic_sources'] if row['source'] == '搜索')
            self.assertIsNone(search['share'])
            self.assertEqual(search['status'], '未列出')
            self.assertEqual(data['provenance']['files'][0]['sha256'], hashlib.sha256(files[0].read_bytes()).hexdigest())

    def test_cutoff_missing_columns_and_sparse_cells(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = workbook(root / 'sparse.xlsx', {
                '指标数据': [['平均播放时长', '完播率', '封面点击率'], ['12.25s', None, '25%']],
                '数据': [['日期', '总播放量'], ['2026-10-01', 5], ['2026-10-02', 7]]})
            data = normalize([path], cutoff_date='2026-10-01', imported_at='now')
            self.assertEqual(data['plays'], 5)
            self.assertEqual(data['points']['average_watch_seconds'], 12.25)
            self.assertIsNone(data['points']['completion_rate'])
            self.assertEqual(data['points']['cover_click_rate'], .25)
            self.assertTrue(any('completion_rate' in warning for warning in data['warnings']))
            self.assertEqual(len(data['daily']), 2)

    def test_invalid_segment_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = workbook(Path(temporary) / 'bad.xlsx', {'进度分析': [['时间', '跳过率'], ['00:08-00:03', '1%']]})
            with self.assertRaisesRegex(ValueError, '无效分段时间'):
                normalize([path], cutoff_date='2026-10-01', imported_at='now')

    def test_missing_whole_column_and_separate_daily_windows(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = workbook(Path(temporary) / 'windows.xlsx', {
                '指标数据': [['平均播放时长', '5秒完播率'], ['21秒', '30%']],
                '每日播放': [['日期', '总播放量'], ['2026-10-01', 1000]],
                '每日涨粉': [['日期', '涨粉量'], ['2026-10-01', 3], ['2026-10-02', 5]],
                '进度分析': [['时间', '跳过率'], ['00:00-00:13', '1%']],
                '抖音': [['来源', '来源占比'], ['推荐', '100%']]})
            data = normalize([path], cutoff_date='2026-10-02', imported_at='now')
            self.assertEqual(data['plays'], 1000)
            self.assertIsNone(data['points']['bounce_2s'])
            self.assertIsNone(data['segments'][0]['rewatch_rate'])
            self.assertIsNone(data['traffic_sources'][0]['comparison_7d'])
            for field in ('bounce_2s', 'rewatch_rate', 'comparison_7d'):
                self.assertTrue(any(field in warning for warning in data['warnings']))
            self.assertIsNone(data['daily'][0]['completion_5s'])
            self.assertTrue(any('daily.2026-10-01.completion_5s' in warning for warning in data['warnings']))

    def test_daily_rates_not_overwritten_by_audience_trends(self):
        with tempfile.TemporaryDirectory() as temporary:
            for reverse in (False, True):
                sheets = [('全量', [['日期', '总播放量', '2秒跳出率'], ['2026-10-01', 100, '60%']]),
                          ('观众趋势', [['日期', '涨粉量', '2秒跳出率'], ['2026-10-01', 3, '90%']])]
                path = workbook(Path(temporary) / 'rates.xlsx', dict(reversed(sheets) if reverse else sheets))
                data = normalize([path], cutoff_date='2026-10-02', imported_at='now')
                self.assertEqual(data['daily'][0]['bounce_2s'], .6)
                self.assertEqual(data['daily'][0]['audience_trends']['bounce_2s'], .9)
                self.assertNotIn('attraction', data['datasets'])

    def test_invalid_files_return_value_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bad = root / 'invalid.xlsx'
            bad.write_bytes(b'not a zip')
            missing = root / 'missing.xlsx'
            with ZipFile(missing, 'w'):
                pass
            malformed = root / 'malformed.xlsx'
            with ZipFile(malformed, 'w') as archive:
                archive.writestr('xl/sharedStrings.xml', '<broken')
            for path in (bad, missing, malformed):
                with self.subTest(path=path), self.assertRaisesRegex(ValueError, '无效 XLSX'):
                    normalize([path], cutoff_date='2026-10-01', imported_at='now')

    def test_duplicate_rows_and_invalid_headers_rejected(self):
        cases = [
            [[0, '来源占比'], ['推荐', '100%']],
            [['来源', '来源占比'], ['推荐', '50%'], ['推荐', '50%']],
            [['日期', '总播放量'], ['2026-10-01', 1], ['2026-10-01', 2]],
            [['时间', '跳过率'], ['00:00-00:08', '1%'], ['00:00-00:08', '2%']],
        ]
        with tempfile.TemporaryDirectory() as temporary:
            for rows in cases:
                path = workbook(Path(temporary) / 'invalid.xlsx', {'数据': rows})
                with self.subTest(rows=rows), self.assertRaises(ValueError):
                    normalize([path], cutoff_date='2026-10-01', imported_at='now')


if __name__ == '__main__':
    unittest.main()
