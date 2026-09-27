"""Review failure modes, effective settings and deposited-path parsing."""
from pathlib import Path
from types import SimpleNamespace
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from inspect_gcode import read_paths
from review_print import footprint, review


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
        for suffix in ("G20\n", "G2 X2 Y2 E0.1\n",
                       "G1 Z0.4 E0.1\n"):
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as tmp:
                source = Path(tmp) / "bad.gcode"
                source.write_text("G21\nG90\nM83\n;Z:0.2\nG1 X1 Y1 Z0.2\n" + suffix)
                with self.assertRaises(ValueError):
                    read_paths(source)

    def test_footprint_includes_half_width_and_counts_support(self):
        segments = [
            {"role": "Brim", "a": [0.2, 1], "b": [2, 1], "width_mm": 0.4},
            {"role": "Support interface", "a": [1, 1], "b": [2, 1], "width_mm": 0.4},
        ]
        result = footprint({0.2: segments}, [10, 10, 10])
        self.assertAlmostEqual(result["xy_bounds_including_half_width_mm"][0], 0.0)
        self.assertEqual(result["support_segments"], 1)
        self.assertTrue(result["inside_safe_volume"])

    def test_no_stale_output_reuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            files = self._inputs(p)
            output = p / "run"
            output.mkdir()
            with self.assertRaises(FileExistsError):
                self._review(files, output)

    def test_zero_exit_without_completed_plate_is_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            files = self._inputs(p)
            def fake(*args, **kwargs):
                if args[0][-1] == "--help":
                    return SimpleNamespace(returncode=0, stdout="OrcaSlicer 2.x", stderr="")
                output = Path(args[0][args[0].index("--outputdir") + 1])
                (output / "result.json").write_text(json.dumps({"return_code": 0, "sliced_plates": []}))
                return SimpleNamespace(returncode=0)
            with patch("review_print.slicer_prefix", return_value=["fake"]), \
                 patch("review_print.subprocess.run", side_effect=fake):
                with self.assertRaisesRegex(RuntimeError, "completed plate"):
                    self._review(files, p / "run")

    def test_completed_result_without_gcode_is_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            files = self._inputs(p)
            def fake(command, **kwargs):
                if command[-1] == "--help":
                    return SimpleNamespace(returncode=0, stdout="OrcaSlicer 2.4.2", stderr="")
                output = Path(command[command.index("--outputdir") + 1])
                (output / "result.json").write_text(json.dumps({
                    "return_code": 0, "sliced_plates": [{"id": 1, "warning_message": ""}],
                }))
                (output / "effective-settings.json").write_text("{}")
                return SimpleNamespace(returncode=0)
            with patch("review_print.slicer_prefix", return_value=["fake"]), \
                 patch("review_print.subprocess.run", side_effect=fake):
                with self.assertRaisesRegex(RuntimeError, "fresh nonempty G-code"):
                    self._review(files, p / "run")

    def test_requires_matching_gcode_for_every_sliced_plate(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            files = self._inputs(p)
            def fake(command, **kwargs):
                if command[-1] == "--help":
                    return SimpleNamespace(returncode=0, stdout="OrcaSlicer 2.4.2", stderr="")
                output = Path(command[command.index("--outputdir") + 1])
                (output / "plate_1.gcode").write_text(ORCA_GCODE)
                (output / "result.json").write_text(json.dumps({
                    "return_code": 0, "sliced_plates": [{"id": 2, "warning_message": ""}],
                }))
                (output / "effective-settings.json").write_text("{}")
                return SimpleNamespace(returncode=0)
            with patch("review_print.slicer_prefix", return_value=["fake"]), \
                 patch("review_print.subprocess.run", side_effect=fake):
                with self.assertRaisesRegex(RuntimeError, r"reported plate IDs \[2\] but wrote G-code for plate IDs \[1\]"):
                    self._review(files, p / "run")

    def test_rejects_duplicate_gcode_plate_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            files = self._inputs(p)
            def fake(command, **kwargs):
                if command[-1] == "--help":
                    return SimpleNamespace(returncode=0, stdout="OrcaSlicer 2.4.2", stderr="")
                output = Path(command[command.index("--outputdir") + 1])
                (output / "plate_1.gcode").write_text(ORCA_GCODE)
                (output / "orca_plate_1.gcode").write_text(ORCA_GCODE)
                (output / "result.json").write_text(json.dumps({
                    "return_code": 0, "sliced_plates": [{"id": 1, "warning_message": ""}],
                }))
                (output / "effective-settings.json").write_text("{}")
                return SimpleNamespace(returncode=0)
            with patch("review_print.slicer_prefix", return_value=["fake"]), \
                 patch("review_print.subprocess.run", side_effect=fake):
                with self.assertRaisesRegex(RuntimeError, "duplicate G-code plate IDs"):
                    self._review(files, p / "run")

    def test_completed_review_preserves_notice_and_selected_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            files = self._inputs(p)
            def fake(command, **kwargs):
                if command[-1] == "--help":
                    return SimpleNamespace(returncode=0, stdout="OrcaSlicer 2.4.2", stderr="")
                output = Path(command[command.index("--outputdir") + 1])
                (output / "plate_1.gcode").write_text(ORCA_GCODE)
                (output / "result.json").write_text(json.dumps({
                    "error_string": "Success.", "return_code": 0,
                    "sliced_plates": [{"id": 1, "warning_message": "Long bridging extrusions"}],
                }))
                (output / "effective-settings.json").write_text(json.dumps({
                    "printer_model": "Qidi Q2C", "filament_type": ["PETG"],
                    "sparse_infill_density": "7%", "sparse_infill_pattern": "adaptivecubic",
                }))
                kwargs["stdout"].write("Detected print stability issue\n")
                return SimpleNamespace(returncode=0)
            with patch("review_print.slicer_prefix", return_value=["fake"]), \
                 patch("review_print.subprocess.run", side_effect=fake):
                result = self._review(files, p / "run")
            self.assertTrue(result["review_required"])
            self.assertEqual(result["effective_settings"]["filament_type"], ["PETG"])
            self.assertEqual(result["plates"][0]["support_segments"], 1)
            self.assertEqual(result["plates"][0]["plate"], 1)
            self.assertEqual(result["safe_build_volume_mm"], [270, 270, 256])

    @staticmethod
    def _inputs(path):
        files = {name: path / f"{name}.json" for name in ("printer", "process", "filament")}
        for item in files.values():
            item.write_text("{}")
        model = path / "model.stl"
        model.write_text("test input")
        files["model"] = model
        return files

    def _review(self, files, output):
        return review(files["model"], files["printer"], files["process"], files["filament"],
                      output)


if __name__ == "__main__":
    unittest.main()
