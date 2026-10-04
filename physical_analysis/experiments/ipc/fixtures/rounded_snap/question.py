"""Synthetic/local contact benchmark derived from historical failed-product geometry.

Only a clamped elastic leaf/root pad and translating cylindrical cam remain.
No enclosure, contents, guides, lid, print layout or storage-product architecture.
Historical coordinates/material metadata preserve identity-bound numerical evidence;
they are not recommendations for a future product or calibrated material data.
"""
import cadquery as cq
from physical_analysis import SnapFitQuestion, Support, Motion, MatingPart, Material, Region, PETG_SCREEN

ARM_ROOT_X=-16.0
ARM_TIP_X=-34.0
ARM_Y=27.8
ARM_T=2.4
CAM_R=2.4
DEPTH=3.2


def _block(x,y,z,dx,dy,dz):
    return cq.Workplane('XY').box(dx,dy,dz,centered=False).translate((x,y,z))


def leaf():
    arm=_block(ARM_TIP_X,ARM_Y-ARM_T/2,0,ARM_ROOT_X-ARM_TIP_X,ARM_T,DEPTH)
    tip=cq.Workplane('XY').center(ARM_TIP_X,ARM_Y).circle(CAM_R).extrude(DEPTH)
    root=_block(ARM_ROOT_X,ARM_Y-ARM_T/2-2,0,3,ARM_T+2,DEPTH)
    return arm.union(tip).union(root).edges('|Z').fillet(.5)


def cam():
    return cq.Workplane('XY').center(-38,31.8).circle(CAM_R).extrude(DEPTH+.3+.6).translate((0,0,-.3))


def question(mesh=1.0, penalty=6000, modulus=PETG_SCREEN.youngs_modulus_MPa, max_increment=.025):
    material=Material('uncalibrated solid PETG',modulus,PETG_SCREEN.poisson_ratio,
        'Explicit isotropic short-term screening assumption, not derived from wall count or filament data',PETG_SCREEN.strain_limit)
    return SnapFitQuestion(name='snap_cycle',part=leaf(),part_name='arm',material=material,
        supports=(Support(Region.plane('x',ARM_ROOT_X+3)),),
        contact_region=Region(lower=(ARM_TIP_X-CAM_R-.1,ARM_Y-.1,-.01),upper=(ARM_TIP_X+CAM_R+.1,100,100)),
        mating_parts=(MatingPart('body_cam',cam().translate((8,0,0)),Motion.round_trip((-8,0,0))),),
        observations={'tip':Region(lower=(ARM_TIP_X-CAM_R-.1,ARM_Y+.3,-.01),
            upper=(ARM_TIP_X+CAM_R+.1,ARM_Y+CAM_R+.1,DEPTH+.01))},
        mesh_size_mm=mesh,penalty_N_mm3=penalty,max_increment=max_increment,
        contact_free_at=(.5,1),return_observation='tip',return_tolerance_mm=1e-6,
        displacement_limits_mm={'tip':((-.15,.15),(-1.1,.01),(-.01,.01))})
