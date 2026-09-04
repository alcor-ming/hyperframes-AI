from __future__ import annotations

from importlib.machinery import SourceFileLoader
import importlib.util
from pathlib import Path
from unittest import mock
import subprocess
import unittest


REPO = Path(__file__).resolve().parents[1]
LOADER = SourceFileLoader("asr_wsl_bridge", str(REPO / ".studio" / "asr_wsl_bridge.py"))
SPEC = importlib.util.spec_from_loader("asr_wsl_bridge", LOADER)
assert SPEC
BRIDGE = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(BRIDGE)


class AsrWslBridgeTest(unittest.TestCase):
    def test_one_fixed_wsl_call_carries_job_values_in_environment(self) -> None:
        video = r"D:\AI\AI+hyperframes\works\active\source video.mp4"
        output = r"D:\AI\AI+hyperframes\works\active\asr output"
        completed = subprocess.CompletedProcess([], 23)
        with mock.patch.object(BRIDGE.subprocess, "run", return_value=completed) as run:
            code = BRIDGE.bridge(
                [
                    "transcribe-faster",
                    video,
                    "--output-dir",
                    output,
                    "--language",
                    "auto",
                ],
                {
                    "HYPERFRAMES_WSL_DISTRO": "OtherDistro",
                    "HYPERFRAMES_WSL_ASR_SCRIPT": "/tmp/untrusted.sh",
                },
            )

        self.assertEqual(23, code)
        run.assert_called_once()
        command = run.call_args.args[0]
        self.assertEqual(
            BRIDGE.WSL_COMMAND,
            command[:-1],
        )
        self.assertEqual(BRIDGE.WSL_SCRIPT, command[-1])
        self.assertLess(
            BRIDGE.WSL_SCRIPT.index('"$HYPERFRAMES_BRIDGE_ASR_SCRIPT" check'),
            BRIDGE.WSL_SCRIPT.index('exec "$HYPERFRAMES_BRIDGE_ASR_SCRIPT" transcribe-faster'),
        )
        self.assertNotIn(str(video), command)
        env = run.call_args.kwargs["env"]
        self.assertEqual(video, env["HYPERFRAMES_BRIDGE_VIDEO"])
        self.assertEqual(output, env["HYPERFRAMES_BRIDGE_OUTPUT"])
        self.assertEqual(BRIDGE.DEFAULT_ASR_SCRIPT, env["HYPERFRAMES_BRIDGE_ASR_SCRIPT"])
        self.assertTrue(set(BRIDGE.BRIDGE_ENV).issubset(set(env["WSLENV"].split(":"))))
        self.assertEqual(r"C:\Windows\System32\wsl.exe", command[0])

    def test_rejects_commands_outside_the_transcription_contract(self) -> None:
        with mock.patch.object(BRIDGE.subprocess, "run") as run:
            self.assertEqual(2, BRIDGE.bridge(["doctor"], {}))
        run.assert_not_called()

    def test_rejects_paths_outside_the_workstore(self) -> None:
        with mock.patch.object(BRIDGE.subprocess, "run") as run:
            code = BRIDGE.bridge(
                [
                    "transcribe-faster",
                    r"C:\Users\Jym\private.mp4",
                    "--output-dir",
                    r"D:\AI\AI+hyperframes-other\output",
                    "--language",
                    "auto",
                ],
                {},
            )
        self.assertEqual(2, code)
        run.assert_not_called()

    def test_windows_resolves_junctions_before_workstore_check(self) -> None:
        resolved = {
            BRIDGE.WORKSTORE: r"D:\AI\AI+hyperframes",
            r"D:\AI\AI+hyperframes\works\linked\video.mp4": r"C:\escaped\video.mp4",
        }
        resolvers = []

        def path(value: str) -> object:
            resolver = mock.Mock(return_value=resolved[value])
            resolvers.append(resolver)
            return mock.Mock(resolve=resolver)

        fake_path = mock.Mock()
        fake_path.side_effect = path
        with mock.patch.object(BRIDGE.os, "name", "nt"), mock.patch.object(
            BRIDGE, "Path", fake_path
        ):
            self.assertIsNone(
                BRIDGE.workstore_path(r"D:\AI\AI+hyperframes\works\linked\video.mp4")
            )
        for resolver in resolvers:
            resolver.assert_called_once_with(strict=False)


if __name__ == "__main__":
    unittest.main()
