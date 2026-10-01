"""Generate the thread comparison from retained results, without launching solves."""
import gzip
import json
from pathlib import Path
from physical_analysis.results import AnalysisResult
from physical_analysis.studies import compare_results


def summarize(*, write=True):
    root=Path(__file__).resolve().parents[3]
    groups={
        'compression':('physical_analysis/experiments/ipc/performance/compression_threads_', (1,2,4,8,16),'push'),
        'rounded_snap_prefix':('physical_analysis/experiments/ipc/performance/rounded_snap_prefix_threads_', (1,8,16),'drive')}
    result={}
    for group,(prefix,counts,motion) in groups.items():
        rows=[];baseline=None
        for n in counts:
            path=root/(prefix+str(n));r=AnalysisResult(**json.loads((path/'result.json').read_text())).require_completed()
            if baseline is None:baseline=r
            for key in ('input_sha256','mesh_sha256','executable_sha256'):
                if r.provenance[key]!=baseline.provenance[key]:raise ValueError('Performance candidates differ beyond threading')
            if r.metrics['independent_mesh_intersection']:raise ValueError('Intersecting performance candidate')
            if r.metrics['accepted_time_interval']!=baseline.metrics['accepted_time_interval']:
                raise ValueError('Performance candidates have different physical time intervals')
            comparison=compare_results(baseline,r,metrics=(f'peak_motion_force_N.{motion}',
                'max_abs_principal_strain','max_displacement_mm'),relative_tolerance=.01)
            if not all(v['passes'] for v in comparison.values()):raise ValueError('Threading materially changes the result')
            mesh=json.loads(gzip.decompress((path/'mesh.json.gz').read_bytes()))
            rows.append(dict(threads=n,run=prefix+str(n),status=r.status,
                **r.provenance['native_timing'],speedup=baseline.provenance['native_timing']['wall_seconds']/r.provenance['native_timing']['wall_seconds'],
                force_N=r.metrics['peak_motion_force_N'][motion],displacement_mm=r.metrics['max_displacement_mm'],
                peak_Green_strain=r.metrics['max_abs_principal_strain'],
                independent_mesh_intersection=r.metrics['independent_mesh_intersection'],
                max_free_dof_residual_N=r.metrics['max_free_dof_residual_norm_N'],
                max_balance_relative=r.metrics['max_force_balance_relative'],
                native_operation_completed=r.metrics['native_operation_completed'],
                accepted_time_interval=r.metrics['accepted_time_interval'],time_steps=mesh['steps'],
                comparison_with_one_thread=comparison,
                mesh={name:dict(nodes=len(m['points_mm']),tetrahedra=len(m['tets']),triangles=len(m['triangles']))
                      for name,m in mesh['parts'].items()},
                input_sha256=r.provenance['input_sha256'],mesh_sha256=r.provenance['mesh_sha256'],
                executable_sha256=r.provenance['executable_sha256']))
        result[group]=dict(fastest_tested_threads=min(rows,key=lambda r:r['wall_seconds'])['threads'],runs=rows)
    result['machine']=json.loads((Path(__file__).with_name('performance')/'machine.json').read_text())['machine']
    result['limits']='One timed solve per configuration; no universal optimum or formal timing statistics. Native process wall/CPU time includes initialization and native I/O, excludes Python extraction. Prefix completion is not snap passage. One-percent comparison is a numerical equivalence screen, not physical validation.'
    output=Path(__file__).with_name('performance')/'summary.json'
    if write:
        output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return result


if __name__=='__main__':
    d=summarize()
    for group in ('compression','rounded_snap_prefix'):
        print(group,d[group]['fastest_tested_threads'])
        for r in d[group]['runs']:print(r['threads'],round(r['wall_seconds'],2),round(r['cpu_percent'],1),round(r['speedup'],3))
