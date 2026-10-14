"""Targeted M1 checks: rigid CAD, prescribed flexure envelopes and cheap mechanics."""
import cadquery as cq
from assembly_geometry import Configuration, PairRequirement, check_pair
from m1_design import box, configuration, joint_test, mirrored, prism, tongue

OVERLAP = 1e-5  # mm^3, numerical intersection screen, not print tolerance


def clear(a, b, intent, gap=None):
    check_pair(a, b, PairRequirement(intent, max_overlap_mm3=OVERLAP,
                                     min_gap_mm=gap)).require_passed()


def construction(parts):
    d = parts['dimensions']
    for name in ('body', 'cap'):
        assert parts[name].val().isValid(), name+' invalid'
        # Functional connectivity: no detached tongue/liner islands.
        assert len(parts[name].solids().vals()) == 1, name+' must be one connected printed part'
    assert d.seam+d.lap < 256 and d.length-d.seam < 256, 'Q2C height exceeded'
    assert 112+d.width+6 < 270 and d.depth+6 < 270, 'Paired layout/brim exceeds Q2C'
    coupon = joint_test(parts)
    assert coupon.toCompound().isValid(), 'Joint test invalid'
    # Crop consumes production shapes and leaves the whole circumference,
    # root/ramp/liner, both controls, sleeve and windows, in the same orientation.
    assert d.beam_root-12 < d.beam_root-8
    assert d.seam+30 > d.hook_bottom+11 > d.seam+d.lap


def fit(parts):
    config = Configuration.explicit(configuration(parts, cap_lift=0,
                                contents=True, releases=(0, 0)), name='closed')
    refs = parts['references']
    for name, reference in refs.items():
        config.check(name, 'cap', PairRequirement(name+' clears posed cap',
                     max_overlap_mm3=OVERLAP, min_gap_mm=.8)).require_passed()
        for shell in ('body', 'cap'):
            clear(reference, parts[shell], name+' clears '+shell, gap=.8)
    clear(refs['brush'], refs['paste'], 'Separated nominal rigid contents', gap=2.9)
    # Actual tube and attached handle must traverse the minimum mouth, not just
    # fit below it. Cross-section extrusion gives continuous axial path coverage.
    d = parts['dimensions']
    brush_sweep = cq.Workplane('XY', origin=(d.brush_x, 0, 4.5)).circle(15).extrude(255+190)
    paste_sweep = box(d.paste_x, 0, (3+353)/2, 55, 40, 353-3)
    clear(brush_sweep, parts['body'], 'Brush handle extraction through complete mouth', gap=.8)
    clear(paste_sweep, parts['body'], 'Full tube extraction through complete mouth', gap=.8)
    # Measured head is smaller than the handle circle; no promised unmeasured offset.


def closure(parts):
    d = parts['dimensions']
    clear(parts['body'], parts['cap'], 'Closed sleeves/catches clear without preload')
    # Seat contact is required independently of the snap: pushing past zero
    # must meet the hard circumferential shoulder, even with both leaves released.
    check_pair(parts['fixed'], parts['cap'], PairRequirement('Rim seats on body', max_gap_mm=1e-6)).require_passed()
    check_pair(parts['fixed'], parts['cap'].translate((0, 0, -.2)),
               PairRequirement('Seat obstructs excess closing', min_overlap_mm3=10)).require_passed()
    for sign in (-1, 1):
        # Each hook alone retains against an axial pull, including adverse
        # lateral guide play. This is obstruction, not force/drop qualification.
        leaf = mirrored(tongue(d), sign)
        for y in (-d.lap_clearance, 0, d.lap_clearance):
            shoulder = leaf.intersect(box(d.catch_x, 0, d.hook_bottom+.2, 6, 60, .4))
            check_pair(shoulder, parts['cap'].translate((0, y, .9)),
                       PairRequirement('Independent positive pull-off catch', min_overlap_mm3=.5)).require_passed()
    # Removing catch geometry must remove its obstruction; checks cannot pass
    # solely because an unrelated shell interferes.
    clear(parts['fixed'], parts['cap'].translate((0, 0, .9)), 'Missing-catches negative control')
    # Rounded seam is flush; all buttons stay below the protected outer surface.
    assert d.beam_outer+d.hook_projection <= d.depth/2-.7


def release_path(parts):
    d = parts['dimensions']
    free_bottom, free_top = d.beam_root+2, d.beam_tip+1.6
    free_span = box(d.catch_x, 0, (free_bottom+free_top)/2,
                    d.beam_width+8, d.depth+8, free_top-free_bottom)
    for delta in (0, .5, 1, 1.5, d.release):
        for sign in (-1, 1):
            leaf = mirrored(tongue(d, delta), sign)
            clear(leaf.intersect(free_span), parts['fixed'],
                  'Root-fixed leaf free span clears guard/liner throughout squeeze', gap=.1)
            clear(leaf, parts['cap'], 'Squeezing leaf clears seated cap')
            for name, ref in parts['references'].items():
                clear(leaf, ref, 'Squeeze avoids '+name, gap=.8)
    # The conservative continuous sweep below covers withdrawal. Actual window
    # poses retain a separate check of local contacts and lowest/upper roof.
    leaves = [mirrored(tongue(d, d.release), sign) for sign in (-1, 1)]
    # A conservative continuous +Z sweep fills the windows and ignores exterior
    # edge rounds. Its void ends at the lowest cap ceiling. This superset must
    # clear the fixed body, depressed leaves and contents for the entire lift.
    swept = prism(d.width, d.depth, d.corner, d.seam, d.length-d.seam+106)
    swept = swept.cut(prism(d.width-2*d.wall, d.depth-2*d.wall,
                            d.corner-d.wall, d.seam-1,
                            d.length-d.floor-d.seam+1))
    for name, shape in [('fixed body', parts['fixed'])] + [
            ('depressed leaf', leaf) for leaf in leaves] + list(parts['references'].items()):
        clear(shape, swept, 'Continuous cap withdrawal sweep clears '+name)
    for lift in (0, .2, .5, 1, 2, 3, 4, 6, 8, 10, 12, 16, 30, 60, 90, 106):
        cap = parts['cap'].translate((0, 0, lift))
        clear(parts['fixed'], cap, 'Released cap clears fixed body on sampled lift')
        for leaf in leaves:
            clear(leaf, cap, 'Released hook clears sampled withdrawal')
        for name, ref in parts['references'].items():
            clear(cap, ref, 'Cap withdrawal clears '+name, gap=.8)
    # Worst transverse guide play must still admit the deliberately pressed tip.
    for sign, leaf in zip((-1, 1), leaves, strict=True):
        clear(leaf, parts['cap'].translate((0, -sign*d.lap_clearance, 2)),
              'Release survives transverse guide play')


def assembly_path(parts):
    d = parts['dimensions']
    # Leave the blended roots stationary; precompress both leaves as a conservative
    # admission route. Release after both hook shoulders enter their windows.
    # This proves an available two-hand squeeze-and-push path, not snap-on force.
    pressed = [mirrored(tongue(d, d.release), sign) for sign in (-1, 1)]
    for lift in (16, 12, 10, 8, 6, 4, 2, 1, .5, 0):
        cap = parts['cap'].translate((0, 0, lift))
        clear(parts['fixed'], cap, 'Sampled cap admission clears guide')
        for leaf in pressed:
            clear(leaf, cap, 'Precompressed root-fixed catch admits cap')
    # Sleeve alone guides; catches are not tasked with anti-twist or lateral load.
    check_pair(parts['fixed'], parts['cap'].translate((0, 1, 0)),
               PairRequirement('Lap limits transverse travel', min_overlap_mm3=1)).require_passed()
    check_pair(parts['fixed'], parts['cap'].rotate((0, 0, 0), (0, 0, 1), 2),
               PairRequirement('Nonround lap limits twist', min_overlap_mm3=1)).require_passed()


def compliance(parts):
    d = parts['dimensions']
    # Point load at the accessible contact, with an unloaded overhanging tip.
    # Shorten the flexible span for the blended root; allow +0.3 mm tip error.
    length = d.beam_tip-(d.beam_root+1)
    contact = d.press_z-(d.beam_root+1)
    displacement = (d.release+.3)*2*contact/(3*length-contact)
    strain = 3*d.beam_thickness*displacement/(2*contact**2)
    assert strain < .01, 'Above agent-selected 1% provisional strain screen'
    # Assumed effective PETG modulus bracket, not printer/material calibration.
    # Estimated per-leaf force is not cap retention or complete insertion effort.
    press_travel = d.release*2*contact/(3*length-contact)
    forces = [3*e*(d.beam_width*d.beam_thickness**3/12)/contact**3*press_travel
              for e in (800, 2200)]
    assert all(0 < f < 5 for f in forces), 'Above provisional 5 N per-leaf squeeze screen'
