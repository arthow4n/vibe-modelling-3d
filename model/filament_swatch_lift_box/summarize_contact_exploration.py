"""Generate the alternate-formulation record from retained native evidence."""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def main(labels):
    labels=labels or sorted(p.name for p in (ROOT/'notes/analysis').glob('explore_*') if p.is_dir())
    rows=[]
    for label in labels:
        directory=ROOT/'notes/analysis'/label
        case=json.loads((directory/'case.json').read_text())
        result=json.loads((directory/'result.json').read_text())
        progress_path=directory/'progress.json'
        progress=json.loads(progress_path.read_text()) if progress_path.exists() else None
        metrics=result['metrics']
        rows.append(dict(run=label,backend=result['provenance'].get('backend'),status=result['status'],
            completed=result['completed'],mesh_mm={p['name']:p['mesh_size_mm'] for p in case['parts']},
            mesh_from=result['provenance'].get('mesh_reuse',{}).get('input_sha256'),
            penalty_N_mm3=[c['penalty_N_mm3'] for c in case['contacts']],max_increment=case['max_increment'],
            formulation=case.get('febio') or [c['discretization'] for c in case['contacts']],
            input_sha256=result['provenance'].get('input_sha256'),native_input_sha256=result['provenance'].get('native_input_sha256'),
            peak_actuation_N=metrics.get('peak_motion_force_N'),peak_principal_strain=metrics.get('max_abs_principal_strain'),
            peak_strain_part=metrics.get('max_strain_part'),peak_strain_centroid_mm=metrics.get('max_strain_element_centroid_mm'),
            native_max_penetration_mm=metrics.get('max_penetration_mm'),max_force_balance_relative=metrics.get('max_force_balance_relative'),
            final_observations=metrics.get('observations'),last_converged_fraction=progress.get('last_converged_fraction') if progress else None,
            errors=result['errors']))
    answer=dict(runs=rows,limits='Native completion is distinct from model acceptance. Failed or incomplete operations have no successful whole-path metrics. Release-only cases assume an unloaded assembled state; they do not prove closing. Mesh-source identity is explicit; equal requested mesh size is not equal actual mesh. Numerical force tolerance is not a material property.')
    target=ROOT/'notes/contact_exploration';target.mkdir(parents=True,exist_ok=True)
    (target/'summary.json').write_text(json.dumps(answer,indent=2)+'\n')
    lines=['# Generated formulation exploration','',
           '| Run | Backend | Native/API outcome | Last saved fraction | Native overlap (mm) | Diagnostic peak actuation (N) | Diagnostic peak strain |',
           '| --- | --- | --- | ---: | ---: | --- | ---: |']
    def number(v):return '—' if v is None else f'{v:.6g}'
    for r in rows:
        forces='—' if r['peak_actuation_N'] is None else ', '.join(f'{k} {v:.3g}' for k,v in r['peak_actuation_N'].items())
        lines.append(f"| [{r['run']}](../analysis/{r['run']}/result.json) | {r['backend']} | {r['status']} | {number(r['last_converged_fraction'])} | {number(r['native_max_penetration_mm'])} | {forces} | {number(r['peak_principal_strain'])} |")
    lines.extend(('',answer['limits'],''))
    (target/'results.md').write_text('\n'.join(lines))
    print(json.dumps(dict(runs=len(rows),summary=str(target/'summary.json'))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('labels',nargs='*');a=p.parse_args();main(a.labels)
