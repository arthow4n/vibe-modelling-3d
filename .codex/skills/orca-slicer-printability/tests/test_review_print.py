"""Review Orca slice status, effective settings and artifact cleanup."""
from pathlib import Path
from types import SimpleNamespace
import json
import re
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from review_print import DEFAULTS, build_parser, review


EFFECTIVE_SETTINGS = {
    "printer_model": "Qidi Q2C",
    "printer_variant": "0.4",
    "nozzle_diameter": ["0.4"],
    "printable_area": ["0x0", "270x0", "270x270", "0x270"],
    "printable_height": "256",
    "filament_type": ["PETG"],
    "sparse_infill_density": "7%",
    "sparse_infill_pattern": "adaptivecubic",
}


class ReviewTests(unittest.TestCase):
    def test_cli_help_matches_profile_defaults_and_exposes_only_unified_options(self):
        help_text = re.sub(r"-\s+", "-", build_parser().format_help())
        help_text = " ".join(help_text.split())
        skill_text = (Path(__file__).resolve().parents[1] / "SKILL.md").read_text()
        for profile in (
                "qidi-q2c-0.4-nozzle.json",
                "qidi-q2c-0.20-standard-adaptive-cubic-7.json",
                "generic-petg-qidi-q2c-0.4.json"):
            self.assertIn(profile, help_text)
        for profile in DEFAULTS.values():
            path = profile.as_posix()
            self.assertIn(path, help_text)
            self.assertIn(path, skill_text)
        for option in ("--model", "--printer", "--process", "--filament",
                       "--placement", "--keep-run"):
            self.assertIn(option, help_text)
        for removed in ("--bed", "--out", "--slicer", "--timeout", "--purpose", "--profile-scope"):
            self.assertNotIn(removed, help_text)
        self.assertIn("default: center", help_text)
        self.assertIn("default: false", help_text)

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

            with patch("review_print.slicer_prefix", return_value=["fake"]), \
                    patch("review_print.subprocess.run", side_effect=fake), \
                    self.assertRaisesRegex(RuntimeError, "completed plate"):
                self._review(files)
            self.assertFalse(run_dirs[0].exists())

    def test_default_run_is_removed_and_report_contains_orca_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = self._inputs(Path(tmp))
            run_dirs = []

            def fake(command, **kwargs):
                if command[-1] == "--help":
                    return SimpleNamespace(returncode=0, stdout="OrcaSlicer 2.4.2", stderr="")
                output = Path(command[command.index("--outputdir") + 1])
                run_dirs.append(output)
                (output / "result.json").write_text(json.dumps({
                    "error_string": "Success.", "return_code": 0,
                    "sliced_plates": [{"id": 1, "warning_message": "Long bridging extrusions"}],
                }))
                (output / "effective-settings.json").write_text(json.dumps(EFFECTIVE_SETTINGS))
                kwargs["stdout"].write("Detected print stability issue\n")
                return SimpleNamespace(returncode=0)

            with patch("review_print.slicer_prefix", return_value=["fake"]), \
                    patch("review_print.subprocess.run", side_effect=fake):
                result = self._review(files)
            self.assertTrue(result["review_required"])
            self.assertEqual(result["effective_settings"]["filament_type"], ["PETG"])
            self.assertEqual(result["sliced_plates"], [1])
            self.assertFalse(run_dirs[0].exists())

    def test_keep_run_preserves_artifacts_and_records_location(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = self._inputs(Path(tmp))

            def fake(command, **kwargs):
                if command[-1] == "--help":
                    return SimpleNamespace(returncode=0, stdout="OrcaSlicer 2.4.2", stderr="")
                output = Path(command[command.index("--outputdir") + 1])
                (output / "plate_1.gcode").write_text("historical artifact")
                (output / "result.json").write_text(json.dumps({
                    "return_code": 0, "sliced_plates": [{"id": 1, "warning_message": ""}],
                }))
                (output / "effective-settings.json").write_text(json.dumps(EFFECTIVE_SETTINGS))
                return SimpleNamespace(returncode=0)

            with patch("review_print.slicer_prefix", return_value=["fake"]), \
                    patch("review_print.subprocess.run", side_effect=fake):
                result = self._review(files, keep_run=True)
            kept = Path(result["kept_run_directory"])
            try:
                self.assertTrue((kept / "plate_1.gcode").is_file())
                self.assertTrue((kept / "summary.json").is_file())
                self.assertEqual(json.loads((kept / "summary.json").read_text())["kept_run_directory"], str(kept))
            finally:
                shutil.rmtree(kept)

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
