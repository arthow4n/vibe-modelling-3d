"""Review failure modes, effective settings and deposited-path parsing."""
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
from inspect_gcode import read_paths
from review_print import build_parser, footprint, printer_volume, review


ORCA_GCODE = """G21
G90
M83
;TYPE:Custom
G91
G1 X5 E1
G90
;LAYER_CHANGE
;Z:0.2
;WIDTH:0.4
;TYPE:Perimeter
G1 X1 Y1 Z0.2
G1 X3 Y1 E0.1
;TYPE:Internal Bridge
G91
G1 X2 E0.2
;TYPE:Support interface
G90
G1 X4 Y2 E0.3
; filament used [g] = 1.2
"""
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
    def test_parses_orca_relative_coordinates_roles_and_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "slice.gcode"
            source.write_text(ORCA_GCODE)
            layers, metadata = read_paths(source)
        self.assertEqual(metadata["filament used [g]"], "1.2")
        self.assertEqual([path["role"] for path in layers[0.2]],
                         ["Perimeter", "Internal Bridge", "Support interface"])
        self.assertAlmostEqual(layers[0.2][0]["length_mm"], 2.0)
        self.assertAlmostEqual(layers[0.2][1]["length_mm"], 2.0)

    def test_absolute_extrusion_and_historical_prusa_markers(self):
        gcode = "G21\nG90\nM82\n;Z:0.2\n;TYPE:Bridge infill\nG92 E0\nG1 X1 Y1 Z0.2\nG1 X3 Y1 E1\nG1 X4 Y1 E0.5\nG1 X5 Y1 E1.2\n"
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "slice.gcode"
            source.write_text(gcode)
            layers, _ = read_paths(source)
        self.assertEqual(len(layers[0.2]), 2)
        self.assertAlmostEqual(layers[0.2][0]["filament_mm"], 1.0)
        self.assertAlmostEqual(layers[0.2][1]["filament_mm"], 0.7)

    def test_rejects_unsupported_units_arcs_and_nonplanar_extrusion(self):
        for suffix in ("G20\n", "G2 X2 Y2 E0.1\n", "G1 Z0.4 E0.1\n"):
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as tmp:
                source = Path(tmp) / "bad.gcode"
                source.write_text("G21\nG90\nM83\n;Z:0.2\nG1 X1 Y1 Z0.2\n" + suffix)
                with self.assertRaises(ValueError):
                    read_paths(source)

    def test_footprint_includes_half_width_counts_support_and_uses_profile_origin(self):
        segments = [
            {"role": "Brim", "a": [-4.8, 1], "b": [2, 1], "width_mm": 0.4},
            {"role": "Support interface", "a": [1, 1], "b": [2, 1], "width_mm": 0.4},
        ]
        volume = {"xy_bounds_mm": [-5, 0, 95, 70], "height_mm": 80}
        result = footprint({0.2: segments}, volume)
        self.assertAlmostEqual(result["xy_bounds_including_half_width_mm"][0], -5.0)
        self.assertEqual(result["support_segments"], 1)
        self.assertTrue(result["inside_printer_volume"])
        outside = footprint({0.2: [{**segments[0], "a": [-5.1, 1]}]}, volume)
        self.assertFalse(outside["inside_printer_volume"])

    def test_printer_volume_comes_from_effective_rectangular_area_and_height(self):
        volume = printer_volume({
            "printable_area": ["-5x2", "95x2", "95x72", "-5x72"],
            "printable_height": "80",
        })
        self.assertEqual(volume["xy_bounds_mm"], [-5, 2, 95, 72])
        self.assertEqual(volume["dimensions_mm"], [100, 70, 80])
        self.assertEqual(volume["height_mm"], 80)

    def test_rejects_missing_or_nonrectangular_printer_area(self):
        for settings in (
                {"printable_area": ["0x0", "1x0", "1x1"], "printable_height": 10},
                {"printable_area": ["0x0", "1x0", "0.8x1", "0x1"], "printable_height": 10},
                {"printable_area": ["0x0", "1x0", "1x1", "0x1"]}):
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                printer_volume(settings)

    def test_cli_help_matches_profile_defaults_and_exposes_only_unified_options(self):
        help_text = re.sub(r"-\s+", "-", build_parser().format_help())
        help_text = " ".join(help_text.split())
        for profile in (
                "qidi-q2c-0.4-nozzle.json",
                "qidi-q2c-0.20-standard-adaptive-cubic-7.json",
                "generic-petg-qidi-q2c-0.4.json"):
            self.assertIn(profile, help_text)
        for option in ("--model", "--printer", "--process", "--filament",
                       "--placement", "--expect-no-supports", "--keep-run"):
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

    def test_completed_result_without_gcode_is_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = self._inputs(Path(tmp))

            def fake(command, **kwargs):
                if command[-1] == "--help":
                    return SimpleNamespace(returncode=0, stdout="OrcaSlicer 2.4.2", stderr="")
                output = Path(command[command.index("--outputdir") + 1])
                (output / "result.json").write_text(json.dumps({
                    "return_code": 0, "sliced_plates": [{"id": 1, "warning_message": ""}],
                }))
                (output / "effective-settings.json").write_text(json.dumps(EFFECTIVE_SETTINGS))
                return SimpleNamespace(returncode=0)

            with patch("review_print.slicer_prefix", return_value=["fake"]), \
                    patch("review_print.subprocess.run", side_effect=fake), \
                    self.assertRaisesRegex(RuntimeError, "fresh nonempty G-code"):
                self._review(files)

    def test_requires_matching_gcode_for_every_sliced_plate(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = self._inputs(Path(tmp))

            def fake(command, **kwargs):
                if command[-1] == "--help":
                    return SimpleNamespace(returncode=0, stdout="OrcaSlicer 2.4.2", stderr="")
                output = Path(command[command.index("--outputdir") + 1])
                (output / "plate_1.gcode").write_text(ORCA_GCODE)
                (output / "result.json").write_text(json.dumps({
                    "return_code": 0, "sliced_plates": [{"id": 2, "warning_message": ""}],
                }))
                (output / "effective-settings.json").write_text(json.dumps(EFFECTIVE_SETTINGS))
                return SimpleNamespace(returncode=0)

            with patch("review_print.slicer_prefix", return_value=["fake"]), \
                    patch("review_print.subprocess.run", side_effect=fake), \
                    self.assertRaisesRegex(RuntimeError, r"reported plate IDs \[2\] but wrote G-code for plate IDs \[1\]"):
                self._review(files)

    def test_rejects_duplicate_gcode_plate_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = self._inputs(Path(tmp))

            def fake(command, **kwargs):
                if command[-1] == "--help":
                    return SimpleNamespace(returncode=0, stdout="OrcaSlicer 2.4.2", stderr="")
                output = Path(command[command.index("--outputdir") + 1])
                (output / "plate_1.gcode").write_text(ORCA_GCODE)
                (output / "orca_plate_1.gcode").write_text(ORCA_GCODE)
                (output / "result.json").write_text(json.dumps({
                    "return_code": 0, "sliced_plates": [{"id": 1, "warning_message": ""}],
                }))
                (output / "effective-settings.json").write_text(json.dumps(EFFECTIVE_SETTINGS))
                return SimpleNamespace(returncode=0)

            with patch("review_print.slicer_prefix", return_value=["fake"]), \
                    patch("review_print.subprocess.run", side_effect=fake), \
                    self.assertRaisesRegex(RuntimeError, "duplicate G-code plate IDs"):
                self._review(files)

    def test_default_run_is_removed_and_report_contains_printer_and_path_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = self._inputs(Path(tmp))
            run_dirs = []

            def fake(command, **kwargs):
                if command[-1] == "--help":
                    return SimpleNamespace(returncode=0, stdout="OrcaSlicer 2.4.2", stderr="")
                output = Path(command[command.index("--outputdir") + 1])
                run_dirs.append(output)
                (output / "plate_1.gcode").write_text(ORCA_GCODE)
                (output / "result.json").write_text(json.dumps({
                    "error_string": "Success.", "return_code": 0,
                    "sliced_plates": [{"id": 1, "warning_message": "Long bridging extrusions"}],
                }))
                (output / "effective-settings.json").write_text(json.dumps(EFFECTIVE_SETTINGS))
                kwargs["stdout"].write("Detected print stability issue\n")
                return SimpleNamespace(returncode=0)

            with patch("review_print.slicer_prefix", return_value=["fake"]), \
                    patch("review_print.subprocess.run", side_effect=fake):
                result = self._review(files, expect_no_supports=True)
            self.assertTrue(result["review_required"])
            self.assertEqual(result["effective_settings"]["filament_type"], ["PETG"])
            self.assertEqual(result["plates"][0]["support_segments"], 1)
            self.assertEqual(result["plates"][0]["plate"], 1)
            self.assertEqual(result["printer_volume"]["dimensions_mm"], [270, 270, 256])
            self.assertEqual(result["support_segments"], 1)
            self.assertTrue(result["expect_no_supports"])
            self.assertIn("path_roles", result["plates"][0])
            self.assertFalse(run_dirs[0].exists())

    def test_keep_run_preserves_artifacts_and_records_location(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = self._inputs(Path(tmp))

            def fake(command, **kwargs):
                if command[-1] == "--help":
                    return SimpleNamespace(returncode=0, stdout="OrcaSlicer 2.4.2", stderr="")
                output = Path(command[command.index("--outputdir") + 1])
                (output / "plate_1.gcode").write_text(ORCA_GCODE)
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
