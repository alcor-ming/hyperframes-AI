"""Keep RC2's video Plan readable by the existing Scene projection."""

from pathlib import Path
import sys
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".studio"))
from visual_plan import plan_scene_rows


class RC2RulesTests(unittest.TestCase):
    def test_two_plan_views_keep_one_scene_index_and_one_screen_copy(self):
        template = (ROOT / "tests/fixtures/ANIMATION_PLAN.3.5.2.md").read_text(encoding="utf-8")
        plan = re.sub(r'__[A-Z_]+__', 'null', template)
        plan = re.sub(r'^\*\*延续信息：\*\*.*\n', '', plan, flags=re.M)
        self.assertEqual(["S01"], list(plan_scene_rows(plan)))
        self.assertIn("## S01", template)
        self.assertEqual(1, template.count("```screen\n"))
        self.assertNotIn("Scene 节拍表", template)
        scene = template.split("## S01", 1)[1].split("\n## ", 1)[0]
        self.assertIn("```screen", scene)
        self.assertIn("### 事件序列与例外", scene)

    def test_video_edit_preserves_research_ownership_and_reading_stability(self):
        creative = (ROOT / ".studio/spec/creative.md").read_text(encoding="utf-8")
        design = (ROOT / ".studio/spec/visual-design.md").read_text(encoding="utf-8")
        self.assertIn("不为等义编辑回写第二份 Research 文案", creative)
        self.assertIn("阅读区域保持稳定", design)
        self.assertIn("读完可移动、归组或退场", design)


if __name__ == "__main__":
    unittest.main()
