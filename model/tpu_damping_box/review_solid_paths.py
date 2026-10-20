"""Review solid controls with ordinary Classic; path metadata is not strength.

Retained R1/R2 evidence owns the missing-wall negative control. Here the CAD
is solid; every upright layer must retain a continuous full-thickness section.
"""
import json
from pathlib import Path
from collections import defaultdict
from math import cos, sin, pi
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from execution.identity import digest
from physical_analysis.manufacturing import orca_linear_paths, section_coverage
from review_support_paths import local_paths
import solid_design as d

ROOT = Path(__file__).resolve().parent
MARGIN = .06  # Same bounded path rounding allowance as the R2 review.


def main():
    fig,axes = plt.subplots(2,3,figsize=(12,8))
    results = {}
    for row,name in enumerate(d.NAMES):
        v = d.variant_named(name)
        native = json.loads((ROOT/f'notes/solid_{name}_final.json').read_text())
        assert native['slice']['ok']
        assert native['slice']['input_sha256']==digest(ROOT/f'solid_{name}.stl')
        run = Path(native['slice']['kept_run_directory'])
        settings = json.loads((run/'effective-settings.json').read_text())
        expected = {'wall_generator':'classic','detect_thin_wall':'0',
            'sparse_infill_density':'100%','outer_wall_line_width':'0.42',
            'inner_wall_line_width':'0.45','layer_height':'0.2','enable_support':'0'}
        for key,value in expected.items():
            assert settings[key]==value,(name,key,settings[key])
        # Whole-layout centering preserves the same relative component placement.
        shift = 135-(3+62+v.pad_size/2)/2
        paths = list(orca_linear_paths(run/'plate_1.gcode'))
        cups = local_paths(paths,20+shift,135,34)
        pads = local_paths(paths,62+shift,135,v.pad_size)
        layers = defaultdict(list)
        for p in cups: layers[round(p[4],3)].append(p)
        first,last = round(v.thickness+.2,3),round(v.wall_height,3)
        zs = [round(first+.2*i,3) for i in range(round((last-first)/.2)+1)]
        faces = []
        for angle in (0,90,180,270):
            c,s = cos(angle*pi/180),sin(angle*pi/180)
            widths = []
            for z in zs:
                assert z in layers,(name,'missing upright layer',z)
                swapped = [(-s*x+c*y,c*x+s*y,-s*nx+c*ny,c*nx+s*ny,h,w,r)
                           for x,y,nx,ny,h,w,r in layers[z]]
                for tangent in (-11.,-6.6,-2.2,2.2,6.6,11.):
                    sec = section_coverage(swapped,x_mm=tangent,z_mm=z,
                                           span_mm=(-17,-17+v.thickness))
                    assert len(sec['intervals_mm'])==1,(name,z,angle,tangent,'hollow/missing wall',sec)
                    assert sec['filled_width_mm']>=v.thickness-MARGIN,(name,z,angle,tangent,sec)
                    widths.append(sec['filled_width_mm'])
            faces.append({'face_deg':angle,'layers':len(zs),'z_range_mm':[first,last],
                'tangent_samples_per_layer':6,'minimum_continuous_material_mm':min(widths)})
        for col,(part,z,title) in enumerate(((cups,.2,'cup ID / underside'),
                                              (cups,10.,'solid walls / Z10'),
                                              (pads,.2,'pad ID / underside'))):
            selected = [p for p in part if abs(p[4]-z)<1e-5]
            assert selected,(name,title,'no paths')
            ax = axes[row,col]
            ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in selected],
                colors='#2367b1',linewidths=.6))
            ax.set_xlim(18,-18) if col!=1 else ax.set_xlim(-18,18)
            ax.set_ylim(-18,18);ax.set_aspect('equal');ax.set_xticks([]);ax.set_yticks([])
            ax.set_title(f'{name} / {title}')
        sources = ('design.py','support_design.py','solid_design.py',f'solid_{name}.py',
            'review_solid_paths.py','review_support_paths.py','../../physical_analysis/manufacturing.py',
            'profiles/tpu-support-classic-process.json','profiles/tpu95a.json',
            '../../.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json')
        results[name] = {'checks_passed':True,'artifact_identity':native['reuse']['artifact_identity'],
            'source_sha256':{n:digest(ROOT/n) for n in sources},
            'export_sha256':{f'solid_{name}.{ext}':digest(ROOT/f'solid_{name}.{ext}') for ext in ('step','stl')},
            'effective_process':expected,'wall_continuity':faces,
            'gcode_sha256':digest(run/'plate_1.gcode')}
    fig.suptitle('Solid C controls • actual Classic paths • 100% material fill')
    fig.tight_layout();fig.savefig(ROOT/'renders/solid_path_review.png',dpi=150)
    report = {'category':'slicer-path-metadata','limits':'No physical fit, deposited solidity or damping claim.',
              'rounding_allowance_mm':MARGIN,'variants':results}
    (ROOT/'notes/solid_path_review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({n:r['wall_continuity'] for n,r in results.items()},indent=2))


if __name__=='__main__':
    main()
