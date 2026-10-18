"""M3 prototype: scoped evidence, with unknown physical retention left visible."""
import hashlib
import json
from pathlib import Path

from product_verification import (Plan,Question as Q,Evidence,Status,Directive,
    UserSource,DesignDecision,Hypothesis,CalculationInconclusive,assertion_check,
    protect_recorded_intent)
from m1_verification import requirements

ROOT=Path(__file__).resolve().parent
RECORD='notes/m3.md'


def hashed(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_sources(record,key):
    for file,sha in record[key].items():
        if hashed(ROOT/file)!=sha:
            raise CalculationInconclusive('Evidence predates '+file)


def make_m3_plan(variant,baseline):
    if variant!='slim-m3':raise ValueError(variant)
    intent=requirements(baseline)
    protect_recorded_intent(ROOT,intent)
    scope={'design':variant,'revision':'M3 unprinted prototype',
           'material':'uncalibrated effective PETG E800..2200 MPa',
           'process':'diagnostic 0.4mm nozzle, 0.2mm layers'}
    questions=(
        Q('capture','closure.secure','Both actual flat retaining lands engage and sampled intended operations clear','CAD'),
        Q('proxy','closure.secure','Declared elastica/contact-direction and receiver hypotheses expose weak M1 routes and compare M3 across their uncertainty range','analytical'),
        Q('holding','closure.secure','Actual complete mechanism remains closed under backpack disturbances, including peel and loss of one catch','physical'),
        Q('guide','closure.secure','Long guide provides bearing; reduced bearing-couple estimates show the effects and limits of wall compliance','analytical'),
        Q('operation','closure.end-retention','Force-loaded actual local leaf retracts far enough in declared isolated-root fixture; strain is reported without material acceptance','numerical'),
        Q('comfort','closure.end-retention','Both controls are easy to press, recover and release in actual printed use','physical'),
        Q('aperture','brush.fit','Established individual brush proxy clears revised enclosure','CAD'),
        Q('aperture','paste.fit','Established individual tube proxy clears revised enclosure','CAD'),
        Q('variation','paste.fit','Combined actual contents and alternative tubes load easily','physical'),
        Q('width','form.width-revision','Earlier exact 74.2mm maximum width is preserved','CAD'),
        Q('rounds','form.end-rounds','Handled R4 end geometry preserved','CAD'),
        Q('slice','print.supportfree','Current prototype pair smoke-slices and consequential support locations are inspected','slicer'),
        Q('supportfree','print.supportfree','Actual prototype prints without supports with adequate bridges and free mechanisms','physical'),
        Q('life','print.material','Printed fatigue, recovery, creep and tolerance are adequate','physical'),
        Q('protection','travel.protection','Complete loaded case protects real contents','physical'),
        Q('trial','test.fit','A further physical test supplies actual retention evidence','physical'),
        Q('judgment','form.minimal','Whole-object compactness and controls are acceptable','subjective'),
    )
    def cad():
        data=json.loads((ROOT/'notes/m3/cad.json').read_text())
        require_sources(data,'sources')
        assert data['producer_sha256']==hashed(ROOT/'m3_checks.py')
        assert data['status']=='PASS' and not data['failures']
        assert len(data['poses'])==217
        for side in ('-1','1'):
            assert abs(sum(f['area_mm2'] for f in data['lands'][side])-13.5)<1e-6
    def proxy():
        data=json.loads((ROOT/'notes/m3/proxy.json').read_text())
        require_sources(data,'source_sha256')
        assert data['producer_sha256']==hashed(ROOT/'retention_proxy.py')
        old=data['variants']['M1']['capture_sensitivity']
        new=data['variants']['M3']['capture_sensitivity']
        assert len(old)==len(new)==18
        for a,b in zip(old,new,strict=True):
            assert (a['modulus_MPa'],a['fit_loss_mm'],a['receiver_end_fixity'])==(b['modulus_MPa'],b['fit_loss_mm'],b['receiver_end_fixity'])
            assert a['first_flat_capture_loss_per_catch_N'] is not None
            assert b['first_flat_capture_loss_per_catch_N'] is None or b['first_flat_capture_loss_per_catch_N']>a['first_flat_capture_loss_per_catch_N']
        assert any(not x['guide_small_bending_scope'] for x in data['variants']['M3']['handling_scenarios'])
    def operation():
        data=json.loads((ROOT/'notes/m3/evidence_association.json').read_text())
        require_sources(data,'inputs')
        require_sources(data,'outputs')
        result=json.loads((ROOT/'notes/retention/dental_m3_press_7/result.json').read_text())
        assert result['completed']
        assert result['metrics']['observations']['tooth']['min_mm'][0]>2.
        assert result['metrics']['max_force_balance_relative']<1e-4
    def sliced():
        data=json.loads((ROOT/'notes/m3/evidence_association.json').read_text())
        require_sources(data,'inputs')
        require_sources(data,'outputs')
        receipt=json.loads((ROOT/'notes/m3/export_slice.json').read_text())
        assert receipt['ok'] and receipt['geometry']['valid'] and receipt['slice']['ok']
        assert receipt['slice']['input_sha256']==hashed(ROOT/'m3_case.stl')
        assert (ROOT/'notes/m3/toolpaths.json').is_file()
        # Probe generation stays visible; successful slicing is not support-free proof.
    def width():
        from m3_design import D
        assert abs(D.width+2*D.skin_reinforcement-74.2)<1e-6,'M3 maximum width 77mm; explicit prototype compromise, no waiver of historical exact width criterion'
    groups=(('m3.cad',(('closure.secure','capture'),('brush.fit','aperture'),('paste.fit','aperture'),('form.end-rounds','rounds')),cad,'notes/m3/cad.json'),
        ('m3.proxy',(('closure.secure','proxy'),('closure.secure','guide')),proxy,'notes/m3/proxy.json'),
        ('m3.operation',(('closure.end-retention','operation'),),operation,'notes/retention/dental_m3_press_7/result.json'),
        ('m3.slice',(('print.supportfree','slice'),),sliced,'notes/m3/export_slice.json'),
        ('m3.width',(('form.width-revision','width'),),width,'m3_design.py'))
    return Plan(variant,intent,scope,questions=questions,
        checks=tuple(assertion_check(id,targets,run,ref,scope) for id,targets,run,ref in groups),
        retained=(Evidence('m1.failed.reference',(('closure.secure','holding'),),Status.FAIL,
            'Printed M1 separated without controls. Negative reference; no new M3 physical result.',
            'notes/m1.md#full-box-print-feedback--2026-10-15',{'design':'slim-m1'}),),
        directives=(Directive('m3.practical','Deliver a practical revision with adapted simulation and SVG explanations; liner excluded; no physical print requested',
            UserSource(RECORD,'User requests practical proxy/adaptation after full solver limits, new model, cross-section SVGs, no liner work and restrained final review')),),
        decisions=(DesignDecision('m3.prototype','30mm guide, 2mm leaves, 9mm catches and stronger receiver skin; 75mm main/77mm maximum width preserves contents clearance',RECORD),),
        hypotheses=(Hypothesis('m3.contact','Rotating-edge and fixed-world reactions bracket particular contact hypotheses, not all actual contact trajectories; pocket/guide strip compliance is uncalibrated',RECORD),))
