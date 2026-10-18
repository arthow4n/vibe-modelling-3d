"""Qualify bounded-memory FEBio ILUT on two elastic contacting bodies.

This solver fixture is not a case holding-force prediction. Run through execute.py
with a fresh output directory. A deliberately inadequate linear iteration budget
must fail rather than quietly accepting a linear approximation.
"""
import argparse
import json
from pathlib import Path
import cadquery as cq
from physical_analysis import AnalysisCase, Material, Region
from physical_analysis.backends.febio import FebioBackend, FgmresILUT
from physical_analysis.evidence import retain_run


def options(*, inadequate=False, plugin=None):
    # Native FEBio 4.13 rejects MKL's correction warning for a changed restart.
    # Keep its native 150 here; the archived restart-30 counterexample records
    # why that smaller workspace is not currently qualified.
    return FgmresILUT(max_iterations=(1 if plugin else 150) if inadequate else 1000,
        restart_iterations=(1 if inadequate else 30) if plugin else 150,
        relative_tolerance=1e-15 if inadequate else 1e-8,
        absolute_tolerance=1e-15 if inadequate else 1e-12,
        max_fill=1 if inadequate else 12, fill_tolerance=1e-5,
        restart_correction_plugin=plugin)


def make_case(motion_mm):
    c = AnalysisCase('febio_iterative_contact', max_increment=.2)
    m = Material('benchmark', 1200, .3, 'Elastic numerical fixture, not filament calibration')
    c.add_part('block', cq.Workplane('XY').box(2,2,4,centered=False).translate((0,0,.01)),
               material=m, mesh_size_mm=.8)
    c.add_part('floor', cq.Workplane('XY').box(4,4,1,centered=False).translate((-1,-1,-1)),
               material=m, mesh_size_mm=.8)
    c.fix('floor', Region.plane('z',-1))
    c.constrain('block', displacement_mm=(0,0,None))
    c.prescribe_motion('block', Region.plane('z',4.01), displacement_mm=(None,None,-motion_mm))
    c.contact('block',Region.plane('z',.01),'floor',Region.plane('z',0),
              penalty_N_mm3=120000, penetration_limit_mm=.01, discretization='surface_to_surface')
    c.observe('floor',Region.plane('z',0),name='receiving_surface')
    return c


def run_comparison(directory, *, archive=None, plugin=None):
    results = {}
    for label, motion, config in (('direct',.02,None), ('iterative',.02,options(plugin=plugin)),
                                  ('open',.005,options(plugin=plugin)), ('inadequate',.02,options(inadequate=True,plugin=plugin))):
        result = make_case(motion).run(directory/label, backend=FebioBackend(linear_solver=config),
                                      mesh_from=directory/'direct' if label!='direct' else None)
        results[label] = result
        if archive is not None:
            retain_run(directory/label, archive/label)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--restart-plugin', type=Path)
    args = parser.parse_args()
    results = run_comparison(args.directory, archive=args.archive, plugin=args.restart_plugin)
    summary = {name:dict(status=r.status,completed=r.completed,errors=r.errors,
                        metrics=r.metrics,linear_solver=r.provenance.get('linear_solver'))
               for name,r in results.items()}
    print(json.dumps(summary))
    if args.archive is not None:
        (args.archive/'comparison.json').write_text(json.dumps(summary,indent=2)+'\n')


if __name__ == '__main__':
    main()
