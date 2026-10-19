"""Challenge rigid release translation with approximate bending tip rotation.

Small-slope inextensible end-loaded leaf: rotation 1.5*d/L and axial shortening
0.6*d²/L. Effective tip at either rail edge brackets crossbar coupling; this is
not nonlinear contact FEM or a material/force qualification.
"""
import json
import math
from clamshell_design import build,D,base,SEATED_GAP
from clamshell_study import OUT,hashes


def inspect():
    p=build('screw_pin')
    rows=[]
    for gap in (.2,SEATED_GAP):
        shift=SEATED_GAP-gap;top=D.seam-5.8-gap
        loop=p['loop'].translate((0,0,shift))
        rail=loop.intersect(base.box(0,-42,top-2,24,16,4))
        for length,pivot_z in ((17.,top),(20.,top-3)):
            for step in range(15):
                delta=step*.25;angle=-math.degrees(1.5*delta/length);rise=.6*delta**2/length
                r=rail.rotate((0,-D.depth/2-4.8,pivot_z),(1,-D.depth/2-4.8,pivot_z),angle).translate((0,-delta,rise))
                hit=p['body'].union(p['keeper']).intersect(r).val().Volume()
                rows.append(dict(seated_gap_mm=gap,effective_length_mm=length,radial_motion_mm=delta,tip_angle_deg=angle,
                    axial_motion_mm=rise,intersection_mm3=hit))
    data=dict(scope=__doc__,source_sha256=hashes(('clamshell_design.py','clamshell_rail_motion.py','m1_design.py','../sunglasses_case/e_closure.py')),
        poses=rows,reference_gap_maximum_intersection_mm3=max(r['intersection_mm3'] for r in rows if r['seated_gap_mm']==.2),
        selected_maximum_intersection_mm3=max(r['intersection_mm3'] for r in rows if r['seated_gap_mm']==SEATED_GAP))
    (OUT/'rail_motion.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data),flush=True)
    return data


if __name__=='__main__':inspect()
