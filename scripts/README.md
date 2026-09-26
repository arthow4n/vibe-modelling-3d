# CadQuery command

Run from the repository root. Install the locked Python environment with
`uv sync --locked`; use `uv run --locked` for subsequent commands. CadQuery and
its OCP bindings are Python dependencies in the root `pyproject.toml`.
PNG views use CairoSVG from the locked Python environment; SVG views need no
raster conversion. PrusaSlicer is a separate system command for print review.

```sh
uv run --locked python scripts/evaluate_model.py \
  model/vaseline_transfer_spatula/vaseline_transfer_spatula.py \
  --views isometric,front --output-dir renders/print \
  --step vaseline_transfer_spatula.step --stl vaseline_transfer_spatula.stl \
  --report notes/evaluation.json
```

Paths for exports, images and `--report` are relative to the selected entry
point's directory unless absolute. The default four views go to
`renders/scratch/`; `--views none` skips images. Choose only views that answer a
question, and use `--image-format svg` when PNG is unnecessary. Other options
include `--width`, `--height`, `--show-hidden`, `--stl-tolerance`,
`--stl-angular-tolerance`, and `--timeout`; see `--help`.

The command builds trusted Python in a fresh child process with `__file__`, the
file's directory as the working/import directory, and the file's `result` as
selected geometry. If `result` is absent, all `show_object()` values are used.
`result` can be a CadQuery Shape, Workplane, Assembly, or list/tuple of them.
Top-level execution is supported; a `__main__` guard does not run. Sibling
imports are fresh on each invocation. A model may itself write files or invoke
other processes; those side effects are not rolled back on failure or timeout.

The command prints a compact status summary. Add `--report notes/evaluation.json`
to save structured JSON, or `--json` to print it. The JSON contains geometry,
CQGI-discovered top-level parameters, source/local-import hashes, timings,
per-output status and errors.
Only an output with `ok: true` is a current successful artifact; a failed output
may leave an older file at its destination. A view failure does not erase valid
geometry or successful exports. A successful export is not independent mesh
verification: use the existing `check_exports.py` helper on the actual STEP/STL
pair, then run the relevant print review. Units are assumed to be millimetres.
The script does not repair, orient, or rearrange the model.

Some object-owned entry points perform custom exports or checks while building.
Keep those entry points when their behavior matters; the command's optional
exports cover the ordinary single-layout case. `--views none` and no export flags
perform a geometry-only evaluation (apart from model-owned side effects).
