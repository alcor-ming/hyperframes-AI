"""Keep visual outcomes authoritative without adding approval or form gates."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class V342RulesTests(unittest.TestCase):
    def test_visual_outcomes_and_exceptions_live_in_design(self):
        design = read(".studio/spec/visual-design.md")
        for rule in (
            "拆行、拆卡、逐句揭示或少量换词", "最小必要范围", "例外不覆盖周边说明",
            "不等于必须换词", "verbatim", "未识别的图片文字不默认通过",
            "数值、单位、比较对象与归属", "目标观看尺寸下可感知",
            "开场、场内及跨 Scene 交接", "隐藏或离屏动作、空 tween",
            "存在 `<video>` 也不自动通过", "不按动作数量/频率打分",
            "具体例外区间，不新增审批", "不删必要文字、不保留整画面等待",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, design)

    def test_other_contracts_reference_outcomes_and_remove_static_permission(self):
        for path in (
            ".studio/spec/visual-design.md", ".studio/spec/creative.md",
            ".studio/workflow.md", ".studio/templates/ANIMATION_PLAN.template.md",
        ):
            with self.subTest(path=path):
                content = read(path)
                for obsolete in ("正常阅读可以静止", "正常阅读可静止", "不意味着每段都必须运动",
                                 "不能为了加图删改批准文字", "静止可写保留"):
                    self.assertNotIn(obsolete, content)
                if path != ".studio/spec/visual-design.md":
                    self.assertIn("visual-design.md", content)
                    self.assertIn("阅读区域稳定", content)
                    self.assertNotIn("拆行、拆卡、逐句揭示或少量换词", content)
                    self.assertNotIn("提炼说明", content)
                    self.assertNotIn("相似度证明", content)
        for path in (".agents/skills/hyperframes-codex-workflow/SKILL.md",):
            self.assertIn("visual-design.md", read(path))
            self.assertNotIn("拆行、拆卡、逐句揭示或少量换词", read(path))

    def test_qa_diagnoses_without_replacing_viewing_or_acceptance(self):
        qa = read(".studio/spec/hyperframes.md").split("## Draft QA\n", 1)[1].split("## Final QA\n", 1)[0]
        for rule in (
            "来源与实际可见文字", "准确 Studio Draft 中连续观看", "可读性和声画含义",
            "不阻止保存、打开与继续修复 Draft", "QA 通过和接受就绪声明",
            "preview diagnose <target>", "上屏文字照搬定位（D1）", "整画面静止定位（D2）",
            "未覆盖范围标未验证", "不报告工具 PASS", "不导出或编码视频",
            "不写 Plan、接受状态或 Final", "不以 tween 数量或像素变化代替观看判断",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, qa)


if __name__ == "__main__":
    unittest.main()
