"""Reproduce reported STEP trouble and check the replacement exports themselves.

This targeted check exists because the user reported STEP edge warnings. It is
not a routine model audit. Inspect every component, including failed shells.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import cadquery as cq
from rotary_matte_design import EXTENSION
from rotary_printed_fastener_design import ROOT_RADIUS,TIP

ROOT=Path(__file__).resolve().parent


def inspect(path):
    imported=cq.importers.importStep(str(path)).val()
    rows=[]
    for child in imported:
        vertices,triangles=child.tessellate(.003,.5)
        # Join only numerical duplicates; this does not close geometric gaps.
        points=[tuple(round(x,7) for x in p.toTuple()) for p in vertices]
        edges=Counter()
        degenerate=0
        for triangle in triangles:
            a,b,c=(points[i] for i in triangle)
            degenerate+=int(len({a,b,c})<3)
            for x,y in ((a,b),(b,c),(c,a)):
                edges[tuple(sorted((x,y)))]+=1
        rows.append(dict(type=child.ShapeType(),valid=child.isValid(),
            solids=len(child.Solids()),triangles=len(triangles),
            non_two_incident_edges=sum(n!=2 for n in edges.values()),
            degenerate_triangles=degenerate))
    return imported,rows


def main():
    old=ROOT/'rotary_covered_mechanism.step'
    new=ROOT/'rotary_matte_repair.step'
    _,old_rows=inspect(old)
    part,rows=inspect(new)
    assert len(rows)==2
    assert all(r['valid'] and r['solids']==1 and r['non_two_incident_edges']==0
               and r['degenerate_triangles']==0 for r in rows),rows
    # Actual exported screw, not the source's intended root cylinder.
    screw=list(part)[1]
    core=(cq.Workplane('XY',origin=(100,60,4.2+EXTENSION))
          .circle(ROOT_RADIUS-.02).extrude(TIP-4.2-.01))
    missing=core.val().cut(screw).Volume()
    assert missing<1e-5,missing
    assert old_rows[1]['solids']==0 and old_rows[2]['non_two_incident_edges']>0
    report=dict(old=old_rows,replacement=rows,exported_core_missing_mm3=missing,
        weld_tolerance_mm=1e-7,linear_deflection_mm=.003,angular_deflection_rad=.5,
        artifacts={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                   (old,new,ROOT/'rotary_matte_repair.stl')},
        limits='CadQuery/OpenCascade STEP import and tessellation; exact Orca GUI warning not reproduced')
    (ROOT/'notes/matte_rotary/step.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':
    main()
