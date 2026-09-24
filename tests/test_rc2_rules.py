"""Keep RC2's video Plan readable by the existing Scene projection."""

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".studio"))
from visual_plan import plan_scene_rows


class RC2RulesTests(unittest.TestCase):
    def test_two_plan_views_keep_one_scene_index_and_one_screen_copy(self):
        template = (ROOT / ".studio/templates/ANIMATION_PLAN.template.md").read_text(encoding="utf-8")
        plan = template.replace("`<保留实际 ID>`", "S01").replace("`<真实变化或持续阅读状态>`", "01")
        self.assertEqual(["S01"], list(plan_scene_rows(plan)))
        self.assertIn("## 3. 上屏信息表", template)
        self.assertIn("## 4. Scene 节拍表", template)
        self.assertIn("不在 Scene 节拍表重抄", template)

    def test_video_edit_does_not_force_research_rewrite_or_motion(self):
        creative = (ROOT / ".studio/spec/creative.md").read_text(encoding="utf-8")
        design = (ROOT / ".studio/spec/visual-design.md").read_text(encoding="utf-8")
        self.assertIn("不为等义编辑回写第二份 Research 文案", creative)
        self.assertIn("正常阅读可以静止", design)
        self.assertIn("读完可移动、归组或退场", design)


if __name__ == "__main__":
    unittest.main()
