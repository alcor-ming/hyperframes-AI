from pathlib import Path
import tempfile
import unittest

import test_work_cli
import seek_check


class SeekCheckTest(unittest.TestCase):
    def test_author_callbacks_inline_and_exempt_dependencies(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            files = {
                "index.html": '<script>gsap.to(node, {onUpdate: () => node.textContent = "changed"});</script>',
                "author.mjs": 'const fn = () => {}; timeline.eventCallback("onUpdate", fn);',
                "safe.js": '// onUpdate: fn\nconst text = "onUpdate: fn"; timeline.eventCallback("onUpdate"); timeline.eventCallback("onUpdate", null);',
                "vendor/gsap.js": 'const x = {onUpdate: fn};',
                "runtime/helper.js": 'const x = {onUpdate: fn};',
                "library/helper.js": 'const x = {onUpdate: fn};',
            }
            for name, text in files.items():
                path = project / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            report = seek_check.findings(project, list(files))
            self.assertEqual({entry["file"] for entry in report}, {"index.html", "author.mjs"}, report)
            self.assertEqual(len(report), 2)
            self.assertTrue(all(entry["kind"] == "on_update_seek_risk" for entry in report), report)
            (project / "invalid.js").write_text("const = ;")
            self.assertEqual(seek_check.findings(project, ["invalid.js"])[0]["kind"], "seek_scan_unverified")


if __name__ == "__main__":
    unittest.main()
