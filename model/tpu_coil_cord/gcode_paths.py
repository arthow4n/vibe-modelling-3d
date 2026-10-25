"""Read selected Orca linear relative-extrusion paths for the coil experiments."""
import re


def extrusions(file):
    """Read positive extrusion segments; startup purge is outside this review."""
    source=file.read_text()
    if 'M83' not in source:
        raise ValueError('Expected relative extrusion')
    source=source[source.index(';LAYER_CHANGE'):]
    position=dict(X=None,Y=None,Z=None)
    role=''
    number=r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'
    for line in source.splitlines():
        if line.startswith(';TYPE:'):role=line[6:].strip()
        code=line.split(';')[0].strip()
        if not code:continue
        cmd=code.split()[0]
        if cmd in ('M82','G91','G2','G3'):
            raise ValueError('Expected G90/M83 linear paths after the first layer marker')
        if cmd not in ('G0','G1'):continue
        values={a:float(v) for a,v in re.findall(r'([XYZE])('+number+r')',code)}
        before=position.copy()
        position.update({a:v for a,v in values.items() if a in position})
        if values.get('E',0)<=0 or not any(a in values for a in ('X','Y')):continue
        if any(v is None for v in (*position.values(),*before.values())):continue
        yield dict(x=[before['X'],position['X']],y=[before['Y'],position['Y']],z=position['Z'],role=role)


def plot_coil_review(primary, probe, *, axis_height, name, destination):
    """Show bed, mid-height walls, automatic supports and the first roof bridge.

    Inputs are already parsed linear paths in the slicer's bed coordinates.
    This is a visual diagnostic, not an extrusion or support acceptance check.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection

    bridges = [s for s in primary if s['role'] == 'Bridge']
    support = [s for s in probe if s['role'] in ('Support', 'Support interface')]
    roof = min((s['z'] for s in bridges if s['z'] > axis_height), default=axis_height)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout='constrained')

    def draw(ax, paths, color, *, xz=False, width=.65):
        lines = [[(s['x'][0], s['z'] if xz else s['y'][0]),
                  (s['x'][1], s['z'] if xz else s['y'][1])] for s in paths]
        if lines:
            ax.add_collection(LineCollection(lines, colors=color, linewidths=width))
            ax.autoscale_view()

    wall_z = round(axis_height / .2) * .2
    draw(axes[0, 0], [s for s in primary if abs(s['z'] - .2) < 1e-5], '#286a9e')
    draw(axes[0, 1], [s for s in primary if abs(s['z'] - wall_z) < 1e-5], '#286a9e')
    draw(axes[1, 0], support, '#b35c2a', xz=True)
    draw(axes[1, 1], [s for s in primary if abs(s['z'] - roof + .2) < 1e-5], '#b9c1c7', width=1.8)
    draw(axes[1, 1], [s for s in primary if abs(s['z'] - roof) < 1e-5 and s['role'] != 'Bridge'], '#286a9e')
    draw(axes[1, 1], [s for s in bridges if abs(s['z'] - roof) < 1e-5], '#b35c2a')
    for ax, title in zip(axes.flat, [f'{name} bed Z0.2', f'{name} side walls Z{wall_z:g}',
                                   f'{name} support probe: X vs Z', f'{name} roof Z{roof:g}: bridge orange, prior gray']):
        ax.set(title=title, xlabel='Bed X (mm)', ylabel='Z (mm)' if ax == axes[1, 0] else 'Bed Y (mm)')
        if ax != axes[1, 0]:
            ax.set_aspect('equal')
    fig.savefig(destination, dpi=150)
    plt.close(fig)
