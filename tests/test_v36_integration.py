from contextlib import redirect_stdout
import io
import json
import unittest
from unittest.mock import patch

import test_work_appearance
from test_work_cli import WORK_CLI as cli
import appearance
import appearance_rebind
import explainer
import math_chain


class V36IntegrationTest(unittest.TestCase):
    setUp = test_work_appearance.WorkAppearanceTest.setUp
    asset = test_work_appearance.WorkAppearanceTest.asset

    def invoke(self, *arguments):
        args = cli.build_parser().parse_args(["--json", *arguments])
        with redirect_stdout(io.StringIO()) as output:
            args.handler(self.root, args)
        return output.getvalue().strip()

    def create(self, *arguments):
        identity = self.invoke("new", "Fixture", "--workflow", "hyperframes_video", "--account", "a",
                               "--purpose", "standard", "--series", "fixture", *arguments)
        work, _ = cli.locate_work(self.root, identity)
        return identity, work / "variants/main"

    def test_showcase_creation_and_rebind_freeze(self):
        with self.assertRaisesRegex(appearance.AppearanceError, "explicit submodule"):
            self.create("--mode", "showcase")
        identity, variant = self.create("--mode", "showcase", "--submodule", "pdoom")
        state = cli.read_json(variant / "variant.yaml")
        plan = cli.read_frontmatter(variant / "ANIMATION_PLAN.md")
        self.assertEqual(state["appearance_lock"]["submodule"], "pdoom")
        self.assertEqual(state['line'], {'id': 'showcase/pdoom', 'version': 1})
        self.assertEqual(plan["submodule"], "pdoom")
        self.assertEqual(plan["appearance_lock_sha256"], state["appearance_lock"]["sha256"])
        self.assertIn("# Showcase Plan", (variant / "ANIMATION_PLAN.md").read_text())
        before = (variant / "variant.yaml").read_bytes()
        with self.assertRaisesRegex(appearance.AppearanceError, "frozen"):
            self.invoke("--work", identity, "--variant", "main", "appearance", "rebind", "--submodule", "science", "--apply")
        self.assertEqual(before, (variant / "variant.yaml").read_bytes())
        with self.assertRaisesRegex(appearance.AppearanceError, "explicit submodule"):
            self.invoke("variant", "add", "missing", "--account", "a", "--mode", "showcase")
        self.invoke("variant", "add", "science", "--account", "a", "--mode", "showcase", "--submodule", "science")
        sibling = variant.parent / "science"
        self.assertEqual(cli.read_json(sibling / 'variant.yaml')['line'], {'id': 'showcase/science', 'version': 1})
        self.assertEqual(cli.read_json(sibling / "variant.yaml")["appearance_lock"]["submodule"], "science")
        self.assertEqual(cli.read_frontmatter(sibling / "ANIMATION_PLAN.md")["submodule"], "science")

    def test_showcase_test_work_needs_no_appearance_assets(self):
        identity = self.invoke("new", "Free", "--workflow", "hyperframes_video", "--purpose", "test",
                               "--mode", "showcase", "--submodule", "science")
        work, _ = cli.locate_work(self.root, identity)
        variant = cli.variant_paths(work)[0]
        lock = cli.read_json(variant / "variant.yaml")["appearance_lock"]
        self.assertEqual((lock["selection"]["theme"], lock["selection"]["background"], lock["assets"]), (None, None, []))
        appearance.verify(variant / "project", lock, check_mounts=False)
        plan = cli.read_frontmatter(variant / "ANIMATION_PLAN.md")
        self.assertEqual((plan["theme"], plan["background"], plan["submodule"]), (None, None, "science"))
        self.invoke("--work", identity, "--variant", variant.name, "appearance", "rebind", "--background", self.green["ref"], "--apply")
        rebound = cli.read_json(variant / "variant.yaml")["appearance_lock"]
        self.assertEqual(rebound["selection"]["background"], self.green)
        self.assertIsNone(rebound["selection"]["theme"])
        with self.assertRaisesRegex(cli.HarnessError, "explainer requires"):
            self.invoke("new", "Plain", "--workflow", "hyperframes_video", "--purpose", "test", "--mode", "explainer")

    def test_math_series_freezes_spec_and_enforces_lyrics(self):
        service = cli.account_service(self.root)
        service.put("series", "fixture", {"name": "Math", "mode": "explainer", "spec": "math-rap"})
        series = service.get("series", "fixture")
        with self.assertRaisesRegex(cli.HarnessError, "captions"):
            self.create("--captions", "off")
        identity, variant = self.create()
        state = cli.read_json(variant / "variant.yaml")
        expected = {key: series[key] for key in ("id", "revision", "mode", "spec")}
        self.assertEqual(state["series_binding"], expected)
        self.assertEqual(state['line'], {'id': 'explainer/math-rap', 'version': 1})
        self.assertEqual(state["appearance_lock"]["mode"], "explainer")
        self.assertTrue(state["appearance_lock"]["selection"]["captions"])
        self.assertEqual(cli.read_frontmatter(variant / "ANIMATION_PLAN.md")["series_binding"], expected)
        before = {name: (variant / name).read_bytes() for name in ("variant.yaml", "ANIMATION_PLAN.md")}
        service.put("series", "fixture", {"name": "Changed", "mode": "card"})
        for name, content in before.items():
            self.assertEqual((variant / name).read_bytes(), content)
        with self.assertRaisesRegex(appearance.AppearanceError, "captions"):
            self.invoke("--work", identity, "--variant", "main", "appearance", "rebind", "--captions", "off", "--apply")
        self.invoke("variant", "add", "next", "--account", "a")
        adopted = cli.read_json(variant.parent / "next/variant.yaml")
        self.assertEqual(adopted["series_binding"]["revision"], series["revision"] + 1)
        self.assertEqual(adopted["mode"], "card")
        self.assertEqual(adopted['line'], {'id': 'card', 'version': 1})

    def test_explainer_line_is_bound_at_creation(self):
        _, variant = self.create('--mode', 'explainer')
        self.assertEqual(cli.read_json(variant / 'variant.yaml')['line'], {'id': 'explainer', 'version': 1})

    def test_plan_and_beats_cli_use_frozen_math_contract(self):
        cli.account_service(self.root).put("series", "fixture", {"name": "Math", "mode": "explainer", "spec": "math-rap"})
        identity, variant = self.create()
        work = variant.parent.parent
        self.assertIn("原作者", (work / "shared/RESEARCH.md").read_text())
        metadata = cli.read_frontmatter(variant / "ANIMATION_PLAN.md")
        metadata["plan_format"] = "3.5.2"
        contract = dict(units=[dict(id="u1", symbol="x", graphic="")], symbols={"x": "box"},
                        invariants=[], zero_basics=[], cues=[dict(cue="a", keep=[], reveal=["u1"], remove=[])])
        (variant / "ANIMATION_PLAN.md").write_text("---\n" + json.dumps(metadata) + "\n---\n## S01\n```math-plan\n" + json.dumps(contract) + "\n```\n")
        (variant / "project/index.html").write_text('<main data-scene-id="S01" data-start="0" data-duration="6"></main><script>const tween={onUpdate:()=>{window.x=1}};</script>')
        cues = explainer.build_cues("a", b'{"characters":[{"char":"a","start":0,"end":1}]}')
        cue_path = variant / "project/runtime/cues.json"
        cli.write_json(cue_path, cues)
        report = json.loads(self.invoke("--work", identity, "--variant", "main", "plan", "check"))
        kinds = {f.get("code", f.get("kind")) for f in report["findings"]}
        self.assertTrue({"math_missing_graphic", "math_trailing_gap", "on_update_seek_risk"}.issubset(kinds))
        audio = work / "formal.wav"
        audio.write_bytes(b"audio fixture")
        upstream = self.base / "hyperframes.mjs"
        upstream.write_text("fixture")
        grid = math_chain.make_beat_grid([0, 1, 2], cli.file_sha256(audio), 3, 0)
        with patch("math_audio.extract", return_value=grid) as extract:
            self.invoke("--work", identity, "--variant", "main", "beats", "build", "--audio", "formal.wav",
                        "--beats-per-bar", "3", "--first-downbeat", "0", "--hyperframes-cli", str(upstream))
            self.assertEqual(extract.call_args.args, (audio, upstream, 3, 0))
        self.assertEqual(cli.read_json(cue_path)["beat_grid"], grid)

    def test_known_cue_runtime_requires_explicit_upgrade(self):
        identity, variant = self.create()
        runtime = variant / "project/runtime/cues.js"
        runtime.write_text("known old cue fixture")
        with patch.object(appearance_rebind, "KNOWN_CUE_RUNTIMES", {cli.file_sha256(runtime)}):
            with self.assertRaisesRegex(appearance.AppearanceError, "upgrade-runtime"):
                self.invoke("--work", identity, "--variant", "main", "appearance", "rebind", "--apply")
            report = json.loads(self.invoke("--work", identity, "--variant", "main", "appearance", "rebind", "--apply", "--upgrade-runtime"))
            self.assertTrue(report["runtime_upgrade"])
        self.assertEqual(runtime.read_bytes(), (test_work_appearance.REPO / ".studio/runtime/cues.js").read_bytes())


if __name__ == "__main__":
    unittest.main()
