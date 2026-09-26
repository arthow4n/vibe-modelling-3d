# Reusable export checks

Use `scripts/check_exports.py` instead of copying a mesh checker into each model.
Call `check_pair(step_path, stl_path, expected_solids, ...)` from a small
object-owned Python entry point evaluated with the shared CadQuery command. It
loads files and checks them; it does not build, repair or replace the model. See
the exercised [case entry point](../../../../model/sunglasses_case/notes/workflow_tools_check.py).

For an ordinary model, build once and save STEP/STL from the same selected
geometry. From the repository root:

```sh
uv run --locked python scripts/evaluate_model.py \
  model/object_name/object_name.py --views none \
  --step object_name.step --stl object_name.stl \
  --report notes/evaluation.json
```

Relative output paths resolve against the entry point's directory. Check each
export's `ok` status and hash in the JSON result. A successful export is not
mesh verification. Then evaluate an object-owned checker entry point:

```sh
uv run --locked python scripts/evaluate_model.py \
  model/object_name/verify_and_export.py --views none
```

The checker entry point can use `Path(__file__).resolve().parent` for a wrapper
in the object's root (or `.parent.parent` for one inside `notes/`). For example:

```python
from pathlib import Path
import importlib.util
import json
import cadquery as cq

object_dir = Path(__file__).resolve().parent
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
The helper's optional CLI can also run in the locked uv environment, but the
shared command is the normal entry point for model builds and views.

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

Synthetic damaged-mesh tests are in `tests/test_export_mesh.py`. Historical
CadQuery MCP validation for the case and E sample, including rejected mismatches,
is retained in [workflow_tools_validation.json](../../../../model/sunglasses_case/notes/workflow_tools_validation.json).
