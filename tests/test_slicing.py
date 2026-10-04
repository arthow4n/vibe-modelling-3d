"""Review Orca slice status, effective settings and artifact cleanup."""
from pathlib import Path
from types import SimpleNamespace
import json
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evaluate_model import _support_roles, review


EFFECTIVE_SETTINGS = {
    "printer_model": "Qidi Q2C",
    "printer_variant": "0.4",
    "nozzle_diameter": ["0.4"],
    "printable_area": ["0x0", "270x0", "270x270", "0x270"],
    "printable_height": "256",
    "filament_type": ["PETG"],
    "enable_support": "0",
    "support_type": "tree(auto)",
    "bridge_no_support": "0",
    "max_bridge_length": "10",
    "support_threshold_angle": "30",
    "sparse_infill_density": "7%",
    "sparse_infill_pattern": "adaptivecubic",
}


class ReviewTests(unittest.TestCase):
    def test_reads_only_orca_support_line_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "plate_1.gcode").write_text(
                "; support material extrusion width = 0.42mm\n"
                ";TYPE:Inner wall\nG1 X1 E.1\n"
                ";TYPE:Support interface\nG1 X2 E.1\n")
            (root / "plate_2.gcode").write_text(";TYPE:Inner wall\nG1 X1 E.1\n")
            result = _support_roles(root, [{"id": 1}, {"id": 2}])
        self.assertEqual(result, [{"plate": 1, "roles": ["Support interface"]}])

    def test_zero_exit_without_completed_plate_is_failure_and_temp_is_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = self._inputs(root)
            run_dirs = []

            def fake(command, **kwargs):
                if command[-1] == "--help":
                    return SimpleNamespace(returncode=0, stdout="OrcaSlicer 2.x", stderr="")
                output = Path(command[command.index("--outputdir") + 1])
                run_dirs.append(output)
                (output / "result.json").write_text(json.dumps({"return_code": 0, "sliced_plates": []}))
                return SimpleNamespace(returncode=0)

            with patch("evaluate_model.slicer_prefix", return_value=["fake"]), \
                    patch("evaluate_model.run_command", side_effect=fake), \
                    self.assertRaisesRegex(RuntimeError, "completed plate"):
                self._review(files)
            self.assertFalse(run_dirs[0].exists())

    def test_default_run_is_removed_and_report_contains_orca_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = self._inputs(Path(tmp))
            run_dirs = []
            probe_commands = []

            def fake(command, **kwargs):
                if command[-1] == "--help":
                    return SimpleNamespace(returncode=0, stdout="OrcaSlicer 2.4.2", stderr="")
                self.assertIsNone(kwargs.get('timeout'))
                output = Path(command[command.index("--outputdir") + 1])
                run_dirs.append(output)
                is_probe = "--enable-support=1" in command
                if is_probe:
                    probe_commands.append(command)
                (output / "plate_1.gcode").write_text(
                    ";TYPE:Support\nG1 X1 E.1\n" if is_probe else
                    ";TYPE:Inner wall\nG1 X1 E.1\n")
                (output / "result.json").write_text(json.dumps({
                    "error_string": "Success.", "return_code": 0,
                    "sliced_plates": [{"id": 1, "warning_message": "Long bridging extrusions"}],
                }))
                (output / "effective-settings.json").write_text(json.dumps({
                    **EFFECTIVE_SETTINGS, "enable_support": "1" if is_probe else "0",
                }))
                kwargs["stdout"].write("Detected print stability issue\n")
                return SimpleNamespace(returncode=0)

            with patch("evaluate_model.slicer_prefix", return_value=["fake"]), \
                    patch("evaluate_model.run_command", side_effect=fake):
                result = self._review(files)
            self.assertTrue(result["review_required"])
            self.assertEqual(result["effective_settings"]["filament_type"], ["PETG"])
            self.assertEqual(result["sliced_plates"], [1])
            self.assertTrue(result["support_probe"]["generated"])
            self.assertEqual(result["support_probe"]["supported_plates"],
                             [{"plate": 1, "roles": ["Support"]}])
            self.assertIn("--bridge-no-support=0", probe_commands[0])
            self.assertIn("--support-type=tree(auto)", probe_commands[0])
            self.assertFalse(run_dirs[0].exists())

    def test_keep_run_preserves_artifacts_and_records_location(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = self._inputs(Path(tmp))

            def fake(command, **kwargs):
                if command[-1] == "--help":
                    return SimpleNamespace(returncode=0, stdout="OrcaSlicer 2.4.2", stderr="")
                output = Path(command[command.index("--outputdir") + 1])
                (output / "plate_1.gcode").write_text(";TYPE:Inner wall\nG1 X1 E.1\n")
                (output / "result.json").write_text(json.dumps({
                    "return_code": 0, "sliced_plates": [{"id": 1, "warning_message": ""}],
                }))
                (output / "effective-settings.json").write_text(json.dumps({
                    **EFFECTIVE_SETTINGS,
                    "enable_support": "1" if "--enable-support=1" in command else "0",
                }))
                return SimpleNamespace(returncode=0)

            with patch("evaluate_model.slicer_prefix", return_value=["fake"]), \
                    patch("evaluate_model.run_command", side_effect=fake):
                result = self._review(files, keep_run=True)
            kept = Path(result["kept_run_directory"])
            try:
                self.assertTrue((kept / "plate_1.gcode").is_file())
                self.assertTrue((kept / "support_probe" / "plate_1.gcode").is_file())
                self.assertTrue((kept / "summary.json").is_file())
                self.assertEqual(json.loads((kept / "summary.json").read_text())["kept_run_directory"], str(kept))
                self.assertFalse(result["support_probe"]["generated"])
                self.assertFalse(result["review_required"])
            finally:
                shutil.rmtree(kept)

    def test_reuses_primary_auto_support_slice(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = self._inputs(Path(tmp))
            slice_commands = []

            def fake(command, **kwargs):
                if command[-1] == "--help":
                    return SimpleNamespace(returncode=0, stdout="OrcaSlicer 2.4.2", stderr="")
                slice_commands.append(command)
                output = Path(command[command.index("--outputdir") + 1])
                (output / "plate_1.gcode").write_text(";TYPE:Support\nG1 X1 E.1\n")
                (output / "result.json").write_text(json.dumps({
                    "return_code": 0, "sliced_plates": [{"id": 1, "warning_message": ""}],
                }))
                (output / "effective-settings.json").write_text(json.dumps({
                    **EFFECTIVE_SETTINGS, "enable_support": "1",
                }))
                return SimpleNamespace(returncode=0)

            with patch("evaluate_model.slicer_prefix", return_value=["fake"]), \
                    patch("evaluate_model.run_command", side_effect=fake):
                result = self._review(files)
            self.assertEqual(len(slice_commands), 1)
            self.assertTrue(result["support_probe"]["generated"])

    def test_probe_failure_preserves_primary_slice_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = self._inputs(Path(tmp))

            def fake(command, **kwargs):
                if command[-1] == "--help":
                    return SimpleNamespace(returncode=0, stdout="OrcaSlicer 2.4.2", stderr="")
                if "--enable-support=1" in command:
                    return SimpleNamespace(returncode=1)
                output = Path(command[command.index("--outputdir") + 1])
                (output / "result.json").write_text(json.dumps({
                    "return_code": 0, "sliced_plates": [{"id": 1, "warning_message": ""}],
                }))
                (output / "effective-settings.json").write_text(json.dumps(EFFECTIVE_SETTINGS))
                return SimpleNamespace(returncode=0)

            with patch("evaluate_model.slicer_prefix", return_value=["fake"]), \
                    patch("evaluate_model.run_command", side_effect=fake):
                result = self._review(files)
            self.assertFalse(result["support_probe"]["ok"])
            self.assertTrue(result["review_required"])
            self.assertEqual(result["sliced_plates"], [1])

    @staticmethod
    def _inputs(path):
        files = {name: path / f"{name}.json" for name in ("printer", "process", "filament")}
        for item in files.values():
            item.write_text("{}")
        model = path / "model.stl"
        model.write_text("test input")
        files["model"] = model
        return files

    def _review(self, files, **kwargs):
        return review(files["model"], files["printer"], files["process"], files["filament"], **kwargs)


if __name__ == "__main__":
    unittest.main()


def test_version_discovery_is_content_bound(tmp_path,monkeypatch):
    from execution import tools
    monkeypatch.setenv('ENGINEERING_DATA',str(tmp_path))
    identity=['tool-one'];calls=[]
    monkeypatch.setattr(tools,'tool_identity',lambda prefix:identity[0])
    def discover():calls.append(True);return '2.4.2'
    assert tools.version(['slicer'],tmp_path,discover)=='2.4.2'
    assert tools.version(['slicer'],tmp_path,discover)=='2.4.2' and len(calls)==1
    identity[0]='tool-two'
    assert tools.version(['slicer'],tmp_path,discover)=='2.4.2' and len(calls)==2


def test_independent_probe_overlaps_primary_and_failure_preserves_primary(tmp_path,monkeypatch):
    import threading,time
    import evaluate_model
    files=ReviewTests._inputs(tmp_path)
    files['process'].write_text(json.dumps(EFFECTIVE_SETTINGS))
    primary=threading.Event();probe=threading.Event()
    def fake(command,**kwargs):
        if command[-1]=='--help':return SimpleNamespace(returncode=0,stdout='OrcaSlicer 2.4.2',stderr='')
        assert kwargs.get('timeout') is None
        is_probe='--enable-support=1' in command
        (probe if is_probe else primary).set()
        assert (primary if is_probe else probe).wait(2),'Slices did not overlap'
        if is_probe:return SimpleNamespace(returncode=1)
        folder=Path(command[command.index('--outputdir')+1])
        (folder/'result.json').write_text(json.dumps(dict(return_code=0,sliced_plates=[{'id':1}])))
        (folder/'effective-settings.json').write_text(json.dumps(EFFECTIVE_SETTINGS))
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(evaluate_model,'slicer_prefix',lambda:['fake'])
    monkeypatch.setattr(evaluate_model,'run_command',fake)
    result=review(files['model'],files['printer'],files['process'],files['filament'],threads=2)
    assert result['sliced_plates']==[1] and not result['support_probe']['ok'] and result['review_required']
