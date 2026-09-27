"""Parse and summarize linear ASCII slicer paths for the Orca review helper.

The parser also covers historical PrusaSlicer output used in this repository.
It follows absolute/relative XYZ and E modes, requires millimetres, and rejects
arcs and unsupported motion rather than guessing.
"""
from collections import defaultdict
import math
from pathlib import Path
import re

TOKEN = re.compile(r"([XYZEF])(-?(?:\d+(?:\.\d*)?|\.\d+))")


def _is_bridge(role):
    return "bridge" in role.casefold()


def _is_support(role):
    return "support" in role.casefold()


def read_paths(path):
    layers = defaultdict(list)
    position = {axis: 0.0 for axis in "XYZ"}
    e_position = 0.0
    xyz_absolute, e_absolute, units_mm = True, None, True
    role, z, width, collecting = "Unknown", None, 0.45, False
    metadata = {}
    with Path(path).open() as source:
        for line_number, raw in enumerate(source, 1):
            line = raw.strip()
            if line.startswith(";TYPE:"):
                role = line[6:].strip()
            elif line.startswith((";Z:", ";Z_HEIGHT:")):
                marker = line.split(":", 1)[1]
                z = round(float(marker), 5)
                layers[z]
                collecting = True
            elif line.startswith(";WIDTH:"):
                width = float(line[7:])
            elif re.match(r";\s*(filament used|estimated printing time)", line, re.I):
                key, value = line[1:].strip().split(" = ", 1)
                metadata[key] = value
            elif re.match(r";\s*EXECUTABLE_BLOCK_END", line):
                collecting = False

            code = line.split(";", 1)[0].strip()
            if not code:
                continue
            pieces = code.split()
            command = pieces[0].upper()
            if command == "G20":
                units_mm = False
                raise ValueError(f"Unsupported inch units G20 at line {line_number}")
            if command == "G21":
                units_mm = True
                continue
            if command == "G90":
                xyz_absolute = True
                continue
            if command == "G91":
                xyz_absolute = False
                continue
            if command == "M82":
                e_absolute = True
                continue
            if command == "M83":
                e_absolute = False
                continue
            if command in ("G2", "G3"):
                raise ValueError(f"Unsupported arc {command} at line {line_number}")
            values = {key: float(value) for key, value in TOKEN.findall(code)}
            if command == "G92":
                position.update({key: value for key, value in values.items() if key in position})
                if "E" in values:
                    e_position = values["E"]
                continue
            if command not in ("G0", "G1"):
                continue
            if not units_mm:
                raise ValueError(f"Unsupported units at line {line_number}")

            start = position.copy()
            if xyz_absolute:
                end = {axis: values.get(axis, position[axis]) for axis in position}
            else:
                end = {axis: position[axis] + values.get(axis, 0.0) for axis in position}
            length = math.hypot(end["X"] - start["X"], end["Y"] - start["Y"])

            delta_e = 0.0
            if "E" in values:
                if e_absolute is None:
                    if collecting:
                        raise ValueError(f"Missing M82/M83 extrusion mode at line {line_number}")
                elif e_absolute:
                    delta_e = values["E"] - e_position
                    e_position = values["E"]
                else:
                    delta_e = values["E"]
                    e_position += delta_e

            if collecting and delta_e > 0:
                if z is None:
                    raise ValueError(f"Missing layer marker at line {line_number}")
                if abs(end["Z"] - start["Z"]) > 1e-5:
                    raise ValueError(f"Nonplanar extrusion at line {line_number}")
                if length > 1e-6:
                    layers[z].append({"role": role, "a": [start["X"], start["Y"]],
                                      "b": [end["X"], end["Y"]], "length_mm": length,
                                      "filament_mm": delta_e, "width_mm": width,
                                      "line": line_number})
            position = end

    if not any(segments for segments in layers.values()):
        raise ValueError("No deposited layers found")
    return layers, metadata


def summarize(layers, metadata):
    roles = defaultdict(lambda: {"segments": 0, "length_mm": 0, "max_segment_mm": 0})
    bridges, per_layer = [], []
    for z, segments in sorted(layers.items()):
        layer_roles = defaultdict(int)
        for segment in segments:
            kind = segment["role"]
            roles[kind]["segments"] += 1
            roles[kind]["length_mm"] += segment["length_mm"]
            roles[kind]["max_segment_mm"] = max(roles[kind]["max_segment_mm"], segment["length_mm"])
            layer_roles[kind] += 1
            if _is_bridge(kind):
                bridges.append({"z": z, **segment})
        per_layer.append({"z": z, "roles": layer_roles})
    return {"metadata": metadata, "layer_count": len(layers), "roles": roles,
            "longest_bridge_segments": sorted(bridges, key=lambda s: s["length_mm"], reverse=True)[:12],
            "layers": per_layer,
            "limits": "Centerline lengths include anchors; no free-air span or physical simulation."}


if __name__ == "__main__":
    raise SystemExit("inspect_gcode.py is an internal parser; use review_print.py")
