"""Registered local spring fill and support-location review, using shared reader.

Not an envelope checker. Orca owns printer fit. PNGs show actual requested
deposited strokes and support placement, not measured polymer or modulus.
"""
import json, hashlib, sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from physical_analysis.manufacturing import orca_linear_paths, section_coverage
import swatch_book_case as m

HERE=Path(__file__).parent

def review(run):
    run=Path(run)
    gcode=run/'plate_1.gcode'
    paths=list(orca_linear_paths(gcode))
    # print_layout() and preserve placement: explicit source registration.
    ox=20.; oy=2*m.DEPTH+40.
    rows=[]
    for x in (ox+12,ox+22):
        for z in (.6,2.2,4.2,6.2):
            rows.append({'x_mm':x,'z_mm':z,'span_mm':[oy,oy+m.LEAF_T],
                **section_coverage(paths,x_mm=x,z_mm=z,span_mm=(oy,oy+m.LEAF_T))})
    assert max(r['uncovered_width_mm'] for r in rows)<.05, rows
    # Show one consequential layer through the spring, preserving width metadata.
    local=[p for p in paths if abs(p[4]-4.2)<1e-5 and
           min(p[0],p[2])>=ox-2 and max(p[0],p[2])<=ox+40 and
           min(p[1],p[3])>=oy-2 and max(p[1],p[3])<=oy+10 and
           not p[-1].startswith(('Support','Brim'))]
    fig,ax=plt.subplots(figsize=(10,3))
    for x,y,nx,ny,z,width,role in local:
        ax.plot([x-ox,nx-ox],[y-oy,ny-oy],color='#245c85',lw=3*width)
    for x in (12,22): ax.plot([x,x],[0,m.LEAF_T],color='#d2691e',lw=1)
    ax.set_aspect('equal');ax.set_xlabel('Catch print X (mm)');ax.set_ylabel('Y (mm)')
    ax.set_title('Actual Orca layer at Z = 4.2 mm; orange lines are reviewed sections')
    fig.tight_layout(); fig.savefig(HERE/'renders/print/catch_paths.png',dpi=160);plt.close(fig)
    supports=[p for p in paths if p[-1].startswith('Support')]
    deposited=[p for p in paths if not p[-1].startswith(('Support','Brim'))]
    fig,ax=plt.subplots(figsize=(7,7))
    for selected,color,width in ((deposited,'#c6cbd0',.15),(supports,'#d55e00',.6)):
        ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in selected],colors=color,linewidths=width))
    ax.autoscale();ax.set_aspect('equal');ax.set_xlabel('Bed X (mm)');ax.set_ylabel('Bed Y (mm)')
    ax.set_title('Support paths in orange; all layers projected onto XY')
    fig.tight_layout();fig.savefig(HERE/'renders/print/support_locations.png',dpi=160);plt.close(fig)
    # Locations, not print-fit recomputation. Buckets connect supports to CAD jobs.
    categories={}
    for p in supports:
        x=(p[0]+p[2])/2;y=(p[1]+p[3])/2
        if y>170 and x<65: name='catch tooth'
        elif 80<y<115: name='rear hinge barrels'
        elif y<50: name='front catch mount/nut access'
        else: name='cover keeper/other: review projection'
        categories[name]=categories.get(name,0)+1
    report={'gcode_sha256':hashlib.sha256(gcode.read_bytes()).hexdigest(),
            'placement':'preserve; source positive bed coordinates',
            'local_solid_paths_established':True,'spring_sections':rows,
            'support_path_categories':categories,
            'limits':'Stroke-width approximation on selected sections; not measured fill, isotropy, layer bonding or calibrated stiffness.'}
    (HERE/'notes/manufacturing_paths.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':review(sys.argv[1])
