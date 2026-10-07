"""API consumer: run one named question, retain compact object evidence.

uv run --locked python model/analysis_phone_stand/analyze.py release /tmp/stand-release
"""
from pathlib import Path
import argparse
import json
import math
from components import *
from physical_analysis import (AnalysisCase, Material, Region, FlexureQuestion,
    StructuralQuestion, Support, Motion, SurfaceForce, BeamApproximation, ManufacturingAssumption)


def material(modulus):
    return Material('PETG solid assumption',modulus,.38,
        'Uncalibrated solid PETG short-term isotropic sensitivity assumption; actual print must be tested',.015)


def release_case(mesh=1.6,modulus=1200):
    # Thumb presses the forward tab. X/Y remain free, matching a frictionless fingertip.
    return FlexureQuestion(name='latch_release',part=latch(),part_name='latch',
        material=material(modulus),mesh_size_mm=mesh,
        supports=(Support(Region(lower=(-100,LATCH_ROOT_Y,LATCH_TOP-LATCH_THICKNESS-.01),
            upper=(100,100,LATCH_TOP-LATCH_THICKNESS+.01)),name='mount'),),
        motion=Motion((None,None,-RELEASE_TRAVEL),Region(lower=(-8,PIVOT_Y-16,LATCH_TOP-.01),
            upper=(8,PIVOT_Y-16,LATCH_TOP+.01)),name='thumb'),
        observations={'tooth':Region(lower=(-6,PIVOT_Y-1,LATCH_TOP+LATCH_TOOTH_HEIGHT-.01),
            upper=(6,PIVOT_Y+1,LATCH_TOP+LATCH_TOOTH_HEIGHT+.01))},
        beam=BeamApproximation(LATCH_LENGTH+16,LATCH_WIDTH,LATCH_THICKNESS,
            'Uniform-width root-to-thumb cantilever is a cheap compliance screen; widened root, tab and tooth require CAD analysis.',
            tip_displacement_mm=RELEASE_TRAVEL),
        acceptance={'peak_motion_force_N.thumb':12},
        manufacturing=ManufacturingAssumption('Side-printed latch, intended solid PETG process; actual bonding and modulus uncalibrated.'))


def structure_case(mesh=3,modulus=1200,mass=PHONE_MASS_KG):
    # Bonded approximation to the two-bolt arm/cradle connection. Bolts checked separately.
    theta=math.radians(45)
    # Apply the 100 g moving-part allowance at the phone load locations too.
    # This is conservative relative to its measured mass and shorter lever arm.
    weight=(mass+.1)*9.81
    normal=weight*math.cos(theta)*(PHONE_HEIGHT/2)/(120-(CRADLE_BOTTOM+6))
    # Seat bears the tangential weight; two halves selected by complete faces at y=32.
    return StructuralQuestion(name='structure_load',
        part=arm().union(cradle()).intersect(box(-50,22,-30,100,140,70)),part_name='structure',
        material=material(modulus),mesh_size_mm=mesh,max_increment=.25,
        supports=(Support(Region.plane('y',22),name='sector_support'),),
        forces=(SurfaceForce(Region(lower=(-30,110,CRADLE_THICKNESS-.01),upper=(30,130,CRADLE_THICKNESS+.01)),(0,0,-normal)),
            SurfaceForce(Region(lower=(-100,CRADLE_BOTTOM+6,CRADLE_THICKNESS),upper=(100,CRADLE_BOTTOM+6,CRADLE_THICKNESS+PHONE_THICKNESS+2)),
                (0,-weight*math.sin(theta),normal-weight*math.cos(theta)))),
        acceptance={'max_displacement_mm':2})


def contact_case(mesh=2.5,modulus=1200,penalty=60000,travel=5.8):
    c=AnalysisCase('tooth_holding' if travel<0 else 'tooth_pass_over',max_increment=.1)
    c.add_part('latch',latch(),material=material(modulus),mesh_size_mm=mesh)
    c.fix('latch',Region(lower=(-100,LATCH_ROOT_Y,LATCH_TOP-LATCH_THICKNESS-.01),
                         upper=(100,100,LATCH_TOP-LATCH_THICKNESS+.01)),name='mount')
    # Actual gear-tooth profile, isolated at the bottom of the wheel. The obstacle
    # translates tangentially: this is a local pass-over experiment, not a rotation solve.
    gear=placed(arm(),60).intersect(box(-ARM_WIDTH/2-1,PIVOT_Y-8,PIVOT_Z-GEAR_TIP-.1,ARM_WIDTH+2,16,5))
    c.add_part('gear_patch',gear,material=material(modulus),mesh_size_mm=mesh)
    c.prescribe_motion('gear_patch',displacement_mm=(0,travel,0),name='drive')
    c.contact('latch',Region(lower=(-100,PIVOT_Y-3,LATCH_TOP+.1),upper=(100,PIVOT_Y+3,30)),
              'gear_patch',Region(upper=(100,100,PIVOT_Z-GEAR_ROOT+.5)),penalty_N_mm3=penalty, penetration_limit_mm=.05)
    c.observe('latch',Region(lower=(-6,PIVOT_Y-1,LATCH_TOP+LATCH_TOOTH_HEIGHT-.01),upper=(6,PIVOT_Y+1,LATCH_TOP+LATCH_TOOTH_HEIGHT+.01)),name='tooth')
    return c

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('question',choices=['release','structure','contact','holding'])
    p.add_argument('directory',type=Path)
    p.add_argument('--mesh',type=float)
    p.add_argument('--modulus',type=float,default=1200)
    p.add_argument('--mass',type=float,default=PHONE_MASS_KG)
    p.add_argument('--penalty',type=float,default=60000)
    a=p.parse_args()
    kwargs={'modulus':a.modulus}
    if a.mesh is not None: kwargs['mesh']=a.mesh
    if a.question=='structure': kwargs['mass']=a.mass
    if a.question in ('contact','holding'): kwargs['penalty']=a.penalty
    if a.question=='holding': kwargs['travel']=-.75
    case={'release':release_case,'structure':structure_case,'contact':contact_case,'holding':contact_case}[a.question](**kwargs)
    r=case.run(a.directory)
    print(json.dumps(dict(status=r.status,errors=r.errors,metrics=r.metrics,
                         strain=r.check_strain_limits() if r.completed else None),indent=2))
