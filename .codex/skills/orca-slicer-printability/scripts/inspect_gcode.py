"""Summarize linear ASCII slicer paths and optionally draw layer windows.

The parser covers OrcaSlicer output and historical PrusaSlicer output used in
this repository. It follows absolute/relative XYZ and E modes, requires
millimetres, and rejects arcs and unsupported motion rather than guessing.
Layer SVGs show deposited centerlines over the previous layer; they do not
simulate plastic, bonding or sag.
"""
import argparse
from collections import defaultdict
import json
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


def clip_segment(a, b, window):
    """Clip centerlines numerically; avoids renderer-dependent SVG clip paths."""
    low, high = 0.0, 1.0
    for axis in (0, 1):
        delta = b[axis] - a[axis]
        minimum, maximum = window[axis], window[axis + 2]
        if abs(delta) < 1e-12:
            if not minimum <= a[axis] <= maximum:
                return None
        else:
            t0, t1 = sorted(((minimum - a[axis]) / delta, (maximum - a[axis]) / delta))
            low, high = max(low, t0), min(high, t1)
            if low > high:
                return None
    return ([a[k] + low * (b[k] - a[k]) for k in (0, 1)],
            [a[k] + high * (b[k] - a[k]) for k in (0, 1)])


def draw_layers(layers, requested, window, output):
    xmin, ymin, xmax, ymax = window
    if xmax <= xmin or ymax <= ymin:
        raise ValueError("Window must have positive width and height")
    scale = min(400 / (xmax - xmin), 400 / (ymax - ymin))
    panel_width, panel_height = (xmax - xmin) * scale + 36, (ymax - ymin) * scale + 100
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{panel_width * len(requested)}" height="{panel_height + 65}" viewBox="0 0 {panel_width * len(requested)} {panel_height + 65}">',
           '<rect width="100%" height="100%" fill="white"/>',
           '<g font-family="DejaVu Sans" font-size="13" fill="#18212b">',
           '<text x="18" y="22">Actual sliced paths: gray = preceding layer; black = current; orange = overhang; red = bridge</text>']
    heights = sorted(layers)
    for index, target in enumerate(requested):
        z = min(heights, key=lambda value: abs(value - target))
        if abs(z - target) > .001:
            raise ValueError(f"Requested layer {target} absent; nearest is {z}")
        previous = heights[heights.index(z) - 1] if heights.index(z) else None
        left, top = index * panel_width + 18, 75
        w, h = (xmax - xmin) * scale, (ymax - ymin) * scale
        svg += [f'<text x="{left}" y="52">Z = {z:.2f} mm; previous = {previous}</text>',
                f'<rect x="{left}" y="{top}" width="{w}" height="{h}" fill="#fafafa" stroke="#b9c0c6"/>',
                '<g>']
        for background, height in [(True, previous), (False, z)]:
            for segment in layers.get(height, []):
                clipped = clip_segment(segment["a"], segment["b"], window)
                if clipped is None:
                    continue
                (ax, ay), (bx, by) = clipped
                role = segment["role"].casefold()
                if _is_bridge(role):
                    color = "#dd293e"
                elif "overhang" in role:
                    color = "#d87500"
                elif _is_support(role):
                    color = "#168ca0"
                else:
                    color = "#20252a"
                if background:
                    color = "#c5c9ce"
                stroke = segment["width_mm"] * scale if background else .11 * scale
                svg.append(f'<line x1="{left + (ax - xmin) * scale}" y1="{top + (ymax - ay) * scale}" x2="{left + (bx - xmin) * scale}" y2="{top + (ymax - by) * scale}" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round"/>')
        svg += ['</g>', f'<text x="{left}" y="{top + h + 22}">Window X {xmin:g}–{xmax:g}, Y {ymin:g}–{ymax:g} mm</text>']
    svg += ['<text x="18" y="' + str(panel_height + 45) + '">Previous paths use reported width; this is not a prediction of sag, bonding or hinge freedom.</text>', '</g></svg>']
    Path(output).write_text("\n".join(svg) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gcode", type=Path)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--svg", type=Path)
    parser.add_argument("--layers", type=float, nargs="+")
    parser.add_argument("--window", type=float, nargs=4, metavar=("XMIN", "YMIN", "XMAX", "YMAX"))
    args = parser.parse_args()
    layers, metadata = read_paths(args.gcode)
    summary = summarize(layers, metadata)
    args.json.write_text(json.dumps(summary, indent=2) + "\n")
    if args.svg:
        if not args.layers or not args.window:
            parser.error("--svg requires --layers and --window")
        draw_layers(layers, args.layers, args.window, args.svg)
    print(json.dumps({"layer_count": len(layers), "roles": summary["roles"], "metadata": metadata}))


if __name__ == "__main__":
    main()
