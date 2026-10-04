"""R2 functional checks on all four actual bases, real cards, G and I3.

One build per variant. Rigid contact/clearance evidence only; no friction,
impact, PETG stiffness, long-term retention or comfort qualification.
"""
import hashlib
import json
import math
from pathlib import Path
import cadquery as cq
import archive_corner_proposals as p
import cap_j4_base_5 as j4
import cap_i_grip_keys as keys
import swatch_reference as ref
import study_archive_corner_support as support
from check_corner_seat import card_envelope

ROOT = Path(__file__).parent
EPS = 1e-6
a = p.r1


def preserve_interfaces(body,old):
    masks = [a.grips.changed_region().val()]
    for y in a.g.detent_centres(a.g.COUNT):
        mask = a.g.block(a.g.OUTER_WIDTH/2-a.g.STEM_THICKNESS,
            a.g.OUTER_WIDTH/2+1.5,y-a.g.STEM_WIDTH/2,y+a.g.STEM_WIDTH/2,
            a.g.ROOT_Z+.01,a.g.TIP_TOP_Z+.1).val()
        masks.extend((mask,mask.mirror('YZ')))
    for end in (-1,1):
        lo,hi = sorted((end*18.75,end*(a.g.FOOT_DEPTH/2+.1)))
        masks.append(a.g.block(-9,9,lo,hi,keys.h.KEY_FLOOR_Z-.1,a.g.SEAM_Z).val())
    for mask in masks:
        x,y = body.intersect(mask),old.intersect(mask)
        assert x.cut(y).Volume()<EPS and y.cut(x).Volume()<EPS, \
            'Accepted grip, catch or lower key capture/stop changed'


def joining(body,old,hood,key,space,core):
    centres = keys.module_centres()
    for end in (-1,1):
        parts = [body,old] if end==1 else [old,body]
        joined = cq.Compound.makeCompound([part.translate((0,y,0))
            for part,y in zip(parts,centres)])
        assert core.intersect(joined).Volume()<EPS, 'Key core hits rigid stop'
        for lift in (0,.2,1,2,4,8,20,48):
            assert space.translate((0,0,lift)).intersect(joined).Volume()<EPS, \
                'Archive wall roofs over the upward key path'
        for xs in (-1,1):
            for ys in (-1,1):
                lo,hi = sorted((xs*3,xs*9))
                yl,yh = sorted((ys*.15,ys*4))
                patch = a.g.block(lo,hi,yl,yh,keys.h.KEY_FLOOR_Z,keys.h.KEY_TOP_Z+.1).val()
                assert key.intersect(joined).intersect(patch).Volume()>1e-5, \
                    'Missing key flank capture'
        for y in centres:
            cover = hood.translate((0,y,0))
            assert key.intersect(cover).Volume()<EPS
            assert key.translate((0,0,.4)).intersect(cover).Volume()>EPS, \
                'Closed G does not keep the joining key captive'


def cards_and_entry(body,cards,envelope,floor,hood):
    for card in cards:
        assert card.intersect(body).Volume()<EPS, 'Source card cannot seat upright'
        assert card.distance(floor)<1e-7, 'Card floats above floor'
        assert card.translate((0,0,-.02)).intersect(floor).Volume()>1e-4, \
            'No actual bottom material reaches the floor'
    for sx,sy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
        for step in range(9):
            f = step/8
            pose = envelope.translate((sx*(1-f),sy*(1-f),p.TOP-p.ENTRY_HEIGHT*f+.01))
            assert pose.intersect(body).Volume()<EPS, 'Offset bundle entry obstructed'
    for z in (p.TOP-p.ENTRY_HEIGHT,30,20,10,p.FLOOR):
        assert envelope.translate((0,0,z)).intersect(body).Volume()<EPS, \
            'Square stack descent obstructed'
    for n in (0,7,14):
        for lift in (0,.5,4,15,45,82):
            moved = cards[n].translate((0,0,lift))
            assert moved.intersect(body).Volume()<EPS, 'Individual extraction obstructed'
            for neighbour in (n-1,n+1):
                if 0<=neighbour<a.COUNT:
                    assert moved.intersect(cards[neighbour]).Volume()<EPS
    stack = cq.Compound.makeCompound(cards)
    assert hood.intersect(stack).Volume()<EPS, 'Exact G roof clashes with the cards'
    walls = body.intersect(a.g.block(-40,40,-30,30,p.FLOOR+.5,p.TOP+1).val())
    for axis in ('X','Y'):
        for angle in (-1,1):
            pivot = (0,0,p.FLOOR)
            end = (1,0,p.FLOOR) if axis=='X' else (0,1,p.FLOOR)
            lever = a.STACK_DEPTH/2 if axis=='X' else ref.HEIGHT/2-ref.swatch_dimension('left_chamfer_size')
            moved = stack.rotate(pivot,end,angle).translate((0,0,lever*abs(math.sin(math.radians(angle)))))
            assert moved.intersect(walls).Volume()>1e-5, 'Full stack lacks upright guidance'


def first_contacts(body,card):
    """Real-card contact before centroid crosses the pocket in normal lean.

    Low-wall and raised-guide intersections exclude the floor. The separate
    yaw study challenges diagonal bypass; this is not an escape-path proof.
    """
    walls = body.intersect(a.g.block(-40,40,-30,30,p.FLOOR+.5,p.TOP+1).val())
    floor = a.g.block(-a.POCKET_WIDTH/2,a.POCKET_WIDTH/2,
        -a.POCKET_DEPTH/2,a.POCKET_DEPTH/2,0,p.FLOOR).val()
    records = []
    for y in (-a.POCKET_DEPTH/2+ref.THICKNESS/2,0,a.POCKET_DEPTH/2-ref.THICKNESS/2):
        for axis in ('X','Y'):
            for sign in (-1,1):
                pivot = (0,y,p.FLOOR)
                end = (1,y,p.FLOOR) if axis=='X' else (0,y+1,p.FLOOR)
                # Up to 45 degrees, sideways floor support is at the flat
                # bottom's end (21 mm), not the absent chamfer corner (25 mm).
                lever = ref.THICKNESS/2 if axis=='X' else ref.HEIGHT/2-ref.swatch_dimension('left_chamfer_size')
                def pose(angle):
                    moved = card.translate((0,y,0)).rotate(pivot,end,sign*angle).translate(
                        (0,0,lever*math.sin(math.radians(angle))))
                    assert moved.distance(floor)<1e-7, 'Lean fixture floats above its actual floor support'
                    assert moved.intersect(floor).Volume()<EPS, 'Lean fixture penetrates the floor'
                    return moved
                lo,hi = 0.,45.
                assert pose(hi).intersect(walls).Volume()>1e-5
                for _ in range(9):
                    mid = (lo+hi)/2
                    if pose(mid).intersect(walls).Volume()>1e-5:
                        hi = mid
                    else:
                        lo = mid
                cg = pose(hi).Center()
                assert abs(cg.x)<a.POCKET_WIDTH/2 and abs(cg.y)<a.POCKET_DEPTH/2, \
                    'CG passes the pocket before retaining contact'
                records.append(dict(y_mm=y,axis=axis,direction=sign,
                    first_contact_bracket_deg=[lo,hi],centroid_xy_mm=[cg.x,cg.y]))
    return records


def main():
    bodies = {name:p.base(name).val() for name in p.PROPOSALS}
    old,hood = j4.base().val(),a.g.cap().val()
    card = ref.card(-ref.THICKNESS/2).val()
    cards = [card.translate((0,(n-(a.COUNT-1)/2)*ref.THICKNESS,0)) for n in range(a.COUNT)]
    # This helper's width argument is 50; its upright height is 80 from study.py.
    envelope = card_envelope(ref.HEIGHT,a.STACK_DEPTH,4).translate((0,a.STACK_DEPTH/2,0)).val()
    floor = a.g.block(-a.POCKET_WIDTH/2,a.POCKET_WIDTH/2,
        -a.POCKET_DEPTH/2,a.POCKET_DEPTH/2,0,p.FLOOR).val()
    key = keys.seated_key(3).val()
    space = keys.seated_key(3,projection=keys.h.KEY_FIT_GAP).val()
    core = keys.key_outline().offset2D(keys.CORE_GROWTH).extrude(keys.KEY_HEIGHT).translate(
        (0,0,keys.h.KEY_FLOOR_Z)).val()
    report = {}
    for name,body in bodies.items():
        assert body.isValid() and len(body.Solids())==1, 'Disconnected retaining guide'
        preserve_interfaces(body,old)
        joining(body,old,hood,key,space,core)
        cards_and_entry(body,cards,envelope,floor,hood)
        report[name] = dict(valid_connected=True,accepted_grips_catches_and_both_lower_ports_preserved=True,
            I3_join_to_J4_both_orientations=True,closed_G_keeps_key_captive=True,
            full_stack_seats_on_floor=True,eight_entry_directions_with_1mm_offset=True,
            first_middle_last_individual_extraction=True,full_stack_one_degree_lean_blocked=True,
            sparse_normal_lean_contacts=first_contacts(body,card))
        print(json.dumps(dict(completed_variant=name)),flush=True)
    support_report = support.run(bodies,card)
    assert all(not indices for indices in support_report['unblocked_challenge_indices'].values()), \
        'A raised guide permits a selected low-wall escape challenge'
    record = dict(ok=True,variants=report,capacity=a.COUNT,
        pocket_mm=[a.POCKET_WIDTH,a.POCKET_DEPTH],tall_height_above_floor_mm=p.TALL_HEIGHT,
        low_wall_above_floor_mm=p.LOW_TOP-p.FLOOR,entry_height_mm=p.ENTRY_HEIGHT,
        sparse_yaw_challenges=len(support_report['cases']),
        low_only_clear_challenges=len(support_report['low_only_clear_challenge_indices']),
        exact_G_rigid_fit='See archive_corner_support.json; only known flexible pad contacts excluded',
        source_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in (
            'check_archive_r2.py','archive_corner_proposals.py','study_archive_corner_support.py',
            'check_corner_seat.py','card_base_corner_seat_5.py','swatch_reference.py','study.py',
            'archive_r1_base_15.py','cap_j4_base_5.py','cap_i_grip_keys.py',
            'cap_g_module_5.py','cap_h_module_5.py','cap_e_thin_5.py','recessed_grips.py',
            '../filament_archive_swatch/filament_archive_swatch.scad')},
        limits='Nominal rigid cards, engraving omitted. Sampled hand-guided entry and vertical extraction. '
            'Gravity/contact screens do not prove all dynamic escape paths. '
            'Printed fit, guide stiffness, comfort, friction and durability are untested. '
            'The unchanged I3 preload is inherited, not a newly calibrated force result.')
    path = ROOT/'notes/archive_r2_checks.json'
    path.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(ok=True,report=str(path),variants=list(report),
        yaw_challenges=record['sparse_yaw_challenges'],low_only_clear_challenges=record['low_only_clear_challenges'])))


if __name__=='__main__':
    main()
