"""Q1 functional contact checks, including actual cards, anchors and old-key joins.

Expected result: rigid travel stays clear, only the intended TPU diaphragms
engage during opening/closing, and the insert has actual geometric capture.
This is not a TPU force, noise, durability or elastic installation solve.
"""
import hashlib
import json
import math
import sys
from pathlib import Path
import cadquery as cq
import quiet_q1 as q
from assembly_geometry import PairRequirement, check_pair, sample_motion
from quiet_assembly import QuietAssembly, fixture
from check_corner_seat import card_envelope
from product_verification import CalculationInconclusive

ROOT=Path(__file__).parent
EPS=1e-6


def valid_boolean(operation, intent):
    try:
        result=operation()
    except (ValueError, RuntimeError) as exc:
        raise CalculationInconclusive(f'{intent}: {exc}') from exc
    if not result.isValid():
        raise CalculationInconclusive(f'{intent}: invalid Boolean result')
    return result


def pair_helpers(q, evidence):
    def pair(a,b,reason,first,second,**criteria):
        answer=check_pair(a,b,PairRequirement(reason,**criteria),first=first,
                          second=second,configuration=q.__name__).require_passed()
        evidence.append(answer.to_dict())
        return answer

    def clear(a,b,reason,first,second):
        return pair(a,b,reason,first,second,max_overlap_mm3=EPS)

    return pair, clear


def closed_checks(model, evidence):
    q=model.model
    closed=model.operating(include_cards=False)
    base,jacket,hood=(closed.shape(name) for name in ('base','insert','hood'))
    pair,clear=pair_helpers(q,evidence)
    for first,second,intent in (('base','insert','Insert fits the actual rigid base'),
            ('hood','base','Closed rigid hood clears the base'),
            ('hood','insert','Closed TPU beads fit the hood pockets')):
        evidence.append(closed.check(first,second,PairRequirement(intent,
            max_overlap_mm3=EPS)).require_passed().to_dict())
    print('Nominal assembled contact checks passed',flush=True,file=sys.stderr)
    return {}


def require_card_fixture(model):
    if len(model.cards)<15:
        raise CalculationInconclusive('Required 15-card collection is under-represented; partial fixture cannot qualify storage')


def card_checks(model, evidence):
    require_card_fixture(model)
    q=model.model
    closed=model.operating(include_cards=True)
    base,jacket,hood=(closed.shape(name) for name in ('base','insert','hood'))
    pair,clear=pair_helpers(q,evidence)
    cards=[closed.shape(f'cards/card_{i:02d}') for i in range(len(model.cards))]
    floor_region=q.block(-q.archive.r1.POCKET_WIDTH/2,q.archive.r1.POCKET_WIDTH/2,
                  -q.archive.r1.POCKET_DEPTH/2,q.archive.r1.POCKET_DEPTH/2,
                  0,q.archive.FLOOR).val()
    floor=valid_boolean(lambda:base.intersect(floor_region),'Actual floor-support crop')
    assert floor.Solids(), 'Actual base has no floor-support region'
    for i,card in enumerate(cards):
        for item,label in ((base,'base'),(jacket,'jacket'),(hood,'hood')):
            clear(card,item,f'Actual card clears {label}',f'cards/card_{i:02d}',label)
        pair(card,floor,'Card seats on the actual floor without penetration',
             f'cards/card_{i:02d}','floor_reference',max_gap_mm=1e-7,max_overlap_mm3=EPS)
        pair(card.translate((0,0,-.02)),floor,'Attempted downward card motion meets its floor',
             f'cards/card_{i:02d}_down_0_02_mm','floor_reference',min_overlap_mm3=1e-4)
    envelope=card_envelope(q.ref.HEIGHT,30.,4).translate((0,15.,0)).val()
    for sx,sy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
        for step in range(9):
            f=step/8
            pose=envelope.translate((sx*(1-f),sy*(1-f),q.CORE_TOP-q.archive.ENTRY_HEIGHT*f+.01))
            clear(pose,base,'Accepted bundle entry clears rigid body',f'bundle_entry_{sx}_{sy}_{step}','base')
            clear(pose,jacket,'TPU top cuff clears bundle entry',f'bundle_entry_{sx}_{sy}_{step}','insert')
    for i in range(0,len(cards),7):
        card=cards[i]
        for lift in (0,2,10,40,82):
            moved=card.translate((0,0,lift))
            clear(moved,base,'Card extraction clears revised base',f'card_{i:02d}_lift_{lift}','base')
            clear(moved,jacket,'Card extraction clears TPU',f'card_{i:02d}_lift_{lift}','insert')
    print('Card support, entry and extraction checks passed',flush=True,file=sys.stderr)
    return {}


def hood_checks(model, evidence):
    q=model.model
    closed=model.operating(include_cards=True)
    base,jacket,hood=(closed.shape(name) for name in ('base','insert','hood'))
    guides=model.guides
    pair,clear=pair_helpers(q,evidence)
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
    free=PairRequirement('Sampled centred hood withdrawal clears rigid base',max_overlap_mm3=EPS)
    path=sample_motion(closed,'hood','base',free,samples=lifts,
        transform=lambda lift:cq.Location((0,0,lift)),parameter='hood_lift',units='mm').require_passed()
    evidence.append(path.to_dict())
    guide_fixture=fixture('hood_and_insert_without_retention_beads',{'hood':hood,'guides_reference':guides})
    path=sample_motion(guide_fixture,'hood','guides_reference',PairRequirement(
        'Hood clears non-retention TPU at sampled lifts; bead exclusion is explicit',max_overlap_mm3=EPS),
        samples=lifts,transform=lambda lift:cq.Location((0,0,lift)),parameter='hood_lift',units='mm').require_passed()
    evidence.append(path.to_dict())
    for lift in lifts:
        moved=hood.translate((0,0,lift))
        # Full insert contact is intentional; its location needs this local mask,
        # not a generic all-pairs prohibition or an elastic-motion claim.
        contact=valid_boolean(lambda:moved.intersect(jacket),f'Full insert contact at lift {lift}')
        if contact.Volume()>EPS:
            outside_beads=valid_boolean(lambda:contact.cut(bead_envelope),f'Bead exclusion at lift {lift}')
            assert outside_beads.Volume()<EPS,'Contact outside intended soft beads'
            peak_overlap=max(peak_overlap,contact.Volume())
            contact_lifts.append(lift)
    assert peak_overlap>EPS,'No geometric retention source; hood is only loose clearance'
    for sx,sy in ((-.2,0),(.2,0),(0,-.2),(0,.2)):
        offset=model.operating(offset_xy=(sx,sy))
        evidence.append(sample_motion(offset,'hood','base',PairRequirement(
            'Small hand-guided offset clears PETG at sampled lifts',max_overlap_mm3=EPS),
            samples=(0,4,10,20,40,84),transform=lambda lift:cq.Location((0,0,lift)),
            parameter='hood_lift',units='mm').require_passed().to_dict())
    for y in q.BEAD_Y:
        for side in (-1,1):
            patch=q.g.mirrored(q.block(q.CORE_X/2-.1,q.BEAD_TIP_X+.1,
                y-q.BEAD_WIDTH/2+.2,y+q.BEAD_WIDTH/2-.2,
                q.BEAD_BOTTOM-.1,q.BEAD_TOP+.1),side).val()
            diaphragm=jacket.intersect(patch).translate((-side*.5,0,0))
            clear(diaphragm,base,'Prescribed inward diaphragm subset has backing space',
                  f'diaphragm_reference_{y}_{side}_inward_0_5_mm','base')
    print('Hood path and diaphragm room checks passed',flush=True,file=sys.stderr)
    return dict(hood_vertical_sample_lifts_mm=lifts,bead_contact_lifts_mm=contact_lifts,
        peak_rigid_bead_overlap_mm3=peak_overlap)


def insert_checks(model, evidence):
    q=model.model
    closed=model.operating()
    base,jacket=(closed.shape(name) for name in ('base','insert'))
    for name,samples,transform,units in (
            ('insert_lift',(1.,),lambda t:cq.Location((0,0,t)),'mm'),
            ('insert_twist',(3.,),lambda t:cq.Location((0,0,0),(0,0,t)),'deg')):
        evidence.append(sample_motion(closed,'insert','base',PairRequirement(
            'Attempted rigid insert movement meets capture geometry; release force unqualified',min_overlap_mm3=EPS),
            samples=samples,transform=transform,parameter=name,units=units).require_passed().to_dict())
    # A pre-expanded rigid envelope answers geometric access, not elastic feasibility.
    expansion=1.035
    if hasattr(q,'installation_envelopes'):
        install=q.installation_envelopes(jacket,expansion)
    else:
        install=[('uniformly expanded sleeve',jacket.scale(expansion).translate((0,0,-q.FOOT_TOP*(expansion-1))))]
    for label,envelope in install:
        access=fixture(label,{'access_reference':envelope,'base':base})
        evidence.append(sample_motion(access,'access_reference','base',PairRequirement(
            f'{label}: independent rigid access screen, not connected elastic installation',max_overlap_mm3=EPS),
            samples=(0,1,5,10,20,40,45),transform=lambda lift:cq.Location((0,0,lift)),
            parameter='access_envelope_lift',units='mm').require_passed().to_dict())
    return dict(installation_envelope_uniform_scale=expansion,
        installation_access_envelopes=[label for label,_ in install])


def landing_checks(model, evidence):
    q=model.model
    closed=model.operating(include_cards=False)
    base,jacket,hood=(closed.shape(name) for name in ('base','insert','hood'))
    pair,clear=pair_helpers(q,evidence)
    # Soft landing has real area under the hood; it is not a bounding-box claim.
    seat=q.block(-40,40,-30,30,q.FOOT_TOP,q.SEAT_TOP).val()
    pair(hood.translate((0,0,-.02)),jacket.intersect(seat),'Downward hood rim meets TPU seating region',
         'hood_down_0_02_mm','insert_seat_reference',min_overlap_mm3=1e-4)
    for side in (-1,1):
        clear(q.finger(side).val(),hood,'Closed hood clears recessed opening grip',f'finger_reference_{side}','hood')
        clear(q.finger(side).val(),jacket,'TPU skirt clears recessed opening grip',f'finger_reference_{side}','insert')
    return {}


def joining_checks(model, evidence):
    q=model.model
    pair,clear=pair_helpers(q,evidence)
    key=q.keys.seated_key(3).val()
    keyspace=q.keys.seated_key(3,projection=q.h.KEY_FIT_GAP).val()
    keycore=(q.keys.key_outline().offset2D(q.keys.CORE_GROWTH)
             .extrude(q.keys.KEY_HEIGHT).translate((0,0,q.h.KEY_FLOOR_Z)).val())
    neighbours=('new','archive_A','display_J4')
    for name in neighbours:
        for end in (-1,1):
            joined=model.joined(name,end=end)
            joined_bases=cq.Compound.makeCompound([joined.shape(n) for n in ('new/base','neighbour/base')])
            sleeve=joined.shape('new/insert')
            clear(keycore,joined_bases,f'{name}/{end}: joining key core clears rigid stop','key_core_reference','joined_bases')
            entry=fixture(joined.name+'_key_entry',{'key_clearance_reference':keyspace,
                'joined_bases':joined_bases,'insert':sleeve})
            for obstacle in ('joined_bases','insert'):
                evidence.append(sample_motion(entry,'key_clearance_reference',obstacle,PairRequirement(
                    'Actual I3 clearance envelope has a sampled insertion route',max_overlap_mm3=EPS),
                    samples=(0,.2,1,2,4,8,20,45),transform=lambda t:cq.Location((0,0,t)),
                    parameter='key_lift',units='mm').require_passed().to_dict())
            for cover in ('new/hood','neighbour/hood'):
                evidence.append(joined.check('key',cover,PairRequirement(
                    'Seated I3 key clears closed hood',max_overlap_mm3=EPS)).require_passed().to_dict())
                evidence.append(sample_motion(joined,'key',cover,PairRequirement(
                    'Attempted key lift meets closed hood and remains captive',min_overlap_mm3=EPS),
                    samples=(1.1,),transform=lambda t:cq.Location((0,0,t)),parameter='key_lift',units='mm').require_passed().to_dict())
            evidence.append(joined.check('new/hood','neighbour/hood',PairRequirement(
                'Adjacent closed hoods do not overlap',max_overlap_mm3=EPS)).require_passed().to_dict())
            for obstacle in ('neighbour/base','neighbour/hood'):
                evidence.append(sample_motion(joined,'new/hood',obstacle,PairRequirement(
                    'Individual opening clears adjacent module',max_overlap_mm3=EPS),
                    samples=(0,4,20,84),transform=lambda t:cq.Location((0,0,t)),
                    parameter='hood_lift',units='mm').require_passed().to_dict())
            # Both flanks of both heads must meet capture material, not merely clear.
            for xs in (-1,1):
                for ys in (-1,1):
                    xl,xh=sorted((xs*3,xs*9));yl,yh=sorted((ys*.01,ys*4))
                    patch=q.block(xl,xh,yl,yh,q.h.KEY_FLOOR_Z,q.h.KEY_TOP_Z+.1).val()
                    pair(key,joined_bases.intersect(patch),f'{name}/{end}: required I3 head-flank capture',
                         'key',f'joined_capture_reference_{xs}_{ys}',min_overlap_mm3=1e-5)
    return {}


def main(q=q, output_name='quiet_q1_checks.json', *, model=None, extra=None):
    model = model or QuietAssembly(q)
    assert model.model is q, 'Assembly and checks must use the same candidate builders'
    evidence=[]
    closed_checks(model,evidence)
    card_checks(model,evidence)
    travel=hood_checks(model,evidence)
    travel.update(insert_checks(model,evidence))
    landing_checks(model,evidence)
    joining_checks(model,evidence)
    lifts=travel['hood_vertical_sample_lifts_mm']
    contact_lifts=travel['bead_contact_lifts_mm']
    peak_overlap=travel['peak_rigid_bead_overlap_mm3']
    expansion=travel['installation_envelope_uniform_scale']
    neighbours=('new','archive_A','display_J4')
    report=dict(ok=True,capacity=15,material_assumption='User reports TPU 95A; brand and printed behavior unknown',
        accepted_card_pocket_and_entry_preserved=True,actual_cards_on_floor=True,
        nominal_three_part_clearance=True,hood_vertical_sample_lifts_mm=lifts,
        rigid_base_clear_at_sampled_offsets_mm=.2,only_soft_beads_contact_during_sampled_centred_travel=True,
        bead_contact_lifts_mm=contact_lifts,peak_rigid_bead_overlap_mm3=peak_overlap,
        diaphragm_inward_room_screen_mm=.5,insert_lift_capture_at_mm=1.,insert_twist_block_at_deg=3.,
        installation_envelope_uniform_scale=expansion,soft_seat_witness=True,recessed_grip_access=True,
        installation_access_envelopes=travel['installation_access_envelopes'],
        existing_I3_key_and_joined_opening_both_ends=list(neighbours),
        assembly_api_evidence=evidence,
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
            (Path(q.__file__),Path(__file__),ROOT/'quiet_assembly.py')},
        limits='Nominal CAD and sampled hand-guided paths. Pre-expanded/independent rigid envelopes are access screens, '
            'not a deformation/contact solve or strain qualification. No printed noise, force, friction, '
            'creep, durability or suspended-load rating. Existing joining-key force is not recalibrated.')
    if extra:
        report.update(extra)
    output=ROOT/'notes'/output_name if output_name else None
    if output:
        output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(ok=True,report=str(output) if output else None,bead_contact_lifts_mm=contact_lifts,
                          joining=list(neighbours))),flush=True)
    return report


if __name__=='__main__':
    main()
