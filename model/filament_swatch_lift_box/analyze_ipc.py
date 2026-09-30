"""Optional IPC investigation of the unchanged real cap/pad path.

Use only after generic and rounded-snap qualification. The default release-only
fixture retains its unloaded-assembled initial-state dependency. No tab motion
is prescribed. Initial offsets are explicit numerical experiments, never hidden.
"""
import argparse
import json
from analyze import snap_question
from analyze_release import release
from physical_analysis.backends.polyfem import IPCSettings, PolyfemBackend


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory');p.add_argument('--complete',action='store_true')
    p.add_argument('--mesh',type=float,default=1.6);p.add_argument('--increment',type=float,default=.006)
    p.add_argument('--activation',type=float,default=.001);p.add_argument('--obstacle-mesh',type=float,default=.5)
    p.add_argument('--initial-z-offset',type=float,default=0)
    p.add_argument('--convergent',action='store_true')
    p.add_argument('--projected',action='store_true')
    p.add_argument('--timeout',type=float,default=1200);p.add_argument('--mesh-from')
    a=p.parse_args()
    c=(snap_question(a.mesh,12000,a.increment,a.timeout).build_case() if a.complete else
       release(a.mesh,12000,a.increment,a.timeout))
    r=c.run(a.directory,mesh_from=a.mesh_from,backend=PolyfemBackend(IPCSettings(
        activation_distance_mm=a.activation,obstacle_mesh_size_mm=a.obstacle_mesh,
        initial_offset_mm=(0,0,a.initial_z_offset),convergent_barrier=a.convergent,projected_newton=a.projected)))
    print(json.dumps(dict(status=r.status,completed=r.completed,errors=r.errors,metrics=r.metrics),indent=2))
