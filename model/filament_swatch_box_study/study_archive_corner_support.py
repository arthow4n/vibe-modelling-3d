"""Targeted sparse-card corner-guide screen; rough proposals, not qualification.

Sample thin-axis leaning with yaw and low-wall-compatible bottom positions.
Use actual source-card CAD to challenge optimistic corner-only assumptions.
"""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
import cadquery as cq
import archive_corner_proposals as p
import swatch_reference as ref

ROOT = Path(__file__).parent
EPS = 1e-6


def lower_footprint(yaw,lean,sign):
    """Project a chamfered-outline envelope clipped at the J-height wall.

    A full rectangle at Z0 invents material in the real bottom chamfers and
    falsely excludes diagonal poses. Holes/top rounding are conservatively
    filled here; actual CAD resolves each retained candidate afterwards.
    """
    width,height,thick = ref.HEIGHT,ref.WIDTH,ref.THICKNESS
    c = ref.swatch_dimension('left_chamfer_size')
    outline = [(-width/2+c,0),(width/2-c,0),(width/2,c),
               (width/2,height),(-width/2,height),(-width/2,c)]
    vertices = np.array([(x,y,z) for y in (-thick/2,thick/2) for x,z in outline])
    psi,t = math.radians(yaw),math.radians(lean)
    u,n = np.array([math.cos(psi),math.sin(psi)]),np.array([-math.sin(psi),math.cos(psi)])
    xy = vertices[:,0,None]*u+(vertices[:,1]*math.cos(t)+sign*vertices[:,2]*math.sin(t))[:,None]*n
    z = vertices[:,2]*math.cos(t)-sign*vertices[:,1]*math.sin(t)+thick/2*math.sin(t)
    world = np.column_stack((xy,z))
    ceiling = p.LOW_TOP-p.FLOOR
    clipped = [v for v in world if v[2]<=ceiling]
    edges = [(i,6+i) for i in range(6)]+[(b+i,b+(i+1)%6) for b in (0,6) for i in range(6)]
    for i,j in edges:
        a,b = world[i],world[j]
        if (a[2]-ceiling)*(b[2]-ceiling)<0:
            clipped.append(a+(b-a)*(ceiling-a[2])/(b[2]-a[2]))
    points = np.array(clipped)
    return points[:,:2].min(axis=0),points[:,:2].max(axis=0)


def cases(card):
    cg = card.Center()
    cases = []
    for yaw in (-22.,-20.,-18.,-16.,-14.,-12.,-10.,-8.,-5.,-2.,0.,
                2.,5.,8.,10.,12.,14.,16.,18.,20.,22.):
        psi = math.radians(yaw)
        u,n = (math.cos(psi),math.sin(psi)),(-math.sin(psi),math.cos(psi))
        for sign in (-1,1):
            for lean in (10.,17.,25.,28.,30.,31.,32.,33.,34.,35.,36.,38.,40.):
                t = math.radians(lean)
                lift = ref.THICKNESS/2*math.sin(t)
                lo,hi = lower_footprint(yaw,lean,sign)
                limits = [(-dim/2-lo[i],dim/2-hi[i])
                          for i,dim in enumerate((p.r1.POCKET_WIDTH,p.r1.POCKET_DEPTH))]
                if any(lo>hi for lo,hi in limits):
                    continue
                y = limits[1][1] if sign>0 else limits[1][0]
                for fraction in (0.,.25,.5,.75,1.):
                    x = limits[0][0]+fraction*(limits[0][1]-limits[0][0])
                    cy = y+cg.x*u[1]+cg.y*math.cos(t)*n[1]+sign*(cg.z-p.FLOOR)*math.sin(t)*n[1]
                    over = sign*cy-p.r1.POCKET_DEPTH/2
                    if over>.03:
                        cases.append(dict(yaw_deg=yaw,lean_deg=lean,direction=sign,
                            x_placement_fraction=fraction,
                            shift_xy_mm=[x,y],floor_lift_mm=lift,
                            cg_beyond_low_wall_mm=over))
    # Near-onset cases are useful escape challenges; avoid thousands of booleans.
    cases.sort(key=lambda c:(abs(c['cg_beyond_low_wall_mm']-.3),
                             abs(abs(c['yaw_deg'])-18),c['lean_deg']))
    # Keep both extreme x placements for each yaw/direction, not just the globally
    # first sorted poses (which could accidentally all have zero yaw).
    selected = {}
    for c in cases:
        if c['x_placement_fraction'] in (0.,.5,1.):
            selected.setdefault((c['yaw_deg'],c['direction'],c['x_placement_fraction']),c)
    result = list(selected.values())[:64]
    assert any(c['yaw_deg']!=0 for c in result), 'Yaw challenges were accidentally excluded'
    return result


def pose(card,c):
    psi = math.radians(c['yaw_deg'])
    u = (math.cos(psi),math.sin(psi),0)
    pivot = (0,0,p.FLOOR)
    return (card.rotate(pivot,(0,0,p.FLOOR+1),c['yaw_deg'])
        .rotate(pivot,(u[0],u[1],p.FLOOR),-c['direction']*c['lean_deg'])
        .translate((*c['shift_xy_mm'],c['floor_lift_mm'])))


def run(bodies=None,card=None):
    """Use supplied geometry so the final multi-variant check builds only once."""
    if card is None:
        card = ref.card(-ref.THICKNESS/2).val()
    challenge = cases(card)
    assert challenge, 'No feasible corner challenge found'
    if bodies is None:
        bodies = {name:p.base(name).val() for name in p.PROPOSALS}
    floor = p.r1.g.block(-p.r1.POCKET_WIDTH/2,p.r1.POCKET_WIDTH/2,
        -p.r1.POCKET_DEPTH/2,p.r1.POCKET_DEPTH/2,0,p.FLOOR).val()
    low_baseline = p.r1.g.rounded_block(p.r1.g.OUTER_WIDTH,p.r1.g.BODY_DEPTH,
        p.LOW_TOP,0,5.).cut(p.pocket()).val()
    raised_zone = p.r1.g.block(-40,40,-30,30,p.LOW_TOP+.01,p.TOP+1).val()
    samples = []
    for c in challenge:
        q = pose(card,c)
        assert q.distance(floor)<1e-7, 'Challenge is not floor-supported'
        overlaps = {name:q.intersect(body) for name,body in bodies.items()}
        row = dict(**c,low_only_intersection_mm3=q.intersect(low_baseline).Volume(),
            intersection_mm3={name:overlap.Volume() for name,overlap in overlaps.items()},
            raised_retaining_intersection_mm3={name:overlap.intersect(raised_zone).Volume()
                                              for name,overlap in overlaps.items()})
        samples.append(row)

    low_clear = [i for i,c in enumerate(samples) if c['low_only_intersection_mm3']<EPS]
    assert low_clear, 'No challenge establishes what the tall guides add'

    free = {name:[i for i,c in enumerate(samples) if c['intersection_mm3'][name]<EPS]
            for name in bodies}
    rolls = {}
    for name,indices in free.items():
        if not indices:
            continue
        c = samples[indices[0]]
        q = pose(card,c)
        sign = c['direction']
        hinge = (0,sign*p.r1.POCKET_DEPTH/2,p.LOW_TOP)
        sequence = []
        for angle in (0.,.2,1.,2.,4.,6.,10.,15.,25.,40.,60.,80.,90.):
            moved = q.rotate(hinge,(1,hinge[1],hinge[2]),-sign*angle)
            overlap = moved.intersect(bodies[name]).Volume()
            sequence.append(dict(additional_roll_deg=angle,intersection_mm3=overlap,
                cg_z_mm=moved.Center().z))
            if overlap>EPS:
                break
        rolls[name] = dict(challenge_index=indices[0],samples=sequence,
            note='Sampled outward rotation about the low rim; not a continuous escape proof.')

    # Exact G rigid fit, with only the known flexible pad contacts excluded.
    hood = p.r1.g.cap().val()
    pads = [p.r1.g.pad(y,s).val() for y in p.r1.g.detent_centres(p.r1.g.COUNT) for s in (-1,1)]
    fit = {}
    for name,body in bodies.items():
        assert body.isValid() and len(body.Solids())==1, 'Disconnected corner guide'
        rigid = body
        for pad in pads:
            rigid = rigid.cut(pad)
        for lift in (0.,2.,20.,84.):
            overlap = hood.translate((0,0,lift)).intersect(rigid)
            assert overlap.Volume()<EPS, 'Rough proposal clashes with exact G rigid structure'
        upright = card.translate((0,(-p.r1.STACK_DEPTH+ref.THICKNESS)/2,0))
        for n in range(p.r1.COUNT):
            assert upright.translate((0,n*ref.THICKNESS,0)).intersect(body).Volume()<EPS
        fit[name] = dict(valid_connected=True,exact_G_rigid_seating_and_sampled_lift_clear=True,
            fifteen_nominal_cards_seat_clear=True,
            key='Complete joined/release checks are in check_archive_r2.py')

    report = dict(low_wall_above_floor_mm=p.LOW_TOP-p.FLOOR,
        low_wall_top_z_mm=p.LOW_TOP,tall_height_above_floor_mm=p.TALL_HEIGHT,
        proposals=p.PROPOSALS,cases=samples,low_only_clear_challenge_indices=low_clear,
        unblocked_challenge_indices=free,
        outward_rolls=rolls,rough_fit=fit,
        scope='Selected diverse thin-axis+yaw gravity-over-low-wall challenges. '
              'Blocked sampled poses are not global retention qualification. '
              'Unblocked CG-beyond-low-wall poses challenge the restoring-contact claim; '
              'outward roll sequences show only their sampled path. '
              'Other rotations, dynamic disturbance and print compliance remain unqualified. '
              'The user accepted completion of this form round; physical comfort is untested.',
        source_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
            for name in ('study_archive_corner_support.py','archive_corner_proposals.py',
                         'swatch_reference.py','archive_r1_base_15.py','study.py',
                         '../filament_archive_swatch/filament_archive_swatch.scad')})
    path = ROOT/'notes/archive_corner_support.json'
    path.write_text(json.dumps(report,indent=2)+'\n')
    return report


def main():
    report = run()
    print(json.dumps(dict(report=str(ROOT/'notes/archive_corner_support.json'),samples=len(report['cases']),
        low_only_clear_cases=len(report['low_only_clear_challenge_indices']),
        sampled_yaws_deg=sorted(set(c['yaw_deg'] for c in report['cases'])),
        unblocked_counts={name:len(v) for name,v in report['unblocked_challenge_indices'].items()},
        outward_rolls=report['outward_rolls'],rough_fit=report['rough_fit'])))


if __name__=='__main__':
    main()
