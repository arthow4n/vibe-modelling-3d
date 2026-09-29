"""Real rounded snap pass-over, using the shared physical intent API.

Hold the lid root, move the body's actual cam relative to it. This local fixture
assumes stiff guides/root; it is not a whole-box stiffness or friction model.
"""
import argparse
import json
from components import *
from physical_analysis import AnalysisCase, Material, Region, PETG_SCREEN

def operation(mesh=1.0, penalty=6000, opening=False, modulus=PETG_SCREEN.youngs_modulus_MPa, cycle=False, max_increment=.00625):
    mat=Material('uncalibrated solid PETG',modulus,PETG_SCREEN.poisson_ratio,
        'Explicit isotropic short-term screening assumption, not derived from wall count or filament data',PETG_SCREEN.strain_limit)
    c=AnalysisCase('snap_cycle' if cycle else ('snap_open' if opening else 'snap_close'),max_increment=max_increment,timeout_seconds=1200)
    c.add_part('arm',snap_arm(),material=mat,mesh_size_mm=mesh)
    c.fix('arm',Region.plane('x',ARM_ROOT_X+3),name='root')
    # In the lid frame, the base moves -X during closure, +X during opening.
    cam=base_cam() if opening else base_cam().translate((8,0,0))
    c.add_part('body_cam',cam,material=mat,mesh_size_mm=mesh)
    c.prescribe_motion('body_cam',displacement_mm=(8 if opening else -8,0,0),name='drive',progress=((0,0),(.5,1),(1,0)) if cycle else None)
    c.contact('arm',Region(lower=(ARM_TIP_X-CAM_R-.1,ARM_Y-.1,-.01),upper=(ARM_TIP_X+CAM_R+.1,100,100)),
              'body_cam',Region(),penalty_N_mm3=penalty,penetration_limit_mm=.02,discretization="surface_to_surface")
    c.observe('arm',Region(lower=(ARM_TIP_X-CAM_R-.1,ARM_Y+.3,-.01),upper=(ARM_TIP_X+CAM_R+.1,ARM_Y+CAM_R+.1,LID_T+.01)),name='tip')
    return c

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('directory'); p.add_argument('--mesh',type=float,default=1.0)
    p.add_argument('--penalty',type=float,default=6000); p.add_argument('--opening',action='store_true')
    p.add_argument('--modulus',type=float,default=PETG_SCREEN.youngs_modulus_MPa); p.add_argument('--cycle',action='store_true'); p.add_argument('--max-increment',type=float,default=.00625)
    a=p.parse_args(); r=operation(a.mesh,a.penalty,a.opening,a.modulus,a.cycle,a.max_increment).run(a.directory)
    print(json.dumps(dict(status=r.status,errors=r.errors,metrics=r.metrics),indent=2))
