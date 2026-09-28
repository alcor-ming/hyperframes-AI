"""Guard v3.5.1 rule ownership, scene truth, and distributable links."""

import importlib.util
from pathlib import Path
import re
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ROUTER = ".agents/skills/hyperframes-codex-workflow/SKILL.md"
VALIDATOR = ".agents/skills/hyperframes-codex-workflow/scripts/validate_package.py"
RULES = ("AGENTS.md", ".studio/templates/WINDOWS_AGENTS.md", ".studio/workflow.md",
         ".studio/spec/creative.md", ".studio/spec/visual-design.md",
         ".studio/spec/hyperframes.md", ".studio/spec/privacy.md", ROUTER,
         ".studio/templates/RESEARCH.template.md", ".studio/templates/ANIMATION_PLAN.template.md")


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class V351RulesTests(unittest.TestCase):
    def test_authority_has_one_identical_owner_per_runtime(self):
        roots = RULES[:2]
        sections = [read(p).split("## 授权边界\n", 1)[1].split("\n## ", 1)[0] for p in roots]
        self.assertEqual(sections[0], sections[1])
        for path in RULES:
            text = read(path)
            expected = int(path in roots)
            for token in ("方向批准一并授权", "未列用途或明显超量再确认",
                          "外部或付费服务必须单独取得用户授权"):
                with self.subTest(path=path, token=token):
                    self.assertEqual(expected, text.count(token))
        for path in roots:
            for token in ("WSL 与 Windows 均可编写组件", "WSL 开发计划可以包含组件编辑",
                          "生产 Work", "Current", "接受状态或 Final", "冻结新版本"):
                self.assertIn(token, read(path))
        self.assertNotIn("/home/", read(roots[1]))

    def test_retired_rules_are_absent_from_active_contracts(self):
        for path in RULES:
            for obsolete in ("text-led", "animation-led", "two-template-mapping.md",
                             "卡片模式后续迁移", "旧表格格式继续有效", "旧 Profile 兼容",
                             "全片零图", "逐 Scene 评估图片", "三种场景策略",
                             "整画面持续变化", "不默认新增 BGM/SFX", "仅卡片模式适用"):
                with self.subTest(path=path, obsolete=obsolete):
                    self.assertNotIn(obsolete, read(path))
        router = read(ROUTER)
        self.assertEqual(["Locate", "Stage Loading"], re.findall(r"^## (.+)$", router, re.M))
        rows = [line for line in router.splitlines() if line.startswith("|") and "hyperframes.md" in line]
        self.assertEqual(1, len(rows))
        self.assertTrue(rows[0].startswith("| Draft |"))

    def test_ab_layers_rhythm_and_hard_boundaries(self):
        design = read(".studio/spec/visual-design.md")
        for token in ("五层管空间", "两者正交", "| 卡片 `card`", "| IP `explainer`",
                      "| 口播 `talking_head`", "A → B → A", "A → B", "隐藏或虚化并冻结",
                      "独立 B 文字组", "跨 Scene 返回 A", "不重播入场",
                      "A1 只约束第 4 层", "阅读保护只约束第 4 层",
                      "第 5 层口播原文不受 A1", "事件间隔不超过 2 秒", "铺开再等",
                      "第 2–4 层", "字幕推进", "背景漂移", "呼吸待机与说话起伏",
                      "持续镜头运动的中间过程不计", "逐处写明原因与区间",
                      "真人出镜区间不受 2 秒上限约束", "第 2、3 层继续产生事件",
                      "不伪造界面、操作结果或数据", "单一 paused timeline", "onUpdate",
                      "快照闭包、不联网", "Draft 与 test-work 不导出视频"):
            with self.subTest(token=token):
                self.assertIn(token, design)
        for section in ("## Plan 检查", "## Q1"):
            self.assertIn("超过 2 秒", design.split(section, 1)[1].split("\n## ", 1)[0])

    def test_research_and_plan_have_one_design_source(self):
        research = read(".studio/templates/RESEARCH.template.md")
        self.assertEqual(["事实与来源", "B-roll 候选", "比喻与例子"],
                         re.findall(r"^### (.+)$", research, re.M))
        for token in ("Work 级", "各 Variant 共享", "可定位位置", "取得状态", "确有缺口"):
            self.assertIn(token, research)
        plan = read(".studio/templates/ANIMATION_PLAN.template.md")
        overview = plan.split("## 概览", 1)[1].split("\n## ", 1)[0]
        self.assertNotIn("screen", overview)
        self.assertNotIn("A/B", overview)
        scene = plan.split("## S01", 1)[1].split("\n## ", 1)[0]
        for token in ("A/B 编排", "### I01", "```screen", "B 素材", "声音 cue", "事件序列"):
            self.assertIn(token, scene)
        self.assertIn("元信息由 CLI", plan)
        self.assertEqual(1, plan.count("```sound"))

    def test_package_checks_deployed_windows_links(self):
        spec = importlib.util.spec_from_file_location("validate_v351", ROOT / VALIDATOR)
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        self.assertEqual([], validator.rule_link_errors(ROOT))
        for path in (".studio/templates/ANIMATION_PLAN.template.md",
                     ".studio/templates/RESEARCH.template.md", ".studio/templates/WINDOWS_AGENTS.md"):
            self.assertIn(path, validator.REQUIRED_HARNESS)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            template = root / ".studio/templates/WINDOWS_AGENTS.md"
            template.parent.mkdir(parents=True)
            template.write_text("[rule](.studio/workflow.md)", encoding="utf-8")
            self.assertTrue(validator.rule_link_errors(root))
            (root / ".studio/workflow.md").write_text("# Workflow", encoding="utf-8")
            self.assertEqual([], validator.rule_link_errors(root))
            template.write_text("[rule](/home/nonportable.md)", encoding="utf-8")
            self.assertTrue(validator.rule_link_errors(root))


if __name__ == "__main__":
    unittest.main()
