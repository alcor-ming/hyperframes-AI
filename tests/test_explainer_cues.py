import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".studio"))
import explainer


def alignment(text, step=0.2):
    return json.dumps({"characters": [{"char": char, "start": round(index * step, 6),
                                      "end": round(index * step + 0.1, 6)}
                                     for index, char in enumerate(text)]}).encode()


class CuesTests(unittest.TestCase):
    def test_shared_asr_text_field_and_explicit_unaligned_character(self):
        raw = json.dumps({"characters": [
            {"text": "你", "start": 0.1, "end": 0.2, "aligned": True},
            {"text": "，", "start": None, "end": None, "aligned": False},
            {"text": "好", "start": 0.3, "end": 0.4, "aligned": True}]}).encode()
        cues = explainer.build_cues("你，好", raw)
        self.assertEqual(0.3, explainer.find_cue(cues, "好"))
        self.assertFalse(cues["characters"][1]["aligned"])
        with self.assertRaisesRegex(explainer.ExplainerError, "cue_unaligned"):
            explainer.find_cue(cues, "，")

    def test_exact_query_mismatch_and_freeze_identity(self):
        raw = alignment("alpha alpha end")
        cues = explainer.build_cues("alpha alpha! end", raw)
        explainer.validate_cues(cues)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), cues["sources"]["alignment_sha256"])
        self.assertEqual(1, len(cues["mismatches"]))
        self.assertEqual("!", cues["mismatches"][0]["script"])
        self.assertIsNone(cues["characters"][11]["start"])
        self.assertEqual(0, explainer.find_cue(cues, {"token": "alpha", "nth": 1}))
        self.assertEqual(1.2, explainer.find_cue(cues, {"token": "alpha", "within": [1, 3]}))
        self.assertEqual(2.1, explainer.find_cue(cues, {"token": "alpha", "nth": 2, "edge": "end"}))
        for query, error in [("alpha", "cue_ambiguous"), ("missing", "cue_not_found"),
                             ("alpha!", "cue_unaligned"), ({"token": "alpha", "nth": 3}, "cue_not_found")]:
            with self.subTest(query=query), self.assertRaisesRegex(explainer.ExplainerError, error):
                explainer.find_cue(cues, query)
        self.assertEqual([[0, 2.9]], cues["speech_intervals"])

    def test_unicode_silence_and_invalid_input(self):
        cues = explainer.build_cues("你好🌟", alignment("你好🌟", step=1))
        self.assertEqual(2, explainer.find_cue(cues, "🌟"))
        self.assertEqual(3, len(cues["speech_intervals"]))
        for raw in (b"{}", b"null", b"bad", b'{"characters":[{"char":"ab","start":0,"end":1}]}',
                    b'{"characters":[{"char":"a","start":1,"end":0}]}'):
            with self.subTest(raw=raw), self.assertRaises(explainer.ExplainerError):
                explainer.build_cues("a", raw)
        for query in ({"token": "你", "nth": True}, {"token": "你", "within": [-1, 5]},
                      {"token": "你", "edge": "middle"}):
            with self.assertRaises(explainer.ExplainerError):
                explainer.find_cue(cues, query)


if __name__ == "__main__":
    unittest.main()
