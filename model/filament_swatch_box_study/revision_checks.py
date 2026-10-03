"""Shared checks for this object's J2/K2 revisions; not a generic framework.

Rigid paths exclude elastic panels. Opposing contact and tilt witnesses answer
the printed alignment failure; no force, creep or continuous-motion claim.
"""
import math
import hashlib
from pathlib import Path
import swatch_reference as ref
import upright_datums as datum
import cap_i_grip_keys as keys
from check_corner_seat import card_envelope


def check_base(module,*,label,datum_side,panel,previous):
    j=datum.j
    base=module.base().val()
    rigid=module.base(include_panels=False,include_detents=False).val()
    assert base.isValid() and len(base.Solids())==1,'Base/rails must be one connected valid solid'
    mask=j.g.block(-24.2,24.2,-j.g.BODY_DEPTH/2,j.g.BODY_DEPTH/2,
                  j.slots.FLOOR-j.ROOT_OVERLAP-.01,23).val()
    a,b=base.cut(mask),previous.cut(mask)
    assert a.cut(b).Volume()<1e-6 and b.cut(a).Volume()<1e-6,'External mates changed'
    nominal_back=datum_side*j.slots.SLOT_WIDTH/2-(ref.THICKNESS if datum_side>0 else 0)
    nominal=ref.card(nominal_back).val()
    overlap=panel.intersect(nominal)
    assert overlap.Volume()>1e-5,'No intended seated contact'
    contact=overlap.BoundingBox()
    low=j.slots.FLOOR+datum.LOW_HEIGHT
    high=j.slots.FLOOR+datum.STRAIGHT_HEIGHT
    assert low<contact.zmin<contact.zmax<high,'Opposing support does not span load region'
    local_rails=datum.rails(0,datum_side).val()
    slot_rails={j.slots.slot_y(n,j.COUNT):local_rails.translate((0,j.slots.slot_y(n,j.COUNT),0))
                for n in range(j.COUNT)}
    cases=[]
    # Construct once per thickness in source space, place into every real slot.
    for thickness in (1.8,2.0,2.2):
        back=(j.slots.SLOT_WIDTH/2-thickness if datum_side>0 else -j.slots.SLOT_WIDTH/2)
        c=ref.card(back,thickness).val()
        for n in range(j.COUNT):
            y=j.slots.slot_y(n,j.COUNT)
            card=c.translate((0,y,0))
            assert card.intersect(rigid).Volume()<1e-6,'Real source card hits rigid guides'
            for x in (-22.4,22.4):
                for z in (low+.5,high-.5):
                    patch=j.g.block(x-.1,x+.1,y-4,y+4,z-.1,z+.1).val()
                    material=card.translate((0,datum_side*.02,0)).intersect(patch)
                    assert material.intersect(slot_rails[y]).Volume()>1e-5,\
                        'Missing lower/upper opposing contact on actual card material'
            cases.append(dict(slot=n,thickness_mm=thickness,source_card_clear=True))
    # Keep the spring's load line fixed. Either lean then meets an opposing rail.
    pivot=(0,datum_side*j.slots.SLOT_WIDTH/2,(contact.zmin+contact.zmax)/2)
    for angle in (-.5,.5):
        tilted=nominal.rotate(pivot,(1,pivot[1],pivot[2]),angle)
        assert tilted.intersect(local_rails).Volume()>1e-5,\
            'A tilt about the spring contact remains unsupported'
    # Correct position/angle through the shorter funnel before lowering straight.
    for sx,sy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
        for step in range(11):
            f=step/10
            ax,ay,yaw=sy*2*(1-f),sx*2*(1-f),sx*(1-f)
            drop=25.2*abs(math.sin(math.radians(ay)))+1.1*abs(math.sin(math.radians(ax))*math.cos(math.radians(ay)))
            c=(card_envelope(50.4,2.2,4).translate((0,1.1,0))
               .rotate((0,0,0),(1,0,0),ax).rotate((0,0,0),(0,1,0),ay)
               .rotate((0,0,0),(0,0,1),yaw).translate((sx*1.5*(1-f),
                   sy*(1-f)+.3*f,j.g.TOP_Z-.15-(j.g.TOP_Z-.15-high)*f+drop)))
            if datum_side<0:
                c=c.mirror('XZ')
            assert c.val().intersect(rigid).Volume()<1e-6, f'Guided entrance blocked: {sx,sy,step}'
    for step in range(9):
        back=j.slots.SLOT_WIDTH/2-2.2 if datum_side>0 else -j.slots.SLOT_WIDTH/2
        c=ref.card(back,2.2).translate((0,0,datum.STRAIGHT_HEIGHT*(1-step/8))).val()
        assert c.intersect(rigid).Volume()<1e-6,'Aligned descent blocked'
    hood=j.g.cap().val()
    assert hood.distance(rigid)<1e-6,'Accepted hood no longer reaches rim'
    for lift in (0,1,16,84):
        assert hood.translate((0,0,lift)).intersect(rigid).Volume()<1e-6,'Hood lift blocked'
        assert hood.translate((0,0,lift)).intersect(panel).Volume()<1e-6,'Hood hits card spring'
    joined=j.g.compound(*[rigid.translate((0,y,0)) for y in keys.module_centres()])
    space=keys.seated_key(3,projection=keys.h.KEY_FIT_GAP).val()
    for lift in (0,.2,1,2,4,8,16,22):
        assert space.translate((0,0,lift)).intersect(joined).Volume()<1e-6,'Accepted key insertion blocked'
    return dict(variant=label,source_transform='Proper -120 degree rotation about (1,1,1); front +Y',
        real_card_cases=cases,opposing_straight_height_from_floor_mm=datum.STRAIGHT_HEIGHT,
        contact_z_mm=[contact.zmin,contact.zmax],support_z_mm=[low,high],
        tilt_witness_angles_deg=[-.5,.5],guided_entry_samples=88,aligned_descent_samples=9,
        scope='Rigid source-card contact/path checks; springs excluded from entry. No physical alignment, force or creep validation.',
        unchanged_external_mates=True,G_hood_seats_and_lifts=True,I_key_entry_clear=True)


def sources(names):
    directory=Path(__file__).resolve().parent
    return {name:hashlib.sha256((directory/name).read_bytes()).hexdigest() for name in names}
