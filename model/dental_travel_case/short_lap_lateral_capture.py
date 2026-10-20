"""Snapshot capture on deformed native triangles; not a holding-force solver.

Virtually withdraw the cap and measure additional radial tooth retraction needed
for clearance. Constant initial compression alone is not called axial capture.
Both the state and the virtual paths are sampled, not continuous-motion proofs.
"""
import json
import gzip
from pathlib import Path
import shutil
import sys
import tempfile

import numpy as np
from physical_analysis.mesh_witness import inspect_mesh_pair
from short_lap_lateral_view import read_frame
from physical_analysis.backends.worker import HEADER, solver_number, summarize
from closure_research_checks import hashes
import short_lap_reinforced as design

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'notes/short_lap'
SPLIT = ((0,3,5),(3,1,4),(5,4,2),(3,4,5))
TRAVEL = (0.,.25,.5,1.,1.5,2.,3.,4.,6.)


def require_current_intent(case, stage, axis):
    """Bind native shapes/fixture to the current dimensions used for selection."""
    from physical_analysis.backends.structural import CalculixBackend
    from physical_analysis.questions import _intent
    from short_lap_lateral import seated_question,pickup_question,targeted_question
    if stage == 'targeted_v2':
        q = targeted_question(axis)
    else:
        factory = {'seated':seated_question,'pickup':pickup_question}[stage]
        q = factory(axis,mesh=2.5,increment=.02,penalty=20000.)
    with tempfile.TemporaryDirectory(prefix='lateral_identity_') as temporary:
        request = CalculixBackend().prepare_request(q.build_case(),Path(temporary))
    if _intent(request) != _intent(case):
        raise ValueError('Native snapshot differs from current geometry or physical fixture')


def retain_snapshot(directory, fraction, *, parent_completed):
    """Keep original native bytes for one accepted frame, never a completed run.

    Unpack gzip files into the matching native directory to repeat inspection.
    This archive deliberately has no AnalysisResult or study completion receipt.
    """
    target = OUT/'snapshots'/f'{directory.parent.name}_{fraction:g}'
    target.mkdir(parents=True,exist_ok=False)
    names = ['case.json','run_metadata.json','regions.json','analysis.sta',
             'analysis.inp','solver.log']
    names += [p.name for p in directory.glob('part_*.brep')]
    for name in names:
        with (directory/name).open('rb') as source, (target/(name+'.gz')).open('wb') as raw:
            with gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as saved:
                shutil.copyfileobj(source,saved)
    with (directory/'analysis.dat').open('rb') as source, (target/'analysis.dat.gz').open('wb') as raw:
        with gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as saved:
            selected = False
            for line in source:
                match = HEADER.match(line.decode('ascii'))
                if match:
                    selected = abs(solver_number(match[2])-fraction) < 1e-8
                if selected:
                    saved.write(line)
    (target/'scope.json').write_text(json.dumps(dict(
        status='accepted_frame_snapshot',completed=False,parent_run_completed=parent_completed,
        accepted_fraction=fraction,
        source_directory=str(directory.relative_to(ROOT)),
        warning='Only one accepted output frame retained. No complete loading path, sensitivity or impact qualification.'),indent=2)+'\n')
    return str(target.relative_to(ROOT))


def surface(mesh, displacement, faces):
    ids = sorted({n for _,_,ns in faces for n in ns})
    if not ids:
        raise ValueError('Empty tooth or cap surface')
    index = {n:i for i,n in enumerate(ids)}
    points = np.array([np.asarray(mesh['nodes'][n])+displacement[n] for n in ids])
    triangles = np.array([[index[ns[i]] for i in tri] for _,_,ns in faces for tri in SPLIT])
    return points,triangles


def review(stage, axis, fraction):
    if stage not in ('seated','pickup','targeted_v2'):
        raise ValueError(stage)
    if axis not in ('x','y'):
        raise ValueError(axis)
    source_identity = hashes(('short_lap_lateral_capture.py','short_lap_lateral_view.py',
        'short_lap_lateral.py','short_lap_reinforced.py','short_lap_refinement.py',
        '../../physical_analysis/mesh_witness.py','../../physical_analysis/backends/worker.py'))
    directory = OUT/'native'/f'lateral_{stage}_{axis}'/'baseline'
    case,metadata,meshes,frame,displacement = read_frame(directory,fraction)
    require_current_intent(case,stage,axis)
    regions = json.loads((directory/'regions.json').read_text())
    nodes = {n:p for mesh in meshes.values() for n,p in mesh['nodes'].items()}
    elements = {e:ns for mesh in meshes.values() for e,ns in mesh['elements'].items()}
    _,history = summarize(case,{fraction:frame},meshes,nodes,elements,regions)
    quality = history[0]
    parent_result = directory/'result.json'
    parent_completed = json.loads(parent_result.read_text())['completed'] if parent_result.exists() else False
    d = design.build(design.SELECTED_OVERLAP)['dimensions']
    cap,cap_tri = surface(meshes['part'],displacement,meshes['part']['surface'])
    radius = d.sleeve_width/2
    body = meshes['body']
    rows = {}
    for sign in (-1,1):
        if axis == 'y' and sign == -1:
            continue  # Mirror image of the retained positive-X half.
        faces = []
        for face in body['surface']:
            initial = np.array([body['nodes'][n] for n in face[2]])
            radial = sign*initial[:,0]
            if (radial.min() >= radius-1e-5 and radial.max() > radius+1e-5
                    and initial[:,2].min() >= d.latch_z-1.3
                    and initial[:,2].max() <= d.latch_z+2.):
                faces.append(face)
        tooth,tooth_tri = surface(body,displacement,faces)
        def blocked(travel,retraction):
            moving = tooth-np.array([sign*retraction,0.,travel])
            r = inspect_mesh_pair(moving,tooth_tri,cap,cap_tri,search_distance_mm=.001)
            if not r['obstacle_surface_closed']:
                raise ValueError('Containment check requires the complete closed cap surface')
            return r['intersection_detected']
        paths = []
        for travel in TRAVEL:
            if blocked(travel,1.2):
                raise ValueError('Retracted-tooth negative control remains obstructed')
            lo,hi = 0.,1.2
            if not blocked(travel,0.):
                hi = 0.
            else:
                while hi-lo > .01:
                    mid = (lo+hi)/2
                    if blocked(travel,mid):
                        lo = mid
                    else:
                        hi = mid
            paths.append(dict(virtual_withdrawal_mm=travel,
                              additional_inward_clearance_shift_mm=hi))
        margin = max(p['additional_inward_clearance_shift_mm'] for p in paths)-paths[0]['additional_inward_clearance_shift_mm']
        rows[str(sign)] = dict(face_count=len(faces),path=paths,
            extra_retraction_above_current_contact_mm=margin,
            sampled_capture_witness=margin >= .05,
            inward_1_2mm_negative_control_clear=True)
    forces = {int(row[0]):np.array(row[1:]) for row in frame['forces']}
    index = 0 if axis == 'x' else 1
    reaction = float(sum(forces[n][index] for n in regions['lateral']['nodes']))*2
    motion = regions['lateral']
    progress = np.asarray(motion['progress'])
    drive = motion['displacement_mm'][index]*float(np.interp(fraction,progress[:,0],progress[:,1]))
    result = dict(scope=__doc__,stage=stage,axis=axis,load_fraction=fraction,
        run_completed=parent_completed,interpretation='Diagnostic accepted snapshot only; full side-release study INCONCLUSIVE',
        snapshot_quality=quality,
        roof_drive_mm=drive+(.1 if stage == 'pickup' else 0.),
        full_fixture_signed_lateral_reaction_N=reaction,
        native_input_sha256=metadata['input_sha256'],native_case_sha256=metadata['case_sha256'],
        native_maximum_penetration_mm=max((max(0.,-r[2]) for r in frame['relative contact displacement']),default=0.),
        radial_bracket_width_at_most_mm=.01,provisional_capture_margin_mm=.05,
        source_sha256=source_identity,
        catches=rows)
    result['native_snapshot'] = retain_snapshot(directory,fraction,parent_completed=parent_completed)
    output = OUT/f'lateral_capture_{stage}_{axis}_{fraction:g}.json'
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit('Use seated|pickup|targeted_v2 x|y ACCEPTED_FRACTION')
    review(sys.argv[1],sys.argv[2],float(sys.argv[3]))
