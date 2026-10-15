"""Two one-sided snap-fit experiments. Millimetres; no case revisions.

A reuses the production M1 builders. B is a different, flat-printed concept,
not a drop-in replacement. Builders return named, positioned components.
"""
from dataclasses import dataclass
from pathlib import Path
import sys

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from model.dental_travel_case import m1_design as m1


def block(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").box(x1-x0, y1-y0, z1-z0)
            .translate(((x0+x1)/2, (y0+y1)/2, (z0+z1)/2)))


def baseline():
    """24 mm-wide strip of one M1 end; keep root, liner, pad and pocket."""
    d = m1.D
    lo, hi = d.beam_root-10, d.seam+20
    # Only the negative-X end contains the at_end(..., +1) production catch.
    crop = block(-d.width/2-1, -d.width/2+11, -12, 12, lo, hi)
    male = m1.body_fixed(d).union(m1.tongue(d)).intersect(crop)
    female = m1.cap(d).intersect(crop)
    return {"leaf_fixture": male, "keeper": female}


@dataclass(frozen=True)
class FlatDimensions:
    length: float = 49.0
    thickness: float = 1.2
    breadth: float = 6.0
    projection: float = 1.0
    clearance: float = .2
    travel: float = 1.2
    root_radius: float = 2.0
    shoulder: float = 42.0
    axial_play: float = .15


F = FlatDimensions()


def flat_leaf(displacement=0):
    """Prescribed end-loaded beam envelope, not a material/contact solution."""
    f = F
    def offset(x):
        s = max(0, x)/f.length
        return displacement*s*s*(3-s)/2
    stations = [f.length*i/24 for i in range(25)]
    upper = [(x, -offset(x)) for x in stations]
    lower = [(x, -f.thickness-offset(x)) for x in reversed(stations)]
    leaf = cq.Workplane("XY").polyline(upper+lower).close().extrude(f.breadth)
    root = block(-6, 0, -6, 0, 0, f.breadth)
    rail = block(-6, 50, -6, -4, 0, f.breadth)
    # A concave R2 spreads the attachment; beam length is not shortened to save PLA.
    fixed = root.union(rail).union(leaf)
    if displacement == 0:
        edges = [e for e in fixed.val().Edges()
                 if abs(e.Center().x) < 1e-6
                 and abs(e.Center().y+f.thickness) < 1e-6]
        if len(edges) != 1:
            raise ValueError("Flat root blend must select one axial edge")
        fixed = fixed.newObject(edges).fillet(f.root_radius)
    tooth_points = [(f.shoulder, -.2), (f.shoulder, f.projection),
                    (f.shoulder+1, f.projection), (f.length, 0),
                    (f.length, -.2)]
    tooth = (cq.Workplane("XY")
             .polyline([(x, y-offset(x)) for x, y in tooth_points])
             .close().extrude(f.breadth))
    return fixed.union(tooth)


def flat_keeper():
    f = F
    # Backplate locates one broad face. The opposite face stays open for inspection.
    back = block(32, 53, -8, 3.2, f.breadth+.25, f.breadth+1.85)
    lower_guide = block(32, 53, -8, -6.25, 0, f.breadth+.3)
    stop = block(50, 53, -8, 3.2, 0, f.breadth+.3)
    ledge = block(32, f.shoulder-f.axial_play, f.clearance, 3.2,
                  0, f.breadth+.3)
    return back.union(lower_guide).union(stop).union(ledge)


def components(variant):
    if variant == "A-original":
        return baseline()
    if variant == "B-flat-PLA":
        return {"leaf_fixture": flat_leaf(), "keeper": flat_keeper()}
    raise ValueError(f"Unknown study variant: {variant!r}")


def assembly(parts, name):
    result = cq.Assembly(name=name)
    for key, shape in parts.items():
        result.add(shape, name=key)
    return result


def print_layout(variant):
    parts = components(variant)
    if variant == "A-original":
        d = m1.D
        parts = {
            "leaf_fixture": parts["leaf_fixture"].translate((d.width/2, 0, -(d.beam_root-10))),
            "keeper": (parts["keeper"].rotate((0, 0, 0), (1, 0, 0), 180)
                       .translate((d.width/2+28, 0, d.seam+20))),
        }
    elif variant == "B-flat-PLA":
        parts = {
            "leaf_fixture": parts["leaf_fixture"],
            "keeper": (parts["keeper"].rotate((0, 0, 0), (1, 0, 0), 180)
                       .translate((0, 17, F.breadth+1.85))),
        }
    return assembly(parts, variant+"_print")
