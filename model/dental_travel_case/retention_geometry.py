"""Exact-CAD M1 capture investigation; no force or printed-fit prediction.

Run through execute.py with an explicit JSON destination. Nominal solids and the
prescribed deformed hook come directly from m1_design. Rigid pose samples are
reported alongside fixed-body interference: an intersecting guide is not a
physically admissible rigid escape path.
"""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

import cadquery as cq
from m1_design import D, at_end, body_fixed, cap, hook, leaf_offset

VOLUME_EPS = 1e-7  # numerical Boolean discrimination, mm3; not a fit allowance
RETRACTION_RESOLUTION = .005  # mm terminal travel


def hook_shape(d, sign, retraction):
    return at_end(hook(d, retraction), sign).val()


def move_cap(shape, d, *, lift, dx, dy, angle_x, angle_y):
    part = shape.rotate((0, 0, d.seam), (1, 0, d.seam), angle_x)
    part = part.rotate((0, 0, d.seam), (0, 1, d.seam), angle_y)
    return part.translate((dx, dy, lift))


def overlap(a, b):
    return a.intersect(b).Volume()


def planar_faces(shape, z, normal_z):
    selected = []
    for face in shape.Faces():
        if face.geomType() == 'PLANE' and abs(face.Center().z-z)<1e-5:
            n = face.normalAt()
            if n.z*normal_z > .999999:
                selected.append(face)
    return selected


def seated_land(d, upper, sign, radial_retraction=0.):
    """Common flat shoulder area after closing only the known axial play."""
    tooth = hook_shape(d, sign, 0).translate((sign*radial_retraction,0,0))
    hook_faces = planar_faces(tooth, d.hook_bottom, -1)
    receiver_faces = planar_faces(upper, d.hook_bottom-d.axial_play, 1)
    witnesses = []
    for hface in hook_faces:
        for rface in receiver_faces:
            aligned = rface.translate((0, 0, d.axial_play))
            common = hface.intersect(aligned)
            if common.Area() > 1e-7:
                bounds = common.BoundingBox()
                witnesses.append(dict(area_mm2=common.Area(),
                    x_extent_mm=[bounds.xmin,bounds.xmax],
                    y_extent_mm=[bounds.ymin,bounds.ymax],
                    hook_normal=list(hface.normalAt().toTuple()),
                    receiver_normal=list(rface.normalAt().toTuple())))
    return witnesses


def retraction_threshold(d, upper, sign, *, rigid):
    """First clear hook at a specified pose; no constitutive deformation claim.

    The rigid option translates the exact undeformed hook radially. The leaf
    option uses the historical prescribed tip-load shape, which shears/slopes
    its shoulder slightly. Neither is a structural or force solution. The radial
    search assumes monotone loss of obstruction for this simple pocket. A zero
    result means no obstruction at this pose (including seated axial play),
    not proof that the catch is disengaged along a withdrawal path.
    """
    original = hook_shape(d, sign, 0)
    def volume(delta):
        # at_end(sign=1) places the tooth at negative world X.
        tooth = (original.translate((sign*delta, 0, 0)) if rigid else
                 hook_shape(d, sign, delta))
        return overlap(tooth, upper)
    initial = volume(0)
    if initial < VOLUME_EPS:
        return dict(initial_overlap_mm3=initial, terminal_retraction_mm=0.,
                    hook_shoulder_retraction_mm=0.)
    lo, hi = 0., 3.5
    if volume(hi) >= VOLUME_EPS:
        return dict(initial_overlap_mm3=initial, terminal_retraction_mm=None,
                    reason='No clear pose within 3.5 mm search bracket')
    while hi-lo > RETRACTION_RESOLUTION:
        mid = (hi+lo)/2
        if volume(mid) < VOLUME_EPS:
            hi = mid
        else:
            lo = mid
    return dict(initial_overlap_mm3=initial, terminal_retraction_mm=hi,
                hook_shoulder_retraction_mm=(hi if rigid else
                    leaf_offset(d, d.hook_bottom, hi)),
                terminal_threshold_bracket_mm=[lo,hi])


def face_catalog(d, upper):
    """Actual receiver surfaces near one hook, including diagonal flanks."""
    records = []
    for face in upper.Faces():
        c = face.Center()
        if c.x < -d.width*.4 and abs(c.y-d.catch_y)<9 and d.hook_bottom-1<c.z<d.hook_bottom+12:
            records.append(dict(type=face.geomType(),area_mm2=face.Area(),
                center_mm=list(c.toTuple()),normal_at_center=list(face.normalAt().toTuple())))
    return records


def investigate():
    d = D
    upper = cap(d).val()
    fixed = body_fixed(d).val()
    poses = []
    # Close-to-seat and pickup contact; offsets bound nominal guide play. Larger
    # offsets are deliberate sensitivity controls, not measured print errors.
    for lift in (0., .1, .15, .2, .25, .4, .6, .9, 1.2, 2., 4., 4.6):
        poses.append(dict(name=f'axial_{lift}',lift=lift))
    for axis in ('dx','dy'):
        for shift in (-.5,-.25,.25,.5):
            poses.append(dict(name=f'{axis}_{shift}',lift=.9,**{axis:shift}))
            poses.append(dict(name=f'seated_{axis}_{shift}',lift=0.,**{axis:shift}))
    for axis in ('angle_x','angle_y'):
        for angle in (.25,.5,1.,2.):
            poses.append(dict(name=f'{axis}_{angle}',lift=.9,**{axis:angle}))
    samples = []
    for requested in poses:
        values = dict(lift=0.,dx=0.,dy=0.,angle_x=0.,angle_y=0.)
        values.update({k:v for k,v in requested.items() if k!='name'})
        posed = move_cap(upper,d,**values)
        records = dict(name=requested['name'],pose=values,
            fixed_body_overlap_mm3=overlap(fixed,posed),catches={})
        for sign in (-1,1):
            records['catches'][str(sign)] = retraction_threshold(d,posed,sign,rigid=True)
        samples.append(records)
    prescribed = []
    for dx in (-.25,0.,.25):
        posed = upper.translate((dx,0,.9))
        prescribed.append(dict(dx_mm=dx,catches={str(s):retraction_threshold(d,posed,s,rigid=False) for s in (-1,1)}))
    controls = []
    for label,delta in [('engaged',0.),('partly_retracted',.5),('nearly_released',1.5),('deliberately_released',d.release)]:
        posed = upper.translate((0,0,.9))
        controls.append(dict(name=label,prescribed_terminal_retraction_mm=delta,
            catch_overlap_mm3={str(s):overlap(hook_shape(d,s,delta),posed) for s in (-1,1)}))
    return dict(schema='dental-m1-exact-capture-v1',
        source_sha256=hashlib.sha256(Path(__file__).with_name('m1_design.py').read_bytes()).hexdigest(),
        dimensions_mm=asdict(d),numerics=dict(volume_epsilon_mm3=VOLUME_EPS,
            retraction_resolution_mm=RETRACTION_RESOLUTION),
        scope='Authoritative nominal CAD, rigid pose and prescribed hook-shape screens. No holding-force, stiffness, elasticity or physical acceptance claim.',
        dimensional_sensitivity='dx/dy +/-0.25 nominal per-side guide play and +/-0.5 enlarged clearance control. Local radial retraction also represents net tooth undersize or receiver outward motion; these are independent offsets, not measured manufacturing distributions.',
        seated_flat_lands={str(s):seated_land(d,upper,s) for s in (-1,1)},
        flat_land_radial_loss_control=[dict(radial_retraction_mm=r,
            catches={str(s):seated_land(d,upper,s,r) for s in (-1,1)})
            for r in (0.,.5,1.,1.5,1.75)],
        flat_land_transverse_sensitivity=[dict(dx_mm=x,dy_mm=y,
            catches={str(s):seated_land(d,upper.translate((x,y,0)),s) for s in (-1,1)})
            for x,y in ((-.25,0),(.25,0),(0,-.25),(0,.25),(0,-.5),(0,.5))],
        receiver_face_catalog_one_side=face_catalog(d,upper),
        rigid_hook_pose_samples=samples,prescribed_leaf_thresholds=prescribed,
        hook_controls=controls,
        removed_hook_control_fixed_body_overlap_mm3=overlap(fixed,upper.translate((0,0,.9))),
        limitations=['Finite pose samples do not establish a continuous opening path.',
            'Rigid guide interference prevents treating a pose as an admissible escape route; deformation requires structural analysis.',
            'No print-error calibration. Hook/receiver dimensional errors can combine with elastic motion.',
            'Fixed body includes production liner and sleeve. Full-size nominal cap is retained, but rigid geometric queries cannot distinguish its compliance from a crop.'])


def main():
    if len(sys.argv)!=2:
        raise SystemExit('Usage: retention_geometry.py OUTPUT_JSON')
    output = Path(sys.argv[1])
    result = investigate()
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(output=str(output),flat_lands=result['seated_flat_lands'],
                         samples=len(result['rigid_hook_pose_samples']))))


if __name__=='__main__':
    main()
