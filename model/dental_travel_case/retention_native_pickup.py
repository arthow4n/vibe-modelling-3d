"""Inspect the M1 pickup pose in an existing native deck; never launch a solver.

This product-local witness checks the actual selected C3D10 boundary faces. It
establishes planar retaining-land coincidence and seating clearance only. Native
contact projection, initial overclosure elsewhere and structural response remain
separate evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from physical_analysis.backends.mesh import select_faces
from physical_analysis.backends.worker import saved_meshes
from model.dental_travel_case.m1_design import D

COORDINATE_TOLERANCE_MM = 1e-6


def cross(a, b):
    return a[0]*b[1]-a[1]*b[0]


def triangle_intersection_area(subject, boundary):
    """Clip two planar corner triangles; interiors in each mesh do not overlap."""
    polygon = [point.copy() for point in subject]
    if cross(boundary[1]-boundary[0], boundary[2]-boundary[0]) < 0:
        boundary = boundary[::-1]
    for a, b in zip(boundary, np.roll(boundary, -1, axis=0)):
        previous_polygon, polygon = polygon, []
        if not previous_polygon:
            break
        previous = previous_polygon[-1]
        previous_distance = cross(b-a, previous-a)
        for current in previous_polygon:
            distance = cross(b-a, current-a)
            if (distance >= -1e-10) != (previous_distance >= -1e-10):
                polygon.append(previous+(current-previous)*previous_distance/(previous_distance-distance))
            if distance >= -1e-10:
                polygon.append(current)
            previous, previous_distance = current, distance
    if len(polygon) < 3:
        return 0.
    return abs(sum(cross(a, b) for a, b in zip(polygon, polygon[1:]+polygon[:1])))/2


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_run(directory):
    directory = Path(directory)
    paths = {name: directory/name for name in ('case.json', 'analysis.inp')}
    hashes = {name: digest(path) for name, path in paths.items()}
    case = json.loads(paths['case.json'].read_text())
    if case['name'] != 'retention_m1' or len(case['contacts']) != 1:
        raise ValueError('This witness requires the M1 assembly case with its single contact pair')
    contact = case['contacts'][0]
    if contact['slave']['part'] != 'body' or contact['master']['part'] != 'cap':
        raise ValueError('This witness requires body-slave / cap-master selections')
    meshes = saved_meshes(case, paths['analysis.inp'])
    report = dict(scope='native planar geometry; no solver launch or contact-field extraction',
                  input_sha256=hashes['analysis.inp'], case_sha256=hashes['case.json'],
                  source=str(directory.resolve()), coordinate_tolerance_mm=COORDINATE_TOLERANCE_MM,
                  retaining_plane_z_mm=D.hook_bottom, parts={}, catches={},
                  native_initial_contact='UNKNOWN',
                  limitations=[
                      'This does not identify the native matched projections or initial overclosure elsewhere.',
                      'Planar corner triangles represent these straight-boundary lands; all six face nodes are checked for coplanarity.',
                      'Positive capture area does not establish holding force, shell stability or resistance to release.'])
    lands = {}
    for role, normal_sign, seat_z in (('slave', -1, D.seam), ('master', 1, D.seam+D.axial_play)):
        selection = contact[role]
        mesh = meshes[selection['part']]
        faces = select_faces(selection, meshes)
        points = np.array([[mesh['nodes'][node] for node in nodes] for _, _, nodes in faces])
        centers = points[:, :3].mean(axis=1)
        normals = np.cross(points[:, 1]-points[:, 0], points[:, 2]-points[:, 0])
        twice_area = np.linalg.norm(normals, axis=1)
        if np.any(twice_area <= 0):
            raise ValueError('Selected boundary includes a degenerate corner triangle')
        normals /= twice_area[:, None]
        interior = np.array([np.mean([mesh['nodes'][node] for node in mesh['elements'][element][:4]], axis=0)
                             for element, _, _ in faces])
        normals[np.einsum('ij,ij->i', normals, centers-interior) < 0] *= -1
        planar = np.max(abs(points[:, :, 2]-D.hook_bottom), axis=1) < COORDINATE_TOLERANCE_MM
        land = planar & (normals[:, 2]*normal_sign > 1-1e-6)
        seat = np.max(abs(points[:, :, 2]-seat_z), axis=1) < COORDINATE_TOLERANCE_MM
        if not np.any(land) or not np.any(seat):
            raise ValueError(f'Missing expected {role} pickup retaining or seating plane')
        lands[role] = (points[land], normals[land])
        report['parts'][selection['part']] = dict(selected_faces=len(faces),
            retaining_faces=int(sum(land)), retaining_area_mm2=float(sum(twice_area[land])/2),
            seat_faces=int(sum(seat)), seat_z_range_mm=[float(points[seat, :, 2].min()), float(points[seat, :, 2].max())],
            seat_area_mm2=float(sum(twice_area[seat])/2))
    for side in (-1, 1):
        selected = {}
        for role, (points, normals) in lands.items():
            mask = points[:, :3, 0].mean(axis=1)*side > 0
            if not np.any(mask):
                raise ValueError(f'Missing {role} retaining land on side {side}')
            selected[role] = points[mask]
            report['catches'].setdefault(str(side), {})[role] = dict(face_count=int(sum(mask)),
                plane_z_range_mm=[float(points[mask, :, 2].min()), float(points[mask, :, 2].max())],
                outward_normal_min=normals[mask].min(axis=0).tolist(),
                outward_normal_max=normals[mask].max(axis=0).tolist())
        report['catches'][str(side)]['coincident_footprint_area_mm2'] = sum(
            triangle_intersection_area(slave[:3, :2], master[:3, :2])
            for slave in selected['slave'] for master in selected['master'])
    body_seat = report['parts']['body']['seat_z_range_mm']
    cap_seat = report['parts']['cap']['seat_z_range_mm']
    report['seat_gap_range_mm'] = [cap_seat[0]-body_seat[1], cap_seat[1]-body_seat[0]]
    if hashes != {name: digest(path) for name, path in paths.items()}:
        raise ValueError('Native inputs changed during inspection; witness not written')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_directory', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    report = inspect_run(args.run_directory)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(output=str(args.output), catches=report['catches'],
                          seat_gap_range_mm=report['seat_gap_range_mm'],
                          native_initial_contact=report['native_initial_contact'])))


if __name__ == '__main__':
    main()
