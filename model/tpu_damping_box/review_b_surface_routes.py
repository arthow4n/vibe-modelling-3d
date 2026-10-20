"""Explain retained B routes; no construction, slicing or profile mutation.

Chains are geometric endpoint discontinuities (>0.005 mm), not measured
retraction/seam events. Raw slices remain the setup-specific source evidence.
"""
import json
from pathlib import Path
from math import dist
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from execution.identity import digest
from physical_analysis.manufacturing import orca_linear_paths
from review_support_paths import local_paths

ROOT = Path(__file__).resolve().parent


def main():
    plt.rcParams['svg.fonttype'] = 'none'
    fig,axes = plt.subplots(2,2,figsize=(12,12))
    records = {}
    for row,name in enumerate(('B08','B16')):
        receipt = json.loads((ROOT/f'notes/support_{name}_final.json').read_text())
        review = json.loads((ROOT/'notes/support_path_review.json').read_text())['variants'][name]
        run = Path(receipt['slice']['kept_run_directory'])
        gcode = run/'plate_1.gcode'
        assert digest(gcode)==review['gcode_sha256']
        assert digest(ROOT/f'support_{name}.stl')==receipt['slice']['input_sha256']
        assert receipt['reuse']['artifact_identity']==review['artifact_identity']
        assert all(digest(ROOT/p)==sha for p,sha in review['source_sha256'].items())
        settings = json.loads((run/'effective-settings.json').read_text())
        paths = local_paths(orca_linear_paths(gcode),114.35,135,34)
        layers = []
        for col,z in enumerate((3.,4.4)):
            selected = [p for p in paths if abs(p[4]-z)<1e-5]
            assert selected
            chains = []
            for p in selected:
                if not chains or dist(chains[-1][-1][2:4],p[:2])>.005:
                    chains.append([])
                chains[-1].append(p)
            full_contours = []
            for chain in chains:
                xs = [p[i] for p in chain for i in (0,2)]
                ys = [p[i] for p in chain for i in (1,3)]
                if max(xs)-min(xs)>30 and max(ys)-min(ys)>30:
                    full_contours.append({'role':chain[0][-1],
                        'start_mm':chain[0][:2], 'closed_to_mm':dist(chain[0][:2],chain[-1][2:4])})
            ax = axes[row,col]
            ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in selected],
                colors='#2367b1',linewidths=.8))
            starts = [c[0][:2] for c in chains]
            ax.scatter([p[0] for p in starts],[p[1] for p in starts],c='#c25e24',s=14,zorder=3)
            for before,after in zip(chains,chains[1:]):
                a,b = before[-1][2:4],after[0][:2]
                ax.plot((a[0],b[0]),(a[1],b[1]),'--',color='#c25e24',lw=.6,alpha=.5)
            ax.set(xlim=(-18,18),ylim=(-18,18),aspect='equal',xlabel='cup X / mm',ylabel='cup Y / mm')
            ax.set_title(f'{name} / Z {z:.1f} mm / {len(chains)} disconnected chains\n'+
                         ('tie row present' if col==0 else 'between tie rows'))
            layers.append({'z_mm':z,'deposition_segments':len(selected),'disconnected_chains':len(chains),
                           'full_width_contours':full_contours})
        records[name] = {'gcode_sha256':digest(gcode),'input_stl_sha256':digest(ROOT/f'support_{name}.stl'),
            'native_receipt':f'notes/support_{name}_final.json',
            'effective_settings':{k:settings[k] for k in ('wall_generator','detect_thin_wall',
                'reduce_crossing_wall','seam_position','seam_gap','wall_loops','outer_wall_line_width',
                'inner_wall_line_width','retraction_length','retraction_minimum_travel','wipe')},
            'layers':layers}
    fig.suptitle('Existing B slices only — ordinary Classic, 0.2 mm layers\n'
                 'Blue: deposited centerlines | orange: chain starts and straight endpoint links (not actual travel routes)',fontsize=12)
    fig.tight_layout(rect=(0,0,1,.94))
    svg = ROOT/'renders/concepts/b_existing_routes.svg'
    fig.savefig(svg)
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    fig.savefig(ROOT/'renders/concepts/b_existing_routes.png',dpi=120)
    result = {'category':'retained-slicer-route-inspection','new_slice':False,
        'limits':'Centerline endpoint links are illustrative, not actual travels, seam counts or physical artifacts. '
                 'Two selected layers of existing slices, excluding pad and inter-part moves. Actual user settings unknown.',
        'chain_break_tolerance_mm':.005,'source_sha256':{p:digest(ROOT/p) for p in
            ('review_b_surface_routes.py','review_support_paths.py','../../physical_analysis/manufacturing.py')},
        'variants':records}
    (ROOT/'notes/b_existing_routes.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({n:r['layers'] for n,r in records.items()},indent=2))


if __name__=='__main__':
    main()
