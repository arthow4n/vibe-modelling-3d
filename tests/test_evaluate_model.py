"""Integration checks for the command's file and artifact contract."""
import json
from pathlib import Path
import subprocess
import sys
from PIL import Image

COMMAND = Path(__file__).resolve().parents[1] / "scripts/evaluate_model.py"


def call(path, *args):
    return subprocess.run([sys.executable, str(COMMAND), str(path), *args],
                          text=True, capture_output=True, timeout=30)


def test_sibling_import_exports_and_view(tmp_path):
    (tmp_path / "dimensions.py").write_text("WIDTH = 13\n")
    source = tmp_path / "piece.py"
    source.write_text("import cadquery as cq\nfrom dimensions import WIDTH\n"
                      "result = cq.Workplane('XY').box(WIDTH, 7, 3)\n")
    run = call(source, "--views", "front", "--image-format", "svg",
               "--output-dir", "renders", "--step", "piece.step", "--stl", "piece.stl",
               "--report", "report.json")
    assert run.returncode == 0, run.stderr + run.stdout
    data = json.loads((tmp_path / "report.json").read_text())
    assert data["ok"] and data["geometry"]["topology"]["solids"] == 1
    assert data["geometry"]["size_mm"] == [13, 7, 3]
    assert len(data["local_module_sha256"]) == 1
    assert all(item["ok"] for item in data["exports"] + data["views"])
    assert (tmp_path / "renders/piece_front.svg").read_text().startswith("<?xml")
    assert (tmp_path / "piece.step").stat().st_size > 0
    assert (tmp_path / "piece.stl").stat().st_size > 0

    png = call(source, "--views", "front", "--output-dir", "renders")
    assert png.returncode == 0, png.stderr + png.stdout
    image = Image.open(tmp_path / "renders/piece_front.png").convert("RGBA")
    assert image.getpixel((0, 0)) == (255, 255, 255, 255)
    assert image.getextrema()[0][0] < 255  # visible model strokes

    # A second worker must read the changed sibling source, not stale bytecode.
    (tmp_path / "dimensions.py").write_text("WIDTH = 17\n")
    rerun = call(source, "--views", "none", "--json")
    assert rerun.returncode == 0, rerun.stderr + rerun.stdout
    assert json.loads(rerun.stdout)["geometry"]["size_mm"][0] == 17


def test_build_error_cannot_claim_old_artifacts(tmp_path):
    source = tmp_path / "broken.py"
    source.write_text("raise ValueError('bad geometry')\n")
    old = tmp_path / "old.step"
    old.write_text("old output")
    run = call(source, "--views", "none", "--step", "old.step", "--report", "report.json")
    assert run.returncode != 0
    data = json.loads((tmp_path / "report.json").read_text())
    assert not data["ok"] and data["errors"][0]["stage"] == "build"
    assert data["exports"] == [] and old.read_text() == "old output"
