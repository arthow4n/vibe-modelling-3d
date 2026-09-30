"""Generate fixed-mesh control evidence from retained runs; launch no solver."""
import gzip
import json
from pathlib import Path
from components import BUTTON_FRONT

ROOT=Path(__file__).resolve().parent
LABELS=('debug_fixed_increment01','debug_increment005','debug_increment0025')


def deck_without_increment(directory):
    lines=gzip.decompress((directory/'analysis.inp.gz').read_bytes()).decode().splitlines()
    index=lines.index('*STATIC')
    lines[index+1]='CONTROLLED STATIC INCREMENT'
    return lines


def without_lid_master_faces(lines):
    kept=[];omit=False
    for line in lines:
        if line.startswith('*'): omit=line=='*SURFACE,NAME=C0MASTER,TYPE=ELEMENT'
        if not omit or line.startswith('*'): kept.append(line)
    return kept


def main():
    baseline=None
    controls=[]
    for label in LABELS:
        directory=ROOT/'notes/analysis'/label
        case=json.loads((directory/'case.json').read_text())
        result=json.loads((directory/'result.json').read_text())
        deck=deck_without_increment(directory)
        if baseline is None: baseline=deck
        same=deck==baseline
        if not same: raise ValueError(f'{label}: control changes more than the static increment')
        controls.append(dict(run=label,input_sha256=result['provenance']['input_sha256'],
            same_native_input_except_static_increment=same,increment=case['max_increment'],
            max_lid_travel_per_closing_or_final_lift_increment_mm=40*case['max_increment'],
            status=result['status'],completed=result['completed']))
    scoped=ROOT/'notes/analysis/debug_mating_side01'
    result=json.loads((scoped/'result.json').read_text())
    case=json.loads((scoped/'case.json').read_text())
    same=without_lid_master_faces(deck_without_increment(scoped))==without_lid_master_faces(baseline)
    if not same: raise ValueError('Contact-scope control changes other native input')
    scope=dict(run='debug_mating_side01',status=result['status'],completed=result['completed'],
        same_native_input_except_lid_master_faces=same,
        lid_master_faces=result['provenance']['contacts'][0]['master']['face_count'],
        master_upper_y_mm=case['contacts'][0]['master']['region']['upper'][1],
        conservative_head_upper_y_mm=BUTTON_FRONT+max(h['observations']['head']['max_mm'][1] for h in result['history']))
    locations=[]
    for name in ('base','tight','increment005','increment0025'):
        data=json.loads((ROOT/f'notes/debug/{name}_contact_locations.json').read_text())
        for frame in data['frames']:
            worst=max(frame['faces'],key=lambda f:f['peak_penetration_mm'])
            locations.append(dict(source=f'{name}_contact_locations.json',
                input_sha256=data['input_sha256'],load_fraction=frame['load_fraction'],
                element=worst['element'],face=worst['face'],
                reported_penetration_mm=worst['peak_penetration_mm'],
                reported_pressure_MPa=worst['peak_pressure_MPa'],
                sampled_lid_CAD=worst['sampled_rigid_CAD']['lid_catch']))
    answer=dict(controls=controls,contact_scope=scope,contact_locations=locations,
        limits='Native deck equality verifies fixed nodes/elements, material, contacts and boundary curves. '
               'Only the static increment line differs. Failed-quality results remain unqualified; '
               'sampled CAD distances are not full intersections or the solver\'s unreported contact quadrature locations. '
               'Stage metrics remain in ../numerical_summary.json rather than a second history table.')
    (ROOT/'notes/debug/summary.json').write_text(json.dumps(answer,indent=2)+'\n')
    print(json.dumps(dict(controls=controls,contact_frames=len(locations)),indent=2))


if __name__=='__main__': main()
