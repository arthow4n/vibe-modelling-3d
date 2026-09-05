"""Summarize ASCII PrusaSlicer paths and optionally draw selected layer windows.

Standard library only. Accepts G21, absolute XYZ, relative E, linear deposition.
Rejects incompatible modes rather than silently producing misleading results.
SVGs show deposited centerlines over previous-layer paths, not simulated plastic.
"""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import re

TOKEN = re.compile(r"([XYZEF])(-?(?:\d+(?:\.\d*)?|\.\d+))")


def read_paths(path):
    layers = defaultdict(list)
    position = {"X": 0.0, "Y": 0.0, "Z": 0.0}
    role, z, width, relative_e = "Unknown", None, 0.45, False
    metadata = {}
    for line_number, raw in enumerate(path.open(), 1):
        line = raw.strip()
        if line.startswith(";TYPE:"):
            role = line[6:]
        elif line.startswith(";Z:"):
            z = round(float(line[3:]), 5)
        elif line.startswith(";WIDTH:"):
            width = float(line[7:])
        elif line.startswith(("; filament used [g]", "; estimated printing time (normal mode)")):
            key, value = line[2:].split(" = ", 1)
            metadata[key] = value
        code = line.split(";", 1)[0].strip()
        if not code:
            continue
        command = code.split()[0]
        if command in ("G20", "G91", "M82", "G2", "G3"):
            raise ValueError(f"Unsupported {command} at line {line_number}")
        if command == "M83":
            relative_e = True
        values = {key: float(value) for key, value in TOKEN.findall(code)}
        if command == "G92":
            position.update({key: value for key, value in values.items() if key in position})
        if command not in ("G0", "G1"):
            continue
        end = {key: values.get(key, position[key]) for key in position}
        length = math.hypot(end["X"]-position["X"], end["Y"]-position["Y"])
        if values.get("E", 0) > 0 and length > 1e-6:
            if not relative_e or z is None:
                raise ValueError(f"Missing M83 or layer marker at line {line_number}")
            if abs(end["Z"]-position["Z"]) > 1e-5:
                raise ValueError(f"Nonplanar extrusion at line {line_number}")
            layers[z].append({"role": role, "a": [position["X"], position["Y"]],
                              "b": [end["X"], end["Y"]], "length_mm": length,
                              "filament_mm": values["E"], "width_mm": width,
                              "line": line_number})
        position = end
    if not layers:
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
            if kind == "Bridge infill":
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
        delta = b[axis]-a[axis]
        minimum, maximum = window[axis], window[axis+2]
        if abs(delta) < 1e-12:
            if not minimum <= a[axis] <= maximum:
                return None
        else:
            t0, t1 = sorted(((minimum-a[axis])/delta, (maximum-a[axis])/delta))
            low, high = max(low, t0), min(high, t1)
            if low > high:
                return None
    return ([a[k]+low*(b[k]-a[k]) for k in (0, 1)],
            [a[k]+high*(b[k]-a[k]) for k in (0, 1)])


def draw_layers(layers, requested, window, output):
    xmin, ymin, xmax, ymax = window
    if xmax <= xmin or ymax <= ymin:
        raise ValueError("Window must have positive width and height")
    scale = min(400/(xmax-xmin), 400/(ymax-ymin))
    panel_width, panel_height = (xmax-xmin)*scale+36, (ymax-ymin)*scale+100
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{panel_width*len(requested)}" height="{panel_height+65}" viewBox="0 0 {panel_width*len(requested)} {panel_height+65}">',
           '<rect width="100%" height="100%" fill="white"/>',
           '<g font-family="DejaVu Sans" font-size="13" fill="#18212b">',
           '<text x="18" y="22">Actual sliced paths: gray = preceding layer; black = current; orange = overhang; red = bridge</text>']
    heights = sorted(layers)
    colors = {"Bridge infill": "#dd293e", "Overhang perimeter": "#d87500",
              "Support material": "#168ca0", "Support material interface": "#168ca0"}
    for index, target in enumerate(requested):
        z = min(heights, key=lambda value: abs(value-target))
        if abs(z-target) > .001:
            raise ValueError(f"Requested layer {target} absent; nearest is {z}")
        previous = heights[heights.index(z)-1] if heights.index(z) else None
        left, top = index*panel_width+18, 75
        w, h = (xmax-xmin)*scale, (ymax-ymin)*scale
        svg += [f'<text x="{left}" y="52">Z = {z:.2f} mm; previous = {previous}</text>',
                f'<rect x="{left}" y="{top}" width="{w}" height="{h}" fill="#fafafa" stroke="#b9c0c6"/>',
                '<g>']
        for background, height in [(True, previous), (False, z)]:
            for segment in layers.get(height, []):
                clipped = clip_segment(segment["a"], segment["b"], window)
                if clipped is None:
                    continue
                (ax, ay), (bx, by) = clipped
                color = "#c5c9ce" if background else colors.get(segment["role"], "#20252a")
                stroke = segment["width_mm"]*scale if background else .11*scale
                svg.append(f'<line x1="{left+(ax-xmin)*scale}" y1="{top+(ymax-ay)*scale}" x2="{left+(bx-xmin)*scale}" y2="{top+(ymax-by)*scale}" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round"/>')
        svg += ['</g>', f'<text x="{left}" y="{top+h+22}">Window X {xmin:g}–{xmax:g}, Y {ymin:g}–{ymax:g} mm</text>']
    svg += ['<text x="18" y="'+str(panel_height+45)+'">Previous paths use reported width; this is not a prediction of sag, bonding or hinge freedom.</text>', '</g></svg>']
    output.write_text("\n".join(svg)+"\n")


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
    args.json.write_text(json.dumps(summary, indent=2)+"\n")
    if args.svg:
        if not args.layers or not args.window:
            parser.error("--svg requires --layers and --window")
        draw_layers(layers, args.layers, args.window, args.svg)
    print(json.dumps({"layer_count": len(layers), "roles": summary["roles"], "metadata": metadata}))


if __name__ == "__main__":
    main()
