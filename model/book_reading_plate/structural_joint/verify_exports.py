from pathlib import Path
import importlib.util,json
import cadquery as cq
root=Path(__file__).resolve().parent
helper=root.parents[2]/'.codex/skills/cadquery-3d-design/scripts/check_exports.py'
spec=importlib.util.spec_from_file_location('export_checks',helper)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
reports={}
for name,count in [('joint_test',6),('thread_fit',6),('hex_driver',1)]:
    reports[name]=m.check_pair(root/f'{name}.step',root/f'{name}.stl',expected_solids=count)
(root/'notes/export_checks.json').write_text(json.dumps(reports,indent=2)+'\n')
print(reports)
result=cq.importers.importStep(str(root/'joint_test.step'))
