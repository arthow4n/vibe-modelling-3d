"""Raised-easel local engineering questions. Run with ./execute.py."""
import argparse
import json
import math
from pathlib import Path
import v2_components as d
from physical_analysis import (Material,Region,Support,Motion,SurfaceForce,MatingPart,
    StructuralQuestion,ContactQuestion,SnapFitQuestion,FlexureQuestion,ManufacturingAssumption,QuestionStudy)

def material(modulus=800):
    return Material('PETG conditional solid',modulus,.38,
        'Uncalibrated isotropic short-term sensitivity assumption; no printed fatigue or strength qualification',.015)

def mounts():
    return tuple(Support(Region((min(side*(d.ROOT_X-3),side*(d.ROOT_X+7)),d.ROOT_Y-5,d.LEAF_Z),
                               (max(side*(d.ROOT_X-3),side*(d.ROOT_X+7)),d.ROOT_Y+5,d.LEAF_Z)),
                         name=f'mount_{i}') for i,side in enumerate((-1,1)))

def release_question(mesh=1.6,modulus=800,penalty=12000):
    # Broad finger proxy moves forward and back; guide friction is outside this fixture.
    finger=d.box(-18,d.ROOT_Y+14+.3,6,36,5,12)
    return SnapFitQuestion(name='v2_keeper_release',part=d.keeper(),part_name='keeper',
        material=material(modulus),supports=mounts(),mesh_size_mm=mesh,max_increment=.1,
        contact_region=Region.plane('y',d.ROOT_Y+14),
        mating_parts=(MatingPart('finger',finger,Motion.round_trip((0,-d.RELEASE_TRAVEL-.3,0),name='thumb')) ,),
        penalty_N_mm3=penalty,penetration_limit_mm=.02,
        observations={'button':Region((-10,d.ROOT_Y+14,8),(10,d.ROOT_Y+14,16))},
        contact_free_at=(1,),return_observation='button',return_tolerance_mm=.01,
        displacement_limits_mm={'button':((-.5,.5),(-7.5,.1),(-.5,.5))},
        acceptance={'peak_motion_force_N.thumb':8},
        manufacturing=ManufacturingAssumption('Keeper XY flat, 0.4 nozzle / 0.2 layers, solid PETG; narrow springs bend in-plane.'))

def holding_question(mesh=1.6,modulus=800,penalty=12000):
    # Active 65-degree hook: accidental 5 N rear-foot lift; seats carry service compression.
    y=d.SEAT_YS[1]
    return ContactQuestion(name='v2_keeper_holding',part=d.keeper(),part_name='keeper',
        material=material(modulus),supports=mounts(),mesh_size_mm=mesh,max_increment=.1,
        forces=(SurfaceForce(Region((-9,y-6,d.HOOK_UNDERSIDE),(9,y-1,d.HOOK_UNDERSIDE)),(0,0,5)),),
        contact_region=Region.plane('z',d.LEAF_Z+d.LEAF_THICKNESS),
        mating_parts=tuple(MatingPart(f'guide_{i}',d.guide_cage(y),Motion((0,0,0),name=f'guide_fixed_{i}'),
                                    Region.plane('z',d.GUIDE_POST_TOP))
                           for i,y in enumerate(d.GUIDE_YS)),
        penalty_N_mm3=penalty,penetration_limit_mm=.02,
        observations={'roof':Region((-9,y-6,d.HOOK_UNDERSIDE),(9,y-1,d.HOOK_UNDERSIDE))},
        acceptance={'max_displacement_mm':2},
        manufacturing=ManufacturingAssumption('Solid keeper and printed guide caps; guide cage idealized rigid, excluding screw preload and cap compliance.'))


def direct_release_question(mesh=1.6,modulus=800):
    return FlexureQuestion(name='v2_direct_release',part=d.keeper(),part_name='keeper',
        material=material(modulus),supports=mounts(),mesh_size_mm=mesh,max_increment=.1,
        motion=Motion.round_trip((None,-d.RELEASE_TRAVEL,None),name='thumb',region=Region.plane('y',d.ROOT_Y+14)),
        acceptance={'peak_motion_force_N.thumb':8},
        manufacturing=ManufacturingAssumption('Solid flat keeper; ideal prescribed button translation excludes finger/guide friction and physical return.'))

def structure_question(mesh=2.4,modulus=800):
    theta=math.radians(50)
    weight=(d.PHONE_MASS_KG+.1)*9.81
    tap=2.0
    upper=(weight*math.cos(theta)*(d.PHONE_HEIGHT/2)+tap*160)/d.UPPER_CONTACT_Y
    lower=weight*math.cos(theta)+tap-upper
    supports=[]
    for i,x in enumerate((-44,44)):
        for j,u in enumerate((d.PIVOT_LOCAL_Y,d.UPPER_CONTACT_Y)):
            supports.append(Support(Region((x-6,u-8,d.FRAME_BACK),(x+6,u+8,-32)),name=f'pin_{i}_{j}'))
    forces=[]
    for x in (-d.CONTACT_X,d.CONTACT_X):
        forces.extend((
            SurfaceForce(Region((x-6,0,0),(x+6,0,13)),(0,-weight*math.sin(theta)/2,0)),
            SurfaceForce(Region((x-5,66,0),(x+5,74,0)),(0,0,-upper/2)),
            SurfaceForce(Region((x-6,0,d.LIP_INNER_Z),(x+6,7,d.LIP_INNER_Z)),(0,0,-lower/2)),
        ))
    return StructuralQuestion(name='v2_cradle_service',part=d.cradle(),part_name='cradle',
        material=material(modulus),supports=tuple(supports),forces=tuple(forces),mesh_size_mm=mesh,
        max_increment=.25,acceptance={'max_displacement_mm':1},
        manufacturing=ManufacturingAssumption('Cradle rear plane on bed; solid PETG plate; pivot-boss regions idealized restrained, excluding joint play.'))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('question',choices=('release','holding','structure','release_direct'))
    p.add_argument('directory',type=Path)
    p.add_argument('--mesh',type=float)
    p.add_argument('--modulus',type=float,default=800)
    p.add_argument('--study',action='store_true')
    p.add_argument('--evidence-baseline',type=Path,help='Identity-check a completed baseline when adding a study; no baseline solve repeated')
    a=p.parse_args()
    kwargs={'modulus':a.modulus}
    if a.mesh is not None: kwargs['mesh']=a.mesh
    q={'release':release_question,'holding':holding_question,'structure':structure_question,'release_direct':direct_release_question}[a.question](**kwargs)
    if a.study:
        metrics=('max_strain_by_part.'+q.part_name, 'peak_motion_force_N.thumb' if a.question.startswith('release') else 'max_displacement_mm')
        r=QuestionStudy(q,'A 20% numerical change must not change the supplied provisional 1.5% strain and per-fixture displacement/force screens',
            metrics,relative_tolerance=.2,mesh_levels=1,motion_levels=1 if a.question.startswith('release') else 0,
            contact_levels=1 if a.question in ('release','holding') else 0).run(a.directory,
                evidence={'baseline':a.evidence_baseline} if a.evidence_baseline else None)
    else:
        r=q.run(a.directory)
    print(json.dumps({'status':r.status,'errors':r.errors,'question':r.metrics.get('question')}))
