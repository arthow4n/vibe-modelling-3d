"""Render actual deposited paths from the three N1 diagnostic slices.

Run with ./execute.py model/tpu_damping_box/review_infill_study.py.
Reads native receipts, checks input/process identity and archives the raw G-code.
No construction or slicing; colors are slicer roles, not different materials.
"""
from collections import Counter
import gzip
import json
from math import hypot
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D

from execution.identity import digest
from physical_analysis.manufacturing import orca_linear_paths

ROOT = Path(__file__).resolve().parent
STUDY = ROOT / 'notes/infill_study'
VIEWS = ROOT / 'renders/concepts'
CONFIGS = {'G20': ('gyroid', '20%'), 'G30': ('gyroid', '30%'), 'X20': ('crosshatch', '20%')}
COLORS = {'Outer wall': '#2466b0', 'Inner wall': '#475569', 'Sparse infill': '#cf711c',
          'Bridge': '#943c9d', 'Internal Bridge': '#943c9d', 'Top surface': '#943c9d',
          'Internal solid infill': '#943c9d', 'Bottom surface': '#943c9d', 'Gap infill': '#399477'}
KEYS = ('wall_generator', 'wall_loops', 'wall_sequence', 'is_infill_first',
        'layer_height', 'initial_layer_print_height', 'outer_wall_line_width',
        'inner_wall_line_width', 'sparse_infill_line_width', 'sparse_infill_pattern',
        'sparse_infill_density', 'infill_wall_overlap', 'top_shell_layers',
        'bottom_shell_layers', 'detect_thin_wall', 'gyroid_optimized', 'fill_multiline')


def selected(paths, z):
    rows = [p for p in paths if abs(p[4] - z) < 1e-5]
    if not rows:
        raise ValueError(f'No deposited paths at Z={z}')
    return rows


def draw(ax, paths, z, *, crop):
    rows = selected(paths, z)
    for role in dict.fromkeys(p[-1] for p in rows):
        subset = [p for p in rows if p[-1] == role]
        ax.add_collection(LineCollection([[(p[0], p[1]), (p[2], p[3])] for p in subset],
                          colors=COLORS[role], linewidths=.9))
    ax.set(xlim=(20, 40) if crop else (-.5, 60.5), ylim=(-.45, 6.45), aspect='equal',
           xlabel='wall length X / mm', ylabel='Y / mm')
    ax.grid(alpha=.12)
    return Counter(p[-1] for p in rows)


def save(fig, name):
    svg = VIEWS / f'{name}.svg'
    fig.savefig(svg)
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')
    fig.savefig(VIEWS / f'{name}.png', dpi=130)
    plt.close(fig)


def main():
    plt.rcParams.update({'svg.fonttype': 'none', 'font.size': 10})
    data, records = {}, {}
    geometry = json.loads((STUDY / 'geometry.json').read_text())
    if not geometry['ok'] or not geometry['geometry']['valid']:
        raise ValueError('Wall proxy has no successful native geometry receipt')
    for name, (pattern, density) in CONFIGS.items():
        native = json.loads((STUDY / f'{name}_review.json').read_text())
        review = native['slice']
        if not review['ok'] or review['input_sha256'] != digest(ROOT / 'infill_wall_study.stl'):
            raise ValueError(f'{name}: missing or stale slice input')
        run = Path(review['kept_run_directory'])
        if digest(run / 'input.stl') != review['input_sha256']:
            raise ValueError(f'{name}: raw slice input mismatch')
        process = STUDY / f'{name}_process.json'
        if digest(process) != digest(run / 'process.json'):
            raise ValueError(f'{name}: raw process mismatch')
        settings = json.loads((run / 'effective-settings.json').read_text())
        expected = {'wall_generator': 'classic', 'wall_loops': '3',
                    'wall_sequence': 'inner-outer-inner wall', 'is_infill_first': '0',
                    'sparse_infill_pattern': pattern, 'sparse_infill_density': density,
                    'top_shell_layers': '6', 'bottom_shell_layers': '6', 'gyroid_optimized': '0'}
        if any(settings[k] != value for k, value in expected.items()):
            raise ValueError(f'{name}: effective settings differ from intended comparison')
        raw = run / 'plate_1.gcode'
        paths = list(orca_linear_paths(raw))
        unknown = set(p[-1] for p in paths) - COLORS.keys()
        if unknown:
            raise ValueError(f'Unmapped deposition roles: {unknown}')
        outer = selected([p for p in paths if p[-1] == 'Outer wall'], 4.)
        # Translate the centered layout to the proxy's CAD coordinates for plots.
        # This is plot registration, not a separate mesh/footprint acceptance test.
        cx = (min(p[i] for p in outer for i in (0, 2)) + max(p[i] for p in outer for i in (0, 2))) / 2
        cy = (min(p[i] for p in outer for i in (1, 3)) + max(p[i] for p in outer for i in (1, 3))) / 2
        paths = [(p[0]-cx+30, p[1]-cy+3, p[2]-cx+30, p[3]-cy+3, *p[4:]) for p in paths]
        for z in (4., 4.2, 4.4):
            if not any(p[-1] == 'Sparse infill' for p in selected(paths, z)):
                raise ValueError(f'{name}: sparse core absent at Z={z}')
        data[name] = paths
        archive = STUDY / f'{name}_paths.gcode.gz'
        archive.write_bytes(gzip.compress(raw.read_bytes(), mtime=0))
        lengths = Counter()
        for p in paths:
            lengths[p[-1]] += hypot(p[2]-p[0], p[3]-p[1])
        layer_rows = []
        for z in (4., 4.2, 4.4, 14.8, 15.):
            rows = selected(paths, z)
            layer_rows.append({'z_mm': z, 'segments_by_role': dict(Counter(p[-1] for p in rows))})
        records[name] = {'native_receipt': f'{name}_review.json', 'gcode_sha256': digest(raw),
                         'gcode_archive': archive.name, 'input_stl_sha256': review['input_sha256'],
                         'process_sha256': digest(process), 'slicer_version': review['slicer_version'],
                         'effective_settings': {k: settings[k] for k in KEYS},
                         'whole_proxy_deposited_length_mm_by_role': dict(lengths),
                         'selected_layers': layer_rows,
                         'support_probe': review['support_probe'], 'notices': review['log_notices']}
    handles = [Line2D([0], [0], color=COLORS[r], lw=2, label=r) for r in
               ('Outer wall', 'Inner wall', 'Sparse infill', 'Bridge')]
    fig, axes = plt.subplots(3, 3, figsize=(15, 9))
    for row, name in enumerate(CONFIGS):
        for col, z in enumerate((4., 4.2, 4.4)):
            draw(axes[row, col], data[name], z, crop=True)
            axes[row, col].set_title(f'{name} / {CONFIGS[name][0]} {CONFIGS[name][1]} / Z {z:.1f} mm', fontsize=10)
            if row < 2:
                axes[row, col].set_xlabel('')
    fig.suptitle('ACTUAL Orca 2.4.2 deposition paths: 60 x 6 x 16 mm straight wall proxy\n'
                 'Consecutive layers; central X 20–40 mm shown. Y=0 contact side, Y=6 backing side.\n'
                 'Classic / 3 wall loops / 0.2 mm layers. Colors = roles, all TPU black. Travels not drawn.', fontsize=13)
    fig.legend(handles=handles, loc='lower center', ncol=4)
    fig.subplots_adjust(left=.055, right=.985, bottom=.10, top=.80, hspace=.65, wspace=.22)
    save(fig, 'infill_study_paths')
    fig, axes = plt.subplots(3, 1, figsize=(15, 7))
    for row, (ax, name) in enumerate(zip(axes, CONFIGS)):
        draw(ax, data[name], 4., crop=False)
        ax.set_title(f'{name}: full straight wall at Z 4.0 mm')
        if row < 2:
            ax.set_xlabel('')
    fig.suptitle('ACTUAL deposited centerlines — full 60 mm wall, 6 mm thick\n'
                 'Blue outer wall | grey inner walls | orange sparse infill. Line widths shown schematically.', fontsize=13)
    fig.subplots_adjust(left=.065, right=.985, bottom=.10, top=.82, hspace=.60)
    save(fig, 'infill_study_full')
    fig, axes = plt.subplots(3, 2, figsize=(12, 8))
    for row, name in enumerate(CONFIGS):
        for col, z in enumerate((14.8, 15.)):
            roles = draw(axes[row, col], data[name], z, crop=True)
            axes[row, col].set_title(f'{name} / Z {z:.1f} mm / '+('beneath roof' if col == 0 else 'first roof layer'))
            if row < 2:
                axes[row, col].set_xlabel('')
    fig.suptitle('ACTUAL roof paths: last sparse layer and first of six closing layers\n'
                 'Purple = Orca bridge/solid roles, not proven bridge quality. Central 20 mm shown. Travels not drawn.', fontsize=12)
    fig.subplots_adjust(left=.07, right=.985, bottom=.10, top=.82, hspace=.65, wspace=.23)
    save(fig, 'infill_study_roofs')
    result = {'category': 'diagnostic-infill-path-comparison', 'proxy': '60 x 6 x 16 mm solid CAD wall',
              'source_sha256': {p: digest(ROOT / p) for p in ('infill_wall_study.py', 'review_infill_study.py')},
              'geometry_receipt': 'geometry.json', 'variants': records,
              'limits': 'Actual deposition only; travel/retraction moves omitted. Proxy has no cup corners, '
                        'lid fit or tall-wall qualification. No physical print or measured surface/damping result.'}
    (STUDY / 'paths.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({name: {'layers': record['selected_layers'],
                            'deposited_length_mm': record['whole_proxy_deposited_length_mm_by_role']}
                      for name, record in records.items()}, indent=2))


if __name__ == '__main__':
    main()
