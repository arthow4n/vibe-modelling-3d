"""Reproduce the small direct/iterative retention-contact solver comparison.

Run through execute.py with a new output directory. This is a solver fixture,
not a dental-case retention-force prediction.
"""
import argparse
import json
from pathlib import Path
import cadquery as cq
from physical_analysis import AnalysisCase, Material, Region
from physical_analysis.backends.structural import CalculixBackend

def make_case(motion_mm):
    c=AnalysisCase('iterative_contact',max_increment=.1)
    m=Material('uniaxial',1200,0,'Poisson-zero uniaxial benchmark')
    c.add_part('block',cq.Workplane('XY').box(2,2,4,centered=False).translate((0,0,.01)),material=m,mesh_size_mm=.8)
    c.add_part('floor',cq.Workplane('XY').box(4,4,1,centered=False).translate((-1,-1,-1)),material=m,mesh_size_mm=1)
    c.fix('floor').constrain('block',displacement_mm=(0,0,None))
    c.prescribe_motion('block',Region.plane('z',4.01),displacement_mm=(None,None,-motion_mm))
    c.contact('block',Region.plane('z',.01),'floor',Region.plane('z',0),penalty_N_mm3=120000,penetration_limit_mm=.05,discretization='surface_to_surface')
    return c

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    results = {}
    for solver in ('default', 'iterative_scaling', 'iterative_cholesky'):
        result = make_case(.02).run(args.directory/solver,
            backend=CalculixBackend(linear_solver=solver))
        results[solver] = dict(status=result.status, errors=result.errors, metrics=result.metrics)
    print(json.dumps(results))


if __name__ == '__main__':
    main()
