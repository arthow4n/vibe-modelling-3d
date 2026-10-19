"""C8 preserves dental intent while checking spatial use before print trials."""
import json
from product_verification import Plan,Question as Q,UserRequirement as U,UserSource as S,DesignDecision,assertion_check
from internal_hinge_verification import make_plan as previous_plan
from closure_research_verification import require_sources
from spine_evidence import OUT,MODELS

RECORD='notes/spine.md'


def motion():
    r=json.loads((OUT/'motion.json').read_text());require_sources(r['source_sha256'])
    for size in ('mini','full'):
        assert r['cases'][size+'_C7']['closed_cavity_intrusion_mm3']>.01
        for kind in ('tpu_spine','edge_pin'):
            case=r['cases'][size+'_'+kind]
            assert case['closed_cavity_intrusion_mm3']<1e-5
            assert case['poses'][-1]['angle_deg']==180
            for row in case['poses']:
                assert max(row['shell_intersection_mm3'],row['release_intersection_mm3'],row['lower_cavity_intersection_mm3'])<1e-5
                assert all(s['connected_solids']==1 and s['shell_intersection_mm3']<1e-5
                    and s['contents_intersection_mm3']<1e-5 for s in row['spines'])


def mounting_geometry():
    import spine_design as d
    p=d.build('tpu_spine',size=d.MINI);rear=d.MINI.depth/2
    outside=d.base.box(0,rear+10,d.MINI.seam,100,20,100)
    for name in ('body','lid'):assert p[name].intersect(outside).val().Volume()<1e-5
    for c in p['centers']:
        s=d.strap(d.MINI,c,0)
        assert s.intersect(outside).val().Volume()<1e-5
        assert sum(s.intersect(p[n]).val().Volume() for n in ('body','lid'))<1e-5
        # Rigid capture witness only: the soft heads could still fold through.
        pull=s.translate((0,.3,0))
        assert sum(pull.intersect(p[n]).val().Volume() for n in ('body','lid'))>.01
        head_region=d.base.box(c,rear-5.8,d.MINI.seam,20,8,45)
        headless=s.cut(head_region)
        assert sum(headless.translate((0,.3,0)).intersect(p[n]).val().Volume() for n in ('body','lid'))<1e-5
    cap=d.pose(d.MINI,p['lid'],180)
    assert abs(cap.val().BoundingBox().zmin)<1e-5  # asked-for coplanar floor pose


def manufacturing(name):
    data=json.loads((OUT/'publication.json').read_text());require_sources(data['source_sha256'])
    require_sources(data['artifacts'][name])
    receipt=json.loads((OUT/(name+'_slice.json')).read_text());s=receipt['slice']
    assert s['ok'] and s['support_probe']['ok']
    if name=='c8_spines':
        assert s['effective_settings']['filament_type']==['TPU']
        assert s['effective_settings']['layer_height']=='0.2'
        assert s['effective_settings']['sparse_infill_density']=='100%'
        assert not s['review_required']
    else:
        review=json.loads((OUT/'manufacturing_review.json').read_text());require_sources(review['source_sha256'])
        assert review['STL_sha256']==s['input_sha256']
        assert review['disposition']=='experimental_print_reviewed'


def make_plan(variant,baseline):
    if variant!='spine-c8-mini':raise ValueError(variant)
    old=previous_plan('hinge-c7-mini',baseline)
    source=S(RECORD,'2026-10-19: user rejects C7 internal shelves before printing; asks for minimal interior obstruction and ideally flat opening, with autonomous further exploration')
    requirements=old.requirements+(U('hinge.clear-cavity','Avoid intrusive hinge structures and contents collisions during opening/closing',source),
        U('hinge.flat-open','Prefer opening the box flat when feasible without sacrificing the interior',source))
    scope=dict(phase='Complete C8 mini-box experiment, full-size rough motion comparison only',materials='PETG shells plus separately printed TPU 95A spines; uncalibrated',method='Exact CAD with a prescribed constant-neutral-length spine path; not force equilibrium')
    qs=tuple(Q('use',r.id,'No C8 physical print; full packing, protection, button pullout, hinge life and operating effort remain unmeasured','physical') for r in requirements)+(
        Q('space','hinge.clear-cavity','Cavity and lower-half motion keepouts, including full shell length and C7 negative reference','CAD'),
        Q('path','hinge.flat-open','One feasible prescribed path to 180 degrees, not a predicted unconstrained flexure motion','CAD'),
        Q('mount','trial.integrated','Flush installed heads and actual flat capture, with a headless negative control; no retention-force rating','CAD'))+tuple(
        Q(n,'trial.integrated','Paired material-specific layouts, native settings and relevant manufacturing review','slicer') for n in MODELS)
    checks=(assertion_check('c8.motion',(('hinge.clear-cavity','space'),('hinge.flat-open','path')),motion,RECORD,scope),
        assertion_check('c8.mount',(('trial.integrated','mount'),),mounting_geometry,RECORD,scope))+tuple(
        assertion_check('c8.slice.'+n,(('trial.integrated',n),),lambda n=n:manufacturing(n),RECORD,scope) for n in MODELS)
    return Plan(variant,requirements,scope,questions=qs,checks=checks,decisions=(
        DesignDecision('c8.materials','Use available TPU 95A as two replaceable recessed spines, PETG for shells; trade multi-material assembly for clear storage and flat opening',RECORD),))
