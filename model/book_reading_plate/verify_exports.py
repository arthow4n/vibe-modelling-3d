from pathlib import Path
import importlib.util,json
import cadquery as cq
ROOT=Path(__file__).resolve().parent
helper=ROOT.parents[1]/'.codex/skills/cadquery-3d-design/scripts/check_exports.py'
spec=importlib.util.spec_from_file_location('export_checks',helper)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
reports={}
for name,count in [('plate_left',1),('plate_right',1),('screws',4)]:
    reports[name]=m.check_pair(ROOT/f'{name}.step',ROOT/f'{name}.stl',expected_solids=count)
(ROOT/'notes/export_checks.json').write_text(json.dumps(reports,indent=2)+'\n')
print({n:r['checks_passed'] for n,r in reports.items()})
result=cq.importers.importStep(str(ROOT/'screws.step'))
