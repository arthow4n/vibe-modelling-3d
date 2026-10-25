"""Independent geometric/image fixtures and the actual managed evaluator boundary."""
import io
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import cadquery as cq
from PIL import Image, ImageChops
import pytest

from assembly_geometry import Configuration, PairRequirement
from cad_inspection import (Camera, Anchor, Frame, Region, Section, Label, Arrow, Highlight,
                            View, Inspection, render, sheet, pair_inspection, motion_inspection)
from cad_inspection.render import section_shape, png, prepare, paths
from cad_inspection.spec import view_from_dict

ROOT = Path(__file__).resolve().parents[1]


def image_for(shape, view):
    svg, settings = render(Inspection(shape, view, 'Inspect fixture'), width=600, height=500)
    return Image.open(io.BytesIO(png(svg))).convert('RGB'), settings


@pytest.mark.parametrize('direction,up', [((0,0,0),(0,0,1)), ((0,0,1),(0,0,2)), ((1,0,0),(0,0,0)), ((float('nan'),0,1),(0,0,1))])
def test_bad_cameras(direction, up):
    with pytest.raises(ValueError):
        Camera(direction, up)


@pytest.mark.parametrize('direction', [(1,-2,.7), (-3,1,2), (0,-1,0), (1,0,0)])
def test_camera_basis_and_actual_raster(direction):
    camera = Camera(direction)
    # A long Z pillar with a wide TOP cap independently distinguishes roll/inversion.
    pillar = cq.Workplane('XY').box(2,2,50,centered=(True,True,False))
    shape = pillar.union(cq.Workplane('XY').box(14,14,2).translate((0,0,51)))
    img, settings = image_for(shape, View(camera, annotations=(Label((0,0,51),'top'),)))
    top = settings['annotation_pixels'][0]['point']
    bottom_projected = camera.project((0,0,0)); top_projected = camera.project((0,0,51))
    assert top_projected[1] > bottom_projected[1]
    # Exclude caption/legend and annotation; compare ink in upper/lower model bands.
    crop = img.crop((180,100,420,440))
    ink = ImageChops.difference(crop, Image.new('RGB',crop.size,'white'))
    bounds = ink.getbbox(); assert bounds is not None
    assert bounds[3]-bounds[1] > bounds[2]-bounds[0]
    assert top[1] < 270
    right, up, d = camera.axes
    assert right.cross(up).dot(d) == pytest.approx(1)
    assert Camera.look_at(direction, (0,0,0)).axes[2].toTuple() == pytest.approx(d.toTuple())


def test_framing_enlarges_and_centers_off_axis_feature_without_cutting():
    shape = cq.Workplane('XY').box(100,20,10).val()
    camera = Camera.named('top')
    whole, a = image_for(shape, View(camera))
    detail, b = image_for(shape, View(camera, Frame(Region.around((40,0,0),(10,10,10)),1),
                                         annotations=(Label((40,0,0),'target'),)))
    assert b['pixels_per_mm'] > 3*a['pixels_per_mm']
    assert b['annotation_pixels'][0]['point'][0] == pytest.approx(300)
    assert b['subject_sha256'] == a['subject_sha256']
    assert b['removed_by_section'] == []
    with pytest.raises(ValueError, match='outside'):
        image_for(shape, View(camera, Frame(Region.around((400,0,0),(10,10,10)))))


def test_sections_known_hollow_profile_and_half_volume_with_arbitrary_plane():
    tube = cq.Workplane('XY').rect(10,8).rect(6,4).extrude(20).val()
    section = section_shape(tube, Section((0,0,7),(0,0,1),'planar'))
    assert len(section.Wires()) == 2
    assert sorted(w.Length() for w in section.Wires()) == pytest.approx([20,36])
    for keep in ('positive','negative'):
        cut = section_shape(tube, Section((0,0,10),(0,0,1),'cutaway',keep))
        assert cut.Volume() == pytest.approx(560)
    cube = cq.Workplane().box(10,10,10).val()
    assert section_shape(cube, Section((0,0,0),(1,1,1),'cutaway')).Volume() == pytest.approx(500)
    with pytest.raises(ValueError, match='Empty'):
        prepare(Inspection(tube, View(Camera.named('top'), section=Section((0,0,50),(0,0,1),'planar')), 'empty'))


def test_complete_scene_occlusion_and_named_component_colors():
    # Back square is completely hidden behind a larger front plate.
    a = cq.Assembly(name='fixture').add(cq.Workplane().box(20,2,20).translate((0,-5,0)),name='front')
    a.add(cq.Workplane().box(4,2,4).translate((0,5,0)),name='back')
    cfg = Configuration.explicit(a,name='closed')
    view = View(Camera.named('front'), colors=(('front','#1769a6'),('back','#ce741c')))
    prepared = prepare(Inspection(cfg,view,'occlusion'))
    curves = paths(prepared[0],planar=False,show_hidden=True)
    assert not any(curves['back'][1])
    assert any(curves['back'][0])
    svg, _ = render(Inspection(cfg,view,'occlusion'))
    assert b'#1769a6' in svg and b'#ce741c' in svg
    with pytest.raises(KeyError):
        prepare(Inspection(cfg,View(Camera.named('front'),components=('typo',)),'missing'))


def test_annotations_escape_text_and_sheet_ids_are_isolated():
    shape = cq.Workplane().box(10,10,10)
    svg, _ = render(Inspection(shape,View(Camera.named('top'),annotations=(
        Label((0,0,0),'<catch & cap>'), Arrow((-2,0,0),(2,0,0),'direction'),
        Highlight(Region.around((0,0,0),(5,5,5)),'region'))),'inspect'))
    assert b'&lt;catch &amp; cap&gt;' in svg
    root = ET.fromstring(sheet([svg,svg]))
    ids = [e.get('id') for e in root.iter() if e.get('id')]
    assert len(ids)==len(set(ids))
    assert len(png(ET.tostring(root))) > 100


def test_annotation_glyphs_are_visible_in_actual_png():
    img, settings = image_for(cq.Workplane().box(10,10,10),View(Camera.named('top'),
        annotations=(Label((0,0,0),'Catch label',(40,0)),)))
    x,y = settings['annotation_pixels'][0]['point']
    glyphs = img.crop((int(x+40),int(y-18),int(x+110),int(y-3)))
    assert sum(r>g*1.5 and r>b*1.5 and r<220 for r,g,b in glyphs.get_flattened_data()) > 30


def test_presets_share_legacy_camera_directions():
    from evaluate_model import VIEWS
    from cad_inspection.spec import PRESETS
    assert VIEWS == PRESETS


def test_pair_and_motion_use_full_geometry_and_exact_hierarchical_pose():
    sub = cq.Assembly(name='sub').add(cq.Workplane().box(2,2,2),name='moving',loc=cq.Location((2,0,0)))
    a = cq.Assembly(name='root',loc=cq.Location((0,5,0))).add(sub,loc=cq.Location((3,0,0)))
    a.add(cq.Workplane().box(2,2,2),name='fixed',loc=cq.Location((10,0,0)))
    cfg = Configuration.explicit(a,name='initial')
    before = cfg.shape('sub/moving').Center().toTuple()
    view = View(Camera.named('top'),section=Section((0,0,0),(0,0,1),'cutaway'))
    pair = pair_inspection(cfg,'sub/moving','fixed',PairRequirement('gap',min_gap_mm=2),view=view,purpose='gap')
    assert pair.answer.gap_mm == pytest.approx(3)
    assert pair.answer.status == 'passed'
    motion = motion_inspection(cfg,'sub/moving','fixed',PairRequirement('clear path',max_overlap_mm3=0),
        samples=(0,3,5),transform=lambda t:cq.Location((t,0,0)),parameter='travel',units='mm',
        select='first_unsuccessful',view=view,purpose='inspect failed sample')
    assert motion.selected_sample == 5
    assert motion.inspection.subject.shape('sub/moving').Center().toTuple() == pytest.approx((10,5,0))
    assert cfg.shape('sub/moving').Center().toTuple() == before
    assert motion.answer.status == 'failed'
    from product_verification import engineering_evidence
    evidence = engineering_evidence('path',(('operation','path'),),motion.answer,'inspection','CAD samples')
    assert evidence.status.value == 'FAIL'


def test_json_strict_boundary():
    v = view_from_dict({'camera': 'front','section':{'origin':[0,0,0],'normal':[1,0,0],'mode':'cutaway'},
                        'annotations':[{'kind':'label','point':[0,0,0],'text':'x'}]})
    assert isinstance(v.camera,Camera)
    with pytest.raises(TypeError):
        view_from_dict({'camera':'front','invented_setting':True})
    from cad_inspection.spec import view_to_dict
    annotated = View(Camera((1,-2,1)),annotations=(Label((0,0,0),'point'),
        Arrow((0,0,0),(1,0,0)),Highlight(Region.around((0,0,0),(2,2,2)))))
    assert view_from_dict(json.loads(json.dumps(view_to_dict(annotated)))) == annotated


def test_every_view_setting_invalidates_controlled_image_reuse(tmp_path,monkeypatch):
    from dataclasses import replace
    from cad_inspection.evaluation import evaluate
    from execution.artifacts import ArtifactCache
    from evaluate_model import atomic_bytes
    monkeypatch.setenv('ENGINEERING_DATA',str(tmp_path/'data'))
    shape = cq.Workplane().box(10,10,10).val()
    base = View(Camera.named('front'),annotations=(Label((0,0,0),'original'),))
    changes = [replace(base,camera=Camera((1,-2,.5))),
        replace(base,frame=Frame(Region.around((2,0,0),(4,4,4)),1)),
        replace(base,section=Section((0,0,0),(1,0,0),'cutaway')),
        replace(base,colors=(('subject','#1769a6'),)),replace(base,components=('subject',)),
        replace(base,annotations=(Label((0,0,0),'changed'),)),replace(base,show_hidden=True)]
    args=dict(inspect=['detail'],file_path=str(tmp_path/'fixture.py'),output_dir=str(tmp_path/'renders'),
              width=600,height=500,runtime='fixture')
    artifacts=ArtifactCache('cad')
    def run(view,retained):
        report={}
        def error(*args,**kwargs):
            raise AssertionError((args,kwargs))
        evaluate({'detail':lambda:Inspection(shape,view,'Inspect fixture')},shape,args,report,
                 artifacts,retained,atomic_bytes,error)
        return report['inspections'][0]
    retained={}
    assert not run(base,retained)['reused']
    repeated=run(base,retained)
    assert repeated['reused'] and repeated['recipe_reused']
    for view in changes:
        assert not run(view,{})['reused']


def test_resolved_recipes_do_not_retain_mutable_coordinate_lists():
    point = [1,2,3]
    camera = Camera(point)
    label = Label(point,'point')
    view = View(camera, annotations=[label], components=['subject'])
    point[0] = 999
    assert camera.direction == (1,2,3) and label.point == (1,2,3)
    assert isinstance(view.annotations,tuple) and isinstance(view.components,tuple)


def test_cutaway_render_preserves_full_source_and_numerical_answer():
    cfg = Configuration.explicit(cq.Assembly(name='fixture')
        .add(cq.Workplane().box(10,10,10),name='a')
        .add(cq.Workplane().box(4,4,4),name='b',loc=cq.Location((5,0,0))),name='closed')
    requirement = PairRequirement('overlap witness', min_overlap_mm3=1)
    original = cfg.check('a','b',requirement)
    from cad_inspection.render import shape_digest
    before = {n:shape_digest(cfg.shape(n)) for n in cfg.names}
    checked = pair_inspection(cfg,'a','b',requirement,view=View(Camera((1,-2,1)),
        section=Section((0,0,0),(1,0,0),'cutaway',keep='negative')),purpose='inspect')
    render(checked.inspection)
    after = cfg.check('a','b',requirement)
    assert after.overlap_mm3 == original.overlap_mm3 == checked.answer.overlap_mm3
    assert {n:shape_digest(cfg.shape(n)) for n in cfg.names} == before


def test_motion_rotated_root_replays_callback_once_and_requires_selected_sample():
    cfg = Configuration.explicit(cq.Assembly(name='fixture',loc=cq.Location((20,0,0),(0,0,30)))
        .add(cq.Workplane().box(2,2,2),name='a',loc=cq.Location((4,0,0),(0,0,20)))
        .add(cq.Workplane().box(2,2,2),name='b',loc=cq.Location((40,0,0))),name='rotated')
    deltas = []
    def transform(t):
        delta = cq.Location((t,0,0),(0,0,t*10))
        deltas.append(delta)
        return delta
    args = dict(configuration=cfg,moving='a',obstacle='b',requirement=PairRequirement('gap',min_gap_mm=1),
                samples=(0,1,2),transform=transform,parameter='travel',units='mm',view=View(Camera.named('top')),purpose='path')
    checked = motion_inspection(**args,select=2)
    assert len(deltas)==3
    expected = cfg.shape('a').moved(deltas[2])
    actual = checked.inspection.subject.shape('a')
    assert actual.Center().toTuple() == pytest.approx(expected.Center().toTuple())
    # Asymmetric vertex coordinates also distinguish wrong rotational replay.
    for a, b in zip(sorted(v.toTuple() for v in actual.Vertices()), sorted(v.toTuple() for v in expected.Vertices())):
        assert a == pytest.approx(b)
    with pytest.raises(ValueError,match='No unsuccessful'):
        motion_inspection(**args,select='first_unsuccessful')


def test_component_anchor_and_frame_follow_selected_motion_pose():
    cfg = Configuration.explicit(cq.Assembly(name='fixture')
        .add(cq.Workplane().box(4,4,4),name='moving',loc=cq.Location((5,0,0)))
        .add(cq.Workplane().box(4,4,4),name='fixed',loc=cq.Location((30,0,0))),name='initial')
    anchor=Anchor('moving',(0,0,0))
    view=View(Camera.named('top'),Frame(Region.around(anchor,(8,8,8)),1),
              components=('moving',),annotations=(Label(anchor,'Moving center'),))
    checked=motion_inspection(cfg,'moving','fixed',PairRequirement('clearance',min_gap_mm=1),
        samples=(0,10),transform=lambda t:cq.Location((t,0,0)),parameter='travel',units='mm',
        select=10,view=view,purpose='follow component')
    svg,settings=render(checked.inspection,width=600,height=500)
    assert settings['annotation_pixels'][0]['point'][0] == pytest.approx(300)
    assert settings['projected_frame_mm'][0] == pytest.approx(10)
    from cad_inspection.spec import view_to_dict
    assert view_from_dict(json.loads(json.dumps(view_to_dict(view)))) == view
    bad=View(Camera.named('top'),annotations=(Label(Anchor('missing',(0,0,0)),'bad'),))
    with pytest.raises(KeyError,match='anchor component'):
        prepare(Inspection(cfg,bad,'missing anchor'))


def call(source,*args):
    return subprocess.run([sys.executable,str(ROOT/'evaluate_model.py'),str(source),*args],
                          text=True,capture_output=True)


def test_managed_lazy_discovery_reuse_specs_exports_and_failed_view(tmp_path,monkeypatch):
    # Isolate cache history: a previous suite may legitimately have rendered
    # the later camera already, in which case reusing it would be correct.
    monkeypatch.setenv('ENGINEERING_DATA',str(tmp_path/'execution'))
    source = tmp_path/'fixture.py'
    source.write_text('''import cadquery as cq
from cad_inspection import Camera, View, Inspection
result = cq.Workplane().box(10,8,6)
def good():
    return Inspection(result, View(Camera((1,-2,1))), 'Inspect the fixture', title='Fixture')
def bad():
    raise RuntimeError('unrequested factory ran')
inspections = {'good': good, 'bad': bad}
''')
    listing = call(source,'--list-inspections','--isolated')
    assert listing.returncode == 0, listing.stdout+listing.stderr
    assert json.loads(listing.stdout)['available_inspections'] == ['good','bad']
    assert not (tmp_path/'renders').exists()
    spec = tmp_path/'view.json'
    spec.write_text(json.dumps({'quick':{'purpose':'Top detail','view':{'camera':'top',
        'frame':{'region':{'minimum':[-2,-2,-2],'maximum':[2,2,2]}}}}}))
    options = ('--inspect','good','--inspect','quick','--view-spec',str(spec),'--reuse','--export','--width','600','--height','500')
    first = call(source,*options)
    assert first.returncode == 0, first.stdout+first.stderr
    r = json.loads(first.stdout)
    assert len(r['inspections'])==2 and r['inspection_sheet']['ok']
    assert all(Path(i['path']).is_file() and Path(i['svg_path']).is_file() for i in r['inspections'])
    assert all('/.execution/engineering-cad-' not in i['path'] for i in r['inspections'])
    exports = {p:Path(p).read_bytes() for p in [e['path'] for e in r['exports']]}
    second = call(source,*options)
    assert second.returncode == 0, second.stdout+second.stderr
    assert all(i['reused'] for i in json.loads(second.stdout)['inspections'])
    assert all(Path(p).read_bytes()==content for p,content in exports.items())
    changed = json.loads(spec.read_text()); changed['quick']['view']['camera']='right'; spec.write_text(json.dumps(changed))
    third = call(source,*options)
    assert third.returncode == 0, third.stdout+third.stderr
    changed_rows = json.loads(third.stdout)['inspections']
    assert not changed_rows[1]['reused']
    # A changed declared input invalidates the retained build, including its
    # factories. Whether independently reconstructed BReps deduplicate is not
    # guaranteed by the kernel. The changed camera itself must be honored.
    assert changed_rows[1]['settings']['view']['camera']['direction'] == [1,0,0]
    failed = call(source,'--inspect','bad','--isolated')
    assert failed.returncode == 1
    assert not json.loads(failed.stdout)['inspections'][0]['ok']
    unknown = call(source,'--inspect','typo')
    assert unknown.returncode == 1 and 'Unknown inspection' in unknown.stdout


def test_managed_inspection_source_change_prevents_publication(tmp_path):
    source = tmp_path/'changing.py'
    source.write_text('''from pathlib import Path
import cadquery as cq
from cad_inspection import Camera, View, Inspection
result = cq.Workplane().box(2,3,4)
def change():
    path = Path(__file__)
    path.write_text(path.read_text()+'\\n# changed during rendering\\n')
    return Inspection(result,View(Camera.named('front')),'source guard')
inspections = {'change': change}
''')
    run = call(source,'--inspect','change','--isolated')
    assert run.returncode==1 and 'inputs changed during execution' in run.stdout
    assert not (tmp_path/'renders').exists()


def test_json_spec_change_between_read_and_identity_is_rejected(tmp_path,monkeypatch):
    import evaluate_model
    from execution import identity
    source=tmp_path/'fixture.py'; source.write_text('result = None\n')
    spec=tmp_path/'view.json'
    spec.write_text(json.dumps({'detail':{'purpose':'inspect','view':{'camera':'front'}}}))
    def change_input(*args,**kwargs):
        spec.write_text(json.dumps({'detail':{'purpose':'changed','view':{'camera':'back'}}}))
        return 'changed-identity'
    monkeypatch.setattr(identity,'cad_identity',change_input)
    with pytest.raises(SystemExit) as exc:
        evaluate_model.main([str(source),'--view-spec',str(spec),'--inspect','detail'])
    assert exc.value.code==2


def test_agent_tool_call_bookkeeping_does_not_invalidate_geometry_identity(tmp_path):
    from execution.identity import environment_identity, cad_identity
    a={'CODEX_TOOL_CALL_ID':'call-a','MODEL_INPUT':'unchanged'}
    b={'CODEX_TOOL_CALL_ID':'call-b','MODEL_INPUT':'unchanged'}
    assert environment_identity(a)==environment_identity(b)
    source=tmp_path/'fixture.py';source.write_text('result = None\n')
    assert cad_identity(source,environment=a)==cad_identity(source,environment=b)
    assert environment_identity(a)!=environment_identity(dict(b,MODEL_INPUT='changed'))
