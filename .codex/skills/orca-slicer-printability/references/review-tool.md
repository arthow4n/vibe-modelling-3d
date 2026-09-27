# Reproducible OrcaSlicer review command

`scripts/review_print.py` runs OrcaSlicer in CLI mode, checks its structured
result and fresh G-code, records the effective settings, parses deposited paths,
checks bounds and optionally draws targeted layer windows. It never sends a
printer job.

From the repository root, a final reference smoke slice can use the maintained
Qidi/PETG profiles by default:

```sh
uv run --locked python .codex/skills/orca-slicer-printability/scripts/review_print.py \
  --model model/object_name/object_name.stl \
  --out model/object_name/notes/orca_review_01 \
  --bed 260 260 250
```

The output path must not exist; the helper refuses stale-output reuse. Defaults
are the Qidi Q2C 0.4 mm nozzle, Generic PETG and a 0.20 mm Standard process with
7% adaptive cubic sparse infill. Supply the user's actual profiles to make
actual-profile observations:

```sh
uv run --locked python .codex/skills/orca-slicer-printability/scripts/review_print.py \
  --model model/object_name/object_name.stl \
  --printer model/object_name/notes/printer.json \
  --process model/object_name/notes/process.json \
  --filament model/object_name/notes/filament.json \
  --profile-scope actual \
  --purpose investigation \
  --out model/object_name/notes/orca_investigation_01 \
  --bed 260 260 250
```

Use the user's confirmed safe dimensions; 260 × 260 × 250 mm is this
repository's practical review envelope, not Orca's system default. `--bed`
checks each oriented axis and includes brim/support paths from the G-code.
`--expect-no-supports` flags any generated support paths. The helper does not
change support settings.

## Placement

`--placement center` is the default. It uses `--arrange 1 --orient 0
--allow-rotations=0`: Orca can relocate the loaded layout but cannot auto-orient
or rotate it. For one STL, this moves the mesh as one object and preserves its
internal part positions. For a multi-object project, automatic arrangement may
change object-to-object positions; inspect the result or choose another mode.

- `--placement preserve` disables arrangement and orientation. Use it only when
  the model's existing bed placement is intentional and valid.
- `--placement assembly` adds `--assemble` before arrangement, grouping loaded
  parts and placing them on one plate while retaining their internal positions.
  This changes a multi-plate project's plate grouping, so choose it deliberately.

The exact arguments are retained in `command.json`. Do not silently rotate,
scale, repair, split or union the input. The slicer checks the delivered mesh;
the placement mode only affects how it is positioned on the plate.

## Targeted layer windows

Add `--windows` only for a named path question that structured output cannot
answer. Example file, with bed coordinates after the selected placement:

```json
[
  {"name":"hinge", "plate":1, "layers":[31.0,34.4,37.8], "window":[78,117,102,139]}
]
```

Omit `plate` for plate 1. Choose heights and bounds from the current geometry
and paths. Missing requested layers fail instead of silently substituting a
different height. For a new window on the same slice, use `inspect_gcode.py` on
the saved G-code; do not reslice. Roles and segment lengths do not establish
anchors or unsupported spans.

## Outputs and acceptance

The fresh output directory contains:

- `command.json`, `summary.json`, `effective-settings.json`, `result.json`, and
  `paths.json`;
- requested SVG windows;
- ignored raw `*.gcode` and `*.log` files.

The helper requires a zero CLI exit, a successful `result.json` with at least one
sliced plate, fresh nonempty G-code, effective-settings export and nonempty
parsed deposition. A zero exit alone is insufficient. Inspect the settings to
confirm selected printer, nozzle, filament type, temperatures and process. The
default profiles are fully resolved snapshots because Orca's direct CLI profile
loading can accept a child preset name while leaving inherited PETG values at
the default PLA values; see [CLI and profile setup](cli-and-paths.md).

Orca warnings and out-of-envelope footprints make the helper exit 2 for review.
Exit 0 means no listed automated review condition was found, not that the part is
printable or physically safe. `review_required` is not a universal pass/fail
verdict. A valid slice does not prove that every intended component is present
or reveal every mesh defect.

In the object's concise evidence record, link the helper report and state:
profile scope/purpose, OrcaSlicer version, input paths, selected effective
settings, smoke acceptance, notices, per-plate footprint/height and support
presence. Report unresolved notices separately from smoke acceptance. The
helper's path bounds include half the reported line width, brims and supports;
they exclude travel, start/end machine motion and physical flow spread. If a
width is absent, the parser's 0.45 mm fallback is only a diagnostic estimate.
Bounds assume a rectangular safe area with origin (0,0).
