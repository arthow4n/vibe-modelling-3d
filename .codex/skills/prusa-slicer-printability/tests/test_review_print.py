"""Review failure modes and actual path footprints without requiring a slicer."""
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from review_print import footprint, review
from inspect_gcode import read_paths

GCODE='M83\nG90\n;Z:0.2\n;WIDTH:0.4\n;TYPE:Perimeter\nG1 Z0.2\nG1 X1 Y1\nG1 X3 Y1 E0.1\n'

class ReviewTests(unittest.TestCase):
    def test_includes_width_and_brim(self):
        segment={'role':'Skirt/Brim','a':[0.1,1],'b':[2,1],'width_mm':0.4}
        result=footprint({0.2:[segment]},[10,10,10])
        self.assertAlmostEqual(result['xy_bounds_including_half_width_mm'][0],-0.1)
        self.assertFalse(result['inside_safe_volume'])

    def test_support_count_and_z_limit(self):
        segment={'role':'Support material interface','a':[1,1],'b':[2,1],'width_mm':0.4}
        result=footprint({251:[segment]},[260,260,250])
        self.assertEqual(result['support_segments'],1)
        self.assertFalse(result['inside_safe_volume'])

    def test_no_stale_output_reuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'m.stl').write_text('model');(p/'p.ini').write_text('profile')
            with self.assertRaises(FileExistsError):review(p/'m.stl',p/'p.ini',p,[10,10,10])

    def test_zero_exit_without_output_is_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'m.stl').write_text('model');(p/'p.ini').write_text('profile')
            with patch('review_print.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout='fake slicer',stderr='')):
                with self.assertRaisesRegex(RuntimeError,'fresh G-code'):
                    review(p/'m.stl',p/'p.ini',p/'run',[10,10,10])

    def test_completed_review_keeps_warning_and_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'m.stl').write_text('model');(p/'p.ini').write_text('profile')
            def fake(command,**kwargs):
                if '--help' in command:return SimpleNamespace(returncode=0,stdout='Fake 1.0',stderr='')
                Path(command[command.index('--output')+1]).write_text(GCODE)
                kwargs['stdout'].write('Detected print stability issues: Long bridging extrusions\n')
                return SimpleNamespace(returncode=0)
            with patch('review_print.subprocess.run',side_effect=fake):
                result=review(p/'m.stl',p/'p.ini',p/'run',[10,10,10],
                    windows=[{'name':'bridge','layers':[0.2],'window':[0,0,4,4]}])
            self.assertTrue(result['review_required'])
            self.assertTrue((p/'run'/'bridge.svg').exists())
            self.assertTrue(result['inside_safe_volume'])

    def test_parser_rejects_unsupported_modes(self):
        for command in ('M82','G91','G20','G2 X2 Y2 E0.1'):
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/'bad.gcode';path.write_text(GCODE+command+'\n')
                with self.assertRaises(ValueError):read_paths(path)

if __name__=='__main__':unittest.main()
