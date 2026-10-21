# B-derived skins and curved joints — actual Classic path investigation

[Object status](../../README.md) · [Compact findings SVG](../../renders/concepts/tie_recommendation_paths.svg) ·
[Nominal stroke overlap](../../renders/concepts/b08_nominal_skin_overlap.svg) ·
[Approved B08 close-up](../../renders/concepts/approved_B08_joint_paths.svg) ·
[Initial skin/profile comparison](../../renders/concepts/tie_skin_paths.svg) ·
[Curved ties versus straight ties](../../renders/concepts/tie_curve_paths.svg) ·
[Refined skins and joints](../../renders/concepts/tie_refined_paths.svg) ·
[N2 before/after root blend](../../renders/concepts/n2_blended_paths.svg)

**Decision:** keep B's discrete ties and change the skin geometry first. **T12**
is the leading compact candidate; **T16** is the stronger normal-perimeter
comparison. Do not promote the rounded/swept roots or the smoother N2 blend as
print-quality improvements: their actual paths add local features and interrupt
tracks behind the visible face. These are choices for the next design discussion,
not new physical approvals or a full-box print batch. [Gyroid remains a separate
candidate](../infill_study/README.md), as the user explicitly requests.

The latest user feedback favors ties over ribs, asks about self-designed curves
and smoother N2 joints, and asks for autonomous inspection of approved B plus
thicker skins/wall counts. The user does not identify a new print or retract
B08/B16 approval. Their earlier tentative B08 print-quality preference remains
scoped to that [physical report](../b_surface_concepts.md).

## What the approved B08 paths actually show

The close-up uses the **retained approved-geometry B08 slice**, not a recreated
box or the new proxy. Its reference setup is ordinary Classic, 0.42 mm outer
width, 0.45 mm inner width, two requested wall loops and thin-wall recovery off.
Exact past user runtime settings are still not independently established.
The original source, mesh and G-code identities are checked against retained
receipts; [full reference G-code](approved_B08_paths.gcode.gz) is archived here.

The visible face already has a straight contour. Behind it, the path around each
CAD air cell turns through the tie junctions at Z 3.0 mm; between rows at Z 4.4 mm,
it runs straight alongside the face. There is a specific thin-skin issue:
**between ties, two nominal 0.42 mm outer-wall passes sit at normal coordinates
0.21 and 0.29 mm inside one 0.5 mm skin**. Their centerlines are only **0.08 mm
apart**. The data are slicer widths and positions, not measured polymer widths.
This is severe nominal stroke overlap compared with the better-spaced controls.

Thus a plausible source of marks is changing nearby deposition/overlap as the
cell contours turn into the joints. That is a stronger geometric hypothesis than
“the outer contour is broken”, which the slice contradicts. It is still **not a
confirmed cause** of the user's surface patterns, bumps or strings. Moisture,
extrusion response, cooling and actual seam behavior are not measured here.
B's physical approval remains valid despite this diagnosis of a possible route
for improvement.

## Controlled geometry and process comparisons

All probes are upright **44 mm-long, 34 mm-high straight walls**, with 4 mm solid
end lands and a 1.6 mm solid foot. The ends represent restrained/solid corner
regions; they are not actual full-cup corners. B's 0.8 mm tie width/height and
4.4 mm pitch are retained for discrete cases, with centers at the established
heights. The wall gap stays **0.6 mm**, independently of skin thickness. Wider
skins increase total wall depth rather than consuming the damping gap.

| Phase / IDs | Geometry tested | Skin on **each** side | Overall wall depth |
| --- | --- | --- | --- |
| Initial T05 / T09 / T13 | Straight B-style ties | 0.5 / 0.9 / 1.3 mm | 1.6 / 2.4 / 3.2 mm |
| Initial R09 / R13 | Rounded, tangent shoulder edges; 1.6 mm root width, 0.8 mm waist | 0.9 / 1.3 mm | 2.4 / 3.2 mm |
| Initial C13 | Constant-normal-width swept S-like tie; roots tangent in plan | 1.3 mm | 3.2 mm |
| Initial W13 | Full-height sinusoidal N2 web; 0.8 mm normal width, **2.4 mm core** | 1.3 mm | 5.0 mm |
| Refined T08 / T12 / T16 | Better-spaced straight-tie skins | 0.8 / 1.2 / 1.6 mm | 2.2 / 3.0 / 3.8 mm |
| Refined R16 / K16 | Rounded / swept ties retried with substantial skins | 1.6 mm | 3.8 mm |
| Native N2 WN13 / WF13 | Same smooth spline web, before / after **R0.25 cavity-root fillets** | 1.3 mm | 5.0 mm |

The T/R/K IDs are local study names. **T16 means 1.6 mm per skin**, not the old
S16/B16 1.6 mm overall sandwich or B16's larger tie size. C13/K16 are swept-tie
studies, not a return to the rejected solid C controls. W13 is a different core
depth and continuous support strategy, so its damping is not a controlled
single-factor comparison to B.

Three initial processes separate slicer settings from actual material width:

| Process | Requested wall loops | Wall order | Other controls |
| --- | --- | --- | --- |
| [P2](P2_process.json) | 2 | Inner/Outer | Existing ordinary-Classic B widths, 0.2 mm layers, 100% fill in CAD material, supports off |
| [P3](P3_process.json) | 3 | Inner/Outer | Same as P2 except requested loop count |
| [P3IOI](P3IOI_process.json) | 3 | Inner/Outer/Inner | Same as P3 except wall order |

Refined probes use P2 and P3IOI; the paired native N2 comparison uses P2.
There are **six successful current retained study slices** covering fourteen probe cases,
plus the unchanged retained B08 reference. All use supplied Qidi Q2C 0.4 mm /
Generic TPU 95A settings, explicit preserved placements and ordinary Classic.
All six complete with no reported notices and no proposed automatic supports.
This does not establish physical bridging, tall-wall integrity or damping.

## Findings that determine the recommendation

**A larger wall-loop setting alone is insufficient.** In the initial geometry,
P2/P3/P3IOI give the same counted long straight skin tracks at the inspected tie
and between-tie layers. The setting cannot fit additional ordinary paths into
missing material. This statement concerns the inspected local tracks, not a
claim that the whole plate's path order or G-code is identical.

**Not every extra line is another normal perimeter.** At Z 3.0 mm, T09's added
long track is **0.130842 mm Gap infill**; T13's is **0.530842 mm Gap infill**.
Those are very different from a normal 0.42/0.45 mm wall pass. This prompted
T08/T12/T16 rather than selecting a skin thickness by counting centerlines.

| Straight-tie skin | Long tracks behind the face at the tie layer, Z 3.0 mm | Interpretation |
| --- | --- | --- |
| 0.5 mm, T05 | One 0.42 mm outer-wall pass | Other boundary routes into ties; heavy nominal overlap between rows. |
| 0.8 mm, T08 | One 0.42 mm outer-wall pass | Between rows its two passes are at 0.21/0.59 mm, much better spaced than 0.5 mm; still no extra long guard track at ties. |
| 1.2 mm, T12 | 0.42 mm outer wall + **0.430842 mm gap fill** | Compact option with a near-normal-width continuous track behind the face. Total wall 3.0 mm. |
| 1.6 mm, T16 | 0.42 mm outer wall + **two 0.45 mm inner walls** | Cleanest normal-perimeter arrangement inspected; no gap-fill role at that tie layer. Total wall 3.8 mm. |

Here “long track” means a **single deposited horizontal G1 move spanning the
central 20 mm**, within the contact-side skin. It is not a string/retraction
count, an acoustic score or a strength threshold. Between-row contours supply
additional lines that turn away again at the ties. The report retains widths,
roles and positions so overlapping or tiny gap-fill lines are not mislabeled as
independent robust walls. [Machine-readable evidence](paths.json).

**Rounded/swept roots trade smooth outlines for extra local work.** R13/C13 lose
the long middle skin track at the first tie layer and create short inner loops
and fill features near roots. R16/K16 recover one normal inner guard behind the
outer face, but T16 retains two and has simpler local routes. The curved starts
also receive `Overhang wall` segments at the first tie layer; no auto support is
proposed. This is why a deep curving bridge was not adopted: keep the discrete
gap short rather than introduce a long unsupported curved span.

**Making N2's actual union smoother also adds paths.** A tangent web centerline
does not ensure a tangent material boundary when the thick web merges into a
skin. WN13/WF13 use the same native spline web; only WF13 adds R0.25 blends at
the actual cavity corners. The slice confirms smoother core-side corners but
also local inner loops/short fill and loss of the long middle gap-fill track.
It is not a print-quality upgrade on current evidence. Keep this as an examined
alternative, not the preferred next liner merely because the CAD looks smoother.

A preliminary fillet of the polygonal approximation failed in the CAD kernel;
[historical native error](n2_polygon_blend_failed.json) is retained. Native spline
boundaries resolved that representation issue. Their vertical intersection edges
can be spline-typed, so the root selector uses actual endpoint direction, length
and core-plane position rather than assuming every straight edge is typed LINE.
The completed native CAD and slice above replace that failed implementation;
no failed build is presented as a finished model.

## Probe correction and connection checks

An early straight-tie probe used `translate` on a pending CadQuery wire before
extrusion. The translation did not move the extruded profile, leaving those ties
short of the second skin despite the end lands keeping the wall CAD-valid.
The approved B models were unaffected. The probe now places the sketch before
extrusion; **both affected plates were rebuilt and all five affected slices
replaced**. Every finding and path view above uses the corrected exports.

[Seven regression cases](../../../../tests/test_tpu_tie_profile.py) pass, including
a negative control reproducing the rejected construction. Final Boolean bodies
also check tie-to-skin material witnesses and intended air spaces. The path reader
checks deposited coverage across the entire 0.6 mm core at the first straight-tie
row; every current straight case reports zero uncovered width. These checks
establish connection in these probes, not printed strength or surface quality.
The only builder edit after native export was removal of trailing blank lines;
that reviewed whitespace cleanup changes no geometry or placement.

## Practical choice and whole-liner limits

**Carry T12 and T16 forward as compact/normal-perimeter alternatives to B**, with
straight ties first. T12 preserves the extra straight track at less thickness;
T16 is the clearest check of whether normal perimeter separation improves the
face. R16 is a lower-priority curved-root comparison if that mechanism is still
wanted; it does not beat T16's path simplicity. Do not pick R13, C13 or WF13 as
the next print-quality improvement. Keep Gyroid G20 as the separate infill route.
These are engineering recommendations, not new user-selected full-box variants.

Thicker skins add material, reduce contents space and may make damping worse.
The tiny gap is deliberately unchanged in this study; the wall proxies do not
establish its useful stroke with the thicker faces. The earlier rejection of
solid C makes a physical B/S damping comparison essential. No claim that T16
will feel better than B is justified. A full-box iteration would need integrated
solid corner lands, gradual transitions, floor and pad construction, fit,
identification and representative tall-wall review. No new lid/box pair or
replacement application liner is delivered here.

## Delivered source, paths and reproduction

The geometry helper is [tie_surface_design.py](../../tie_surface_design.py);
N2's native curves are in [n2_surface_design.py](../../n2_surface_design.py).
STEP archives are lossless gzip copies of each native paired export; these rough
CAD studies have large repeated curved boundaries. Native receipts name the
original `.step`; extracting the archive restores that same file. STL files are
retained unchanged as the actual slice inputs. These are diagnostic studies,
not a recommended printable batch.

| Study plate | Entry point / slice input / native CAD archive | Native evidence |
| --- | --- | --- |
| Initial seven | [Python](../../tie_surface_study.py) · [STL](../../tie_surface_study.stl) · [STEP.gz](../../tie_surface_study.step.gz) | [Geometry](geometry.json) · [P2](P2_review.json) · [P3](P3_review.json) · [P3IOI](P3IOI_review.json) |
| Refined five | [Python](../../tie_surface_refined.py) · [STL](../../tie_surface_refined.stl) · [STEP.gz](../../tie_surface_refined.step.gz) | [Geometry](refined_geometry.json) · [P2](refined_P2_review.json) · [P3IOI](refined_P3IOI_review.json) |
| Native N2 pair | [Python](../../tie_surface_n2_blend.py) · [STL](../../tie_surface_n2_blend.stl) · [STEP.gz](../../tie_surface_n2_blend.step.gz) | [Geometry](n2_blend_geometry.json) · [P2](n2_blend_review.json) |

Full G-code: [initial P2](P2_paths.gcode.gz), [initial P3](P3_paths.gcode.gz),
[initial P3IOI](P3IOI_paths.gcode.gz), [refined P2](R_P2_paths.gcode.gz),
[refined P3IOI](R_P3IOI_paths.gcode.gz), [N2 pair](WF13_paths.gcode.gz).
Views show actual deposited centerlines; travel/retraction moves remain in these
archives. Tint marks nominal skins; path colors are slicer roles, **all TPU black**.
The new study processes retain the [upstream profile attribution](../../profiles/ATTRIBUTION.md).

Build each named entry point with the root `./evaluate_model.py ... --export`.
For the initial plate, reproduce each process using this P2 example:

```sh
./evaluate_model.py model/tpu_damping_box/tie_surface_study.py --export \
  --report model/tpu_damping_box/notes/tie_surface_study/geometry.json --summary
./evaluate_model.py --slice-existing model/tpu_damping_box/tie_surface_study.stl \
  --slice-printer .codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json \
  --slice-process model/tpu_damping_box/notes/tie_surface_study/P2_process.json \
  --slice-filament model/tpu_damping_box/profiles/tpu95a.json \
  --slice-placement preserve --slice-keep-run \
  --report model/tpu_damping_box/notes/tie_surface_study/P2_review.json --summary
./execute.py model/tpu_damping_box/review_tie_surface_study.py
```

Substitute the other plate/process/report combinations listed above before
running the reader. The reader verifies STL/raw-process identities and effective
settings, reuses the shared deposition parser, archives G-code and generates the
views. Retained raw directories are needed for rerendering; after cleanup,
regenerate the listed slices. The archived G-code remains directly inspectable.
Orca's [wall-order documentation](https://github.com/OrcaSlicer/OrcaSlicer/wiki/quality_settings_wall_and_surfaces/644ec80f411f679697a02a98b6efae836beb2ad8)
helps interpret loop/order settings; these decisions rely on the actual paths,
not an assumed outcome from a setting name.

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Diagnostic wall probes | Unknown | Sources, slice-input STLs, lossless STEP archives, six slices and actual path SVGs | No physical print reported or recommended as a batch; finish/strength/damping unmeasured. |
| Final printable liner | N/A | None new | Full corner/floor/pad design and physical comparison remain outside this study. |

Attribution, 2026-10-21: GPT-6 family; exact runtime identifier/reasoning effort
not exposed. Codex shared-workspace CLI/API agent, OpenAI; no subagents. User
supplies tie preference, thick-skin/curve questions and autonomous investigation
scope. Agent authors probes, profiles, analysis and views; Orca 2.4.2 supplies
native slices. Earlier physical approvals and attribution remain scoped intact.
