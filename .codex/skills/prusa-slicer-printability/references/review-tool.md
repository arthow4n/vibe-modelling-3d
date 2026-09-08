# Reproducible review command

`scripts/review_print.py` composes the existing linear ASCII path parser with
PrusaSlicer invocation, fresh-output checks, hashes, notices, estimates, actual
deposited footprint and optional SVG layer windows. It never sends a printer job
and does not rotate, split or arrange components. It centers the supplied layout.

From the repository root, with actual object/profile paths:

```sh
python3 .codex/skills/prusa-slicer-printability/scripts/review_print.py \
  --model model/object_name/object_name.stl \
  --profile model/object_name/notes/review.ini \
  --out model/object_name/notes/review_run_01 \
  --bed 260 260 250 --expect-no-supports \
  --windows model/object_name/notes/windows.json
```

Use the user's safe limits; values above are this repository's confirmed setup,
not tool defaults. `--out` must not exist, preventing stale output from passing.
The profile controls nozzle, material, layers, supports and other settings;
the wrapper does not override them. Confirm the profile matches the intended
investigation and bed. `--expect-no-supports` flags generated supports, rather
than silently changing the profile. Use a self-contained INI; included/external
profile dependencies are not resolved or independently hashed.

Optional window file (bed coordinates, after centering):

```json
[
  {"name":"hinge", "layers":[31.0,34.4,37.8], "window":[78,117,102,139]}
]
```

Select heights and bounds from current geometry/toolpaths; example values belong
to the sunglasses case. Missing requested layers fail rather than silently using
a different height. Omit `--windows` for the initial diagnostic slice. For an
adaptive follow-up, use `inspect_gcode.py` on the saved `slice.gcode` to draw a
new window without reslicing. Its required `--json` argument can target this
run's existing `paths.json`: with the same G-code and unchanged parser, this
rewrites the same summary instead of creating a duplicate. Do not target
`summary.json`, which contains the wrapper's hashes and review results. Preserve
separate evidence when the input or parser changes. See the command in
[CLI and paths](cli-and-paths.md).

Outputs: `command.json`, `summary.json`, `paths.json`, requested SVGs, and ignored
`slice.gcode`/`slice.log`. The summary records input/G-code hashes, CLI help header
with installed version, log notices, filament/time metadata, support count,
and deposition bounds including half path width and brims. Inspect every chosen
SVG (or convert it to PNG); writing an image is not inspection.

Exit 0 means the requested automated checks found no listed review conditions.
Exit 2 means notices, footprint violations or unexpected support paths need
review. Failures such as missing fresh G-code, parser errors and absent layers
exit nonzero; inspect the log and do not claim a completed review. A zero exit
does not certify print quality. Notice extraction is a convenience, not an
exhaustive understanding of slicer diagnostics; retain/read the raw log when
results are uncertain.

The parser requires millimetres, absolute XYZ, relative E, layer comments and
linear planar moves. WIDTH comments are preferred; absent comments retain the
parser's 0.45 mm default, so do not treat such footprint bounds as calibrated.
Bounds assume a rectangular safe area with origin (0,0); they exclude travel,
start/end machine motion and physical flow spread. Path roles and lengths do not
establish anchors, free-air spans or reliable clearance. See [case lessons](case-lessons.md).

Validation uses regression tests in `tests/test_review_print.py` and a real
PrusaSlicer review of the existing case, without editing its geometry. Evidence:
[retained review](../../../../model/sunglasses_case/notes/reusable_tool_review/summary.json).
