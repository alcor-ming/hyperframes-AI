from contextlib import redirect_stderr
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import test_work_cli as fixtures
import cover

cli = fixtures.WORK_CLI


class DraftCoverTest(unittest.TestCase):
    def test_preparation_reuses_cover_and_failure_does_not_touch_video(self):
        with tempfile.TemporaryDirectory() as tmp:
            variant = Path(tmp)
            video = variant / 'video.mp4'; video.write_bytes(b'unchanged video')
            font = variant / 'font.ttf'; font.write_bytes(b'font')
            logo = variant / 'logo.svg'; logo.write_text('<svg/>')
            ref = lambda path: {'path': str(path), 'sha256': cover.digest(path.read_bytes())}
            state = {'design_snapshot': {'id': 'math'}, 'design_values': {'cover.enabled': True},
                     'account': 'a', 'cover_title': 'Chosen title',
                     'cover_recipe': {'width': 640, 'height': 360, 'font': ref(font), 'logo': ref(logo)}}
            def screenshot(command, **kwargs):
                (Path(command[2]) / 'cover.png').write_bytes(b'PNG fixture')
            with patch.object(cover.subprocess, 'run', side_effect=screenshot) as render, patch.object(cli, 'write_variant'):
                cli.prepare_draft_cover(variant, state)
                first = state['cover_id']
                cli.prepare_draft_cover(variant, state)
                self.assertEqual(1, render.call_count)
                self.assertEqual(first, state['cover_id'])
                font.write_bytes(b'changed font')
                with redirect_stderr(io.StringIO()) as error:
                    cli.prepare_draft_cover(variant, state)
                self.assertIn('Cover incomplete', error.getvalue())
                self.assertIn('font', state['cover_issue'])
                self.assertNotIn('current_cover', state)
            self.assertEqual(b'unchanged video', video.read_bytes())

    def test_legacy_disabled_and_missing_title(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(cover, 'render') as render, patch.object(cli, 'write_variant'):
            for state in ({}, {'design_snapshot': {'id': 'math'}, 'design_values': {'cover.enabled': False}}):
                cli.prepare_draft_cover(Path(tmp), state)
                self.assertNotIn('cover_issue', state)
            state = {'design_snapshot': {'id': 'math'}}
            with redirect_stderr(io.StringIO()):
                cli.prepare_draft_cover(Path(tmp), state)
            self.assertIn('title is not adopted', state['cover_issue'])
            render.assert_not_called()
