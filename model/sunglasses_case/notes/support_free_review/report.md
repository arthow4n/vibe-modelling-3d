# Flat-print case inspection — 2026-09-06

PrusaSlicer 2.9.6 was used on the final rounded, tightened hinge revision.
Both broad case panels lie on the bed. All slicing used supports disabled.
The earlier standing-case investigation in `../slicer_review/` is historical;
its 87 mm overhead bridge does not describe the final print orientation.

## Results

| Model | Layers | Bridge infill | Overhang perimeter | Support paths | Diagnostic estimate |
| --- | ---: | ---: | ---: | ---: | --- |
| Complete case | 235 | 0 | 0 | 0 | 263.74 g, 21 h 6 min |
| Hinge coupon | 213 | 0 | 0 | 0 | 15.96 g, 1 h 43 min |

Both commands completed without stability warnings. Estimates use generic
motion settings, not the user's calibrated printer. `case_paths.json` and
`hinge_paths.json` record actual deposited path roles. `hinge_layers.svg` and
`.png` compare selected current layers with the preceding deposited layer:
conical pivots and socket roofs grow progressively and bearing gaps remain.
This is visual toolpath evidence, not a physical sag or tolerance simulation.

`mesh_checks.json` records final STL hashes, dimensions, two watertight
components per model, and bed contact for both parts. Mathematical cone apices
initially exported degenerate facets despite valid CAD and clean slicing;
small flat tips resolved this and the final meshes have paired triangle edges.

A first flat-print trial with 6 top/bottom layers left sparse infill inside the
3 mm panels and produced bridge-role paths over that infill. Their roughly
184 mm full lengths were not free-air spans. With 8 top/bottom layers the
panels are solid throughout and those roles disappear. The final review uses
that setting, 0.2 mm layers, a 0.4 mm nozzle and 5 perimeters.

## Reproduce

Run from the repository root. These files are diagnostic; do not send their
G-code directly to a printer. Temporary G-code and logs are intentionally ignored.

```sh
review_dir=model/sunglasses_case/notes/support_free_review
mkdir -p "$review_dir/run03"
prusa-slicer --load "$review_dir/review.ini" --export-gcode \
  --output "$review_dir/run03/case.gcode" model/sunglasses_case/sunglasses_case.stl
prusa-slicer --load "$review_dir/review.ini" --export-gcode \
  --output "$review_dir/run03/hinge.gcode" model/sunglasses_case/hinge_test.stl
python3 .codex/skills/prusa-slicer-printability/scripts/inspect_gcode.py \
  "$review_dir/run03/case.gcode" --json "$review_dir/case_paths.json" \
  --svg "$review_dir/hinge_layers.svg" --layers 33.6 37.0 40.6 \
  --window 82 117 108 140
python3 .codex/skills/prusa-slicer-printability/scripts/inspect_gcode.py \
  "$review_dir/run03/hinge.gcode" --json "$review_dir/hinge_paths.json"
convert -background white "$review_dir/hinge_layers.svg" "$review_dir/hinge_layers.png"
```

The individual mechanism samples used the same profile and orientation:

```sh
for name in mechanism_test_current mechanism_test_tight_hinge \
  mechanism_test_tight_latch mechanism_test_very_tight_hinge \
  mechanism_test_very_tight_latch; do
  prusa-slicer --load "$review_dir/review.ini" --export-gcode \
    --output "$review_dir/run05/$name.gcode" \
    "model/sunglasses_case/$name.stl"
  python3 .codex/skills/prusa-slicer-printability/scripts/inspect_gcode.py \
    "$review_dir/run05/$name.gcode" \
    --json "$review_dir/${name}_paths.json"
done
```

The user successfully printed the previous, looser hinge. The final 0.6 mm
radial cone clearance and 0.5 mm ear gap are slightly tighter; print success
for these revised tolerances and the complete case is not yet established.

## Individual mechanism samples

The five comparison samples are separate 32 × 104–105 × 47 mm short box slices
in the same open print orientation. PrusaSlicer 2.9.6 sliced all four with
supports disabled and no stability warning, bridge infill, overhang perimeter
or support roles. Each diagnostic slice used about 32.46–32.62 g and 3 h 19 min
with the generic profile.

This is printability evidence only. The user should compare physical hinge play,
latch engagement, release force and light-shake retention before choosing a
production clearance. The samples do not test full-case stiffness or fatigue.
