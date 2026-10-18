"""Bounded force-loaded release-pad study; no retention-force inference."""
import argparse
import json
from pathlib import Path
from physical_analysis import QuestionStudy
from physical_analysis.evidence import retain_run
from retention_structure import press_force_question

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant',choices=('m1','m2b'),required=True)
    p.add_argument('--modulus',type=float,required=True)
    p.add_argument('--mesh',type=float,required=True)
    p.add_argument('--load',type=float,required=True)
    p.add_argument('destination',type=Path)
    a=p.parse_args()
    question=press_force_question(variant=a.variant,modulus=a.modulus,mesh=a.mesh,load=a.load)
    study=QuestionStudy(question,decision='Resolve release travel and root strain under a conforming pad press, '
        'including force-increment and mesh sensitivity before choosing a provisional operating range.',
        metrics=('max_displacement_mm','max_abs_principal_strain'),relative_tolerance=.10,
        motion_levels=1,mesh_levels=1)
    answer=study.run(a.destination.resolve())
    archive=Path(__file__).resolve().parent/'notes/retention'/a.destination.name
    for child in sorted(a.destination.iterdir()):
        if child.is_dir() and (child/'result.json').is_file():
            retain_run(child,archive/child.name)
    (archive/'study_result.json').write_text(json.dumps(answer.to_dict(),indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(status=answer.status,question=answer.metrics['question']),indent=2))
