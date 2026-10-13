import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'.studio'))
import cover


class CoverTest(unittest.TestCase):
    def test_title_change_reuses_assets_and_keeps_video(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);font=root/'font.ttf';logo=root/'logo.svg';video=root/'final.mp4'
            font.write_bytes(b'font fixture');logo.write_text('<svg/>');video.write_bytes(b'video')
            ref=lambda p:{'path':str(p),'sha256':cover.digest(p.read_bytes())}
            recipe={'width':640,'height':360,'font':ref(font),'logo':ref(logo)}
            def screenshot(command,**kwargs): (Path(command[2])/'cover.png').write_bytes(b'PNG fixture')
            with patch.object(cover.subprocess,'run',side_effect=screenshot) as run:
                first=cover.render(root,'first',recipe)
                self.assertEqual(first,cover.render(root,'first',recipe))
                second=cover.render(root,'second',recipe)
                self.assertEqual(run.call_count,2)
            self.assertNotEqual(first['id'],second['id'])
            self.assertEqual(first['files']['font.ttf'],second['files']['font.ttf'])
            self.assertEqual(video.read_bytes(),b'video')
            with self.assertRaises(ValueError): cover.render(root,'third',{**recipe,'font':{'path':str(font),'sha256':'wrong'}})


if __name__=='__main__':unittest.main()

class CoverCliTest(unittest.TestCase):
    def test_account_recipe_and_cover_only_export_keep_video(self):
        import test_work_cli as fixtures
        from contextlib import redirect_stdout
        import io, json
        cli=fixtures.WORK_CLI
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            import shutil
            shutil.copytree(fixtures.REPO/'.studio/templates',root/'.studio/templates')
            font=root/'font.ttf';font.write_bytes(b'font')
            logo=root/'logo.svg';logo.write_text('<svg/>')
            ref=lambda p:{'path':str(p),'sha256':cover.digest(p.read_bytes())}
            cli.account_service(root).put('account','account',{'name':'A','overrides':{'cover':{'width':640,'height':360,'font':ref(font),'logo':ref(logo)}}})
            cli.account_service(root).put('series','series',{'name':'S','design':'stage-full'})
            def invoke(*args):
                with redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(0,cli.main(['--json',*args],root=root))
                return output.getvalue().strip()
            identity=invoke('new','Cover','--workflow','hyperframes_video','--purpose','standard','--series','series','--account','account','--design','stage-full','--variant-id','main')
            work,_=cli.locate_work(root,identity);variant=work/'variants/main'
            video=variant/'final/final.mp4';video.parent.mkdir();video.write_bytes(b'video unchanged')
            def screenshot(command,**kwargs):
                (Path(command[2])/'cover.png').write_bytes((Path(command[2])/'index.html').read_bytes())
            with patch.object(cover.subprocess,'run',side_effect=screenshot):
                first=json.loads(invoke('cover','render','--title','First'))
                exported=json.loads(invoke('cover','export'))
                second=json.loads(invoke('cover','render','--title','Second'))
                again=json.loads(invoke('cover','export'))
            self.assertNotEqual(first['id'],second['id'])
            self.assertEqual(1,exported['sequence']);self.assertEqual(2,again['sequence'])
            self.assertEqual(b'video unchanged',video.read_bytes())
            self.assertEqual(2,len(list(Path(exported['directory']).glob('*.png'))))
            (Path(second['path'])/'cover.png').write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError,'changed'): cover.verify(Path(second['path']))
