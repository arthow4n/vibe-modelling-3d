# Reusable export checks

Use `scripts/check_exports.py` instead of copying a mesh checker into each model.
Call `check_pair(step_path, stl_path, expected_solids, ...)` from a small
object-owned Python entry point evaluated with CadQuery MCP. It loads files and
checks them; it does not build, repair or replace the model. See the exercised
[case entry point](../../../../model/sunglasses_case/notes/workflow_tools_check.py).

The updated customized evaluator defines `__file__` and resolves relative output
paths against the model directory. A root-level object wrapper can therefore use
`Path(__file__).resolve().parent`; a wrapper inside `notes/` uses `.parent.parent`.
For ordinary exports, pass an `exports` list to `evaluate_file` so one build writes
both files, then run the independent checker on that pair:

```json
{"file_path": "/absolute/repository/model/object_name/object_name.py",
 "exports": [{"path": "object_name.step", "format": "STEP"},
             {"path": "object_name.stl", "format": "STL"}]}
```

Check each export's status and hash; a successful export is not mesh verification.
The server preserves geometry and successful exports if a requested view fails.

Compatibility: older running servers may lack `exports` and `__file__`. Inspect
the advertised schema and restart the updated server when available. Until then,
use the existing object-owned export wrapper with one explicit absolute object
path derived from the checkout. Do not repeat failing `__file__` attempts or
replace the required MCP evaluator with a shell script.

Typical entry point (adapt paths to the actual object):

```python
from pathlib import Path
import importlib.util
import json
import cadquery as cq

object_dir = Path(__file__).resolve().parent  # wrapper in the object's root
helper_path = object_dir.parents[1] / '.codex/skills/cadquery-3d-design/scripts/check_exports.py'
spec = importlib.util.spec_from_file_location('export_checks', helper_path)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
step = object_dir / 'object_name.step'
stl = object_dir / 'object_name.stl'
report = helper.check_pair(step, stl, expected_solids=2)
(object_dir / 'notes/export_checks.json').write_text(json.dumps(report, indent=2))
result = cq.importers.importStep(str(step))
```

Use the expected solid count from the design, not the count found in the file.
Ensure the notes directory exists. Keep wrappers/results inside the object.
AGENTS.md's requirement to use CadQuery MCP still applies; the helper's optional
CLI is for environments where that evaluation requirement does not apply and
CadQuery/OCP are already available. Do not install an ad-hoc Python environment.

Checks include valid STEP solids, binary STL length, finite/nondegenerate facets,
two incident faces per edge with consistent winding, positive closed-component
volume, one-to-one component bounds/volume agreement, hashes and optional bed
contact. Pairing does not depend on input solid order. It uses optimal geometric
STEP bounds to avoid confusing loose curved-surface boxes with material below
the bed.

Defaults: bounds/bed tolerance 0.035 mm and relative volume tolerance 1%.
Choose tolerances appropriate to the tessellation and critical dimensions;
never loosen them simply to silence an unexplained mismatch. Bed contact is
required for each component by default. Set `require_bed_contact=False` only for
an intentionally supported/floating arrangement and review its print plan.

Limits: binary STL only, millimetres, and exact shared mesh vertices. The helper
assumes one connected boundary shell per solid. Solids with fully enclosed
cavities can have separate inner shells and need an object-specific check;
their rejection here does not establish a geometry defect. No welding
or automatic repair occurs. Self-intersections are not detected. Matching bounds
and volumes do not prove shape identity, correct nominal dimensions, collision
clearance, strength or printability. Both exports must still originate from the
same print-ready source geometry; inspect views and verify critical dimensions.

Validation: synthetic damaged-mesh tests are in `tests/test_export_mesh.py`.
The case and E sample passed through CadQuery MCP; a wrong component count and
mismatched case STEP/E STL were rejected. Retained evidence:
[workflow_tools_validation.json](../../../../model/sunglasses_case/notes/workflow_tools_validation.json).
