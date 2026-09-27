# OrcaSlicer CLI and path interpretation

This notebook records verified methods and their limits. Findings describe
toolpaths, not guaranteed physical outcomes.

## Install and discover OrcaSlicer

OrcaSlicer is installed here as the user Flatpak
`com.orcaslicer.OrcaSlicer`. The installed package during setup was 2.4.2.
Install and inspect it with:

```sh
flatpak install --user flathub com.orcaslicer.OrcaSlicer
flatpak info com.orcaslicer.OrcaSlicer
flatpak run com.orcaslicer.OrcaSlicer --help
```

The review helper infers the launch command in this order:
`ORCASLICER_COMMAND`, host `orca-slicer`, then Flatpak. The CLI works headlessly;
its app data filesystem grants access to the user home, including this
repository. See [Flathub](https://flathub.org/en/apps/com.orcaslicer.OrcaSlicer)
and the official [CLI mode documentation](https://www.orcaslicer.com/wiki/cli/cli_mode).

For the review command and its argument defaults, use the
[OrcaSlicer skill](../SKILL.md#run-the-review). It passes `--load-settings` with
process/printer profiles and `--load-filaments` with the filament profile,
slices all plates and handles effective settings and path parsing internally.

## Resolve profile inheritance before CLI use

Verified with Flatpak OrcaSlicer 2.4.2 on 2026-09-27: directly loading the
bundled child preset files selected the expected printer/process/filament names,
but did **not** resolve all inherited settings in the headless run. The exported
settings showed `Generic PETG @Qidi Q2C 0.4 nozzle` while `filament_type` and
temperatures remained at PLA defaults (PLA / 200°C / 45°C bed). A successful
slice alone would have hidden this mismatch.

The repository's Q2C profiles are resolved snapshots: each includes values
from its parent profile chain in the OrcaSlicer 2.4.2 Flathub bundle. The
process snapshot overrides only the inherited 0.20 mm Q2C Standard process's
sparse infill to `7%` and `adaptivecubic`. The effective-settings summary must
show Qidi Q2C, nozzle 0.4, PETG, process name, density and pattern as expected.
If Orca changes profile schemas or a base preset, rebuild and re-check these
snapshots instead of assuming inherited values loaded.

The official [infill settings](https://www.orcaslicer.com/wiki/print_settings/strength/strength_settings_infill)
identify `sparse_infill_density` and `sparse_infill_pattern`; valid sparse
patterns include `adaptivecubic`. The bundled Generic PETG preset uses 250°C
nozzle / 245°C first-layer nozzle and 80°C hot plate settings. These are values
from a generic diagnostic profile, not spool-specific calibration.

## Confirm a completed slice

The helper requires a successful CLI exit, `result.json` with a completed plate,
fresh nonempty G-code for each reported plate, exported effective settings, and
parsed deposition. It checks these internally. Review the single JSON report
for effective settings, support paths, bounds and notices; use `--keep-run` if
failure diagnosis needs raw files.

During setup on 2026-09-27, `vaseline_container.stl` sliced in 2.4.2 with the
Qidi Q2C 0.4 / Generic PETG / 0.20 mm / 7% adaptive cubic profiles. The result
reported success with no warning, 114 layers, PETG, 250°C nozzle, 80°C hot
plate, and sparse-infill paths. The profile-derived 270 × 270 × 256 mm Q2C
volume contained the placed paths and 5 mm brim. See the concise record at
[`model/vaseline_container/notes/orcaslicer_setup`](../../../../model/vaseline_container/notes/orcaslicer_setup/README.md).

## Read linear path output

Verified Orca G-code includes `;LAYER_CHANGE`, `;Z:`, `;WIDTH:`, `;TYPE:` and
relative-extrusion mode `M83`. It may use relative XYZ (`G91`) in printer start
code before the first printable layer, then return to `G90`. The internal parser
tracks `G90`/`G91`, `M82`/`M83`, and `G92`; it ignores pre-layer machine paths,
travel and retractions. It accepts linear planar deposition in millimetres and
rejects arcs (`G2`/`G3`) or nonplanar deposition instead of silently applying a
linear move analysis to them. It also accepts historical PrusaSlicer `;Z:` /
`;TYPE:` records so retained model-specific scripts can read archived evidence.

For each positive-E XY move, the parser records its current layer, role,
endpoints, line width, length and extrusion delta. The report counts role totals
and longest bridge-role centerlines. Orca commonly names roles `Sparse infill`,
`Internal Bridge`, `Support`, `Support interface` and `Brim`; confirm roles in
the report. Bridge-role lengths include anchors and are not automatically
free-air spans.

Bounds include half of each reported width and therefore include deposited
brims/supports. They use the effective Orca printer profile's rectangular
`printable_area` coordinates and `printable_height`; nonrectangular printable
areas fail explicitly. The calculation covers linear deposition and excludes
travel, start/end machine motions and flow spread. If width comments are
missing, the parser's 0.45 mm fallback is uncalibrated. These bounds do not
prove original absolute placement, dimensional accuracy, clean topology,
physical bridge behavior or clearance.

The parser is an internal module, not a separate command. No automatic
free-air span, anchor, sag, stress, support-removal accessibility or pass/fail
printability classifier is supplied. No universal safe bridge length or
clearance has been established. A generic diagnostic G-code file is not a
validated printer job.
