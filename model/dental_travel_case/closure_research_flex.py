"""No-contact shell bending: orientation research, never a pull-off prediction.

1N uniform radial traction on one detent crest; the cropped lower rim is
clamped. A linear isotropic PETG hypothesis isolates geometry. Mesh refinement
tests displacement; sharp-corner peak strain is retained without a strength PASS.
"""
from pathlib import Path
import sys
from physical_analysis import StructuralQuestion,Region,Support,SurfaceForce,Material,QuestionStudy
from physical_analysis.evidence import retain_run
import closure_research_design as design

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/closure_research'
MATERIAL=Material('Uncalibrated PETG comparison',1200,.38,
    'Assumed effective isotropic short-term modulus. Not measured FDM data; no strength limit supplied.')


def question(kind):
    if kind not in ('shell_broad','shell_end','slide_wall'):raise ValueError(kind)
    parts=design.sample(kind)
    if kind=='shell_broad':
        r=design.D.sleeve_depth/2+design.D.detent
        pad=Region((-5,r,248.75),(5,r,249.25))
        force=(0,-1,0);base_z=158
    elif kind=='shell_end':
        r=design.D.sleeve_width/2+design.D.detent
        pad=Region((r,-5,248.75),(r,5,249.25))
        force=(-1,0,0);base_z=158
    else:
        pad=Region((38.5,6,44),(38.5,14,49.2))
        force=(1,0,0);base_z=0
    return StructuralQuestion(name='research_'+kind,part=parts['body'],material=MATERIAL,
        supports=(Support(Region.plane('z',base_z)),),forces=(SurfaceForce(pad,force),),
        observations={'pad':pad},mesh_size_mm=2.5,nonlinear=False,max_increment=1.)


def run(kind,directory,evidence_directory):
    if evidence_directory.exists():
        raise ValueError('Choose a new compact evidence directory before running: '+str(evidence_directory))
    study=QuestionStudy(question(kind),decision='Compare shell flexibility, not retention force; ~10% displacement precision suffices for orientation ranking',
        metrics=('max_displacement_mm',),relative_tolerance=.10,mesh_levels=1)
    result=study.run(directory)
    print(kind,result.status,result.metrics.get('question'),flush=True)
    for label in ('baseline','mesh_sensitivity_1'):
        source=directory/label
        if source.exists():retain_run(source,evidence_directory/label)


if __name__=='__main__':
    if len(sys.argv)!=4:raise SystemExit('Usage: closure_research_flex.py KIND NEW_NATIVE_DIRECTORY NEW_COMPACT_DIRECTORY')
    run(sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]))
