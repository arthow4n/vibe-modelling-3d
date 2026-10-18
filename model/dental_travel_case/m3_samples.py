"""M3 full-circumference joint sample, cropped from unchanged production CAD."""
import cadquery as cq
from m1_design import box, print_cap


def joint_sample(parts):
    """Preserve complete roots, controls, receivers and the full guide span.

    Open cut ends save material. No floor, stiffening fixture or viewing window
    is added. Full-size shell compliance and remote handling are not represented.
    Returned body/cap remain in the production assembly frame; result is placed
    in the same upright-body/inverted-cap print orientations as the full case.
    """
    d=parts['dimensions']
    bottom=d.beam_root-12
    top=d.seam+d.lap+12
    def crop(lo,hi):
        return box(0,0,(lo+hi)/2,d.width+2*d.skin_reinforcement+4,
                   d.depth+4,hi-lo)
    body=parts['body'].intersect(crop(bottom,d.seam+d.lap))
    cap=parts['cap'].intersect(crop(d.seam,top))
    assembly=cq.Assembly(name='m3_joint_sample')
    assembly.add(body.translate((0,0,-bottom)),name='body_joint')
    assembly.add(print_cap(cap,top),name='cap_joint')
    return dict(body=body,cap=cap,dimensions=d,body_bottom_mm=bottom,
                cap_top_mm=top,result=assembly)
