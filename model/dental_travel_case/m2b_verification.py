"""M2B evidence composition; independent scopes, no numerical promotion gate."""
import hashlib
import json
import math
from pathlib import Path
from product_verification import (Plan,Question as Q,Evidence,Status,Check,Directive,
    UserSource,DesignDecision,Hypothesis,CalculationInconclusive,assertion_check,
    protect_recorded_intent)
from m1_verification import requirements

ROOT=Path(__file__).resolve().parent
RECORD='notes/m2.md'


def require_guide_evidence(data, axial_play):
    """Validate contact witnesses without imposing a new angular design target."""
    def samples(records, lifts, optional_lifts=()):
        required={(lift,axis,sign) for lift in lifts for axis in ('x','y') for sign in (-1,1)}
        allowed=required|{(lift,axis,sign) for lift in optional_lifts for axis in ('x','y') for sign in (-1,1)}
        actual={(r['lift_mm'],r['axis'],r['direction']) for r in records}
        assert required<=actual<=allowed and len(records)==len(actual), 'Missing or duplicate guide poses'
        resolution=data['angle_resolution_deg']
        assert math.isfinite(resolution) and resolution>0, 'Invalid angle resolution'
        for record in records:
            angle=record['angle_deg']
            bracket=record.get('bracket_deg')
            assert angle is not None and math.isfinite(angle), 'Guide contact was not established'
            assert bracket is not None and len(bracket)==2 and all(math.isfinite(v) for v in bracket), 'Missing guide bracket'
            lo,hi=bracket
            assert 0<=lo<=angle<=hi<=3 and hi-lo<=resolution+1e-12, 'Invalid guide search witness'
    # Earlier receipts also retain .9 mm samples, duplicated in the comparison.
    samples(data['rigid_guide_angular_freeplay'], (0,axial_play/2,axial_play), (.9,))
    comparison=data['baseline_m1_guide_comparison']
    for key in ('samples','m2b_same_pose_samples'):
        samples(comparison[key], (.325,.65,.9))


def make_m2b_plan(variant,baseline):
    if variant!='slim-m2b':
        raise ValueError(variant)
    intent=requirements(baseline)
    protect_recorded_intent(ROOT,intent)
    scope={'design':variant,'revision':'M2B computational research; unprinted',
           'material':'uncalibrated effective PETG hypotheses','process':'proposed0.4nozzle/0.2layers'}
    questions=(
        Q('engagement','closure.secure','Both actual flat retaining lands and declared return/release pose samples have source-associated CAD evidence; no holding-force implication','CAD'),
        Q('guidance','closure.secure','Actual long guide limits tested seam-pivot rocking under declared fixed pose; loaded stiffness is separate','CAD'),
        Q('pull-off','closure.secure','Full deformable case contact resolves axial/off-axis/peel/rock release routes with qualified load, contact, numerical and material sensitivity; negative M1 benchmark challenged','numerical'),
        Q('operation','closure.end-retention','Actual conforming/flat pad support alternatives and release margins, strain and numerical uncertainty resolved for declared loading range','numerical'),
        Q('physical','closure.secure','Printed mechanism retains and releases in travel use with actual contents','physical'),
        Q('aperture','brush.fit','Brush proxy individually passes revised body/mouth with declared clearance','CAD'),
        Q('aperture','paste.fit','55x40box individually passes revised body/mouth; not simultaneous easy packing','CAD'),
        Q('variation','paste.fit','Actual combined contents and alternative tubes load easily through extended sleeve','physical'),
        Q('width','form.width-revision','Preserve the earlier exact25mm exterior-width reduction, including local receiver reinforcement','CAD'),
        Q('rounds','form.end-rounds','Preserve large handled end rounds','CAD'),
        Q('layers','print.supportfree','Targeted first-feature sections stay connected; slicing/support probe remains separate','CAD'),
        Q('slice','print.supportfree','Current paired exports/layout are accepted by named Orca setup with support/path review','slicer'),
        Q('life','print.material','Printed recovery, creep, fatigue and tolerances are physically established','physical'),
        Q('protection','travel.protection','Actual full loaded case protects contents against outside handling loads','physical'),
        Q('trial','test.fit','No new physical print requested; computational coupons do not imply a new printed sample','physical'),
        Q('judgment','form.minimal','User accepts revised whole-object compactness, raised controls and handling','subjective'),
    )
    def cad_record():
        path=ROOT/'notes/retention/m2b_geometry.json'
        if not path.is_file():
            raise CalculationInconclusive('Missing candidate geometric evidence')
        data=json.loads(path.read_text())
        for name in ('m1_design','m2b_design'):
            if hashlib.sha256((ROOT/(name+'.py')).read_bytes()).hexdigest()!=data['source_sha256'][name]:
                raise CalculationInconclusive('Candidate geometry report predates '+name)
        producer=hashlib.sha256((ROOT/'retention_m2b_checks.py').read_bytes()).hexdigest()
        if data.get('producer_sha256')!=producer:
            raise CalculationInconclusive('Candidate geometry producer changed; review retained evidence association')
        from m2b_design import D
        require_guide_evidence(data,D.axial_play)
        assert data['status']=='PASS',data.get('operation_failures')
        assert data['first_layer_connectivity']['status']=='PASS'
    targets=(('closure.secure','engagement'),('closure.secure','guidance'),('brush.fit','aperture'),
             ('paste.fit','aperture'),('form.end-rounds','rounds'),('print.supportfree','layers'))
    cad=assertion_check('m2b.cad',targets,cad_record,'notes/retention/m2b_geometry.json',scope)
    def width():
        from m2b_design import D
        maximum=D.width+2*D.skin_reinforcement
        assert abs(maximum-74.2)<1e-6,f'Local reinforcement width is {maximum}mm; main shell74.2mm. Earlier exact25mm overall reduction is not met.'
    checks=(cad,assertion_check('m2b.width',(('form.width-revision','width'),),width,'m2b_design.py',scope))
    numerical_history=[]
    operation=ROOT/'notes/retention/dental_m2b_press_study/study_result.json'
    if operation.is_file():
        studied=json.loads(operation.read_text())
        confidence=studied['metrics']['question']
        numerical_history.append(Evidence('m2b.operation.inconclusive',
            (('closure.end-retention','operation'),),Status.INCONCLUSIVE,
            'The isolated force-pad study completed but peak strain is mesh-sensitive '
            f"(numerical_evidence_adequate={confidence['numerical_evidence_adequate']}); "
            'The actual-root study demonstrates a channel-clear retracting pose, but its '
            'peak strain remains mesh-sensitive and loaded cap operation is unresolved.',
            str(operation.relative_to(ROOT)),scope))
    if (ROOT/'notes/retention/dental_m1_full_pickup_febio/result.json').is_file():
        numerical_history.append(Evidence('m2b.retention.unresolved',
            (('closure.secure','pull-off'),),Status.INCONCLUSIVE,
            'The actual full-size M1 negative-reference contact model hit native memory '
            'limits. No qualified full-assembly opening-force or release-work comparison '
            'exists for M2B; geometric and local traction improvements do not answer it.',
            'notes/m2.md',scope))
    history=tuple(numerical_history)+(Evidence('m1.full-box.failure',(('closure.secure','physical'),),Status.FAIL,
        'Printed M1 releases without controls and has inadequate joint stability. Negative reference, not a physical result for M2B.',
        'notes/m1.md#full-box-print-feedback--2026-10-15',{'design':'slim-m1'}),)
    return Plan(variant,intent,scope,questions=questions,checks=checks,retained=history,
        directives=(Directive('m2b.no-print','Computational investigation only; no new print requested',
                    UserSource(RECORD,'User explicitly authorized a separate computational retention redesign and requested no new physical print')),),
        decisions=(DesignDecision('m2b.load-path','30mmguide, supported receiver and wider flat catches; raised controls with32mm leaves; rejected undercut alternative retained',RECORD),),
        hypotheses=(Hypothesis('m2b.qualification','Nominal geometric improvement does not establish unintended-opening resistance; native whole-case evidence and operation uncertainty remain decisive',RECORD),))
