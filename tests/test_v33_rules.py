"""Protect production routing and the v3.3 non-export contract."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
ROUTER = ".agents/skills/hyperframes-codex-workflow/SKILL.md"
PROFILE = (
    ".agents/skills/hyperframes-codex-workflow/references/"
    "hyperframes-design-profile-pack-v0.1.0/SKILL.md"
)


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class ProductionRulesTests(unittest.TestCase):
    def test_stage_and_visual_contract_have_one_owner(self):
        workflow = read(".studio/workflow.md")
        self.assertEqual(
            re.findall(r"^## (\d+)\. ", workflow, re.MULTILINE),
            ["1", "2", "3", "4"],
        )
        for path in (
            ROUTER,
            ".agents/skills/hyperframes-anti-ppt/SKILL.md",
            ".studio/recipes/pure-hyperframes.md",
            ".studio/recipes/talking-head.md",
        ):
            with self.subTest(path=path):
                content = read(path)
                self.assertIn(".studio/workflow.md", content)
                self.assertIn(".studio/spec/visual-design.md", content)
                self.assertNotIn("preview render", content)
                self.assertNotIn("自动归档", content)
        profile = read(PROFILE)
        self.assertNotIn("## Execution order", profile)
        self.assertIn("optional", profile)
        self.assertIn(".studio/workflow.md", profile)

    def test_timing_contract_covers_actual_onset_and_seek(self):
        design = read(".studio/spec/visual-design.md")
        for requirement in (
            "最小完整语义单元", "实际起点", "不等说完整句",
            "不得挤动旧文字", "切出返回", "顺序推进", "同场叠层",
            "不新增必读正文", "seek", "回拖", "语义揭示与停留期活动独立检查",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, design)
        plan = read(".studio/templates/ANIMATION_PLAN.template.md")
        self.assertIn("累积终态", plan)
        self.assertIn("场景策略与状态", plan)

    def test_video_boundary_does_not_change_podcast_routing(self):
        workflow = read(".studio/workflow.md")
        router = read(ROUTER)
        self.assertIn("PACKAGE.md", workflow)
        self.assertIn("不是视频设计、制作或接受的前置", workflow)
        self.assertIn("test-work 不进入任何视频导出链", workflow)
        self.assertIn("Finalize 不包含上传/发布，也不自动归档", workflow)
        self.assertIn("planner_skill", router)
        self.assertIn("copy_skill", router)
        self.assertIn("## 播客金句图", workflow)
        for skill in ("dbs-content", "dbs-xhs-title", "dbs-ai-check"):
            self.assertIn(skill, workflow)
        for path in ("AGENTS.md", ".studio/templates/WINDOWS_AGENTS.md"):
            self.assertIn("Draft 与 test-work 不导出视频", read(path))

    def test_new_video_examples_bind_production_accounts(self):
        for line in read("README.md").splitlines():
            if line.startswith("./work new ") and "--workflow hyperframes_video" in line:
                self.assertTrue("--account " in line or "--purpose test" in line, line)
        self.assertIn("shared_inputs", read(ROUTER))
        self.assertIn("text-led", read(ROUTER))


if __name__ == "__main__":
    unittest.main()
