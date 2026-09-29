"""Integration checks for the command's file and artifact contract."""
import json
from pathlib import Path
import subprocess
import sys
from PIL import Image, ImageChops
import pytest
import cadquery as cq
from evaluate_model import render, view_transform

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


@pytest.mark.parametrize('view', ['front', 'back', 'left', 'right', 'isometric', 'isometric_back'])
def test_render_keeps_vertical_pillar_and_top_cap_upright(view):
    """Actual PNG geometry catches sideways side views and inverted/rolled iso."""
    import io
    pillar = cq.Workplane('XY').box(4, 4, 60, centered=False)
    cap = cq.Workplane('XY').box(18, 18, 3, centered=False).translate((-7, -7, 60))
    shape = pillar.union(cap).val()
    png = Image.open(io.BytesIO(render(shape, view, 800, 600, False))).convert('RGB')
    ink = ImageChops.difference(png, Image.new('RGB', png.size, 'white'))
    bounds = ink.getbbox()
    assert bounds is not None
    x0, y0, x1, y1 = bounds
    assert y1-y0 > 2*(x1-x0), 'Z pillar is rolled sideways'
    third = (y1-y0)//3
    upper = ink.crop((x0, y0, x1, y0+third)).getbbox()
    lower = ink.crop((x0, y1-third, x1, y1)).getbbox()
    assert upper[2]-upper[0] > 2*(lower[2]-lower[0]), 'Top cap is not at the top'


def test_view_frame_preserves_bed_axes_and_source_geometry():
    top = view_transform('top')
    assert top.multiply(cq.Vector(1, 0, 0)).toTuple() == pytest.approx((1, 0, 0))
    assert top.multiply(cq.Vector(0, 1, 0)).toTuple() == pytest.approx((0, 1, 0))
    shape = cq.Workplane('XY').box(7, 5, 11, centered=False).val()
    before = [v.toTuple() for v in shape.Vertices()]
    render(shape, 'isometric', 800, 600, False)
    assert [v.toTuple() for v in shape.Vertices()] == before
