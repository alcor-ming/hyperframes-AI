"""Exercise v3.6 template contracts and their local rule links."""
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.studio'))
from math_chain import parse_plan
from visual_plan import plan_scene_rows


class V36RulesTest(unittest.TestCase):
    def test_templates_and_production_boundaries(self):
        template = (ROOT / '.studio/templates/SHOWCASE_PLAN.template.md').read_text()
        values = {'TEMPLATE': 'pure_hyperframes', 'RATIO': '16:9',
                  'SCRIPT_REVISION': '1', 'RESEARCH_REVISION': '1', 'SUBJECT_POSITION': 'null'}
        for key, value in values.items():
            template = template.replace(f'__{key}__', value)
        metadata = json.loads(template.split('---', 2)[1])
        self.assertEqual(metadata['status'], 'draft')
        self.assertIsNone(metadata['author_model'])
        self.assertEqual(list(plan_scene_rows(template)), ['S01'])
        self.assertIn('<!-- plan-metadata:start -->', template)
        research = (ROOT / '.studio/templates/MATH_RESEARCH.template.md').read_text()
        for term in ('原片出处', '原作者', '所用片段', '声音来源', '不插值'):
            self.assertIn(term, research)
        for name in ('AGENTS.md', '.studio/templates/WINDOWS_AGENTS.md', '.studio/templates/CLAUDE.template.md'):
            text = (ROOT / name).read_text()
            for term in ('开发仓', '/mnt/d/AI/AI+hyperframes', 'work-wsl.sh', 'Opus 5.5'):
                self.assertIn(term, text)
        refinement = (ROOT / '.studio/templates/SHOWCASE_REFINEMENT.template.md').read_text()
        for term in ('积木', '动作配方或规则', '内容资产', '仅属于本片', 'pack / validate / accept'):
            self.assertIn(term, refinement)

    def test_new_rule_links_and_math_example(self):
        paths = ['.studio/spec/showcase.md', '.studio/spec/showcase-pdoom.md',
                 '.studio/spec/showcase-science.md', '.studio/spec/math-rap.md',
                 '.studio/templates/CLAUDE.template.md']
        for name in paths:
            path = ROOT / name
            base = ROOT if name.endswith('CLAUDE.template.md') else path.parent
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                resolved = (base / target.split('#')[0]).resolve()
                self.assertTrue(resolved.is_relative_to(ROOT) and resolved.is_file(), target)
        math_rules = (ROOT / '.studio/spec/math-rap.md').read_text()
        example = re.search(r'```math-plan\n(.*?)\n```', math_rules, re.S)[0]
        parsed = parse_plan('## S01\n\n' + example)
        self.assertEqual(parsed['S01']['cues'][0]['reveal'], ['U01'])
        for term in ('【图】', '【码】', '【未实现】', '严重度', '推荐分镜', '首个强拍', '不新增音频门禁'):
            self.assertIn(term, math_rules)


if __name__ == '__main__':
    unittest.main()
