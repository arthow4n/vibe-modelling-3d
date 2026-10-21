"""Review actual B08 and adaptive skin/joint probes under Classic processes.

No geometry construction or slicing. Uses the shared deposited-move parser;
centerlines and geometric track counts are not strings, retractions or strength.
"""
from collections import Counter
from dataclasses import replace
import gzip
import json
from math import hypot
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Patch
from execution.identity import digest
from physical_analysis.manufacturing import orca_linear_paths, section_coverage
import tie_surface_design as design
import n2_surface_design as n2

ROOT = Path(__file__).resolve().parent
NOTES = ROOT / 'notes/tie_surface_study'
VIEWS = ROOT / 'renders/concepts'
PROFILES = {'P2': ('2', 'inner wall/outer wall'), 'P3': ('3', 'inner wall/outer wall'),
            'P3IOI': ('3', 'inner-outer-inner wall')}
COLORS = {'Outer wall': '#2466b0', 'Inner wall': '#475569', 'Gap infill': '#c52d66',
          'Internal solid infill': '#cf711c', 'Bottom surface': '#cf711c',
          'Top surface': '#cf711c', 'Bridge': '#943c9d', 'Internal Bridge': '#943c9d',
          'Sparse infill': '#cf711c', 'Overhang wall': '#73823e'}
LAYERS = (2.8, 3., 3.2, 3.4, 3.6, 4.4)
JOBS = {
    **{n: ('tie_surface_study', n, design.INITIAL_NAMES, f'{n}_review.json') for n in PROFILES},
    **{f'R_{n}': ('tie_surface_refined', n, design.REFINED_NAMES, f'refined_{n}_review.json') for n in ('P2','P3IOI')},
    'WF13': ('tie_surface_n2_blend','P2',n2.NAMES,'n2_blend_review.json'),
}


def case_variant(name):
    return replace(design.variant_named('W13'), name=name, joint=('blended continuous' if name == 'WF13' else 'native continuous')) if name in n2.NAMES else design.variant_named(name)


def case_placement(name):
    return n2.position(name) if name in n2.NAMES else design.placement(name)


def layer(paths, z):
    found = [p for p in paths if abs(p[4]-z) < 1e-5]
    if not found:
        raise ValueError(f'Missing deposited layer {z}')
    return found


def track_details(paths, z, skin):
    """Distinct single G1 straight tracks covering the central 20 mm of skin."""
    found = []
    for x, y, nx, ny, _, width, role in layer(paths, z):
        if abs(y-ny) > 1e-5 or not (0 < y < skin):
            continue
        if min(x, nx) > -10 or max(x, nx) < 10:
            continue
        if not any(abs(y-row['y_mm']) < 1e-5 for row in found):
            found.append({'y_mm': y, 'width_mm': width, 'role': role})
    return sorted(found, key=lambda row: row['y_mm'])


def tracks(paths, z, skin):
    return [row['y_mm'] for row in track_details(paths,z,skin)]


def roles_and_lengths(paths, z):
    result = Counter()
    for x, y, nx, ny, _, width, role in layer(paths, z):
        result[role] += hypot(nx-x, ny-y)
    return dict(result)


def draw(ax, paths, v, z, *, xlim=(-5.5, 5.5)):
    selected = layer(paths, z)
    ax.axhspan(0, v.skin, color='#eaf1f8')
    ax.axhspan(v.skin+v.core, v.depth, color='#eaf1f8')
    for role in dict.fromkeys(p[-1] for p in selected):
        moves = [p for p in selected if p[-1] == role]
        ax.add_collection(LineCollection([[(p[0], p[1]), (p[2], p[3])] for p in moves],
                          colors=COLORS[role], linewidths=1.1))
    ax.set(xlim=xlim, ylim=(-.18, v.depth+.18), aspect='equal',
           ylabel='through wall / mm')
    ax.grid(alpha=.12)


def save(fig, name):
    svg = VIEWS / f'{name}.svg'
    fig.savefig(svg)
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    fig.savefig(VIEWS / f'{name}.png', dpi=130)
    plt.close(fig)


def main():
    plt.rcParams.update({'svg.fonttype': 'none', 'font.size': 10})
    data, findings = {}, {}
    geometry = json.loads((NOTES/'geometry.json').read_text())
    if not geometry['geometry']['valid'] or not all(x['ok'] for x in geometry['exports']):
        raise ValueError('No successful current proxy export receipt')
    for name, (model, process, case_names, report) in JOBS.items():
        loops, sequence = PROFILES[process]
        geometry_name = {'tie_surface_study':'geometry.json','tie_surface_refined':'refined_geometry.json',
                         'tie_surface_n2_blend':'n2_blend_geometry.json'}[model]
        model_geometry = json.loads((NOTES/geometry_name).read_text())
        if not model_geometry.get('ok') or not model_geometry['geometry']['valid']:
            raise ValueError(f'{name}: no successful native geometry receipt')
        native = json.loads((NOTES/report).read_text())['slice']
        if not native['ok'] or native['input_sha256'] != digest(ROOT/f'{model}.stl'):
            raise ValueError(f'{name}: missing or stale STL slice')
        run = Path(native['kept_run_directory'])
        if digest(run/'input.stl') != native['input_sha256']:
            raise ValueError(f'{name}: raw slice input mismatch')
        if digest(run/'process.json') != digest(NOTES/f'{process}_process.json'):
            raise ValueError(f'{name}: raw process mismatch')
        settings = json.loads((run/'effective-settings.json').read_text())
        expected = {'wall_generator': 'classic', 'wall_loops': loops, 'wall_sequence': sequence,
                    'layer_height': '0.2', 'detect_thin_wall': '0', 'enable_support': '0',
                    'outer_wall_line_width': '0.42', 'inner_wall_line_width': '0.45',
                    'sparse_infill_density': '100%'}
        if any(settings[k] != val for k, val in expected.items()):
            raise ValueError(f'{name}: unexpected effective settings')
        raw = run/'plate_1.gcode'
        paths = list(orca_linear_paths(raw))
        unknown = set(p[-1] for p in paths)-COLORS.keys()
        if unknown:
            raise ValueError(f'Unmapped printed roles {unknown}')
        (NOTES/f'{name}_paths.gcode.gz').write_bytes(gzip.compress(raw.read_bytes(), mtime=0))
        cases = {}
        data[name] = {}
        for case_name in case_names:
            v = case_variant(case_name)
            cx, cy = case_placement(v.name)
            local = [(x-cx,y-cy,nx-cx,ny-cy,z,w,r) for x,y,nx,ny,z,w,r in paths
                     if abs((x+nx)/2-cx) < design.LENGTH/2+.5 and -.5 < (y+ny)/2-cy < v.depth+.5]
            if not local:
                raise ValueError(f'{name}/{v.name}: absent probe')
            core_section = None
            if v.joint == 'straight':
                core_section = section_coverage(local,x_mm=0,z_mm=3.,span_mm=(v.skin,v.skin+v.core))
                if core_section['uncovered_width_mm'] > .06:
                    raise ValueError(f'{name}/{v.name}: first tie row does not span the core in sliced paths')
            data[name][v.name] = local
            cases[v.name] = {'skin_mm': v.skin, 'gap_mm': v.core, 'joint': v.joint, 'straight_tie_core_section': core_section,
                            'layers': {str(z): {'straight_skin_tracks_y_mm': tracks(local,z,v.skin),
                            'straight_skin_track_details': track_details(local,z,v.skin),
                            'deposited_length_mm_by_role': roles_and_lengths(local,z)} for z in LAYERS}}
        findings[name] = {'gcode_sha256': digest(raw), 'input_stl_sha256': native['input_sha256'],
                          'process_sha256': digest(NOTES/f'{process}_process.json'), 'model_stem': model, 'native_receipt': report, 'process_file': f'{process}_process.json',
                          'effective_settings': {k: settings[k] for k in expected},
                          'slicer_version': native['slicer_version'],
                          'support_probe': native['support_probe'], 'notices': native['log_notices'],
                          'cases': cases}
    # Reuse exact retained B08 geometry/profile evidence, not a newly invented baseline.
    receipt = json.loads((ROOT/'notes/support_B08_final.json').read_text())['slice']
    old = json.loads((ROOT/'notes/b_existing_routes.json').read_text())['variants']['B08']
    raw = Path(receipt['kept_run_directory'])/'plate_1.gcode'
    if digest(raw) != old['gcode_sha256'] or digest(ROOT/'support_B08.stl') != receipt['input_sha256']:
        raise ValueError('Retained approved B08 association changed')
    original = [(y-135., -15.4-(x-114.35), ny-135., -15.4-(nx-114.35), z,w,r)
                for x,y,nx,ny,z,w,r in orca_linear_paths(raw)
                if -17.05 < (x+nx)/2-114.35 < -15.35 and abs((y+ny)/2-135) < 15.]
    (NOTES/'approved_B08_paths.gcode.gz').write_bytes(gzip.compress(raw.read_bytes(),mtime=0))
    baseline = {'native_receipt': '../support_B08_final.json', 'gcode_sha256': digest(raw),
                'input_stl_sha256': receipt['input_sha256'],
                'straight_skin_tracks_y_mm': {str(z): tracks(original,z,.5) for z in (3.,4.4)},
                'straight_skin_track_details': {str(z): track_details(original,z,.5) for z in (3.,4.4)},
                'local_transform': 'tangent=rawY-135; normal=-15.4-(rawX-114.35); left wall only'}
    legend = [Patch(color=COLORS[r], label=r) for r in ('Outer wall','Inner wall','Gap infill','Internal solid infill','Bridge')]
    fig, axes = plt.subplots(3,3,figsize=(15,10))
    for row, case in enumerate(('T05','T09','T13')):
        v = design.variant_named(case)
        for col, process in enumerate(PROFILES):
            draw(axes[row,col],data[process][case],v,3.)
            count = len(tracks(data[process][case],3.,v.skin))
            axes[row,col].set_title(f'{case}: {v.skin:.1f} mm skin / {process}\n{count} straight 20 mm skin track(s)',fontsize=10)
            if row==2: axes[row,col].set_xlabel('along wall / mm')
    fig.suptitle('ACTUAL Classic paths at tie row Z 3.0 mm — increase skin material versus wall-loop setting\n'
                 'P2: 2 loops | P3: 3 loops | P3IOI: 3 loops + Inner/Outer/Inner\n'
                 'Blue-grey tint = solid skins in CAD. Line colours = slicer roles; all TPU black. Travels omitted.',fontsize=13)
    fig.legend(handles=legend,loc='lower center',ncol=5,fontsize=9)
    fig.subplots_adjust(left=.06,right=.985,bottom=.10,top=.79,hspace=.80,wspace=.23)
    save(fig,'tie_skin_paths')
    fig, axes = plt.subplots(4,2,figsize=(13,15))
    for row, case in enumerate(('T13','R13','C13','W13')):
        v = design.variant_named(case)
        for col,z in enumerate((3.,4.4)):
            draw(axes[row,col],data['P3'][case],v,z)
            axes[row,col].set_title(f'{case} / {v.joint} / Z {z:.1f} mm',fontsize=11)
            if row==3: axes[row,col].set_xlabel('along wall / mm')
    fig.suptitle('ACTUAL Classic paths: straight, rounded-root, swept ties and full-height N2 web\n'
                 'All skins 1.3 mm / P3. T/R/C gap 0.6 mm; W13 gap 2.4 mm.\n'
                 'Left: discrete ties active. Right: between tie rows (W13 remains continuous).\n'
                 'Pink = gap fill, blue/grey = walls, orange = solid fill. These are centerlines, not measured polymer.',fontsize=13)
    fig.legend(handles=legend,loc='lower center',ncol=5,fontsize=9)
    fig.subplots_adjust(left=.07,right=.985,bottom=.08,top=.85,hspace=.55,wspace=.20)
    save(fig,'tie_curve_paths')
    fig, axes = plt.subplots(2,1,figsize=(13,6))
    v = design.variant_named('T05')
    for ax,z in zip(axes,(3.,4.4)):
        draw(ax,original,v,z,xlim=(-6.5,6.5))
        ax.set_title(f'Approved B08 actual left wall / Z {z:.1f} mm / '+('ties present' if z==3. else 'between ties'))
    axes[-1].set_xlabel('along wall / mm')
    fig.suptitle('EXISTING B08 slice: 0.5 mm skins / 0.6 mm gap / 0.8 mm ties\n'
                 'Visible face at normal 0 mm; no new geometry or profile. Its outer path already stays straight.\n'
                 'Blue = outer walls; tint = CAD skins. All TPU black. Physical defect cause remains unconfirmed.',fontsize=12)
    fig.subplots_adjust(left=.08,right=.985,bottom=.13,top=.69,hspace=.85)
    save(fig,'approved_B08_joint_paths')
    fig, axes = plt.subplots(5,2,figsize=(13,17))
    for row, case in enumerate(design.REFINED_NAMES):
        v = case_variant(case)
        for col,z in enumerate((3.,4.4)):
            draw(axes[row,col],data['R_P2'][case],v,z)
            details = track_details(data['R_P2'][case],z,v.skin)
            label = ', '.join(f"{r['width_mm']:.3f} {r['role']}" for r in details)
            axes[row,col].set_title(f'{case} / {v.skin:.1f} mm skin / Z {z:.1f} mm\n'+label,fontsize=9)
            if row==4: axes[row,col].set_xlabel('along wall / mm')
    fig.suptitle('ADAPTIVE Classic study / original P2 settings / actual deposition\n'
                 '0.8 and 1.2 mm skins; straight, rounded and swept ties at 1.6 mm.\n'
                 'Left: first tie layer. Right: between rows. Gap fill is listed separately from normal walls.',fontsize=13)
    fig.legend(handles=legend,loc='lower center',ncol=5,fontsize=9)
    fig.subplots_adjust(left=.07,right=.985,bottom=.07,top=.87,hspace=.55,wspace=.23)
    save(fig,'tie_refined_paths')
    fig, axes = plt.subplots(1,2,figsize=(13,5))
    for ax, label, rows in zip(axes,('WN13: tangent centreline, unblended union','WF13: actual cavity roots blended R0.25'),
                                (data['WF13']['WN13'],data['WF13']['WF13'])):
        draw(ax,rows,design.variant_named('W13'),3.,xlim=(-3.5,3.5))
        ax.set_title(label,fontsize=11); ax.set_xlabel('along wall / mm')
    fig.suptitle('N2 root refinement / actual P2 Classic paths at Z 3.0 mm\n'
                 'Same 1.3 mm skins, 2.4 mm gap and continuous web. Only the cavity-corner blend changes.\n'
                 'Tint = CAD skins; line colours = slicer roles below. All TPU black.',fontsize=12)
    fig.legend(handles=legend,loc='lower center',ncol=5,fontsize=9)
    fig.subplots_adjust(left=.07,right=.985,bottom=.17,top=.74,wspace=.23)
    save(fig,'n2_blended_paths')
    fig, axes = plt.subplots(3,2,figsize=(13,10))
    choices = (('T05','P2','Original-sized skin'),('T12','R_P2','Compact candidate'),('T16','R_P2','Normal-perimeter comparison'))
    for row,(case,job,label) in enumerate(choices):
        v = case_variant(case)
        for col,z in enumerate((3.,4.4)):
            draw(axes[row,col],data[job][case],v,z)
            axes[row,col].set_title(f'{label}: {v.skin:.1f} mm PER SKIN / {v.depth:.1f} mm total / Z {z:.1f}',fontsize=10)
            if row==2: axes[row,col].set_xlabel('along wall / mm')
    fig.suptitle('Keep the discrete ties; change the skin first — actual ordinary Classic paths\n'
                 'Left: tie layer. Right: between rows. All gaps 0.6 mm; original P2 settings.\n'
                 'Blue = outer walls, grey = inner walls, pink = gap fill. Tint = CAD skins. All TPU black.\n'
                 'Contents-side face is Y=0; backing is at the top. No T12/T16 physical results; damping remains unknown.',fontsize=12)
    fig.legend(handles=legend,loc='lower center',ncol=5,fontsize=9)
    fig.subplots_adjust(left=.065,right=.985,bottom=.10,top=.77,hspace=.70,wspace=.23)
    save(fig,'tie_recommendation_paths')
    fig, axes = plt.subplots(1,2,figsize=(11,5))
    for ax,label,rows,skin in zip(axes,('Retained B08: 0.5 mm skin','T08 control: 0.8 mm skin'),
                                 (track_details(original,4.4,.5),track_details(data['R_P2']['T08'],4.4,.8)),(.5,.8)):
        ax.add_patch(plt.Rectangle((0,.12),skin,.66,facecolor='#f2f5f8',edgecolor='#183247',lw=1.5))
        for row,color in zip(rows,('#2466b0','#475569')):
            ax.add_patch(plt.Rectangle((row['y_mm']-row['width_mm']/2,.22),row['width_mm'],.46,
                                      facecolor=color,alpha=.32))
            ax.plot((row['y_mm'],row['y_mm']),(.17,.74),color=color,lw=2)
        spacing = rows[1]['y_mm']-rows[0]['y_mm']
        overlap = (rows[0]['width_mm']+rows[1]['width_mm'])/2-spacing
        ax.set_title(label+f'\nCenter spacing {spacing:.2f} mm / nominal overlap {overlap:.2f} mm',fontsize=11)
        ax.set(xlim=(-.05,.92),ylim=(0,.9),xlabel='through skin / mm',yticks=[])
        ax.grid(axis='x',alpha=.15)
    fig.suptitle('Width/position metadata from actual Classic paths BETWEEN ties (Z 4.4 mm)\n'
                 'Two 0.42 mm passes: coloured bands show nominal width, vertical lines their centres.\n'
                 'All TPU black. This is an end-on width diagram, not measured deposited bead shape.',fontsize=12)
    fig.text(.5,.035,'The 0.8 mm control reduces nominal overlap; T12/T16 separately address the extra straight track at tie joints.',ha='center',fontsize=10)
    fig.subplots_adjust(left=.07,right=.985,bottom=.17,top=.69,wspace=.26)
    save(fig,'b08_nominal_skin_overlap')
    output = {'category': 'diagnostic-tie-skin-path-study', 'baseline': baseline,
              'variants': findings, 'geometry_receipt': 'geometry.json',
              'source_sha256': {p:digest(ROOT/p) for p in ('tie_surface_study.py','tie_surface_refined.py','tie_surface_n2_blend.py','n2_surface_design.py','tie_surface_design.py','review_tie_surface_study.py')},
              'track_definition': 'Distinct horizontal single deposition moves spanning X -10 to +10 mm within the contact-side CAD skin. Not seam/travel/string counts.',
              'limits': 'Straight 34 mm-high wall probes, not full cups, lid/floor construction, print qualification or damping evidence.'}
    (NOTES/'paths.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({p:{n:{str(z):len(row['straight_skin_tracks_y_mm']) for z,row in c['layers'].items() if z in ('3.0','4.4')}
                        for n,c in r['cases'].items()} for p,r in findings.items()},indent=2))


if __name__ == '__main__':
    main()
