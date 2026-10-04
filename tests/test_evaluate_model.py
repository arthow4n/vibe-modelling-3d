"""Integration checks for the command's file and artifact contract."""
import json
from pathlib import Path
import subprocess
import sys
from PIL import Image, ImageChops
import pytest
import cadquery as cq
from evaluate_model import render, view_transform

COMMAND = Path(__file__).resolve().parents[1] / "evaluate_model.py"


def call(path, *args):
    return subprocess.run([sys.executable, str(COMMAND), str(path), *args],
                          text=True, capture_output=True, timeout=30)


def test_sibling_import_exports_and_view(tmp_path):
    (tmp_path / "dimensions.py").write_text("WIDTH = 13\n")
    source = tmp_path / "piece.py"
    source.write_text("import cadquery as cq\nfrom dimensions import WIDTH\n"
                      "result = cq.Workplane('XY').box(WIDTH, 7, 3)\n")
    run = call(source, "--views", "front", "--output-dir", "renders", "--export")
    assert run.returncode == 0, run.stderr + run.stdout
    data = json.loads(run.stdout)
    assert data["ok"] and data["geometry"]["valid"]
    assert all(item["ok"] for item in data["exports"] + data["views"])
    assert (tmp_path / "renders/piece_front.png").stat().st_size > 0
    assert (tmp_path / "piece.step").stat().st_size > 0
    assert (tmp_path / "piece.stl").stat().st_size > 0

    png = call(source, "--views", "front", "--output-dir", "renders")
    assert png.returncode == 0, png.stderr + png.stdout
    image = Image.open(tmp_path / "renders/piece_front.png").convert("RGBA")
    assert image.getpixel((0, 0)) == (255, 255, 255, 255)
    assert image.getextrema()[0][0] < 255  # visible model strokes

    # A second worker must read the changed sibling source, not stale bytecode.
    (tmp_path / "dimensions.py").write_text("raise RuntimeError('fresh sibling loaded')\n")
    rerun = call(source, "--views", "none")
    assert rerun.returncode != 0
    assert "fresh sibling loaded" in json.loads(rerun.stdout)["errors"][0]["message"]


def test_build_error_cannot_claim_old_artifacts(tmp_path):
    source = tmp_path / "broken.py"
    source.write_text("raise ValueError('bad geometry')\n")
    old = tmp_path / "broken.step"
    old.write_text("old output")
    run = call(source, "--views", "none", "--export")
    assert run.returncode != 0
    data = json.loads(run.stdout)
    assert not data["ok"] and data["errors"][0]["stage"] == "build"
    assert data["exports"] == [] and old.read_text() == "old output"
    assert not (tmp_path / "broken.stl").exists()


@pytest.mark.parametrize("failed", [False, True])
def test_report_retains_native_success_or_failure_with_summary(tmp_path, failed):
    source = tmp_path / "piece.py"
    source.write_text("raise ValueError('bad geometry')\n" if failed else
                      "import cadquery as cq\nresult = cq.Workplane('XY').box(3, 4, 5)\n")
    destination = tmp_path / "notes" / "review.json"
    run = call(source, "--views", "none", "--report", str(destination), "--summary")
    native = json.loads(destination.read_text())
    summary = json.loads(run.stdout)
    assert run.returncode == (1 if failed else 0)
    assert native["ok"] == summary["ok"] == (not failed)
    assert native["errors"] == summary["errors"]
    assert summary["report_path"] == str(destination)
    assert native["timings_seconds"] == summary["timings_seconds"]


def test_saved_report_matches_default_stdout(tmp_path):
    source = tmp_path / "broken.py"
    source.write_text("raise ValueError('retain the native error')\n")
    destination = tmp_path / "review.json"
    run = call(source, "--views", "none", "--report", str(destination))
    assert run.returncode == 1
    assert json.loads(destination.read_text()) == json.loads(run.stdout)


def test_changed_revision_cannot_replace_current_report(tmp_path,capsys):
    from argparse import Namespace
    from execution.identity import cad_identity
    from evaluate_model import emit_report
    source=tmp_path/'part.py';source.write_text('result = 1\n')
    identity=cad_identity(source)
    destination=tmp_path/'review.json';destination.write_text('newer evidence')
    source.write_text('result = 2\n')
    report={'ok':True,'errors':[]}
    emit_report(report,Namespace(report=destination,summary=True,
        _publication=(source,(),None,identity)))
    assert destination.read_text()=='newer evidence'
    assert not report['ok'] and report['errors'][0]['stage']=='report'
    assert 'report_path' not in json.loads(capsys.readouterr().out)


def test_summary_keeps_slice_review_status_and_full_saved_settings(tmp_path, monkeypatch, capsys):
    import evaluate_model
    existing = tmp_path / "piece.stl"
    existing.write_text("mock slice input")
    destination = tmp_path / "notes" / "review.json"
    probe = {"ok": True, "generated": True, "supported_plates": [1]}
    monkeypatch.setattr(evaluate_model, "review", lambda *a, **kw: {
        "review_required": True, "support_probe": probe,
        "log_notices": ["Review support placement"], "effective_settings": {"wall_loops": "2"}})
    code = evaluate_model.main(["--slice-existing", str(existing),
                                "--report", str(destination), "--summary"])
    summary = json.loads(capsys.readouterr().out)
    native = json.loads(destination.read_text())
    assert code == 2 and native["ok"] and summary["ok"]
    assert summary["slice"]["review_required"] and summary["slice"]["support_probe"] == probe
    assert summary["slice"]["log_notices"] == ["Review support placement"]
    assert "effective_settings" not in summary["slice"]
    assert native["slice"]["effective_settings"] == {"wall_loops": "2"}


def test_report_write_failure_preserves_completed_stage_status(tmp_path, capsys, monkeypatch):
    from argparse import Namespace
    from evaluate_model import emit_report
    destination = tmp_path / "review.json"
    destination.write_text("previous report")
    def reject_replace(*args):
        raise OSError("report replacement failed")
    monkeypatch.setattr(Path, "replace", reject_replace)
    report = {"ok": True, "geometry": {"valid": True}, "errors": []}
    emit_report(report, Namespace(report=destination, summary=True))
    output = json.loads(capsys.readouterr().out)
    assert not output["ok"] and output["errors"][0]["stage"] == "report"
    assert output["geometry"]["valid"] and "report_path" not in output
    assert destination.read_text() == "previous report"
    assert list(tmp_path.iterdir()) == [destination]


def test_report_cannot_replace_repository_profile_from_another_working_directory(tmp_path, monkeypatch):
    import evaluate_model
    profile = evaluate_model.REPO_ROOT / evaluate_model.DEFAULTS["printer"]
    original = profile.read_bytes()
    source = tmp_path / "piece.py"
    source.write_text("raise AssertionError('must reject before building')\n")
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as error:
        evaluate_model.main([str(source), "--report", str(profile)])
    assert error.value.code == 2 and profile.read_bytes() == original


@pytest.mark.parametrize("options", [
    ["--summary"], ["--report", "piece.py"], ["--report", "profile.json", "--slice"]])
def test_report_options_reject_missing_evidence_or_input_collision(tmp_path, options):
    source = tmp_path / "piece.py"
    original = "import cadquery as cq\nresult = cq.Workplane('XY').box(3, 4, 5)\n"
    source.write_text(original)
    profile = tmp_path / "profile.json"
    profile.write_text("original profile")
    options = [str(tmp_path / item) if item in ("piece.py", "profile.json") else item for item in options]
    if "--slice" in options:
        options += ["--slice-printer", str(profile)]
    run = call(source, *options)
    assert run.returncode == 2 and not run.stdout
    assert source.read_text() == original and profile.read_text() == "original profile"


@pytest.mark.parametrize('view', ['front', 'back', 'left', 'right', 'isometric', 'isometric_back'])
def test_render_keeps_vertical_pillar_and_top_cap_upright(view):
    """Actual PNG geometry catches sideways side views and inverted/rolled iso."""
    import io
    pillar = cq.Workplane('XY').box(4, 4, 60, centered=False)
    cap = cq.Workplane('XY').box(18, 18, 3, centered=False).translate((-7, -7, 60))
    shape = pillar.union(cap).val()
    png = Image.open(io.BytesIO(render(shape, view, 800, 600, False))).convert('RGB')
    ink = ImageChops.difference(png, Image.new('RGB', png.size, 'white'))
    bounds = ink.getbbox()
    assert bounds is not None
    x0, y0, x1, y1 = bounds
    assert y1-y0 > 2*(x1-x0), 'Z pillar is rolled sideways'
    third = (y1-y0)//3
    upper = ink.crop((x0, y0, x1, y0+third)).getbbox()
    lower = ink.crop((x0, y1-third, x1, y1)).getbbox()
    assert upper[2]-upper[0] > 2*(lower[2]-lower[0]), 'Top cap is not at the top'


def test_view_frame_preserves_bed_axes_and_source_geometry():
    top = view_transform('top')
    assert top.multiply(cq.Vector(1, 0, 0)).toTuple() == pytest.approx((1, 0, 0))
    assert top.multiply(cq.Vector(0, 1, 0)).toTuple() == pytest.approx((0, 1, 0))
    shape = cq.Workplane('XY').box(7, 5, 11, centered=False).val()
    before = [v.toTuple() for v in shape.Vertices()]
    render(shape, 'isometric', 800, 600, False)
    assert [v.toTuple() for v in shape.Vertices()] == before


def test_default_skips_views_and_geometry_reuse_invalidates_inputs(tmp_path):
    sibling=tmp_path/'dimension.py';sibling.write_text('WIDTH=3\n')
    data=tmp_path/'data.txt';data.write_text('5')
    source=tmp_path/'reuse.py'
    source.write_text('import cadquery as cq\nfrom dimension import WIDTH\n'
                      'result=cq.Workplane("XY").box(WIDTH,4,int(open("data.txt").read()))\n')
    first=json.loads(call(source,'--reuse','--dependency',str(data)).stdout)
    second=json.loads(call(source,'--reuse','--dependency',str(data)).stdout)
    assert first['ok'] and first['views']==[] and first['exports']==[]
    assert not first['reuse']['geometry'] and second['reuse']['geometry']
    sibling.write_text('WIDTH=6\n')
    changed=json.loads(call(source,'--reuse','--dependency',str(data)).stdout)
    assert changed['ok'] and not changed['reuse']['geometry']
    data.write_text('8')
    changed_data=json.loads(call(source,'--reuse','--dependency',str(data)).stdout)
    assert changed_data['ok'] and not changed_data['reuse']['geometry']


def test_reused_exports_are_identity_bound_and_restore_tampered_output(tmp_path):
    source=tmp_path/'piece.py';source.write_text('import cadquery as cq\nresult=cq.Workplane("XY").box(3,4,5)\n')
    first=json.loads(call(source,'--reuse','--export').stdout)
    step=tmp_path/'piece.step';original=step.read_bytes();step.write_text('tampered')
    second=json.loads(call(source,'--reuse','--export').stdout)
    assert first['ok'] and second['ok'] and second['reuse']['geometry']
    assert all(e['reused'] for e in second['exports']) and step.read_bytes()==original


def test_changed_source_during_build_cannot_overwrite_artifacts(tmp_path):
    source=tmp_path/'slow.py';source.write_text('import cadquery as cq,time\nopen("started","w").write("yes")\ntime.sleep(.7)\nresult=cq.Workplane("XY").box(3,4,5)\n')
    previous=tmp_path/'slow.step';previous.write_text('previous')
    process=subprocess.Popen([sys.executable,str(COMMAND),str(source),'--export'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    import time
    deadline=time.monotonic()+15
    while not (tmp_path/'started').exists() and time.monotonic()<deadline:time.sleep(.02)
    assert (tmp_path/'started').exists()
    source.write_text('raise ValueError("new revision")\n')
    stdout,stderr=process.communicate(timeout=10)
    assert process.returncode==1 and not json.loads(stdout)['ok']
    assert previous.read_text()=='previous' and not (tmp_path/'slow.stl').exists()


def test_automatic_artifacts_preserve_script_side_effects_and_dynamic_inputs(tmp_path,monkeypatch):
    monkeypatch.setenv('ENGINEERING_DATA',str(tmp_path/'records'))
    source=tmp_path/'dynamic.py'
    source.write_text('import cadquery as cq\nfrom pathlib import Path\np=Path("count")\np.write_text(str(int(p.read_text())+1 if p.exists() else 1))\nresult=cq.Workplane("XY").box(int(Path("size").read_text()),4,5)\n')
    (tmp_path/'size').write_text('3')
    first=json.loads(call(source,'--export').stdout)
    second=json.loads(call(source,'--export').stdout)
    assert first['ok'] and second['ok'] and not second['reuse']['geometry']
    assert (tmp_path/'count').read_text()=='2'
    assert all(e['reused'] for e in second['exports'])
    (tmp_path/'size').write_text('7')
    third=json.loads(call(source,'--export').stdout)
    assert third['ok'] and not any(e['reused'] for e in third['exports'])
    assert third['reuse']['artifact_identity']!=second['reuse']['artifact_identity']


def test_declaration_automates_geometry_reuse_and_fresh_overrides(tmp_path):
    source=tmp_path/'declared.py'
    source.write_text('import cadquery as cq\nresult=cq.Workplane("XY").box(int(open("size").read()),4,5)\n')
    (tmp_path/'size').write_text('3')
    source.with_suffix('.execution.json').write_text(json.dumps(dict(schema_version=1,deterministic=True,inputs=['size'])))
    assert not json.loads(call(source).stdout)['reuse']['geometry']
    assert json.loads(call(source).stdout)['reuse']['geometry']
    assert not json.loads(call(source,'--fresh').stdout)['reuse']['geometry']
    (tmp_path/'size').write_text('7')
    assert not json.loads(call(source).stdout)['reuse']['geometry']


def test_unavailable_trace_and_cache_storage_preserves_cad(tmp_path,monkeypatch):
    target=tmp_path/'not_directory';target.write_text('occupied')
    monkeypatch.setenv('ENGINEERING_DATA',str(target))
    source=tmp_path/'shape.py';source.write_text('import cadquery as cq\nresult=cq.Workplane("XY").box(3,4,5)\n')
    report=json.loads(call(source,'--export').stdout)
    assert report['ok'] and all(e['ok'] for e in report['exports'])


def test_custom_environment_inputs_invalidate_geometry(tmp_path,monkeypatch):
    source=tmp_path/'environment.py';source.write_text('import cadquery as cq,os\nresult=cq.Workplane("XY").box(int(os.environ["ENGINEERING_DIMENSION"]),4,5)\n')
    monkeypatch.setenv('ENGINEERING_DIMENSION','3')
    assert not json.loads(call(source,'--reuse').stdout)['reuse']['geometry']
    assert json.loads(call(source,'--reuse').stdout)['reuse']['geometry']
    monkeypatch.setenv('ENGINEERING_DIMENSION','7')
    assert not json.loads(call(source,'--reuse').stdout)['reuse']['geometry']


@pytest.mark.parametrize('options,expected', [([],1536),(['--memory-mb','1792'],1792),
    (['--export'],1024),(['--views','front'],1024),(['--slice'],1024)])
def test_geometry_memory_declaration_stage_scope_and_explicit_override(tmp_path,monkeypatch,capsys,options,expected):
    import evaluate_model
    from execution import cad
    source=tmp_path/'budgeted.py';source.write_text('result = 1\n')
    source.with_suffix('.execution.json').write_text(json.dumps(dict(schema_version=1,deterministic=False,
        resources=dict(geometry_memory_mb=1536))))
    requests=[]
    def dispatch(request,**kwargs):
        requests.append(request)
        return dict(ok=True,errors=[],exports=[],views=[])
    monkeypatch.setattr(cad,'execute',dispatch)
    assert evaluate_model.main([str(source),*options])==0
    capsys.readouterr()
    assert requests[0]['memory_mb']==expected
    assert not requests[0]['reuse']


@pytest.mark.parametrize('memory',[True,0,-1,'1024'])
def test_invalid_geometry_memory_declaration_is_rejected(tmp_path,memory):
    source=tmp_path/'budgeted.py';source.write_text('result = 1\n')
    source.with_suffix('.execution.json').write_text(json.dumps(dict(schema_version=1,deterministic=False,
        resources=dict(geometry_memory_mb=memory))))
    run=call(source)
    assert run.returncode==2 and 'positive integer' in run.stderr


def test_geometry_memory_declaration_reaches_actual_coordinator(tmp_path,monkeypatch):
    from execution.history import iter_records
    import uuid
    monkeypatch.setenv('ENGINEERING_INSTANCE',uuid.uuid4().hex)
    monkeypatch.setenv('ENGINEERING_DATA',str(tmp_path/'records'))
    source=tmp_path/'budgeted.py'
    source.write_text('import cadquery as cq\nresult=cq.Workplane("XY").box(3,4,5)\n')
    declaration=source.with_suffix('.execution.json')
    declaration.write_text(json.dumps(dict(schema_version=1,deterministic=False,resources=dict(geometry_memory_mb=1536))))
    run=call(source,'--fresh')
    assert run.returncode==0,run.stdout+run.stderr
    first=list(iter_records(tmp_path/'records'))
    assert first[0]['requested_memory_mb']==1536 and first[0]['admission']['requested_memory_mb']==1536
    declaration.unlink()
    run=call(source,'--fresh')
    assert run.returncode==0,run.stdout+run.stderr
    records=list(iter_records(tmp_path/'records'))
    assert sorted(r['requested_memory_mb'] for r in records)==[1024,1536]
