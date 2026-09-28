"""Protect selective imagery and complete screen information without new gates."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ROUTER = ".agents/skills/hyperframes-codex-workflow/SKILL.md"


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


class V343RulesTests(unittest.TestCase):
    def test_selective_images_keep_authority_and_evidence_boundaries(self):
        for name in ("AGENTS.md", ".studio/templates/WINDOWS_AGENTS.md",
                     ".studio/spec/creative.md", ".studio/workflow.md",
                     ".studio/templates/RESEARCH.template.md",
                     ".studio/templates/ANIMATION_PLAN.template.md"):
            with self.subTest(name=name):
                text = read(name)
                for obsolete in ("默认不生成", "不默认调用图片", "不生成则写无", "不强制配图"):
                    self.assertNotIn(obsolete, text)
                for obsolete in ("全片零图", "逐 Scene 评估图片", "旧 Plan 表格格式继续有效"):
                    self.assertNotIn(obsolete, text)
                if name in ("AGENTS.md", ".studio/templates/WINDOWS_AGENTS.md"):
                    for required in ("Asset Brief", "一并授权", "未列用途或明显超量", "提供方"):
                        self.assertIn(required, text)
                else:
                    self.assertNotIn("一并授权", text)

    def test_plan_blocks_and_checks_carry_complete_information(self):
        plan = read(".studio/templates/ANIMATION_PLAN.template.md")
        metadata = json.loads(plan.split("---", 2)[1].replace("__SCRIPT_REVISION__", "1")
                              .replace("__RESEARCH_REVISION__", "1")
                              .replace("__SUBJECT_POSITION__", "null"))
        self.assertNotIn("profile", metadata)
        for text in ("### I01", "```screen", "## S01", "B 素材", "## 自检", "| Scene | 一句话摘要 |"):
            self.assertIn(text, plan)
        self.assertNotIn("| 实际表达 |", plan)
        design = read(".studio/spec/visual-design.md")
        for text in ("任一通道", "必要条件、数值、单位、比较对象与归属",
                     "## Plan 检查", "Q1", "Three.js / Remotion", "优先复用", "长正文留 DOM/SVG"):
            self.assertIn(text, design)
        self.assertNotIn("反 PPT", design)

    def test_dispatch_follows_plan_and_discovery_precedes_dispatch(self):
        workflow = read(".studio/workflow.md")
        for text in ("Plan 阶段", "查包、场景源与配方", "原样转交", "不附加比 Plan 更严",
                     "完整上屏正文", "回报准确冲突", "短自检单"):
            self.assertIn(text, workflow)
        router = read(ROUTER)
        for text in ("| Plan |", "| Draft |", "visual-design.md", "hyperframes.md"):
            self.assertIn(text, router)

    def test_retired_routing_leaves_legacy_profiles_and_podcast_intact(self):
        retired = "hyperframes-" + "anti-ppt"
        self.assertFalse((ROOT / ".agents/skills" / retired / "SKILL.md").exists())
        for name in (".studio/capabilities.yaml", ROUTER, "README.md", ".gitignore",
                     ".agents/skills/hyperframes-codex-workflow/scripts/validate_package.py"):
            self.assertNotIn(retired, read(name))
        capabilities = read(".studio/capabilities.yaml")
        self.assertNotIn("\nprofiles:", capabilities)
        self.assertNotIn("\n  default:", capabilities)
        self.assertIn("podcast_quote_image: [bundled_asr, image_generation]", capabilities)
        self.assertIn("package_pipeline:", capabilities)
        self.assertTrue((ROOT / ".agents/skills/hyperframes-codex-workflow/references/"
                         "hyperframes-design-profile-pack-v0.1.0/SKILL.md").is_file())
        for name in ("README.md", ".studio/templates/WINDOWS_AGENTS.md"):
            text = read(name)
            for required in ("资产开发任务完成", "component list --audit", "component source-add",
                             "JSON front matter", "source_ref", "classification_status", "WSL 不代改"):
                self.assertIn(required, text)


if __name__ == "__main__":
    unittest.main()
