"""Exercise named Q1/Q1F engineering, preserving historical print files/results.

Runs the full migrated engineering suite and compares retained legacy outcomes.
Also challenges real component placements and the deliberate retention source.
No exports, slices, physical solver or geometry parameter changes.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import cadquery as cq
from assembly_geometry import PairRequirement, check_pair
import quiet_q1
import quiet_q1_flush
from quiet_assembly import QuietAssembly
from check_quiet_q1 import main, EPS
from check_quiet_q1_flush import local_checks

ROOT=Path(__file__).parent


def same_geometry(actual, expected, intent):
    """Targeted placement regression, not a generic export/bounds audit.

    A mistaken assembly Location would change the print or inspection geometry;
    compare both directed cut volumes under the existing 1e-6 mm3 screen.
    """
    for a,b in ((actual,expected),(expected,actual)):
        difference=a.cut(b)
        assert difference.isValid(), f'{intent}: invalid regression Boolean'
        assert difference.Volume()<=EPS, f'{intent}: native placement changes geometry'


def qualify(model, report):
    q=model.model
    old_name='quiet_q1_flush_checks.json' if q is quiet_q1_flush else 'quiet_q1_checks.json'
    historical_path=ROOT/'notes'/old_name
    historical=json.loads(historical_path.read_text())
    # Numerical source fingerprints are deliberately historical. Compare the
    # substantive outcomes; the new record owns its current source identity.
    compared=[]
    for name,value in historical.items():
        if name=='source_sha256':
            continue
        if name=='peak_rigid_bead_overlap_mm3':
            assert math.isclose(report[name],value,rel_tol=1e-7,abs_tol=EPS), name
        else:
            assert report[name]==value, name
        compared.append(name)

    closed=model.operating()
    opened=model.operating(lift_mm=84)
    for name,shape in (('base',model.base),('insert',model.insert),('hood',model.hood)):
        same_geometry(closed.shape(name),shape,f'Closed {name}')
    same_geometry(opened.shape('hood'),model.hood.translate((0,0,84)),'Open hood +Z placement')
    same_geometry(closed.shape('hood'),model.hood,'Closed snapshot stable after opening')
    same_geometry(model.print_job('base').shape('base'),q.print_base().val(),'Base print job')
    same_geometry(model.print_job('insert').shape('insert'),q.print_jacket().val(),'TPU print job')
    hood_print=(q.g.hood_print(q.hood()).translate(
        (q.g.PRINT_ANCHOR[0]+q.g.HOOD_SHIFT,q.g.PRINT_ANCHOR[1],0)).val()
        if q is quiet_q1_flush else q.print_hood().val())
    same_geometry(model.print_job('hood').shape('hood'),hood_print,'Hood print job')
    # The print snapshots must contain exactly one physical component. Analysis
    # proxies and loaded cards can never leak into these selections.
    for component in ('base','insert','hood'):
        assert model.print_job(component).names==(component,)
    for neighbour in ('new','archive_A','display_J4'):
        other,depth,cover=model.neighbour(neighbour)
        for end in (-1,1):
            row=model.joined(neighbour,end=end)
            same_geometry(row.shape('new/base'),model.base.translate((0,-end*q.FOOT_Y/2,0)),row.name+' new base')
            same_geometry(row.shape('neighbour/base'),other.translate((0,end*depth/2,0)),row.name+' neighbour base')
            same_geometry(row.shape('neighbour/hood'),cover.translate((0,end*depth/2,0)),row.name+' neighbour hood')
            same_geometry(row.shape('key'),q.keys.seated_key(3).val(),row.name+' key at seam')

    # Preserve identities while comparing the previous independent view layout.
    # Subtracting compounds containing deliberate overlaps produced an invalid
    # Boolean in this trial; it can also hide one part inside another. Compare
    # the exact component set and each positioned part before compounding.
    if q is quiet_q1_flush:
        scene=model.inspection()
        old=model.neighbour('archive_A')[0]
        expected={
            'mixed_row/neighbour/base':old.translate((0,-q.FOOT_Y/2,0)),
            'mixed_row/neighbour/hood':q.g.cap().val().translate((0,-q.FOOT_Y/2,0)),
            'mixed_row/new/base':model.base.translate((0,q.FOOT_Y/2,0)),
            'mixed_row/new/insert':model.insert.translate((0,q.FOOT_Y/2,0)),
            'mixed_row/new/hood':model.hood.translate((0,q.FOOT_Y/2,0)),
            'mixed_row/key':q.keys.seated_key(3).val(),
            'open_box/base':model.base.translate((90,0,0)),
            'open_box/insert':model.insert.translate((90,0,0)),
            'detached_insert':model.insert.translate((165,0,-q.FOOT_TOP)),
            **{f'open_box/card_{i:02d}':model.cards[i].translate((90,0,0))
               for i in range(0,len(model.cards),7)}}
        assert set(scene.names)==set(expected), 'Inspection loses or adds a component'
        for name,shape in expected.items():
            actual=scene.shape(name)
            if '/card_' in name:
                # Coincident source-card subtraction also produced invalid
                # Boolean geometry. This question is rigid placement, not a
                # second source-card construction qualification: check its
                # native transform and every transformed source vertex datum.
                assert scene.location(name).toTuple()==((90,0,0),(0,0,0)), name
                a=sorted(v.Center().toTuple() for v in actual.Vertices())
                b=sorted(v.Center().toTuple() for v in shape.Vertices())
                assert a and len(a)==len(b), f'{name}: card datum set changed'
                assert all(math.dist(x,y)<=1e-7 for x,y in zip(a,b)), f'{name}: misplaced card datums'
            else:
                same_geometry(actual,shape,f'Q1F inspection {name}')

    no_overlap=PairRequirement('Wrong downward hood placement must be rejected',max_overlap_mm3=EPS)
    bad=model.operating(lift_mm=-1)
    negative=bad.check('hood','base',no_overlap)
    assert negative.calculation_completed and negative.status=='failed', negative.to_dict()
    contact_lift=report['bead_contact_lifts_mm'][len(report['bead_contact_lifts_mm'])//2]
    moved=model.hood.translate((0,0,contact_lift))
    retention=PairRequirement('The specified withdrawal pose must meet retention material',min_overlap_mm3=EPS)
    positive=check_pair(moved,model.insert,retention,first='hood',second='insert',configuration='retention_witness').require_passed()
    absent=check_pair(moved,model.guides,retention,first='hood',second='guides_reference',configuration='beads_removed')
    assert absent.calculation_completed and absent.status=='failed', absent.to_dict()
    # A lifted real card is collision-free but no longer seated: required contact
    # must reject that configuration, independently of the clearance checks.
    floor=model.base.intersect(q.block(-q.archive.r1.POCKET_WIDTH/2,q.archive.r1.POCKET_WIDTH/2,
        -q.archive.r1.POCKET_DEPTH/2,q.archive.r1.POCKET_DEPTH/2,0,q.archive.FLOOR).val())
    floating=check_pair(model.cards[0].translate((0,0,1)),floor,PairRequirement(
        'Card must seat on its floor',max_gap_mm=1e-7,max_overlap_mm3=EPS),
        first='floating_card',second='floor_reference',configuration='card_lifted_1_mm')
    assert floating.calculation_completed and floating.status=='failed', floating.to_dict()
    return dict(legacy_outcomes_compared=compared,
        historical_evidence_sha256=hashlib.sha256(historical_path.read_bytes()).hexdigest(),
        native_pose_and_print_selection_regressions=True,
        negatives=[negative.to_dict(),absent.to_dict(),floating.to_dict()],
        required_retention_witness=positive.to_dict(),
        preserved_print_artifact_sha256={path.name:hashlib.sha256(path.read_bytes()).hexdigest()
            for stem in (('quiet_q1_flush_base_15','quiet_q1_flush_jacket_95a','cap_g_hood_5')
                         if q is quiet_q1_flush else ('quiet_q1_base_15','quiet_q1_jacket_95a','quiet_q1_hood'))
            for path in [ROOT/(stem+suffix) for suffix in ('.step','.stl')]})


def run(variant='q1f'):
    q=quiet_q1_flush if variant=='q1f' else quiet_q1
    model=QuietAssembly(q)
    extra=local_checks(model) if q is quiet_q1_flush else None
    name=f'quiet_{variant}_assembly_checks.json'
    report=main(q,None,model=model,extra=extra)
    # Publish successful qualification only after all regressions and deliberate
    # failures behaved as expected; failed partial work cannot keep ok=True.
    path=ROOT/'notes'/name
    try:
        report['assembly_api_qualification']={'status':'passed',**qualify(model,report)}
    except Exception as exc:
        report['ok']=False
        report['assembly_api_qualification']={'status':'failed','error':str(exc)}
        path.write_text(json.dumps(report,indent=2)+'\n')
        raise
    report['source_sha256'][Path(__file__).name]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(ok=True,variant=variant,report=str(path),
        engineering_queries=len(report['assembly_api_evidence']),negative_cases=3)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant',choices=('q1f','q1'),default='q1f')
    run(parser.parse_args().variant)
