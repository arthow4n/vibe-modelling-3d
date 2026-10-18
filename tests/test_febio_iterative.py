"""Native bounded-memory solver qualification and failure control."""
import json
import os
import re
from pathlib import Path
from dataclasses import replace
import xml.etree.ElementTree as ET
import pytest
from physical_analysis.backends.febio import FebioBackend, FgmresILUT
from model.dental_travel_case.retention_febio_solver_qualification import options, run_comparison


@pytest.mark.parametrize('field,value', [('max_iterations',True),('restart_iterations',0),
    ('max_fill',1.5),('relative_tolerance',float('nan')),('absolute_tolerance',0),
    ('fill_tolerance',False),('restart_iterations',1001)])
def test_invalid_linear_options_rejected(field,value):
    fields=dict(options().__dict__);fields[field]=value
    with pytest.raises(ValueError):FgmresILUT(**fields)
    with pytest.raises(TypeError):FebioBackend(linear_solver='fgmres')


PLUGIN=Path(os.environ.get('FEBIO_RESTART_PLUGIN',
    '~/.local/opt/febio-fgmres-restart-3ef378562-headers-qualified/libfgmres_restart_checked.so')).expanduser()


@pytest.mark.parametrize('plugin',[None,PLUGIN],ids=['native150','corrected30'])
def test_native_ilut_matches_direct_and_rejects_insufficient_iterations(tmp_path,plugin):
    results=run_comparison(tmp_path,plugin=plugin)
    direct=results['direct'].require_completed()
    iterative=results['iterative'].require_completed()
    opened=results['open'].require_completed()
    for field in ('max_penetration_mm','max_abs_principal_strain'):
        assert iterative.metrics[field]==pytest.approx(direct.metrics[field],rel=1e-5,abs=1e-8)
    assert iterative.metrics['peak_motion_force_N']==pytest.approx(direct.metrics['peak_motion_force_N'],rel=1e-5)
    assert iterative.metrics['max_force_balance_relative']<1e-6
    assert abs(opened.metrics['peak_motion_force_N']['BC2'])<1e-6
    assert iterative.metrics['observations']['receiving_surface']['mean_mm'][2]<0
    failed=results['inadequate']
    assert not failed.completed and not failed.metrics
    assert 'failed or did not finish' in str(failed.errors)
    log=(tmp_path/'inadequate/solver.log').read_text()
    assert 'FGMRES:' in log
    calls=re.search(r'Total calls to linear solver[ .\t]*:\s*(\d+)',log)
    assert calls is not None, 'Native solver statistics are missing'
    assert int(calls[1])>0
    native=ET.parse(tmp_path/'iterative/analysis.feb').find('./Control/solver/linear_solver')
    assert native.attrib['type']==('fgmres_restart_checked' if plugin else 'fgmres')
    assert native.findtext('max_restart')==('30' if plugin else '150')
    assert native.findtext('fail_max_iters')=='1'
    recorded=json.loads((tmp_path/'iterative/case.json').read_text())['febio']['linear_solver']
    assert iterative.provenance['linear_solver']==recorded
    assert recorded['max_fill']==12 and recorded['replace_zero_diagonal'] is False
    assert ET.parse(tmp_path/'direct/analysis.feb').find('./Control/solver/linear_solver') is None


def test_plugin_identity_mismatch_rejected_before_native_launch(tmp_path):
    plugin=tmp_path/'libfgmres_restart_checked.so'
    plugin.write_bytes(b'changed native plugin')
    (tmp_path/'build_manifest.json').write_text(json.dumps(dict(plugin_sha256='wrong')))
    backend=FebioBackend(linear_solver=replace(options(),restart_correction_plugin=plugin))
    with pytest.raises(ValueError,match='differs from its build manifest'):
        backend.configure_request(dict(loads=[],nonlinear=True,contacts=[]))
