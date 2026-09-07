"""Validate reusable export helper against existing case artifacts; no model edits."""
from pathlib import Path
import importlib.util
import json
import cadquery as cq

HERE=Path(globals().get('__file__','/home/hevar/git/vibe-modelling-3d/model/sunglasses_case/notes/workflow_tools_check.py')).resolve().parent
CASE=HERE.parent
REPO=HERE.parents[2]
spec=importlib.util.spec_from_file_location('check_exports',REPO/'.codex/skills/cadquery-3d-design/scripts/check_exports.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
report={}
for name in ('sunglasses_case','E_extra_firm_side_printed_keeper'):
    report[name]=helper.check_pair(CASE/(name+'.step'),CASE/(name+'.stl'),3)
rejections=[]
for stl,count in [('sunglasses_case.stl',2),('E_extra_firm_side_printed_keeper.stl',3)]:
    try:
        helper.check_pair(CASE/'sunglasses_case.step',CASE/stl,count)
    except ValueError as exc:
        rejections.append(str(exc))
    else:
        raise AssertionError('Expected mismatch was accepted')
report['expected_rejections']=rejections
(HERE/'workflow_tools_validation.json').write_text(json.dumps(report,indent=2)+'\n')
result=cq.importers.importStep(str(CASE/'sunglasses_case.step'))
