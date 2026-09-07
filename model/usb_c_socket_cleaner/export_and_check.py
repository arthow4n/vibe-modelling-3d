"""Export the final print-ready source and perform lightweight file checks."""
from pathlib import Path
import json
import struct
import runpy

import cadquery as cq


directory = Path(__file__).resolve().parent
namespace = runpy.run_path(str(directory / "usb_c_socket_cleaner.py"))
result = namespace["result"]
shape = result.val()
assert shape.isValid()
assert len(shape.Solids()) == 1

bounding_box = shape.BoundingBox()
bounds = [
    bounding_box.xmin,
    bounding_box.ymin,
    bounding_box.zmin,
    bounding_box.xmax,
    bounding_box.ymax,
    bounding_box.zmax,
]

step_path = directory / "usb_c_socket_cleaner.step"
stl_path = directory / "usb_c_socket_cleaner.stl"
cq.exporters.export(shape, str(step_path))
cq.exporters.export(shape, str(stl_path), tolerance=0.025, angularTolerance=0.1)

reloaded = cq.importers.importStep(str(step_path)).val()
reloaded_box = reloaded.BoundingBox()
reloaded_bounds = [
    reloaded_box.xmin,
    reloaded_box.ymin,
    reloaded_box.zmin,
    reloaded_box.xmax,
    reloaded_box.ymax,
    reloaded_box.zmax,
]
assert reloaded.isValid() and len(reloaded.Solids()) == 1
assert max(abs(a - b) for a, b in zip(bounds, reloaded_bounds)) < 0.01

stl_data = stl_path.read_bytes()
triangle_count = struct.unpack_from("<I", stl_data, 80)[0]
assert len(stl_data) == 84 + 50 * triangle_count

vertices = []
for index in range(triangle_count):
    triangle = struct.unpack_from("<12fH", stl_data, 84 + 50 * index)
    vertices.extend((triangle[3:6], triangle[6:9], triangle[9:12]))
mesh_bounds = [
    min(vertex[axis] for vertex in vertices) for axis in range(3)
] + [max(vertex[axis] for vertex in vertices) for axis in range(3)]
assert max(abs(a - b) for a, b in zip(bounds, mesh_bounds)) < 0.03

report = {
    "units": "mm",
    "source": "usb_c_socket_cleaner.py",
    "solids": 1,
    "bounds_mm": [round(value, 4) for value in bounds],
    "volume_cm3": round(shape.Volume() / 1000.0, 4),
    "stl_triangles": triangle_count,
    "step_bounds_agree_within_mm": 0.01,
    "stl_bounds_agree_within_mm": 0.03,
    "physical_testing": "not yet printed or tested in a physical receptacle",
}
(directory / "notes" / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
