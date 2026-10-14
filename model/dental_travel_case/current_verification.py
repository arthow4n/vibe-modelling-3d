"""Architecture-specific questions composed from the current CAD checks."""
from functools import cache
import json
from pathlib import Path
from product_verification import (UserRequirement as U, UserSource as S, Question as Q,
    Plan, Directive, Evidence, Status, assertion_check, protect_recorded_intent, protect_user_requirements, CalculationInconclusive)

ROOT=Path(__file__).resolve().parent
RECORD='notes/README.md'
LATEST=RECORD+'#backpack-retention-and-cylinder-direction--2026-10-14'
SOURCE=S(LATEST,'User authorized rounded R2/C and a grippable threaded cylinder; cylinder explicitly needs no clips or separators')


def make_current_plan(variant, baseline):
    if variant not in ('rounded-c','plain-cylinder'):
        raise ValueError('Unknown current architecture: '+variant)
    cylindrical=variant=='plain-cylinder'
    requirements=list(baseline)
    changes={}
    if cylindrical:
        requirements[1]=U('paste.fit','Carry toothpaste with variation room in a plain shared cavity',SOURCE)
        changes['paste.fit']=SOURCE
    requirements+= [
        U('form.rounded','Make the enclosure rounded overall and the hinge recessed where used',SOURCE),
        U('travel.protection','Protect the contents during backpack use; retain the brush in the hinged case',SOURCE),
        U('print.supportfree','Make the selected architecture support-free',S(LATEST,'User asked for a support-free rounded R2/C combination')),
    ]
    if cylindrical:
        requirements.append(U('cylinder.simple','Provide a middle threaded joint, grippable exterior and plain interior',SOURCE))
    else:
        requirements.append(U('clip.revision','Reduce both clip bore and entry mouth by 3 mm while preserving the working socket interface',
            S(RECORD+'#clip-feedback--2026-10-14','User reported printed clip and socket fit and requested both openings 3 mm smaller'),
            ('Bore reduction 3 mm','Mouth reduction 3 mm')))
    protect_recorded_intent(ROOT,requirements,changes=changes)
    recorded=json.loads((ROOT/'notes/verification_sources.json').read_text())['variants'][variant]
    previous=tuple(U(r['id'],r['text'],S(**r['source']),tuple(r['acceptance_criteria'])) for r in recorded)
    protect_user_requirements(previous,requirements)
    scope=dict(design=variant,material='intended PETG',process='0.4 mm nozzle / 0.2 mm layers',revision='2026-10-14 unprinted')
    questions=[]; groups=[]; retained=[]
    def add(id,targets,criterion,fn,reference,mode='CAD'):
        for rid,qid in targets: questions.append(Q(qid,rid,criterion,mode))
        groups.append(assertion_check(id,tuple(targets),fn,reference,scope))
    if cylindrical:
        import cylinder_checks as checks
        import cylinder_design as design
        @cache
        def candidate(): return design.build()
        add('case.construction',[('print.material','construction'),('test.fit','representative')],
            'Two connected cups and short joint test preserve full mating geometry and print orientation',
            lambda:checks.construction(candidate()),'cylinder_checks.py#construction')
        add('contents.fit',[('brush.fit','envelope'),('paste.fit','envelope'),('cylinder.simple','plain')],
            '255 mm brush with original 30 mm handle and 60 x 44 mm tube fit the plain cavity with separation',
            lambda:checks.packing(candidate()),'cylinder_checks.py#packing')
        add('thread.path',[('cylinder.simple','joint'),('travel.protection','capture')],
            '61 helical poses at 30 degree steps and subsequent loaded straight lift clear; unturned axial pull meets flanks',
            lambda:checks.thread_motion(candidate()),'cylinder_checks.py#thread_motion')
    else:
        import r2_checks as checks
        from r2_design import build
        @cache
        def candidate(): return build()
        for id,targets,fn,criterion in (
            ('case.construction',[('print.material','construction'),('test.fit','representative')],checks.construction,'Connected parts; cropped seven-part test retains production local interfaces'),
            ('contents.fit',[('brush.fit','envelope'),('paste.fit','envelope')],checks.fit,'30 mm brush shell envelope; complete mounts accommodate inferred 27 mm grip target; 180 x 60 x 44 mm tube'),
            ('brush.capture',[('travel.protection','capture'),('clip.revision','capture')],checks.brush_capture,'Foot gates and closed keeper caps obstruct brush escape geometrically'),
            ('case.closure',[('travel.protection','closure')],checks.closure,'Closed latch obstructs lift; free leaf release proxy clears while its root remains fixed'),
            ('hinge.capture',[('travel.protection','hinge')],checks.pin_capture,'Pin heads and opposed tip barbs capture both joints'),
            ('hinge.admission',[('print.material','assembly')],checks.admission,'Sampled admission of compressed free-arm proxy clears empty bearing ports; no elastic insertion force claim'),
        ):
            add(id,targets,criterion,lambda fn=fn:fn(candidate()),'r2_checks.py#'+fn.__name__)
        add('flexure.screen',[('print.material','compliance')],'Straight-beam analogies below agent-selected uncalibrated 1% strain screen',checks.compliance,'r2_checks.py#compliance','analytical')
        def motion():
            route=json.loads((ROOT/'notes/r2_cad_route.json').read_text())['route']
            assert route and route[-1]['lid_degrees']==180
            checks.foundation_path(candidate(),route,subdivisions=3)
        add('hinge.path',[('brush.fit','path'),('paste.fit','path')],
            'Added bed foundations clear the unchanged qualified moving actors on the same <=1 degree sampled route',motion,'r2_checks.py#foundation_path')
        verify_motion_basis_inputs()
        basis=json.loads((ROOT/'notes/r2_before_foundations_verification.json').read_text())
        assert basis['variant']==variant and basis['report']['scope']==scope, 'Historical motion scope changed'
        outcome=next(e for e in basis['report']['evidence'] if e['id']=='hinge.path')
        for rid in ('brush.fit','paste.fit'):
            questions.append(Q('path-basis',rid,'Original complete loaded CAD clears 193 coupled poses, hardware and table; reviewed unchanged builder/actors/route, excluding added feet','CAD'))
        retained.append(Evidence('hinge.path.basis',(('brush.fit','path-basis'),('paste.fit','path-basis')),Status(outcome['status']),
            'Original complete motion evidence retained after review; four bed feet qualified separately',
            'notes/r2_before_foundations_verification.json',scope))
        def correction():
            from parameters import HANDLE_DIAMETER,CLIP_THROAT
            from r2_parts import GRIP_DIAMETER,GRIP_THROAT
            assert abs(HANDLE_DIAMETER-GRIP_DIAMETER-3)<1e-8, 'Nominal bore correction differs from 3 mm'
            assert abs(CLIP_THROAT-GRIP_THROAT-3)<1e-8, 'Mouth correction differs from 3 mm'
        add('clip.correction',[('clip.revision','dimensions')],'Both measured old bore and mouth reduce by exactly 3 mm',correction,'components.py#sized_clip')
    def slice_receipts():
        import hashlib
        names=('cylinder_case','cylinder_thread_test') if cylindrical else (
            'r2_body','r2_lid','r2_hardware','r2_handle_clip','r2_section_test')
        for name in names:
            receipt=ROOT/'notes/slicer_review'/f'{name}.json'
            if not receipt.exists():
                raise CalculationInconclusive('Missing final slice receipt: '+name)
            record=json.loads(receipt.read_text())
            review=record.get('slice',{})
            assert record['ok'] and record['geometry']['valid'],name+' export/evaluation failed'
            assert review.get('ok'),name+' slice did not complete'
            digest=hashlib.sha256((ROOT/f'{name}.stl').read_bytes()).hexdigest()
            assert review['input_sha256']==digest,name+' receipt does not match delivered STL'
            assert review['support_probe']['ok'] and not review['support_probe']['generated'],name+' automatic support probe needs review'
            assert not review['review_required'],name+' unresolved slicer notice'
            settings=review['effective_settings']
            assert settings['layer_height']=='0.2' and settings['nozzle_diameter']==['0.4'],name+' unexpected layer/nozzle setup'
            assert settings['filament_type']==['PETG'],name+' unexpected material'
    add('print.slice',[('print.supportfree','slice')],
        'Matching delivered STL receipts accepted under named PETG profiles with no generated supports; physical print and GUI STEP import unqualified',
        slice_receipts,'notes/slicer_review','slicer')
    for rid,criterion in (
        ('brush.fit','Actual brush fits without unintended button pressure'),('paste.fit','Actual desired tubes fit without unwanted squeeze'),
        ('print.material','Printed effort, recovery and life are satisfactory'),('test.fit','New sample gives useful physical fit observations'),
        ('travel.protection','Actual backpack pressure and handling remain satisfactory'),
        ('form.rounded','User finds the complete enclosure suitably rounded'),
        ('print.supportfree','Actual bridges, overhangs and layer adhesion print successfully without supports'),
    ):
        questions.append(Q('physical',rid,criterion,'physical'))
    if cylindrical:
        questions.append(Q('wet-grip','cylinder.simple','Fluted exterior grips comfortably with wet hands','physical'))
    else:
        questions.append(Q('physical','clip.revision','Revised bore/mouth grip and release the actual brush comfortably','physical'))
    return Plan(variant,tuple(requirements),scope,checks=tuple(groups),retained=tuple(retained),questions=tuple(questions),
        directives=(Directive('floss.optional','No dedicated floss bay',SOURCE),
                    Directive('interior.choice','Cylinder has no separators or clips; hinged case retains positive brush capture',SOURCE)))


# Reviewed source association for retained native motion evidence. These guard
# the unchanged original builder, actors, route and locked CAD environment.
# Changed inputs require a fresh full-motion run, never a hash-only promotion.
MOTION_BASIS_FILES = {'../../assembly_geometry/__init__.py': 'caee31b0a2082acd3c6f2dd25d564d8b68e761afb3375cf18af07fd796a2a745',
 '../../assembly_geometry/configuration.py': '254614125932f1268c43c004f1dbb4b35904f296aeb2cb86c2ae699e87609f72',
 '../../assembly_geometry/experiments/native_probe.py': '45c0ddb5f1dac952b686e34760d43db96ac7e56b6e950eb08939e99721193701',
 '../../assembly_geometry/experiments/qualify.py': 'e6e7989b1289d0cecc523a6eaf12b5a19a82974df46211948807107ffb267b0f',
 '../../assembly_geometry/queries.py': '93c2b98b4e833c89c790922146ab2767d52304558bb54ed92eda47a116b3f7ce',
 '../../uv.lock': 'decadf8943fd324455151518a1b14eef612e6df01d3faf4d57b5b7d754de1ec8',
 'components.py': 'eb49a8bf6ee60982e35ffef981526f2cad3b03c1c96f465eeb23eea1139d9206',
 'mechanisms.py': 'b36912b830375ab3e9e7c5bf8178ea6fdf992186e7d4e53181dce4e78a968b57',
 'notes/r2_before_foundations_verification.json': 'd4d165a2f92bf328b716df1c1fdefe14467b15f4041ffba6d479ef3c22e5249b',
 'notes/r2_cad_route.json': 'd23d406892c1989bab4b8721befd96349ddc19210e54b223e17b5bb5b11660a0',
 'parameters.py': 'f867132ab1f1d9fb1c079b6ac6d93fc8c97e9bfee39eaca11944737aa9b774d3',
 'r2_geometry.py': '12cc2e35c68bb637aecc1ddb52deb7fae9d92f728bfc8c6bf20a40304a47a1a9',
 'r2_parts.py': '76f9cb2f8c0057a5640abdd2e6f134bb256649d1861568d6a0e89cc573ed5ed2'}
MOTION_BASIS_FUNCTIONS = {'r2_checks.py:clear': '66fc16e4fc8996b3d18301d88eca9eab0f108a2fb00a62fa8622a6f49f0f7baf',
 'r2_checks.py:path': 'e8c9c76c5b018fe1c11a2d8d08fdde2d4a1688024f0770e6193f1675c6cf0d48',
 'r2_design.py:_build_without_bed_foundations': '19c9a1cef16c0b0eb577880b86cbb848a96265f0108e43a5dfd97a114d68c77d',
 'r2_design.py:flip_lid': '07d79aab3d9b4e62039a0c2fc4470cc6dd97beb201d813373cbcaa3553df1cd5',
 'r2_design.py:references': '8b923c759fffbeb50c27b6d978939e70d8e7eceb029311b7a9154a506707085b'}


def verify_motion_basis_inputs():
    import ast
    import hashlib
    for name,expected in MOTION_BASIS_FILES.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected, 'Full motion recheck required: '+name
    for item,expected in MOTION_BASIS_FUNCTIONS.items():
        name,fn=item.split(':')
        source=(ROOT/name).read_text()
        node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name==fn)
        text=ast.get_source_segment(source,node)
        if fn=='_build_without_bed_foundations':
            text=text.replace('def _build_without_bed_foundations():','def build():',1)
        assert hashlib.sha256(text.encode()).hexdigest()==expected, 'Full motion recheck required: '+item
    from r2_checks import OVERLAP
    assert OVERLAP==1e-5,'Full motion criterion changed'
