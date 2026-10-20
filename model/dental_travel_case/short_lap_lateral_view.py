"""Inspect an accepted half-X native frame at its actual mirror cut.

This is a deformed FE section, not a new CAD model or physical validation.
Quadratic surface faces are displayed as four triangles through their midsides.
"""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from physical_analysis.backends.worker import iter_dat, saved_meshes

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'notes/short_lap'


def accepted_times(path):
    times = []
    for line in path.read_text().splitlines():
        fields = line.split()
        if len(fields) == 7 and all(v.isdigit() for v in fields[:4]):
            times.append(float(fields[4]))
    return times


def read_frame(directory, fraction):
    if fraction not in accepted_times(directory/'analysis.sta'):
        raise ValueError('Choose a recorded accepted load fraction')
    case = json.loads((directory/'case.json').read_text())
    metadata = json.loads((directory/'run_metadata.json').read_text())
    for field,name in (('input_sha256','analysis.inp'),('case_sha256','case.json')):
        if metadata[field] != hashlib.sha256((directory/name).read_bytes()).hexdigest():
            raise ValueError('Frozen native identity changed')
    meshes = saved_meshes(case,directory/'analysis.inp')
    nodes = {n:p for mesh in meshes.values() for n,p in mesh['nodes'].items()}
    frame = next((frame for time,frame in iter_dat(directory/'analysis.dat')
                  if abs(time-fraction) < 1e-8),None)
    if frame is None or not all(field in frame for field in
            ('displacements','forces','stresses','strains','relative contact displacement','contact stress')):
        raise ValueError('The requested complete output frame is not available')
    gaps,pressures = frame['relative contact displacement'],frame['contact stress']
    if len(gaps) != len(pressures) or any(g[:2] != p[:2] for g,p in zip(gaps,pressures)):
        raise ValueError('Incomplete or differently ordered native contact fields')
    displacements = {int(row[0]):np.array(row[1:]) for row in frame['displacements']}
    if set(displacements) != set(nodes) or not all(np.isfinite(v).all() for v in displacements.values()):
        raise ValueError('Incomplete or non-finite displacement field')
    return case,metadata,meshes,frame,displacements


def view(stage, fraction):
    if stage not in ('seated','pickup','targeted_v2'):
        raise ValueError(stage)
    directory = OUT/'native'/f'lateral_{stage}_x'/'baseline'
    case,metadata,meshes,frame,displacements = read_frame(directory,fraction)
    nodes = {n:p for mesh in meshes.values() for n,p in mesh['nodes'].items()}
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    fig,axes = plt.subplots(1,3,figsize=(12,6),gridspec_kw={'width_ratios':[1.7,1,1]})
    for part,color in (('body','#4187b5'),('part','#e49b43')):
        triangles = []
        for _,_,ids in meshes[part]['surface']:
            if not all(abs(nodes[n][1]) < 1e-6 for n in ids):
                continue
            points = np.array([nodes[n]+displacements[n] for n in ids])[:,[0,2]]
            triangles.extend(points[list(tri)] for tri in ((0,3,5),(3,1,4),(5,4,2),(3,4,5)))
        if not triangles:
            raise ValueError('Missing actual mirror-cut triangles')
        for ax in axes:
            ax.add_collection(PolyCollection(triangles,facecolor=color,edgecolor='none',alpha=.9))
    for ax in axes:
        ax.set_aspect('equal')
        ax.set_xlabel('X (mm)')
        ax.grid(alpha=.2)
    axes[0].set(xlim=(-40,48),ylim=(155,268),ylabel='Z (mm)',title='Complete cap and clamped body crop')
    axes[1].set(xlim=(-38,-29),ylim=(194,207),title='Negative-X bite')
    axes[2].set(xlim=(29,38),ylim=(194,207),title='Positive-X bite')
    penetration = max((max(0.,-row[2]) for row in frame['relative contact displacement']),default=0.)
    motion = json.loads((directory/'regions.json').read_text())['lateral']
    progress = np.asarray(motion['progress'])
    drive = motion['displacement_mm'][0]*float(np.interp(fraction,progress[:,0],progress[:,1]))
    drive += .1 if stage == 'pickup' else 0.
    title = (f'Accepted FE frame: lateral roof drive {drive:.4g} mm; axial roof DOF free\n'
             f'Blue: body; orange: cap. Native maximum penetration {penetration:.4g} mm; quality not inferred from image.')
    fig.suptitle(title,fontsize=11)
    fig.tight_layout(rect=(0,0,1,.91))
    stem = OUT/f'lateral_{stage}_x_{fraction:g}'
    for suffix in ('.svg','.png'):
        fig.savefig(str(stem)+suffix,dpi=180)
    svg = Path(str(stem)+'.svg')
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    print(json.dumps(dict(frame=fraction,figure=str(stem),max_penetration_mm=penetration)))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Use seated|pickup|targeted_v2 ACCEPTED_FRACTION')
    view(sys.argv[1],float(sys.argv[2]))
