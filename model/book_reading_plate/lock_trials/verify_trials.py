from pathlib import Path
import importlib.util,json
import cadquery as cq
root=Path(__file__).resolve().parent
helper=root.parents[2]/'.codex/skills/cadquery-3d-design/scripts/check_exports.py'
spec=importlib.util.spec_from_file_location('checker',helper)
checker=importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
from lock_trials import VARIANTS
reports={}
for letter,name in VARIANTS.items():
    stem=f'{letter}_{name}'
    reports[letter]=checker.check_pair(root/f'{stem}.step',root/f'{stem}.stl',expected_solids=2)
(root/'notes/export_checks.json').write_text(json.dumps(reports,indent=2)+'\n')
result=cq.importers.importStep(str(root/'A_compact_6mm.step'))
