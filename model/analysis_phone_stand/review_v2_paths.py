"""Selected solid FE sections and support accessibility on the final plates."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from physical_analysis.manufacturing import orca_linear_paths, section_coverage

ROOT = Path(__file__).parent

def paths(name):
    report = json.loads((ROOT/f'notes/v2_{name}_final_review.json').read_text())
    gcode = Path(report['slice']['kept_run_directory'])/'plate_1.gcode'
    return report, gcode, list(orca_linear_paths(gcode))

if __name__ == '__main__':
    base, bg, bp = paths('base')
    mechanism, mg, mp = paths('mechanism')
    sections = [('left spring',96,2,(245.4,246.6)),
                ('right spring',196,2,(245.4,246.6)),
                ('cradle ledge',229,30,(11,16)),
                ('cradle rear pad',229,30,(82,90))]
    reviewed = [dict(name=n,x=x,z=z,span=span,**section_coverage(mp,x_mm=x,z_mm=z,span_mm=span))
                for n,x,z,span in sections]
    report = dict(scope='Selected actual local solid sections; no material calibration, ordinary-wall audit or printer-envelope reconstruction',
        gcode_sha256=hashlib.sha256(mg.read_bytes()).hexdigest(),
        slice_input_sha256=mechanism['slice']['input_sha256'],sections=reviewed)
    (ROOT/'notes/v2_solid_sections.json').write_text(json.dumps(report,indent=2)+'\n')
    fig, axes = plt.subplots(2,2,figsize=(12,10),layout='constrained')
    for ax, strokes, z, label in zip(axes.flat,[bp,bp,mp,mp],[2.6,55.4,13.2,59.4],
        ['Base underside recesses','Base pivot openings','Keeper roofs','Cradle lips']):
        for role, color in [('model','#555555'),('Support','#00a6b5'),('Support interface','#b62baa')]:
            segments = [[(x0,y0),(x1,y1)] for x0,y0,x1,y1,zz,w,r in strokes
                if abs(zz-z)<.001 and (r==role if role!='model' else not r.startswith('Support'))]
            ax.add_collection(LineCollection(segments,colors=color,linewidths=.5,label=role))
        ax.autoscale();ax.set_aspect('equal');ax.set_title(f'{label}: Z {z:g} mm');ax.set_xlabel('X (mm)');ax.set_ylabel('Y (mm)')
    axes[0,0].legend(loc='upper right');fig.savefig(ROOT/'notes/v2_support_review.png',dpi=140)
    print(json.dumps({'sections':reviewed,'gcode':str(mg)}))
