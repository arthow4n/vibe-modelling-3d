"""Optional qualification experiment; reuse the current SnapFitQuestion intent.

Does not select a new default or redesign the object. Qualify generic IPC
benchmarks before interpreting this operation; compare retained evidence using
the shared study tools. Exact native meshes can be frozen with --mesh-from.
"""
import argparse
import json
from analyze import operation
from physical_analysis.backends.polyfem import IPCSettings, PolyfemBackend


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory');p.add_argument('--mesh',type=float,default=.7)
    p.add_argument('--increment',type=float,default=.025)
    p.add_argument('--activation',type=float,default=.001)
    p.add_argument('--obstacle-mesh',type=float,default=.3)
    p.add_argument('--convergent',action='store_true')
    p.add_argument('--projected',action='store_true')
    p.add_argument('--timeout',type=float,default=1200);p.add_argument('--mesh-from')
    a=p.parse_args()
    question=operation(mesh=a.mesh,cycle=True,max_increment=a.increment)
    question.timeout_seconds=a.timeout
    r=question.build_case().run(a.directory,mesh_from=a.mesh_from,
        backend=PolyfemBackend(IPCSettings(activation_distance_mm=a.activation,
                                         obstacle_mesh_size_mm=a.obstacle_mesh,
                                         convergent_barrier=a.convergent,projected_newton=a.projected)))
    print(json.dumps(dict(status=r.status,completed=r.completed,errors=r.errors,metrics=r.metrics),indent=2))
