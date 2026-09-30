"""Real rounded snap pass-over, using the shared physical intent API.

Hold the lid root, move the body's actual cam relative to it. This local fixture
assumes stiff guides/root; it is not a whole-box stiffness or friction model.
"""
import argparse
import json
from components import *
from physical_analysis import (SnapFitQuestion, Support, Motion, MatingPart,
                               ManufacturingAssumption, Material, Region, PETG_SCREEN)

def operation(mesh=1.0, penalty=6000, opening=False, modulus=PETG_SCREEN.youngs_modulus_MPa, cycle=False, max_increment=.00625):
    mat=Material('uncalibrated solid PETG',modulus,PETG_SCREEN.poisson_ratio,
        'Explicit isotropic short-term screening assumption, not derived from wall count or filament data',PETG_SCREEN.strain_limit)
    # In the lid frame, the base moves -X during closure, +X during opening.
    cam=base_cam() if opening else base_cam().translate((8,0,0))
    return SnapFitQuestion(name='snap_cycle' if cycle else ('snap_open' if opening else 'snap_close'),
        part=snap_arm(),part_name='arm',material=mat,
        supports=(Support(Region.plane('x',ARM_ROOT_X+3)),),
        contact_region=Region(lower=(ARM_TIP_X-CAM_R-.1,ARM_Y-.1,-.01),upper=(ARM_TIP_X+CAM_R+.1,100,100)),
        mating_parts=(MatingPart('body_cam',cam,(Motion.round_trip if cycle else Motion)((8 if opening else -8,0,0))),),
        observations={'tip':Region(lower=(ARM_TIP_X-CAM_R-.1,ARM_Y+.3,-.01),
            upper=(ARM_TIP_X+CAM_R+.1,ARM_Y+CAM_R+.1,LID_T+.01))},
        mesh_size_mm=mesh,penalty_N_mm3=penalty,max_increment=max_increment,timeout_seconds=1200,
        contact_free_at=(.5,1) if cycle else (1,),return_observation='tip' if cycle else None,
        return_tolerance_mm=1e-6,
        displacement_limits_mm={'tip':((-.15,.15),(-RELIEF_INWARD_SCREEN,.01),(-.01,.01))},
        manufacturing=ManufacturingAssumption('Flat lid; in-layer spring. Existing snap_paths review found effectively solid local paths; isotropic PETG remains uncalibrated.'))

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('directory'); p.add_argument('--mesh',type=float,default=1.0)
    p.add_argument('--penalty',type=float,default=6000); p.add_argument('--opening',action='store_true')
    p.add_argument('--modulus',type=float,default=PETG_SCREEN.youngs_modulus_MPa); p.add_argument('--cycle',action='store_true'); p.add_argument('--max-increment',type=float,default=.00625)
    a=p.parse_args(); r=operation(a.mesh,a.penalty,a.opening,a.modulus,a.cycle,a.max_increment).run(a.directory)
    print(json.dumps(dict(status=r.status,errors=r.errors,metrics=r.metrics),indent=2))
