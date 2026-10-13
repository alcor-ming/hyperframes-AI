import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.studio'))
from sfx_generate import generate
from tts import digest, wav_info


class SfxGenerateTest(unittest.TestCase):
    def test_real_jsfxr_asset_and_reproducibility(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for kind in ('click', 'whoosh', 'riser', 'fall', 'impact'):
                params = {'kind': kind, 'seed': 17}
                first = generate(None, params, root / kind, engine='jsfxr')
                second = generate(None, params, root / (kind + '-repeat'), engine='jsfxr')
                self.assertEqual(first['files'], second['files'])
                self.assertGreater(first['duration'], 0)
                self.assertGreaterEqual(first['hit_offset'], 0)
                self.assertLessEqual(first['hit_offset'], first['duration'])
                for name, sha in first['files'].items():
                    self.assertEqual(sha, digest((root / kind / name).read_bytes()))
                self.assertEqual(first['duration'], wav_info(root / kind / 'audio.wav')['duration'])
                asset = json.loads((root / kind / 'asset.json').read_text())
                self.assertEqual('audio.mp3', asset['entry'])
                with self.assertRaisesRegex(ValueError, 'exists'):
                    generate(None, params, root / kind, engine='jsfxr')
            silent = generate(None, {'kind': 'click', 'gain': 0}, root / 'silent', engine='jsfxr')
            self.assertFalse(json.loads((root / 'silent/asset.json').read_text())['hit_offset_estimated'])
            self.assertEqual(silent['parameters']['gain'], 0)

    def test_invalid_parameters_and_linked_destination_do_not_write(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for params in ({'kind': 'missing'}, {'kind': 'click', 'duration': 1},
                           {'kind': 'click', 'seed': True}, {'kind': 'click', 'gain': float('nan')}):
                with self.assertRaises(ValueError):
                    generate(None, params, root / 'bad', engine='jsfxr')
                self.assertFalse((root / 'bad').exists())
            (root / 'link').symlink_to(root, target_is_directory=True)
            with self.assertRaises(ValueError):
                generate(None, {'kind': 'click'}, root / 'link/new', engine='jsfxr')
            self.assertFalse((root / 'new').exists())


if __name__ == '__main__':
    unittest.main()
