"""Read retained native evidence; no reruns, scoring or inferred qualification."""
import argparse
import hashlib
import json
from pathlib import Path
from physical_analysis import AnalysisResult
from physical_analysis.studies import compare_results

ROOT=Path(__file__).resolve().parent
EVIDENCE=ROOT/'notes/retention'


def read(name):
    result=AnalysisResult(**json.loads((EVIDENCE/name/'result.json').read_text()))
    actual=hashlib.sha256((EVIDENCE/name/'case.json').read_bytes()).hexdigest()
    recorded=result.provenance.get('case_sha256')
    if (recorded is None and result.completed) or (recorded is not None and recorded!=actual):
        raise ValueError('Retained case identity differs: '+name)
    return result


def summarize():
    names=('dental_m1_eccentric_12','dental_m1_land_12','dental_m1_exact_land_12',
           'dental_m1_exact_soft','dental_m1_exact_stiff','dental_m1_exact_mesh08',
           'dental_m1_land_curved08','dental_m1_full_curv8',
           'dental_m1_stub_land_12','dental_m2b_land_12','dental_m2b_land_fullwidth_12',
           'dental_m1_full_pickup','dental_m1_crop_pickup_febio',
           'dental_m1_full_pickup_febio','dental_m1_crop_ilut_pickup',
           'dental_m1_crop_ilut50_pickup')
    records={}
    for name in names:
        result=read(name)
        case=json.loads((EVIDENCE/name/'case.json').read_text())
        records[name]=dict(status=result.status,completed=result.completed,
            errors=result.errors,material=case['parts'][0]['material'],
            mesh=result.provenance.get('mesh'),
            loaded_areas=result.provenance.get('loads'),
            shoulder=result.metrics.get('observations',{}).get('shoulder'),
            peak_strain=result.metrics.get('max_abs_principal_strain'),
            max_force_balance_relative=result.metrics.get('max_force_balance_relative'),
            resources=result.provenance.get('execution_resources'),
            case_sha256=hashlib.sha256((EVIDENCE/name/'case.json').read_bytes()).hexdigest())
    comparison=compare_results(read('dental_m1_exact_land_12'),read('dental_m1_land_curved08'),
        metrics=('max_displacement_mm','max_abs_principal_strain'),relative_tolerance=.10)
    fair={}
    for name,area in [('dental_m1_stub_land_12',12.),('dental_m2b_land_fullwidth_12',13.5)]:
        result=read(name)
        actual=result.provenance['loads'][0]['area_mm2']
        if not result.completed or abs(actual-area)>1e-6:
            raise ValueError('Incomplete or partial receiving-land traction: '+name)
        fair[name]=dict(actual_loaded_area_mm2=actual,
            inward_shoulder_mean_mm=result.metrics['observations']['shoulder']['mean_mm'][0],
            peak_strain=result.metrics['max_abs_principal_strain'])
    return dict(fair_root_stub_traction_comparison=fair,scope='Actual-CAD M1 eccentric axial-traction diagnostic, not holding force. '
                     'Full-contact attempt incomplete; no product approval.',
                records=records,mesh_comparison=comparison,
                interpretation='Inward retraction is robust to declared material and mesh choices. '
                    'Local strain does not meet the requested 10% mesh comparison. '
                    'The imposed traction does not follow migrating receiver contact; no release barrier follows.',
                m1_source_sha256=hashlib.sha256((ROOT/'m1_design.py').read_bytes()).hexdigest())


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('destination',type=Path)
    a=p.parse_args()
    answer=summarize()
    a.destination.write_text(json.dumps(answer,indent=2,allow_nan=False)+'\n')
    print(json.dumps(answer,indent=2,allow_nan=False))
