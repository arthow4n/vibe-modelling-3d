"""Integration checks for the command's file and artifact contract."""
import json
from pathlib import Path
import subprocess
import sys
from PIL import Image

COMMAND = Path(__file__).resolve().parents[1] / "evaluate_model.py"


def call(path, *args):
    return subprocess.run([sys.executable, str(COMMAND), str(path), *args],
                          text=True, capture_output=True, timeout=30)


def test_sibling_import_exports_and_view(tmp_path):
    (tmp_path / "dimensions.py").write_text("WIDTH = 13\n")
    source = tmp_path / "piece.py"
    source.write_text("import cadquery as cq\nfrom dimensions import WIDTH\n"
                      "result = cq.Workplane('XY').box(WIDTH, 7, 3)\n")
    run = call(source, "--views", "front", "--output-dir", "renders", "--export")
    assert run.returncode == 0, run.stderr + run.stdout
    data = json.loads(run.stdout)
    assert data["ok"] and data["geometry"]["valid"]
    assert all(item["ok"] for item in data["exports"] + data["views"])
    assert (tmp_path / "renders/piece_front.png").stat().st_size > 0
    assert (tmp_path / "piece.step").stat().st_size > 0
    assert (tmp_path / "piece.stl").stat().st_size > 0

    png = call(source, "--views", "front", "--output-dir", "renders")
    assert png.returncode == 0, png.stderr + png.stdout
    image = Image.open(tmp_path / "renders/piece_front.png").convert("RGBA")
    assert image.getpixel((0, 0)) == (255, 255, 255, 255)
    assert image.getextrema()[0][0] < 255  # visible model strokes

    # A second worker must read the changed sibling source, not stale bytecode.
    (tmp_path / "dimensions.py").write_text("raise RuntimeError('fresh sibling loaded')\n")
    rerun = call(source, "--views", "none")
    assert rerun.returncode != 0
    assert "fresh sibling loaded" in json.loads(rerun.stdout)["errors"][0]["message"]


def test_build_error_cannot_claim_old_artifacts(tmp_path):
    source = tmp_path / "broken.py"
    source.write_text("raise ValueError('bad geometry')\n")
    old = tmp_path / "broken.step"
    old.write_text("old output")
    run = call(source, "--views", "none", "--export")
    assert run.returncode != 0
    data = json.loads(run.stdout)
    assert not data["ok"] and data["errors"][0]["stage"] == "build"
    assert data["exports"] == [] and old.read_text() == "old output"
    assert not (tmp_path / "broken.stl").exists()
