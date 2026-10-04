"""Solid-mechanics sections and generated support removal paths, not envelope rechecks."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from physical_analysis.manufacturing import orca_linear_paths,section_coverage

ROOT=Path(__file__).parent


def review():
    report=json.loads((ROOT/'notes/v3_final_review.json').read_text())
    gcode=Path(report['slice']['kept_run_directory'])/'plate_1.gcode'
    paths=list(orca_linear_paths(gcode))
    sections=[]
    for side,x in (('right',231),('left',179)):
        for i,y in enumerate((193,199,205)):
            sections.append((f'{side} return leg {i+1}',x,2,(y-.4,y+.4)))
    sections.extend((('nose crossbar',205,2,(161,171)),
                     ('housing guide bearing',78,22.4,(41,49)),
                     ('cradle upper standoff',200,13,(118,130)),
                     ('cradle ledge',225,13,(47,52))))
    checked=[dict(name=n,x=x,z=z,span=span,**section_coverage(paths,x_mm=x,z_mm=z,span_mm=span))
             for n,x,z,span in sections]
    out=dict(scope='Registered mechanics sections and selected support layers; no material calibration or printer-envelope reconstruction',
        gcode_sha256=hashlib.sha256(gcode.read_bytes()).hexdigest(),
        slice_input_sha256=report['slice']['input_sha256'],sections=checked)
    (ROOT/'notes/v3_solid_sections.json').write_text(json.dumps(out,indent=2)+'\n')
    fig,axes=plt.subplots(2,2,figsize=(13,10),layout='constrained')
    for ax,z,title,limits in zip(axes.flat,(22,31.2,13.2,43.2),
            ('Guide + spring cavities','Root pockets and hood','Cradle lower outboard pad','Cradle upper outboard pad'),
            ((10,122,28,102),(10,122,28,102),(175,245,42,148),(175,245,42,148))):
        for role,color in (('model','#555555'),('Support','#00a6b5'),('Support interface','#b62baa')):
            segments=[[(x0,y0),(x1,y1)] for x0,y0,x1,y1,zz,w,r in paths
                if abs(zz-z)<.001 and (r==role if role!='model' else not r.startswith('Support'))]
            ax.add_collection(LineCollection(segments,colors=color,linewidths=.7,label=role))
        ax.set_xlim(limits[:2]);ax.set_ylim(limits[2:]);ax.set_aspect('equal')
        ax.set_title(f'{title}: Z {z:g} mm');ax.set_xlabel('X mm');ax.set_ylabel('Y mm')
    axes[0,0].legend();fig.savefig(ROOT/'notes/v3_support_review.png',dpi=140)
    print(json.dumps({'sections':checked,'support_image':str(ROOT/'notes/v3_support_review.png')}))


if __name__=='__main__':review()
