from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.studio'))
import work_context
from test_work_cli import WORK_CLI as cli


class WorkContextTest(unittest.TestCase):
    def test_session_pairs_and_command_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); runtime=cli.runtime_root(root)
            with work_context.command(runtime,'director'):
                cli.write_current(root,'work-a','variant1')
            with work_context.command(runtime,'editor'):
                self.assertIsNone(cli.read_pointer(root,'current-work'))
                cli.write_current(root,'work-b','variant2')
            with work_context.command(runtime,'director'):
                self.assertEqual('work-a',cli.read_pointer(root,'current-work'))
                # A nested independent command changes disk; this running command keeps its pair.
                with work_context.command(runtime,'director'):
                    cli.write_current(root,'work-c','variant3')
                self.assertEqual('variant1',cli.read_pointer(root,'current-variant'))
            with work_context.command(runtime,'director'):
                self.assertEqual('work-c',cli.read_pointer(root,'current-work'))
                cli.clear_current_if(root,'work-b')
                self.assertEqual('variant3',cli.read_pointer(root,'current-variant'))
                cli.clear_current_if(root,'work-c')
                self.assertIsNone(cli.read_pointer(root,'current-work'))
            with work_context.command(runtime,'editor'):
                self.assertEqual('work-b',cli.read_pointer(root,'current-work'))
                self.assertEqual('variant2',cli.read_pointer(root,'current-variant'))

    def test_legacy_pair_imported_once_and_link_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime=Path(temporary)
            (runtime/'current-work').write_text('legacy')
            (runtime/'current-variant').write_text('main')
            with work_context.command(runtime,'default'):
                self.assertEqual({'work':'legacy','variant':'main'},work_context.read(runtime))
                work_context.write(runtime,'new','variant1')
            (runtime/'current-work').write_text('stale')
            with work_context.command(runtime,'default'):
                self.assertEqual('new',work_context.read(runtime)['work'])
            (runtime/'contexts/linked.json').symlink_to(runtime/'contexts/default.json')
            with self.assertRaises(ValueError):
                with work_context.command(runtime,'linked'): pass
            with self.assertRaises(ValueError):
                with work_context.command(runtime,'../escape'): pass


if __name__=='__main__': unittest.main()
