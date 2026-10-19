"""C7 mini-box evidence composes with retained dental-case user intent."""
import json
from product_verification import Plan, Question as Q, UserRequirement as U, UserSource as S, assertion_check
from clamshell_verification import make_clamshell_plan
from closure_research_verification import require_sources
from internal_hinge_delivery import OUT,MODELS

RECORD='notes/internal_hinge.md'


def motion():
    data=json.loads((OUT/'motion.json').read_text());require_sources(data['source_sha256'])
    for size in ('mini','full'):
        assert data['cases'][size+'_naive_internal']['sweep'][1]['intersection_mm3']>1
        assert data['cases'][size+'_raised_seam']['sweep'][3]['intersection_mm3']>.1
        for kind in ('internal_screw','internal_cone'):
            row=data['cases'][size+'_'+kind]
            assert row['valid'] and set(row['connected_solids'].values())=={1}
            assert row['open90_minimum_surface_gap_mm']>.29
            assert all(p['intersection_mm3']<1e-5 for p in row['sweep'] if p['angle_deg']<=100)
            assert all(p['released_loop_intersection_mm3']<1e-5 for p in row['released_loop_sweep'])
            assert next(p for p in row['sweep'] if p['angle_deg']==110)['intersection_mm3']>1
    return data


def publication():
    p=json.loads((OUT/'publication.json').read_text());require_sources(p['source_sha256'])
    for n in MODELS: require_sources(p['artifacts'][n])


def mini_geometry():
    import internal_hinge_design as d
    from c7_mini_pip import layout
    for kind in ('internal_screw','internal_cone'):
        p=d.build(kind,size=d.MINI)
        outside=d.base.box(0,d.MINI.depth/2+10,d.MINI.seam,100,20,100)
        assert sum(p[n].intersect(outside).val().Volume() for n in ('body','lid'))<1e-5
    # Reconstruct the rejected equal-width fixed strips on the actual cone box.
    # It has no overlapping material at 90deg, yet its touching wall edges can
    # fuse. This protects a distinction that a binary intersection check misses.
    p=d.build('internal_cone',size=d.MINI)
    shell=d.shell(d.MINI)
    whole=shell.union(shell.rotate((0,0,d.MINI.seam),(1,0,d.MINI.seam),180))
    touching=p['body']
    for c in p['centers']:
        for lo,hi in ((c-6,c-3),(c+3,c+6)):
            strip=d.base.box((lo+hi)/2,d.MINI.axis_y,d.MINI.seam,hi-lo+.6,30,30)
            touching=touching.union(whole.intersect(strip).intersect(d.cylinder(d.MINI,10.)))
    opened=d.rotate(p,p['lid'],90)
    assert touching.intersect(opened).val().Volume()<1e-5
    assert touching.val().distance(opened.val())<1e-7
    a=layout()
    # A specifically suspected failure: rotating rounded panels can lift one
    # moving component off the bed. This is not a generic export-bounds audit.
    for n in ('body','lid'):
        assert abs(a.objects[n].obj.val().BoundingBox().zmin)<1e-5
    assert a.objects['body'].obj.intersect(a.objects['lid'].obj).val().Volume()<1e-5
    assert a.objects['body'].obj.val().distance(a.objects['lid'].obj.val())>.29


def manufacturing(name):
    publication()
    r=json.loads((OUT/(name+'_slice.json')).read_text())
    assert r['slice']['ok'] and r['slice']['support_probe']['ok']
    review=json.loads((OUT/'manufacturing_review.json').read_text());require_sources(review['source_sha256'])
    assert review['layouts'][name]['STL_sha256']==r['slice']['input_sha256']
    assert review['layouts'][name]['disposition']=='experimental_print_reviewed'


def make_plan(variant,baseline):
    if variant!='hinge-c7-mini':raise ValueError(variant)
    previous=make_clamshell_plan('clamshell-c6',baseline)
    source=S(RECORD,'2026-10-19: user rejects unhinged wall-only trial, requests internal/flat-exterior hinge exploration including print-in-place and complete working mini box with loop and keeper')
    req=previous.requirements+(U('hinge.internal','Explore hiding the hinge within a flat rear exterior, including print-in-place feasibility',source),
        U('trial.integrated','Provide a minimal complete box with connected hinge, loop and matching keeper for meaningful operation testing',source))
    scope=dict(phase='C7 complete mini-box exploration, not adopted full case',material='Uncalibrated PETG hypothesis',process='0.4mm nozzle / 0.2mm reference layers')
    qs=tuple(Q('use',r.id,'No new physical validation; mini boxes cannot validate full dental packing or backpack protection','physical') for r in req)+(
        Q('motion','hinge.internal','Actual CAD internal pivot, negative controls and 0–100 degree sampled release/opening; overtravel remains blocked','CAD'),
        Q('mini','trial.integrated','Complete connected box geometry with unchanged loop/keeper and bed contact in captive print pose','CAD'))+tuple(
        Q(n,'trial.integrated','Paired sample exports and scoped native support review; actual fit and bridge quality remain unprinted','slicer') for n in MODELS)
    checks=(assertion_check('c7.motion',(('hinge.internal','motion'),),motion,RECORD,scope),
        assertion_check('c7.mini',(('trial.integrated','mini'),),mini_geometry,RECORD,scope))+tuple(
        assertion_check('c7.slice.'+n,(('trial.integrated',n),),lambda n=n:manufacturing(n),RECORD,scope) for n in MODELS)
    return Plan(variant,req,scope,questions=qs,checks=checks)
