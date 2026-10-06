"""Authoritative jar pair and specified helical withdrawal, without re-exporting."""
import json
from pathlib import Path
import runpy
import cadquery as cq
from assembly_geometry import Configuration, PairRequirement, sample_motion

ROOT = Path(__file__).resolve().parent


def load():
    return runpy.run_path(str(ROOT/'vaseline_container.py'))


def configuration(m, *, opening_deg=0, print_layout=False):
    delta = (cq.Location((0, 0, m['THREAD_PITCH']*opening_deg/360)) *
             cq.Location((0, 0, 0), (0, 0, opening_deg)))
    a = cq.Assembly(name='jar').add(m['base'], name='base').add(
        m['print_lid'] if print_layout else m['lid'], name='lid',
        loc=cq.Location() if print_layout else delta)
    return Configuration.explicit(a, name='print' if print_layout else f'opening_{opening_deg:g}_deg',
        kind='print' if print_layout else 'operating', parameters={'opening_deg': opening_deg})


def withdrawal_checks(m):
    closed = configuration(m)
    motion = sample_motion(closed, 'lid', 'base', PairRequirement(
        'Prescribed thread withdrawal has no solid obstruction', max_overlap_mm3=1e-5),
        samples=range(0, 1081, 30), transform=lambda t:
            cq.Location((0, 0, m['THREAD_PITCH']*t/360)) * cq.Location((0, 0, 0), (0, 0, t)),
        parameter='opening', units='deg').require_passed()
    return motion.to_dict()


def retention_checks(m):
    closed = configuration(m)
    retention = sample_motion(closed, 'lid', 'base', PairRequirement(
        'Axial pull without turning must meet thread flanks', min_overlap_mm3=1),
        samples=(.8,), transform=lambda t: cq.Location((0, 0, t)),
        parameter='axial_pull', units='mm').require_passed()
    return retention.to_dict()


def verify(m):
    return dict(withdrawal=withdrawal_checks(m), retention=retention_checks(m))


if __name__ in ('__main__', '__cqgi__'):
    model = load()
    if __name__ == '__main__':
        print(json.dumps(verify(model), indent=2))
    result = configuration(model).assembly()
