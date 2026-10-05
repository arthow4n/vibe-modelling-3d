"""Q1 functional contact checks, including actual cards, anchors and old-key joins.

Expected result: rigid travel stays clear, only the intended TPU diaphragms
engage during opening/closing, and the insert has actual geometric capture.
This is not a TPU force, noise, durability or elastic installation solve.
"""
import hashlib
import json
import math
from pathlib import Path
import cadquery as cq
import quiet_q1 as q
import archive_corner_proposals as old_archive
import cap_j4_base_5 as old_display
from check_corner_seat import card_envelope

ROOT=Path(__file__).parent
EPS=1e-6


def clear(a,b,reason):
    overlap=a.intersect(b).Volume()
    assert overlap<EPS,f'{reason}: {overlap:.8g} mm3'


def main(q=q, output_name='quiet_q1_checks.json'):
    base,jacket,hood=q.base().val(),q.jacket().val(),q.hood().val()
    guides=q.jacket(include_beads=False).val()
    clear(base,jacket,'Jacket does not fit the actual rigid base')
    clear(base,hood,'Closed rigid hood touches base')
    clear(jacket,hood,'Closed TPU beads do not fit their pockets')
    print('Nominal assembled contact checks passed',flush=True)
    cards=[card.val() for card in q.cards()]
    floor=q.block(-q.archive.r1.POCKET_WIDTH/2,q.archive.r1.POCKET_WIDTH/2,
                  -q.archive.r1.POCKET_DEPTH/2,q.archive.r1.POCKET_DEPTH/2,
                  0,q.archive.FLOOR).val()
    for card in cards:
        for item,label in ((base,'base'),(jacket,'jacket'),(hood,'hood')):
            clear(card,item,f'Actual card touches {label}')
        assert card.distance(floor)<1e-7,'Card floats above its intended floor'
        assert card.translate((0,0,-.02)).intersect(floor).Volume()>1e-4,'No card floor support'
    envelope=card_envelope(q.ref.HEIGHT,30.,4).translate((0,15.,0)).val()
    for sx,sy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
        for step in range(9):
            f=step/8
            pose=envelope.translate((sx*(1-f),sy*(1-f),q.CORE_TOP-q.archive.ENTRY_HEIGHT*f+.01))
            clear(pose,base,'Accepted bundle entry altered')
            clear(pose,jacket,'TPU top cuff obstructs bundle entry')
    for card in cards[::7]:
        for lift in (0,2,10,40,82):
            moved=card.translate((0,0,lift))
            clear(moved,base,'Card extraction obstructed by revised base')
            clear(moved,jacket,'Card extraction obstructed by TPU')
    print('Card support, entry and extraction checks passed',flush=True)
    # Sample the entire hand-guided vertical path; do not call it continuous proof.
    bead_masks=[]
    for y in q.BEAD_Y:
        for side in (-1,1):
            bead_masks.append(q.g.mirrored(q.block(q.JACKET_X/2-.02,q.BEAD_TIP_X+.05,
                y-q.BEAD_WIDTH/2-.05,y+q.BEAD_WIDTH/2+.05,
                q.BEAD_BOTTOM-.05,q.BEAD_TOP+.05),side).val())
    bead_envelope=cq.Compound.makeCompound(bead_masks)
    peak_overlap=0.
    contact_lifts=[]
    fine_end=max(12,math.ceil(q.BEAD_TOP-q.SEAT_TOP+2))
    lifts=sorted(set([i*.25 for i in range(fine_end*4+1)]+[16.,24.,36.,48.,64.,84.]))
    for lift in lifts:
        moved=hood.translate((0,0,lift))
        clear(moved,base,'Rigid hood/base collision on vertical path')
        clear(moved,guides,'Hood rubs non-retention TPU during vertical travel')
        contact=moved.intersect(jacket)
        if contact.Volume()>EPS:
            assert contact.cut(bead_envelope).Volume()<EPS,'Contact outside intended soft beads'
            peak_overlap=max(peak_overlap,contact.Volume())
            contact_lifts.append(lift)
    assert peak_overlap>EPS,'No geometric retention source; hood is only loose clearance'
    for sx,sy in ((-.2,0),(.2,0),(0,-.2),(0,.2)):
        for lift in (0,4,10,20,40,84):
            clear(hood.translate((sx,sy,lift)),base,'Small hand-guided offset hits PETG')
    for y in q.BEAD_Y:
        for side in (-1,1):
            patch=q.g.mirrored(q.block(q.CORE_X/2-.1,q.BEAD_TIP_X+.1,
                y-q.BEAD_WIDTH/2+.2,y+q.BEAD_WIDTH/2-.2,
                q.BEAD_BOTTOM-.1,q.BEAD_TOP+.1),side).val()
            diaphragm=jacket.intersect(patch).translate((-side*.5,0,0))
            clear(diaphragm,base,'Insufficient backing space for TPU diaphragm travel')
    assert jacket.translate((0,0,1.)).intersect(base).Volume()>EPS,'Insert has no upward geometric capture'
    assert jacket.rotate((0,0,0),(0,0,1),3.).intersect(base).Volume()>EPS,'Insert has no twist location'
    # A pre-expanded rigid envelope answers geometric access, not elastic feasibility.
    expansion=1.035
    if hasattr(q,'installation_envelopes'):
        install=q.installation_envelopes(jacket,expansion)
    else:
        install=[('uniformly expanded sleeve',jacket.scale(expansion).translate((0,0,-q.FOOT_TOP*(expansion-1))))]
    for label,envelope in install:
        for lift in (0,1,5,10,20,40,45):
            clear(envelope.translate((0,0,lift)),base,f'{label}: installation access blocked')
    print('Hood path, diaphragm room and insert capture checks passed',flush=True)
    # Soft landing has real area under the hood; it is not a bounding-box claim.
    seat=q.block(-40,40,-30,30,q.FOOT_TOP,q.SEAT_TOP).val()
    assert hood.translate((0,0,-.02)).intersect(jacket).intersect(seat).Volume()>1e-4,'No TPU landing under rim'
    for side in (-1,1):
        clear(q.finger(side).val(),hood,'Closed hood blocks recessed opening grip')
        clear(q.finger(side).val(),jacket,'TPU skirt blocks recessed opening grip')
    key=q.keys.seated_key(3).val()
    keyspace=q.keys.seated_key(3,projection=q.h.KEY_FIT_GAP).val()
    keycore=(q.keys.key_outline().offset2D(q.keys.CORE_GROWTH)
             .extrude(q.keys.KEY_HEIGHT).translate((0,0,q.h.KEY_FLOOR_Z)).val())
    neighbours={'new':(base,q.FOOT_Y,hood),'archive_A':(old_archive.base('continuous').val(),q.g.FOOT_DEPTH,q.g.cap().val()),
                'display_J4':(old_display.base().val(),q.g.FOOT_DEPTH,q.g.cap().val())}
    for name,(other,depth,otherhood) in neighbours.items():
        for end in (-1,1):
            # Butted feet, preserving I3's accepted KEY_SEAM_GAP=0 setup.
            newshift=-end*q.FOOT_Y/2
            oldshift=end*depth/2
            pair=cq.Compound.makeCompound([base.translate((0,newshift,0)),other.translate((0,oldshift,0))])
            covers=[hood.translate((0,newshift,0)),otherhood.translate((0,oldshift,0))]
            sleeve=jacket.translate((0,newshift,0))
            clear(keycore,pair,f'{name}: joining key core hits a rigid stop')
            for lift in (0,.2,1,2,4,8,20,45):
                clear(keyspace.translate((0,0,lift)),pair,f'{name}: rigid key entry blocked')
                clear(keyspace.translate((0,0,lift)),sleeve,f'{name}: TPU blocks key entry')
            for cover in covers:
                clear(key,cover,f'{name}: key clashes with closed hood')
                assert key.translate((0,0,1.1)).intersect(cover).Volume()>EPS,f'{name}: hood does not keep key captive'
            clear(covers[0],covers[1],f'{name}: adjacent closed hoods overlap')
            for lift in (0,4,20,84):
                clear(covers[0].translate((0,0,lift)),other.translate((0,oldshift,0)),f'{name}: neighbouring base blocks opening')
                clear(covers[0].translate((0,0,lift)),covers[1],f'{name}: neighbouring hood blocks opening')
            # Both flanks of both heads must meet capture material, not merely clear.
            for xs in (-1,1):
                for ys in (-1,1):
                    xl,xh=sorted((xs*3,xs*9));yl,yh=sorted((ys*.01,ys*4))
                    patch=q.block(xl,xh,yl,yh,q.h.KEY_FLOOR_Z,q.h.KEY_TOP_Z+.1).val()
                    assert key.intersect(pair).intersect(patch).Volume()>1e-5,f'{name}: missing head-flank capture'
    report=dict(ok=True,capacity=15,material_assumption='User reports TPU 95A; brand and printed behavior unknown',
        accepted_card_pocket_and_entry_preserved=True,actual_cards_on_floor=True,
        nominal_three_part_clearance=True,hood_vertical_sample_lifts_mm=lifts,
        rigid_base_clear_at_sampled_offsets_mm=.2,only_soft_beads_contact_during_sampled_centred_travel=True,
        bead_contact_lifts_mm=contact_lifts,peak_rigid_bead_overlap_mm3=peak_overlap,
        diaphragm_inward_room_screen_mm=.5,insert_lift_capture_at_mm=1.,insert_twist_block_at_deg=3.,
        installation_envelope_uniform_scale=expansion,soft_seat_witness=True,recessed_grip_access=True,
        installation_access_envelopes=[label for label,_ in install],
        existing_I3_key_and_joined_opening_both_ends=list(neighbours),
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(q.__file__),Path(__file__))},
        limits='Nominal CAD and sampled hand-guided paths. Pre-expanded/independent rigid envelopes are access screens, '
            'not a deformation/contact solve or strain qualification. No printed noise, force, friction, '
            'creep, durability or suspended-load rating. Existing joining-key force is not recalibrated.')
    output=ROOT/'notes'/output_name
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(ok=True,report=str(output),bead_contact_lifts_mm=contact_lifts,
                          joining=list(neighbours))),flush=True)


if __name__=='__main__':
    main()
