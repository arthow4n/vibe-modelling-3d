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
