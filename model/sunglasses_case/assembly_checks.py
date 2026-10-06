"""Named production configurations and inspection checks; no export side effects.

Run with execute.py for diagnostics or evaluate_model.py for the closed view.
"""
import json
from pathlib import Path
import runpy
import cadquery as cq
from assembly_geometry import Configuration, PairRequirement, sample_motion, rigid_location

ROOT = Path(__file__).resolve().parent


def load(*, verify=True, **dimensions):
    return runpy.run_path(str(ROOT/'sunglasses_case.py'),
                         init_globals={'EXPORT': False, 'VERIFY': verify, **dimensions})


def hinge_location(m, angle):
    return rigid_location(lambda frame: m['close'](frame, angle))


def configuration(m, *, angle=180, name='closed', print_layout=False):
    a = cq.Assembly(name='case').add(m['body'], name='body').add(
        m['open_lid'], name='lid', loc=hinge_location(m, 0 if print_layout else angle))
    a.add(m['print_keeper'] if print_layout else m['keeper'], name='keeper')
    return Configuration.explicit(a, name=name, kind='print' if print_layout else 'operating',
                                  parameters={'hinge_angle_deg': 0 if print_layout else angle})


def closed_checks(m):
    closed = configuration(m)
    free = PairRequirement('Closed lid clears body and keeper', max_overlap_mm3=.001)
    checks = [closed.check('lid', n, free).require_passed().to_dict() for n in ('body', 'keeper')]
    # Intentional tapered keeper interference: accepted original upper bound.
    checks.append(closed.check('body', 'keeper', PairRequirement(
        'Accepted seated wedge interference stays below original bound', max_overlap_mm3=1)).require_passed().to_dict())
    for answer,limit in zip(checks,(.001,.001,1)):
        assert answer['overlap_mm3']<limit, ('Original strict closed-fit limit violated',answer)
    return checks


def hinge_checks(m):
    # The original sweep excludes the elastic loop. Keep that distinction explicit;
    # this inspection-only assembly is a view of the original lid_shell feature.
    shell = Configuration.explicit(cq.Assembly(name='shell_path').add(m['body'], name='body').add(
        m['lid_shell'], name='lid_shell'), name='shell_only')
    sweep = sample_motion(shell, 'lid_shell', 'body', PairRequirement(
        'Rigid hinge shell path clears body; loop excluded', max_overlap_mm3=.001),
        samples=range(0, 181, 5), transform=lambda t: hinge_location(m, t),
        parameter='hinge_angle', units='deg').require_passed()
    return sweep.to_dict()


def retention_checks(m):
    return m['verify_retention'](m['loop'],m['keeper'])


def release_checks(m):
    released = m['close'](m['loop']).translate((0, -m['closure'].RELEASE_TRAVEL-.3, 0))
    release = Configuration.explicit(cq.Assembly(name='release').add(released, name='loop').add(
        m['body'].union(m['keeper']), name='body_and_keeper'), name='loop_after_prescribed_release', kind='intermediate')
    withdrawal = sample_motion(release, 'loop', 'body_and_keeper', PairRequirement(
        'Prescribed released loop clears keeper on sampled lift; flexure not simulated', max_overlap_mm3=.001),
        samples=(0, .4, 2, 5, 9), transform=lambda t: cq.Location((0, 0, t)),
        parameter='lift', units='mm').require_passed()
    return withdrawal.to_dict()


def verify(m):
    return dict(checks=closed_checks(m)+retention_checks(m),
                hinge=hinge_checks(m), release=release_checks(m))


if __name__ in ('__main__', '__cqgi__'):
    model = load()
    if __name__ == '__main__':
        print(json.dumps(verify(model), indent=2))
    result = configuration(model).assembly()
