"""Compose space recovery, preserved mechanism and physical unknowns for M5."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from product_verification import (Plan,Question,Directive,UserSource,DesignDecision,
    Hypothesis,CalculationInconclusive,assertion_check)
from m4_verification import make_m4_plan,visual_evidence as m4_visual

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/m5'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def require_sources(records):
    for name,digest in records.items():
        if sha(ROOT/name)!=digest:raise CalculationInconclusive('Evidence predates '+name)


def current_record(name):
    data=json.loads((OUT/name).read_text())
    require_sources(data['source_sha256'])
    return data


def current_publication(kind):
    if kind not in ('case','joint'):raise ValueError(kind)
    record=json.loads((OUT/'publication.json').read_text())
    require_sources(record['inputs']);require_sources(record['artifacts'][kind])
    return record


def cad():
    data=current_record('cad.json')
    assert data['producer_sha256']==sha(ROOT/'m5_checks.py')
    assert data['status']=='PASS' and all(p['clear'] for p in data['poses'])
    assert data['unchanged_m4_leaf_symmetric_difference_mm3']<1e-6
    assert all(r['old_receiver_strip_missing_mm3']<1e-5 for r in data['preserved_receiver_strips'])
    assert data['sample']['production_body_crop_and_complete_cap']


def space():
    data=current_record('space_study.json')
    old,new=(data['cases'][n] for n in ('M4','flat77'))
    gains=[new[f'central_volume_ml_{s}mm']-old[f'central_volume_ml_{s}mm'] for s in (2,4)]
    assert min(gains)>abs(gains[0]-gains[1]),'Gain unresolved by integration refinement'
    assert new['sections_mm2']['220']>old['sections_mm2']['220']
    assert new['individual_tube_gap_mm']>=.8
    assert data['cases']['flat75']['individual_tube_overlap_mm3']>0
    for name in ('interior_sections','guard_length','variants','corner_bearing'):
        block=ET.parse(OUT/(name+'.svg')).find('{http://www.w3.org/2000/svg}metadata')
        association=json.loads(block.text)
        assert association['data_sha256']==sha(OUT/'space_study.json')
        assert association['generator_sha256']==sha(ROOT/'m5_drawings.py')
        assert association['contact_sha256']==sha(OUT/'contact.json')
    return data


def contact():
    data=current_record('contact.json')
    nominal=data['cases']['nominal']
    assert all(nominal[axis]['guide_before_catch'] for axis in ('x','y'))
    assert nominal['diagonal']['guide_angle_deg']<nominal['diagonal']['catch_angle_deg']
    assert not data['cases']['short_guide_control']['y']['guide_before_catch']
    old=m4_visual()['cases']
    rejected_limit=min(p['tooth_centroid_axial_rise_mm'] for p in old['M4_fit_0.2_0.35']['proxy_contact_edge_controls'])
    assert data['cases']['rejected_loose_corners']['diagonal']['maximum_land_axial_demand_mm']>rejected_limit
    for name,case in data['cases'].items():
        if name.startswith('fit_'):
            proxy=old['M4_'+name]['proxy_contact_edge_controls']
            limit=min(p['tooth_centroid_axial_rise_mm'] for p in proxy)
            assert case['y']['far_land_axial_demand_mm']<limit
            if 'diagonal' in case:assert case['diagonal']['maximum_land_axial_demand_mm']<limit


def operation():
    cad()
    association=json.loads((ROOT/'notes/m3/evidence_association.json').read_text())
    require_sources(association['inputs']);require_sources(association['outputs'])
    data=json.loads((ROOT/'notes/retention/dental_m3_press_7/result.json').read_text())
    assert data['completed'] and data['metrics']['observations']['tooth']['min_mm'][0]>2


def sliced(kind):
    current_publication(kind)
    receipt=json.loads((OUT/(kind+'_export_slice.json')).read_text())
    assert receipt['ok'] and receipt['geometry']['valid'] and receipt['slice']['ok']
    assert (OUT/(kind+'_toolpaths.json')).is_file()


def make_m5_plan(variant,baseline):
    if variant!='slim-m5':raise ValueError(variant)
    previous=make_m4_plan('slim-m4',baseline)
    questions=tuple(replace(q,criterion='Current leaf equals M4; isolated pressure evidence only, full-cap release remains separate')
                    if q.id=='operation' else q for q in previous.questions)
    questions+=(Question('space','form.minimal','Actual central sections recover usable space while preserving the existing individual tube passage','CAD'),)
    scope=dict(design=variant,revision='M5 unprinted space-recovery prototype',material='uncalibrated PETG',
               process='0.4mm nozzle /0.2mm diagnostic PETG')
    def width():
        from m5_design import D
        assert abs(D.width-74.2)<1e-6,'Flat 77mm keeps the M4 maximum; historical 74.2mm criterion still fails'
    groups=(('m5.cad',(('closure.secure','capture'),('brush.fit','aperture'),('paste.fit','aperture'),('form.end-rounds','rounds'),('test.fit','sample')),cad,'cad.json'),
        ('m5.space',(('form.minimal','space'),),space,'space_study.json'),
        ('m5.contact',(('closure.secure','contact-order'),),contact,'contact.json'),
        ('m5.operation',(('closure.end-retention','operation'),),operation,'cad.json'),
        ('m5.slice',(('print.supportfree','slice'),),lambda:sliced('case'),'case_export_slice.json'),
        ('m5.sample-slice',(('test.fit','sample-slice'),),lambda:sliced('joint'),'joint_export_slice.json'),
        ('m5.width',(('form.width-revision','width'),),width,'../../m5_design.py'))
    return Plan(variant,previous.requirements,scope,questions=questions,
        checks=tuple(assertion_check(id,targets,run,'notes/m5/'+ref,scope) for id,targets,run,ref in groups),
        retained=previous.retained,
        directives=(Directive('m5.space','Explore useful interior recovery while retaining flat exterior, mechanism evidence and matching test piece',
                    UserSource('notes/m5.md','User challenges excessive internal mechanism space; requests autonomous alternatives and a new reasonable variant; M4 unprinted')),),
        decisions=(DesignDecision('m5.layout','Short guards, stepped perimeter guide and flat77 shell preserve leaf/pocket and recover storage space','notes/m5.md'),),
        hypotheses=(Hypothesis('m5.limits','Section stiffness and guide-first geometry support comparison, not a printed holding-force or shell-spreading rating','notes/m5.md'),))
