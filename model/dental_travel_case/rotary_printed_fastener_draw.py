"""Actual horizontal CAD sections and sliced core paths, old versus replacement."""
from pathlib import Path
from collections import Counter
import json,hashlib
import xml.etree.ElementTree as ET
import cadquery as cq
import cairosvg
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from physical_analysis.manufacturing import orca_linear_paths,section_coverage
from rotary_refinement_design import printed_axle as old_axle
from rotary_printed_fastener_design import printed_axle

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'renders/tests/printed_fasteners'
NOTES=ROOT/'notes/printed_fasteners'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    # Section actual solid geometry, rather than sketching the intended core.
    chunks=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="400" viewBox="0 0 900 400"><rect width="900" height="400" fill="#f5f7f8"/><g font-family="sans-serif" fill="#18303a"><text x="30" y="35" font-size="23">Actual thread sections at 6 mm above the bed</text>']
    for index,(name,part,caption) in enumerate((('OLD M6 AXLE',old_axle(),'Empty centre: confirmed in delivered STEP'),('COARSE REPLACEMENT',printed_axle(),'Filled centre: confirmed in delivered STEP'))):
        section=part.section(6.)
        raw=cq.exporters.getSVG(section.val(),opts={'width':360,'height':270,'projectionDir':(0,0,1),'showHidden':False,'marginLeft':20,'marginTop':20})
        xml=ET.fromstring(raw);xml.set('x',str(30+440*index));xml.set('y','85')
        chunks.append(f'<text x="{30+440*index}" y="73" font-size="19">{name}</text>')
        chunks.append(ET.tostring(xml,encoding='unicode'))
        chunks.append(f'<text x="{30+440*index}" y="378" font-size="16">{caption}</text>')
    chunks.append('</g></svg>');(OUT/'thread_sections.svg').write_text(''.join(chunks))
    cairosvg.svg2png(url=str(OUT/'thread_sections.svg'),write_to=str(OUT/'thread_sections.png'))
    # Actual role paths; supports omitted from the core comparison.
    sources=[]
    for label,report in [('Old hollow axle','rotary_refinement/axle_review.json'),('Coarse replacement','printed_fasteners/print_review.json')]:
        r=json.loads((ROOT/'notes'/report).read_text());g=Path(r['slice']['kept_run_directory'])/'plate_1.gcode'
        sources.append((label,r,g,list(orca_linear_paths(g))))
    sample=[v for v in sources[1][3] if v[-1]=='Outer wall' and abs(v[4]-1.2)<1e-5 and max(v[0],v[2])<135]
    xs=[v[i] for v in sample for i in (0,2)];ys=[v[i] for v in sample for i in (1,3)]
    centres=[(135.,135.),((min(xs)+max(xs))/2,(min(ys)+max(ys))/2)]
    colors={'Outer wall':'#153a53','Inner wall':'#39a1c9','Internal solid infill':'#d7771b','Sparse infill':'#cc3161','Overhang wall':'#9359a6'}
    fig,axes=plt.subplots(2,3,figsize=(11,7.5));evidence=[]
    for row,(label,report,g,paths) in enumerate(sources):
        x,y=centres[row];samples=[]
        for col,z in enumerate((1.2,2.8,6.)):
            ax=axes[row,col]
            local=[v for v in paths if abs(v[4]-z)<1e-5 and not v[-1].startswith(('Support','Brim')) and max(v[0],v[2])<x+7]
            for a,b,c,d,zz,width,role in local:ax.plot([a-x,c-x],[b-y,d-y],color=colors.get(role,'#777'),linewidth=width*8,solid_capstyle='round')
            coverage=section_coverage(local,x_mm=x,z_mm=z,span_mm=(y-.8,y+.8))
            if row==1:assert coverage['uncovered_width_mm']<.01,(z,coverage)
            samples.append(dict(z_mm=z,centre_span_mm=1.6,coverage=coverage,roles=dict(Counter(v[-1] for v in local))))
            ax.set(xlim=(-5,5),ylim=(-5,5),aspect='equal',title=f'{label}\nZ {z:g} mm');ax.set_xlabel('mm from axle centre');ax.grid(alpha=.2)
        evidence.append(dict(label=label,input_stl_sha256=report['slice']['input_sha256'],gcode_sha256=hashlib.sha256(g.read_bytes()).hexdigest(),centre_xy_mm=[x,y],samples=samples))
    fig.suptitle('Actual toolpaths: head, shoulder and thread\nOrange = solid infill; pink = sparse infill. CAD hole remains empty regardless of infill.')
    fig.tight_layout();fig.savefig(OUT/'core_paths.svg');fig.savefig(OUT/'core_paths.png',dpi=140);plt.close(fig)
    (NOTES/'core_paths.json').write_text(json.dumps(dict(scope='Selected-profile local core paths; not deposited density or strength',comparison=evidence),indent=2)+'\n')
    for path in OUT.glob('*.svg'):
        path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
    print('Saved actual CAD sections and old/new core path evidence')


if __name__=='__main__':main()
