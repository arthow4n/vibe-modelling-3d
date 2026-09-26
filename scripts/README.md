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
  --step vaseline_transfer_spatula.step --stl vaseline_transfer_spatula.stl
```

Export and image paths are relative to the selected entry point's directory
unless absolute. STEP and STL are disabled unless `--step` or `--stl` is
specified. The default four views go to `renders/scratch/`; `--views none`
skips images. Choose only views that answer a question, and use
`--image-format svg` when PNG is unnecessary. `--help` lists every default.

Visual inspection is optional and should answer a specific question. JSON names
output paths but contains no image content. Select a `views` entry with `ok: true`
and load its `path`; a failed render can leave an older file at that path. When
the agent environment can compose tool operations, run the command, parse its
JSON, and read the selected successful PNG within one outer call. Otherwise open
the selected image in a following call. Reuse saved files rather than rendering
again just to view them.

The command builds trusted Python in a fresh child process with `__file__`, the
file's directory as the working/import directory, and the file's `result` as
selected geometry. If `result` is absent, all `show_object()` values are used.
`result` can be a CadQuery Shape, Workplane, Assembly, or list/tuple of them.
Top-level execution is supported; a `__main__` guard does not run. Sibling
imports are fresh on each invocation. A model may itself write files or invoke
other processes; those side effects are not rolled back on failure or timeout.

The command always prints one complete JSON report to stdout. It contains
geometry, CQGI-discovered top-level parameters, source/local-import hashes,
timings, per-output status and errors. The process exit code is zero for a
successful evaluation and nonzero when evaluation fails.
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
