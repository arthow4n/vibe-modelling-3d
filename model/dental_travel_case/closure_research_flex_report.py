"""Retain native shell displacements and draw their physical meaning."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
from dataclasses import replace
import numpy as np
from physical_analysis.backends.worker import saved_meshes,iter_dat
from closure_research_drawings import canvas,label,save,BLUE,ORANGE
from closure_research_flex import question

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/closure_research'


def report(directories):
    if len(directories)!=3:raise ValueError('Supply broad, end and slide native study directories')
    cases={};curves={}
    for kind,directory in zip(('shell_broad','shell_end','slide_wall'),directories):
        study=json.loads((directory/'study_result.json').read_text())
        run=directory/'mesh_sensitivity_1'
        answer=json.loads((run/'result.json').read_text())
        # Actual native geometry/fixture identity, even after an unrelated
        # candidate changes in the shared CAD source. Never rebind hashes alone.
        replace(question(kind),mesh_size_mm=1.75).read_evidence(run)
        assert answer['completed'] and answer['metrics']['question']['numerical_evidence_adequate']
        native_case=json.loads((run/'case.json').read_text())
        mesh=saved_meshes(native_case,run/'analysis.inp')['part']
        _,fields=list(iter_dat(run/'analysis.dat'))[-1]
        displacements={int(row[0]):row[1:] for row in fields['displacements']}
        axis=1 if kind=='shell_broad' else 0
        tangent=1-axis
        if kind!='slide_wall':
            radial=23.45 if axis==1 else 36.35
            points=[]
            for n,p in mesh['nodes'].items():
                if abs(p[tangent])<2.5 and radial-.1<=p[axis]<=radial+.7:
                    u=displacements[n]
                    points.append(dict(z_mm=p[2],radial_mm=p[axis],radial_displacement_mm=u[axis]))
            curves[kind]=points
        delta=abs(answer['metrics']['observations']['pad']['mean_mm'][axis])
        baseline=json.loads((directory/'baseline/result.json').read_text())
        old_delta=abs(baseline['metrics']['observations']['pad']['mean_mm'][axis])
        cases[kind]=dict(pad_mean_displacement_at_1N_mm=delta,
            pad_response_relative_mesh_change=abs(delta-old_delta)/delta,
            maximum_displacement_mm=answer['metrics']['max_displacement_mm'],
            max_principal_strain_at_1N=answer['metrics']['question']['peak_strain'],
            max_force_balance_relative=answer['metrics']['max_force_balance_relative'],
            displacement_range_E900_E1800_mm=[delta*1200/1800,delta*1200/900],
            solver_input_sha256=answer['provenance']['input_sha256'],
            mesh=answer['provenance']['mesh'],
            load_patch=answer['provenance']['loads'],
            numerical_confidence=study['metrics']['question']['numerical_confidence'])
        shutil.copyfile(directory/'study_result.json',OUT/'flex'/kind/'study_result.json')
    output=dict(scope='Linear no-contact 1N radial shell traction, clamped specimen base. No pull-off force, full contact or fatigue prediction.',
        source_sha256={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in
            ('m1_design.py','closure_research_design.py','closure_research_flex.py','closure_research_flex_report.py')},
        material=dict(E_MPa=1200,nu=.38,calibrated=False),cases=cases)
    (OUT/'flex_summary.json').write_text(json.dumps(output,indent=2)+'\n')
    (OUT/'deformation_witness.json').write_text(json.dumps(dict(scope=output['scope'],points=curves),indent=2)+'\n')
    items=canvas('The existing wall really can act as the spring',820)
    label(items,25,78,'Actual refined-mesh nodes at 1N. Blue = undeformed; orange = radial motion enlarged 10×; heights undeformed.',17)
    for col,kind in enumerate(('shell_broad','shell_end')):
        x0=col*600
        values=curves[kind]
        radial=23.45 if col==0 else 36.35
        xf=lambda r,z,x0=x0:(x0+245+24*(r-radial),140+4.5*(255-z))
        for point in values:
            for deformed,color in ((False,BLUE),(True,ORANGE)):
                r=point['radial_mm']+(10*point['radial_displacement_mm'] if deformed else 0)
                x,y=xf(r,point['z_mm'])
                items.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="1.5" fill="{color}"/>')
        label(items,x0+25,119,'R1: broad wall' if col==0 else 'R2: end wall',22)
        value=cases[kind]['pad_mean_displacement_at_1N_mm']
        label(items,x0+25,625,f'Mean crest retraction: {value:.3f} mm under 1N.',18)
        label(items,x0+25,659,'The bottom cut ring is clamped; the rim is free.',17)
    ratio=cases['shell_broad']['pad_mean_displacement_at_1N_mm']/cases['shell_end']['pad_mean_displacement_at_1N_mm']
    label(items,25,711,f'The broad wall is about {ratio:.1f}× more compliant in this fixture. That is a real geometry difference, not extra spring boxes.',18)
    label(items,25,749,'Both cap and body can flex during a real snap; these separate radial loads are not a holding-force simulation.',17)
    label(items,25,786,'Native inputs, mesh refinement, force balance and material assumptions are retained. PETG print behavior remains unmeasured.',16)
    save('wall_flexure',items,extra_sources=('closure_research_flex_report.py',),
         data_files=('notes/closure_research/flex_summary.json','notes/closure_research/deformation_witness.json'))
    print(json.dumps(output),flush=True)


if __name__=='__main__':report([Path(p) for p in sys.argv[1:]])
