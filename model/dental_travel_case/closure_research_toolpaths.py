"""Inspect the slider's new 1.2mm rail necks, not a generic slice audit."""
import hashlib
import json
from pathlib import Path
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from physical_analysis.manufacturing import orca_linear_paths,section_coverage

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/closure_research'


def inspect(directory):
    receipt=json.loads((OUT/'slide_wall_slice.json').read_text())
    assert directory.resolve()==Path(receipt['slice']['kept_run_directory']).resolve()
    path=directory/'plate_1.gcode'
    paths=list(orca_linear_paths(path))
    # Native layout X centres 0/110; centring at 135 gives +80. The flipped
    # lid's Y35 section becomes printerY135. Swap X/Y for the existing reader.
    swapped=[(y,x,ny,nx,z,w,r) for x,y,nx,ny,z,w,r in paths]
    sections={};fig,axes=plt.subplots(1,2,figsize=(10,3),layout='constrained')
    for ax,(name,span) in zip(axes,(('left',(154.95,156.15)),('right',(223.85,225.05)))):
        coverage=section_coverage(swapped,x_mm=135,z_mm=2.2,span_mm=span)
        crossings=set()
        for x,y,nx,ny,z,width,role in paths:
            if abs(z-2.2)>1e-5 or min(y,ny)>135 or max(y,ny)<135 or abs(ny-y)<1e-9:continue
            at=x+(nx-x)*(135-y)/(ny-y)
            if span[0]-.3<=at<=span[1]+.3:
                crossings.add(round(at,5))
                ax.plot([x,nx],[y,ny],lw=width*5,label=role)
        coverage['path_centres_crossing_mm']=sorted(crossings)
        assert len(crossings)>=2,'Thin neck has fewer than two crossing paths'
        ax.set(xlim=(span[0]-.4,span[1]+.4),ylim=(130,140),title=name+' rail neck at Z2.2',xlabel='Printer X (mm)',ylabel='Printer Y (mm)')
        sections[name]=coverage
    fig.savefig(OUT/'rail_paths.svg')
    vector=OUT/'rail_paths.svg'
    vector.write_text('\n'.join(line.rstrip() for line in vector.read_text().splitlines())+'\n')
    fig.savefig(OUT/'rail_paths.png',dpi=140);plt.close(fig)
    answer=dict(scope='Specific current-profile rail-neck paths/width approximation; no deposited material or strength calibration.',
        producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        STL_sha256=receipt['slice']['input_sha256'],gcode_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        layer_mm=2.2,section_printer_Y_mm=135,sections=sections)
    (OUT/'rail_paths.json').write_text(json.dumps(answer,indent=2)+'\n')
    print(json.dumps(answer))


if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Usage: closure_research_toolpaths.py RETAINED_SLIDER_SLICE_DIRECTORY')
    inspect(Path(sys.argv[1]))
