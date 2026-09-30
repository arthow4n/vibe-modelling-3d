"""Structural question cross-check, leaving the cheaper joint equations intact.

Use a symmetry half of the real monolithic L-profile. This isolates the whole-L
beam assumption in load_checks.py, excluding lap/bolt compliance deliberately.
It is not a numerical load rating for the assembled plate.
"""
import argparse
import json
from pathlib import Path
from components import P, base, box
from measure_structure import section
from physical_analysis import (StructuralQuestion, Support, SurfaceForce, Region,
                               Material, ManufacturingAssumption)


def question(mesh=10, plain_back=False):
    end = P.width/2-P.end_chamfer if plain_back else P.width/2
    part = base().intersect(box(0,end,P.thickness,P.inner_height,0,P.thickness)) if plain_back else base().intersect(box(0,end,-1,P.height+1,-1,P.lip_height+1))
    anchor_y = P.thickness if plain_back else P.height
    return StructuralQuestion(name='plain_back_symmetry' if plain_back else 'whole_L_symmetry', part=part, part_name='plate',
        material=Material('book plate effective solid',800,.4,
            'Same explicit effective modulus as load_checks.py; not calibrated printed PETG'),
        supports=(Support(Region.plane('x',0),(0,None,None),'midspan_symmetry'),
                  Support(Region.plane('x',end),(None,None,0),'end_support'),
                  Support(Region(lower=(0,anchor_y,-1),upper=(0,anchor_y,P.lip_height+1)),
                          (None,0,None),'lateral_anchor')),
        forces=(SurfaceForce(Region.plane('x',0),(0,0,-3*9.81/2)),
                SurfaceForce(Region.plane('z',P.thickness),(0,0,-1.6*9.81/2))),
        observations={'midspan':Region.plane('x',0),'supported_end':Region.plane('x',end)},
        mesh_size_mm=mesh, nonlinear=False,
        manufacturing=ManufacturingAssumption('Effective homogeneous section assumption from the analytical record; actual lap, infill, warping and creep excluded.'))


def cross_check(result, plain_back=False):
    # Reuse the object's targeted CAD section routine; historical section hashes
    # predate repository source maintenance and are not current-build evidence.
    inertia = (P.inner_height-P.thickness)*P.thickness**3/12 if plain_back else section(base(),100)['Iy_mm4']
    span = P.width-2*P.end_chamfer if plain_back else P.width
    prediction = 3*9.81*span**3/(48*800*inertia)+5*1.6*9.81*span**3/(384*800*inertia)
    q = result.metrics['question']
    numerical = -q['deformation_mm']['midspan']['mean_mm'][2]
    comparison = dict(analytical_monolithic_sag_mm=prediction,numerical_mean_midspan_sag_mm=numerical,
        numerical_to_analytical=numerical/prediction,
        supported_end_max_abs_z_mm=max(abs(q['deformation_mm']['supported_end'][k][2]) for k in ('min_mm','max_mm')),
        peak_strain_location_mm=q['peak_strain_location_mm'],
        scope=('Actual CAD back clipped clear of lip/edge rounds; same plain-back sensitivity equation with clipped span/width.' if plain_back else
            'Half-span symmetry of actual continuous L-profile; face loads allow section distortion and twist absent from the beam equation.')+' Joint compliance excluded; book point and distributed plate loads use the analytical record assumptions.')
    # Wide tolerance checks the order and load path, not precision or acceptance.
    comparison['order_and_support_response_agree'] = (
        q['numerical_evidence_adequate'] and .5 < numerical/prediction < 1.5
        and comparison['supported_end_max_abs_z_mm'] < 1e-6
        and abs(q['peak_strain_location_mm'][0]) < P.width/4)
    return comparison


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('--mesh',type=float,default=10)
    parser.add_argument('--plain-back',action='store_true')
    args = parser.parse_args()
    result = question(args.mesh,args.plain_back).run(args.directory)
    result.require_completed()
    result.metrics['question']['structural_cross_check'] = cross_check(result,args.plain_back)
    result.write(args.directory/'result.json')
    print(json.dumps(result.metrics['question'],indent=2))
