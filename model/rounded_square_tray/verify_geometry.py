"""Measure important surfaces and exercise one smaller parameter configuration."""
from pathlib import Path
import json
import cadquery as cq
from rounded_square_tray import result
from tray_geometry import build_tray


def planar_face_at(shape, z):
    faces = [f for f in shape.Faces() if f.geomType() == "PLANE"
             and abs(f.BoundingBox().zmin - z) < 1e-5
             and abs(f.BoundingBox().zmax - z) < 1e-5]
    assert len(faces) == 1, (z, len(faces))
    return faces[0]


floor = planar_face_at(result, 6)
bed = planar_face_at(result, 0)
rim = planar_face_at(result, 37)
assert abs(floor.BoundingBox().xlen - 200) < 1e-4
assert abs(floor.BoundingBox().ylen - 200) < 1e-4
section = cq.Workplane("XY").add(result).section(20).wires().vals()
assert len(section) == 2
inner, outer = sorted(section, key=lambda w: w.BoundingBox().xlen)
assert abs(inner.BoundingBox().xlen - 220) < 1e-4
assert abs(inner.BoundingBox().ylen - 220) < 1e-4
rim_wires = sorted(rim.Wires(), key=lambda w: w.BoundingBox().xlen)
rim_land = (rim_wires[1].BoundingBox().xlen - rim_wires[0].BoundingBox().xlen) / 2
assert rim_land > 3
alternate = build_tray(180, 25, 26, 5, 9, 6, 8, 2, 2, 6)
assert alternate.isValid() and len(alternate.Solids()) == 1
assert abs(alternate.BoundingBox().zlen - 31) < 1e-4
report = {
    "valid": result.isValid(), "solids": len(result.Solids()),
    "flat_floor_xy_mm": [floor.BoundingBox().xlen, floor.BoundingBox().ylen],
    "floor_z_mm": floor.Center().z, "rim_z_mm": rim.Center().z,
    "cavity_xy_at_z20_mm": [inner.BoundingBox().xlen, inner.BoundingBox().ylen],
    "straight_wall_horizontal_thickness_at_z20_mm": (outer.BoundingBox().xlen - inner.BoundingBox().xlen) / 2,
    "flat_rim_land_straight_side_mm": rim_land,
    "bed_contact_xy_mm": [bed.BoundingBox().xlen, bed.BoundingBox().ylen],
    "bed_contact_area_mm2": bed.Area(),
    "alternate_configuration": {"cavity": 180, "corner": 25, "depth": 26,
        "base": 5, "wall": 9, "inset": 6, "floor_round": 8,
        "rim_rounds": 2, "bottom_round": 6, "valid_one_solid": True},
}
Path(__file__).with_name("notes").joinpath("geometry_checks.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
