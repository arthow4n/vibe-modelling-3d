"""Derive the compact numerical record from retained native/question evidence."""
import json
from pathlib import Path
import swatch_book_case as m

HERE=Path(__file__).parent

def summarize():
    checks=json.loads((HERE/'notes/product_checks.json').read_text())
    output={'physically_validated':False,'operations':{}}
    for operation in ('release','closing'):
        directory=HERE/'notes/analysis'/operation
        study=json.loads((directory/'study_result.json').read_text())
        rows=[]
        for label in study['metrics']['question']['study']['runs']:
            r=json.loads((directory/label/'result.json').read_text());q=r['metrics']['question']
            final=r['history'][-1]['observations']['free_leaf'] if r['history'] else None
            row={ 'run':label,'status':r['status'],'solver_completed':q['solver_completed'],
                 'operation_completed':q['operation_completed'],
                 'native_passage_checks':q['numerical_evidence_adequate'],
                 'peak_force_N':q['peak_actuation_force_N'],'peak_strain':q['peak_strain'],
                 'peak_strain_location_mm':q['peak_strain_location_mm'],
                 'provisional_design_screen_passes':q['design_screen_passes'],
                 'max_penetration_mm':q['max_penetration_mm'],
                 'force_balance_relative':q['max_force_balance_relative'],
                 'final_unloaded_leaf_max_error_mm':max(abs(v) for k in ('min_mm','max_mm') for v in final[k]) if final else None}
            if operation=='release' and r['history']:
                peak=min(r['history'],key=lambda h:abs(h['load_fraction']-.5))
                bead=peak['observations']['bead'];leaf=peak['observations']['free_leaf']
                row.update(bead_min_inward_mm=bead['min_mm'][1],leaf_max_inward_mm=leaf['max_mm'][1],
                    actual_arc_release_margin_mm=bead['min_mm'][1]-checks['retention']['circular_envelope_actual_arc_deflection_bound_mm'],
                    travel_stop_clearance_mm=m.LEAF_STOP_GAP-leaf['max_mm'][1])
                assert row['actual_arc_release_margin_mm']>.05
                assert row['travel_stop_clearance_mm']>0
            rows.append(row)
        output['operations'][operation]={'runs':rows,
            'selected_metrics_stable':study['metrics']['question']['selected_metrics_stable'],
            'numerical_confidence':study['metrics']['question']['numerical_confidence'],
            'study_stopping_reasons':study['metrics']['question']['study']['stopping_reason']}
    (HERE/'notes/analysis_summary.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))

if __name__=='__main__':summarize()
