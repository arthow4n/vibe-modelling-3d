# Unified OrcaSlicer review command

`scripts/review_print.py` is the only user-facing review command. It runs
OrcaSlicer in CLI mode, checks its structured result and fresh G-code, reads
effective settings, summarizes deposited paths, checks bounds against the
selected printer profile, and prints one JSON report to stdout. It never sends a
printer job.

From the repository root, use the maintained Qidi Q2C / PETG defaults:

```sh
uv run --locked python .codex/skills/orca-slicer-printability/scripts/review_print.py \
  --model model/object_name/object_name.stl
```

The profiles are Qidi Q2C with a 0.4 mm nozzle, Generic PETG, and a 0.20 mm
Standard process with 7% adaptive cubic sparse infill. The Q2C profile defines
an effective 270 × 270 × 256 mm printable volume, matching the
[manufacturer's build volume](https://us.qidi3d.com/products/q2c). There is no
separate bed argument: Orca's exported `printable_area` and `printable_height`
are the source of machine bounds. The helper accepts axis-aligned rectangular
printable areas and fails clearly for another shape.

To use other Orca profiles, replace the three files together as appropriate:

```sh
uv run --locked python .codex/skills/orca-slicer-printability/scripts/review_print.py \
  --model model/object_name/object_name.stl \
  --printer model/object_name/notes/printer.json \
  --process model/object_name/notes/process.json \
  --filament model/object_name/notes/filament.json \
  --placement preserve
```

The `--printer` profile also supplies bounds. For stricter usable dimensions,
make those limits part of that profile. The helper does not add an independent
conservative bed override. Use `--expect-no-supports` when support-free output
is an explicit requirement; support segments are reported either way.

## Arguments and defaults

These values must match `review_print.py --help`:

| Argument | Default |
| --- | --- |
| `--model MODEL` | Required |
| `--printer PRINTER` | `.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json` |
| `--process PROCESS` | `.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.20-standard-adaptive-cubic-7.json` |
| `--filament FILAMENT` | `.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/generic-petg-qidi-q2c-0.4.json` |
| `--placement {preserve,center,assembly}` | `center` |
| `--expect-no-supports` | Off (`false`) |
| `--keep-run` | Off (`false`) |

There are no `--out`, `--bed`, `--slicer`, `--timeout`, `--purpose`, or
`--profile-scope` arguments. Orca is inferred from `ORCASLICER_COMMAND`, then a
host `orca-slicer`, then Flatpak OrcaSlicer. The internal CLI timeout is 600
seconds.

## Placement

`--placement center` is the default. It uses `--arrange 1 --orient 0
--allow-rotations=0`: Orca can relocate the loaded layout but cannot auto-orient
or rotate it. For one STL, this moves the mesh as one object and preserves its
internal part positions. For a multi-object project, automatic arrangement may
change object-to-object positions; use the intentional existing layout with
`preserve`, or choose `assembly` to group the loaded parts onto one plate while
retaining their internal positions.

Do not silently rotate, scale, repair, split or union input geometry. Placement
only affects how the slicer positions the delivered mesh.

## Output and acceptance

The command prints one JSON report with the model and profile paths, slicer
version header, effective printer volume and selected settings, placement,
the `expect_no_supports` choice, notices, and per-plate:

- XY bounds including half line width, brim and generated support paths;
- layer range, layer count and support-segment count;
- deposited path-role totals, longest bridge-role centerlines, and G-code
  filament/time metadata.

Travel, start/end machine motion, physical flow spread, anchor/free-air span,
clearance and physical print quality are not measured. A missing G-code width
uses the parser's 0.45 mm fallback and is only a diagnostic estimate.
The notice list combines structured plate warnings with keyword-filtered log
lines; an empty list does not prove the full slicer log contains no messages.
Use `--keep-run` if full log review is needed. Mesh-repair status and retention
of every intended component are not assessed.

By default G-code, logs, `result.json`, effective settings and other temporary
files are deleted at exit. `--keep-run` retains these files and includes
`kept_run_directory` in the JSON. On an error, that flag also keeps the files
and the error identifies the directory. The usual evidence record should
contain the concise stdout summary and relevant conclusion, not the transient
files.

The helper requires a zero CLI exit, a successful Orca result with one or more
sliced plates, fresh nonempty G-code for every reported plate, effective
settings and nonempty parsed deposition. A zero exit alone is insufficient.
Check the effective settings for printer, nozzle, filament and process values.
The default profiles are resolved snapshots because Orca's direct CLI profile
loading can leave inherited PETG values at PLA defaults; see
[CLI and profile setup](cli-and-paths.md).

Warnings, out-of-profile-volume paths, and a violated `--expect-no-supports`
condition make the helper exit 2 for review. Exit 0 means no listed automated
condition was found, not that every intended component is present or that the
model is printable or physically safe.
