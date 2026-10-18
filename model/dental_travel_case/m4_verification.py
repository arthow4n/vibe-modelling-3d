"""M4: actual contact order, matching coupon and scoped retained evidence."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from product_verification import (Plan,Question as Q,Evidence,Status,Directive,
    UserSource,DesignDecision,Hypothesis,CalculationInconclusive,assertion_check,protect_recorded_intent)
from m1_verification import requirements

ROOT=Path(__file__).resolve().parent
RECORD='notes/m4.md'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def require_sources(records):
    for name,digest in records.items():
        if sha(ROOT/name)!=digest:raise CalculationInconclusive('Evidence predates '+name)


def current_publication(artifact):
    if artifact not in ('case','joint'):raise ValueError(artifact)
    data=json.loads((ROOT/'notes/m4/publication.json').read_text())
    require_sources(data['inputs'])
    require_sources(data['artifacts'][artifact])
    return data


def visual_evidence():
    directory=ROOT/'notes/overlap_exploration'
    data=json.loads((directory/'contact_sequence.json').read_text())
    require_sources(data['source_sha256'])
    for name in ('case_motion','catch_before_guide','overlap_choice'):
        document=ET.parse(directory/(name+'.svg'))
        block=document.find('{http://www.w3.org/2000/svg}metadata')
        if block is None:raise CalculationInconclusive('Missing visual source association')
        association=json.loads(block.text)
        assert association['data_sha256']==sha(directory/'contact_sequence.json')
        assert association['generator_sha256']==sha(ROOT/'overlap_drawings.py')
    old,new=data['cases']['M3_overlap_30_floating'],data['cases']['M4']
    assert old['first_catch_contact_deg']<old['guide_only_onset']['angle_deg']
    assert sum(old['hook_intersection_at_guide_only_pose_mm3'].values())>1e-5
    assert new['guide_only_onset']['angle_deg']<new['first_catch_contact_deg']
    from m4_design import D
    assert new['transverse_shift_mm']==D.lap_clearance
    assert max(new['hook_intersection_at_guide_only_pose_mm3'].values())<1e-5
    assert new['depth_rocking']['guide']['angle_deg']<min(x['angle_deg'] for x in new['depth_rocking']['catches'].values() if x['angle_deg'] is not None)
    varied=[v for k,v in data['cases'].items() if k.startswith('M4_fit_')]
    assert len(varied)==9
    for case in varied:
        low=min(x['tooth_centroid_axial_rise_mm'] for x in case['proxy_contact_edge_controls'])
        assert case['demanded_far_land_axial_motion_mm']<low
    rejected=data['cases']['M4_rejected_centered_only']
    assert rejected['demanded_far_land_axial_motion_mm']>min(x['tooth_centroid_axial_rise_mm'] for x in rejected['proxy_contact_edge_controls'])
    diagonal=json.loads((directory/'diagonal_witness.json').read_text())
    require_sources(diagonal['source_sha256'])
    assert diagonal['cases']['nominal']['guide_angle_deg']<diagonal['cases']['nominal']['catch_angle_deg']
    for case in diagonal['cases'].values():
        assert case['maximum_corner_axial_demand_mm']<case['minimum_proxy_axial_rise_mm']
    return data


def make_m4_plan(variant,baseline):
    if variant!='slim-m4':raise ValueError(variant)
    intent=requirements(baseline)
    protect_recorded_intent(ROOT,intent)
    scope={'design':variant,'revision':'M4 unprinted prototype',
        'material':'uncalibrated effective PETG hypotheses','process':'0.4mm nozzle /0.2mm diagnostic PETG'}
    questions=(
        Q('capture','closure.secure','Actual flat capture, return and withdrawal have current CAD evidence','CAD'),
        Q('contact-order','closure.secure','Committed scale drawings and actual CAD witness first guide/catch contacts; old blocked ghost poses are identified','CAD'),
        Q('holding','closure.secure','Complete printed case holds under backpack handling and unintended release routes','physical'),
        Q('operation','closure.end-retention','Current leaf is the studied M3 pressure-fixture leaf after a rigid translation; whole-cap release contact remains separate','numerical'),
        Q('comfort','closure.end-retention','Printed controls release comfortably and recover','physical'),
        Q('aperture','brush.fit','Established individual brush proxy clears the extended sleeve','CAD'),
        Q('aperture','paste.fit','Established individual tube proxy passes extended sleeve','CAD'),
        Q('variation','paste.fit','Real combined contents and alternative tubes load comfortably','physical'),
        Q('width','form.width-revision','Historical exact74.2mm maximum width criterion','CAD'),
        Q('rounds','form.end-rounds','Handled end rounds preserved','CAD'),
        Q('slice','print.supportfree','Current full-case export pair smoke-slices with inspected support/bridge locations','slicer'),
        Q('physical','print.supportfree','Printed bridges and free mechanisms are adequate without supports','physical'),
        Q('life','print.material','Printed layer strength, fatigue and creep are adequate','physical'),
        Q('protection','travel.protection','Actual contents remain protected under use','physical'),
        Q('sample','test.fit','Current sample retains full guide, both roots and receivers from the same production source','CAD'),
        Q('sample-slice','test.fit','Current sample pair matches current full-case source version and slice','slicer'),
        Q('trial','test.fit','Physical observations are available from the current sample','physical'),
        Q('judgment','form.minimal','Current full-case handling and prolonged insertion are accepted','subjective'))
    def cad():
        data=json.loads((ROOT/'notes/m4/cad.json').read_text())
        require_sources(data['source_sha256'])
        assert data['producer_sha256']==sha(ROOT/'m4_checks.py')
        assert data['status']=='PASS' and all(p['clear'] for p in data['poses'])
        assert data['sample']['root_support_and_receiver_preserved']
    def operation():
        cad()
        data=json.loads((ROOT/'notes/m4/cad.json').read_text())
        assert data['unchanged_m3_catch_symmetric_difference_mm3']<1e-6
        association=json.loads((ROOT/'notes/m3/evidence_association.json').read_text())
        require_sources(association['inputs'])
        require_sources(association['outputs'])
        result=json.loads((ROOT/'notes/retention/dental_m3_press_7/result.json').read_text())
        assert result['completed'] and result['metrics']['observations']['tooth']['min_mm'][0]>2
    def sliced(kind):
        current_publication(kind)
        report=json.loads((ROOT/('notes/m4/'+kind+'_export_slice.json')).read_text())
        assert report['ok'] and report['geometry']['valid'] and report['slice']['ok']
        assert (ROOT/('notes/m4/'+kind+'_toolpaths.json')).is_file()
    def width():
        from m4_design import D
        assert abs(D.width+2*D.skin_reinforcement-74.2)<1e-6,'Local maximum width77mm remains an explicit prototype compromise'
    groups=(('m4.cad',(('closure.secure','capture'),('brush.fit','aperture'),('paste.fit','aperture'),('form.end-rounds','rounds'),('test.fit','sample')),cad,'notes/m4/cad.json'),
        ('m4.visual',(('closure.secure','contact-order'),),visual_evidence,'notes/overlap_exploration/catch_before_guide.svg'),
        ('m4.operation',(('closure.end-retention','operation'),),operation,'notes/m4/cad.json'),
        ('m4.slice',(('print.supportfree','slice'),),lambda:sliced('case'),'notes/m4/case_export_slice.json'),
        ('m4.sample-slice',(('test.fit','sample-slice'),),lambda:sliced('joint'),'notes/m4/joint_export_slice.json'),
        ('m4.width',(('form.width-revision','width'),),width,'m4_design.py'))
    return Plan(variant,intent,scope,questions=questions,
        checks=tuple(assertion_check(id,targets,run,ref,scope) for id,targets,run,ref in groups),
        retained=(Evidence('m1.failed.reference',(('closure.secure','holding'),),Status.FAIL,
            'Printed M1 releases without controls; negative reference, no M4 physical result.',
            'notes/m1.md#full-box-print-feedback--2026-10-15',{'design':'slim-m1'}),),
        directives=(Directive('m4.visual-proof','Investigate whether motion matters physically; commit exploration drawings and update full model plus sample together if corrected',
            UserSource(RECORD,'User requested scale exploration evidence, mechanism correction if benefit is insufficient, synchronized test piece and reusable workflow')),),
        decisions=(DesignDecision('m4.guide-first','78mm overlap, .15mm side clearance and .40mm axial play route nominal peeling into guide bearing before catch load',RECORD),),
        hypotheses=(Hypothesis('m4.limits','Guide-first CAD contact is not a physical holding-force or wall-strength rating; gap/contact/material uncertainties remain visible',RECORD),))
