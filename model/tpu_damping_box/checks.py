"""Targeted CAD witnesses; imported only when product geometry is requested."""
import cadquery as cq
import design as d

def overlap(a,b):
    return a.val().intersect(b.val()).Volume()


def contained(witness,part):
    assert witness.val().cut(part.val()).Volume() < 1e-6, 'Required continuous skin/material missing'


def no_overlap(a,b):
    assert overlap(a,b) < 1e-6, 'Forbidden part interference'


def candidate(name):
    return d.body(), d.cup(name), d.pad_closed(name)


def fit_checks(parts):
    body,cup,pad = parts
    placed = cup.translate((0,0,d.FLOOR))
    no_overlap(placed,body)
    no_overlap(placed,pad)
    no_overlap(pad,body)
    for travel in (0,8,20,36):
        no_overlap(placed.translate((0,0,travel)),body)
    # Actual planar walls and a constant-section cavity also exclude a blocker
    # between these poses; this is not a general continuous-path algorithm.
    cavity = d.block(26,26,26,d.FLOOR+4)
    no_overlap(cavity,placed)
    no_overlap(cavity,pad)
    for axis in range(3):
        for shift in (-7,0,7):
            xyz=[0,0,d.FLOOR+17]
            xyz[axis] += shift
            probe=d.block(12,12,12,-6).translate(tuple(xyz))
            no_overlap(probe,placed)
            no_overlap(probe,pad)


def skin_checks(parts):
    _,cup,pad=parts
    contained(d.block(26,26,0.6,3.4),cup)
    wall=d.block(0.6,26,26,4).translate((-13.3,0,0))
    for angle in (0,90,180,270):
        contained(wall.rotate((0,0,0),(0,0,1),angle),cup)
    contained(d.block(26,26,0.6,d.FLOOR+30),pad)
    # No relief, lettering or core web is permitted in the nominal cavity.
    no_overlap(d.block(26,26,26,4),cup)
    no_overlap(d.block(26,26,26,d.FLOOR+4),pad)


def core_checks(name,parts):
    _,cup,_=parts
    if name=='A':
        contained(d.block(26,26,2.4,0.8),cup)
        return
    # Witnesses lie between the two central webs for every adopted topology.
    floor_air=d.block(0.2,2,0.2,1.1)
    no_overlap(floor_air,cup)
    v=d.variant_named(name)
    inner= d.CUP_SIZE/2-d.BACKING
    wall_air=d.block(0.2,0.2,2,18).translate((-inner+0.4,0,0))
    for angle in (0,90,180,270):
        no_overlap(wall_air.rotate((0,0,0),(0,0,1),angle),cup)
    pad=d.pad_print(name)
    no_overlap(d.block(0.2,2,0.2,1.3),pad)
    # Web attachment is material, not an infill instruction.
    for x in (-d.RIB_PITCH/2,d.RIB_PITCH/2):
        if v.core=='straight':
            contained(d.block(0.2,2,0.2,1.5).translate((x,0,0)),cup)


def label_checks(name,parts):
    _,cup,_=parts
    glyph=d.label_cut(name,0.25)
    no_overlap(glyph,cup)
    no_overlap(glyph,d.pad_print(name))
    # Just above the recess must remain connected backing.
    contained(glyph.translate((0,0,0.35)),cup)
    contained(glyph.translate((0,0,0.35)),d.pad_print(name))
    assert set(d.VARIANTS)==set('ABCDEF'), 'Batch variant coverage changed'


def closure_checks(body):
    for x,y in d.SCREW_CENTRES:
        z=d.BODY_HEIGHT-d.NUT_ROOF-d.NUT_SLOT_HEIGHT+0.2
        nut=cq.Workplane('XY').polygon(6,2*5.5/(3**0.5)).extrude(2.4).translate((x,y,z))
        sign=1 if x>0 else -1
        for distance in (0,2,4,6,9):
            no_overlap(nut.translate((sign*distance,0,0)),body)
        assert overlap(nut.translate((0,0,3)),body)>1, 'Nut has no load-bearing roof'
        shaft=cq.Workplane('XY').center(x,y).circle(1.5).extrude(12).translate((0,0,d.BODY_HEIGHT-8.8))
        no_overlap(shaft,body)
        no_overlap(shaft,d.lid_closed())
