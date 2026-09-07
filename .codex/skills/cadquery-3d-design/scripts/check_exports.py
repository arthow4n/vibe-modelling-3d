"""Read-only STEP/binary-STL consistency checks. Import inside a CadQuery MCP entry point.

Checks topology, winding, bounds, component volume and optional bed contact.
Does not prove shape identity, absence of self-intersections, strength or printability.
"""
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import hashlib
import json
import math
import struct


def mesh_components(path):
    raw = Path(path).read_bytes()
    if len(raw) < 84:
        raise ValueError('Expected a nonempty binary STL')
    count = struct.unpack_from('<I', raw, 80)[0]
    if count == 0 or len(raw) != 84 + 50 * count:
        raise ValueError('Invalid binary STL length/count; ASCII STL is not supported')
    parent = list(range(count))
    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    owners = defaultdict(list)
    directions = Counter()
    triangles = []
    for i in range(count):
        values = struct.unpack_from('<12f', raw, 84 + 50*i)
        if not all(math.isfinite(v) for v in values):
            raise ValueError(f'Nonfinite triangle {i}')
        tri = [tuple(values[3+3*j:6+3*j]) for j in range(3)]
        u = [tri[1][k]-tri[0][k] for k in range(3)]
        v = [tri[2][k]-tri[0][k] for k in range(3)]
        cross = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
        if sum(c*c for c in cross) <= 1e-20:
            raise ValueError(f'Degenerate triangle {i}')
        triangles.append(tri)
        for j in range(3):
            a, b = tri[j], tri[(j+1) % 3]
            edge = tuple(sorted((a, b)))
            owners[edge].append(i)
            directions[edge] += 1 if a < b else -1
    if any(len(indices) != 2 for indices in owners.values()):
        raise ValueError('Open or nonmanifold mesh edges')
    if any(directions.values()):
        raise ValueError('Inconsistent adjacent triangle winding')
    for a, b in owners.values():
        parent[root(a)] = root(b)
    grouped = defaultdict(list)
    for i, tri in enumerate(triangles):
        grouped[root(i)].append(tri)
    components = []
    for tris in grouped.values():
        points = [p for tri in tris for p in tri]
        # Translate near the component before summing signed tetrahedron volumes.
        origin = points[0]
        volume = 0.0
        for tri in tris:
            a, b, c = [[p[k]-origin[k] for k in range(3)] for p in tri]
            volume += (a[0]*(b[1]*c[2]-b[2]*c[1]) + a[1]*(b[2]*c[0]-b[0]*c[2]) + a[2]*(b[0]*c[1]-b[1]*c[0])) / 6
        if volume <= 0:
            raise ValueError('Nonpositive shell volume: reversed winding or unsupported enclosed cavity shell')
        components.append({'bounds_mm': [min(p[k] for p in points) for k in range(3)] +
                           [max(p[k] for p in points) for k in range(3)],
                           'volume_mm3': volume, 'triangles': len(tris)})
    return components


def check_pair(step_path, stl_path, expected_solids, tolerance=0.035,
               volume_relative_tolerance=0.01, require_bed_contact=True):
    import cadquery as cq
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib
    if expected_solids < 1 or not math.isfinite(tolerance) or tolerance <= 0:
        raise ValueError('Positive expected count and bounds tolerance required')
    if not math.isfinite(volume_relative_tolerance) or volume_relative_tolerance <= 0:
        raise ValueError('Positive relative volume tolerance required')
    step_path, stl_path = Path(step_path), Path(stl_path)
    solids = cq.importers.importStep(str(step_path)).solids().vals()
    meshes = mesh_components(stl_path)
    if len(solids) != expected_solids or len(meshes) != expected_solids:
        raise ValueError(f'Expected {expected_solids} components; STEP={len(solids)}, STL={len(meshes)}')
    cad = []
    for solid in solids:
        if not solid.isValid() or solid.Volume() <= 0:
            raise ValueError('Invalid STEP solid')
        box = Bnd_Box()
        BRepBndLib.AddOptimal_s(solid.wrapped, box, False, False)
        cad.append({'bounds_mm': list(box.Get()), 'volume_mm3': solid.Volume()})
    # Find a one-to-one assignment; do not rely on float sorting or solid order.
    candidates = []
    for mesh in meshes:
        candidates.append([i for i, solid in enumerate(cad)
            if max(abs(a-b) for a, b in zip(mesh['bounds_mm'], solid['bounds_mm'])) <= tolerance
            and abs(mesh['volume_mm3']-solid['volume_mm3'])/solid['volume_mm3'] <= volume_relative_tolerance])
    def match(todo, used):
        if not todo:
            return []
        j = min(todo, key=lambda k: len(set(candidates[k])-used))
        for i in candidates[j]:
            if i not in used:
                tail = match([k for k in todo if k != j], used | {i})
                if tail is not None:
                    return [(j, i)] + tail
        return None
    pairs = match(list(range(len(meshes))), set())
    if pairs is None:
        raise ValueError('STEP/STL component bounds or volumes do not match')
    if require_bed_contact and any(abs(c['bounds_mm'][2]) > tolerance for c in cad+meshes):
        raise ValueError('A component does not meet Z=0 within tolerance')
    return {'checks_passed': True, 'expected_solids': expected_solids,
            'bounds_tolerance_mm': tolerance, 'volume_relative_tolerance': volume_relative_tolerance,
            'bed_contact_required': require_bed_contact,
            'step_components': cad, 'stl_components': meshes, 'component_assignment': pairs,
            'STEP_sha256': hashlib.sha256(step_path.read_bytes()).hexdigest(),
            'STL_sha256': hashlib.sha256(stl_path.read_bytes()).hexdigest(),
            'limits': 'Binary STL in mm; exact shared vertices required. Bounds/volume agreement is not shape identity. No self-intersection, force or printability simulation.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('step', type=Path)
    parser.add_argument('stl', type=Path)
    parser.add_argument('--expected-solids', type=int, required=True)
    parser.add_argument('--json', type=Path, required=True)
    parser.add_argument('--tolerance', type=float, default=0.035)
    parser.add_argument('--volume-relative-tolerance', type=float, default=0.01)
    parser.add_argument('--allow-floating', action='store_true')
    args = parser.parse_args()
    report = check_pair(args.step, args.stl, args.expected_solids, args.tolerance,
                        args.volume_relative_tolerance, not args.allow_floating)
    args.json.write_text(json.dumps(report, indent=2)+'\n')
    print('Export checks passed; physical printability remains unverified.')


if __name__ == '__main__':
    main()
