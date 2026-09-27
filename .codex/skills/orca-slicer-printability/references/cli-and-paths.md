# OrcaSlicer CLI and path interpretation

This notebook records verified methods and their limits. Findings describe
toolpaths, not guaranteed physical outcomes.

## Install and discover the Flatpak CLI

OrcaSlicer is installed here as the user Flatpak
`com.orcaslicer.OrcaSlicer`. The installed package during setup was 2.4.2.
Install and inspect it with:

```sh
flatpak install --user flathub com.orcaslicer.OrcaSlicer
flatpak info com.orcaslicer.OrcaSlicer
flatpak run com.orcaslicer.OrcaSlicer --help
```

The Flatpak CLI works headlessly; its app data filesystem grants access to the
user home, including this repository. Invoke `flatpak run` directly when no
host `orca-slicer` executable exists. See [Flathub](https://flathub.org/en/apps/com.orcaslicer.OrcaSlicer)
and the official [CLI mode documentation](https://www.orcaslicer.com/wiki/cli/cli_mode).

The CLI accepts model inputs followed by options. `--load-settings` takes
semicolon-separated process/printer JSON paths; `--load-filaments` takes
semicolon-separated filament paths. `--slice 0` slices all plates. Use
`--export-settings` to preserve effective settings and inspect them rather than
trusting preset names alone. A direct reference command is:

```sh
PRINTER=.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json
PROCESS=.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.20-standard-adaptive-cubic-7.json
FILAMENT=.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/generic-petg-qidi-q2c-0.4.json
RUN=model/object_name/notes/orca_review_01

flatpak run com.orcaslicer.OrcaSlicer model/object_name/object_name.stl \
  --load-settings "$PROCESS;$PRINTER" \
  --load-filaments "$FILAMENT" \
  --arrange 1 --orient 0 --allow-rotations=0 --slice 0 \
  --outputdir "$RUN" --export-settings "$RUN/effective-settings.json"
```

`--arrange 1` centers/places the loaded layout; `--orient 0` and
`--allow-rotations=0` retain the intended orientation. For a single STL, Orca
places its one mesh as a whole. For a multi-object project use the documented
helper placement modes and inspect the resulting layout before making any
claim about retained object-to-object positions. CLI flag behavior is documented
in [CLI transforms](https://www.orcaslicer.com/wiki/cli/cli_transform).

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
sparse infill to `7%` and `adaptivecubic`. The effective-settings export must
show Qidi Q2C, nozzle 0.4, PETG, process name, density and pattern as expected.
If Orca changes profile schemas or a base preset, rebuild and re-check these
snapshots instead of assuming inherited values loaded.

The official [infill settings](https://www.orcaslicer.com/wiki/print_settings/strength/strength_settings_infill)
identify `sparse_infill_density` and `sparse_infill_pattern`; valid sparse
patterns include `adaptivecubic`. The selected bundled Generic PETG preset
uses 250°C nozzle / 245°C first-layer nozzle and 80°C hot plate settings. These
are values from the generic diagnostic profile, not spool-specific calibration.

## Confirm a completed slice

Do not equate exit code zero with a completed slice. For each fresh output,
check all of the following:

- the CLI process returned zero;
- `result.json` reports `return_code: 0` and one or more `sliced_plates`;
- every expected plate has fresh nonempty G-code;
- effective settings match the requested printer, nozzle, material and process;
- deposited paths can be parsed from the G-code.

During setup on 2026-09-27, `vaseline_container.stl` sliced in 2.4.2 with the
Qidi Q2C 0.4 / Generic PETG / 0.20 mm / 7% adaptive cubic profiles. The result
reported success with no warning, 114 layers, PETG, 250°C nozzle, 80°C hot
plate, and sparse-infill paths. The 260 × 260 × 250 mm reference envelope
contained the placed paths and 5 mm brim. Evidence is retained in
[`model/vaseline_container/notes/orcaslicer_setup`](../../../../model/vaseline_container/notes/orcaslicer_setup/README.md).

## Read linear path output

Verified Orca G-code includes `;LAYER_CHANGE`, `;Z:`, `;WIDTH:`, `;TYPE:` and
relative-extrusion mode `M83`. It may use relative XYZ (`G91`) in printer start
code before the first printable layer, then return to `G90`. The shared parser
tracks `G90`/`G91`, `M82`/`M83`, and `G92`; it ignores pre-layer machine paths,
travel and retractions. It accepts linear planar deposition in millimetres and
rejects arcs (`G2`/`G3`) or nonplanar deposition instead of silently applying a
linear move analysis to them. The parser also accepts historical PrusaSlicer
`;Z:` / `;TYPE:` records so older repository evidence scripts keep working.

For each positive-E XY move, the parser records its current layer, role,
endpoints, line width, length and extrusion delta. It counts role totals and
longest bridge-role centerlines. Orca commonly names roles `Sparse infill`,
`Internal Bridge`, `Support`, `Support interface` and `Brim`; confirm the roles
present in each output. Bridge-role lengths include anchors and are not
automatically free-air spans. Compare with preceding layers before deciding
what is unsupported.

Bounds include half of each reported width and therefore include deposited
brims/supports. They are based on linear deposition only and exclude travel,
start/end machine motions and flow spread. If width comments are missing, the
parser's 0.45 mm fallback is uncalibrated. Bounds assume a rectangular bed with
origin (0,0). They do not prove original absolute placement, dimensional
accuracy, clean topology, physical bridge behavior or clearance.

No automatic free-air span, anchor, sag, stress, support-removal accessibility
or pass/fail printability classifier is supplied. No universal safe bridge
length or clearance has been established. A generic diagnostic G-code file is
not a validated printer job.
