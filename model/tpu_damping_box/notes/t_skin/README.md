# T08/T16 complete M1-marked liner pairs

The user selects **T08 and T16**, then selects **M1 compact full-name markings**
and requests the actual boxes for printing in the existing experiment shell.
This supersedes the earlier SVG-only marking phase and T12/T16 research shortlist.
**Latest physical report:** both pairs have now been printed. **T08 became the
golden standard at that stage**: the user finds its damping effectively equivalent to earlier
approved models and its appearance substantially better than B/S. **T16 is
rejected**: it feels too firm and produces somewhat more sound. Do not recommend
T16 as a damping improvement merely because its extra perimeter paths look clean.
B/S remain historical approved references. The subsequent [thinner-gap print report](../thin_gap/README.md#physical-feedback--2026-10-21) selects L20 as the current preferred baseline; T08 remains an approved control.
See [reported feedback](#physical-feedback--2026-10-21).

| Pair | Primary STEP / matching STL / source | Upright construction | Contents width | Pad width |
| --- | --- | --- | --- | --- |
| T08 M1 | [STEP](../../t_skin_T08_m1.step) · [STL](../../t_skin_T08_m1.stl) · [Python](../../t_skin_T08_m1.py) | 0.8 / 0.6 air / 0.8 mm = **2.2 mm total wall** | 29.6 mm | 32.0 mm |
| T16 M1 | [STEP](../../t_skin_T16_m1.step) · [STL](../../t_skin_T16_m1.stl) · [Python](../../t_skin_T16_m1.py) | 1.6 / 0.6 air / 1.6 mm = **3.8 mm total wall** | 26.4 mm | 30.4 mm |

Each file contains **one complete upright cup and its matching flat lid pad**,
with both undersides on the bed. Each file is a separate plate; arrange the
parts if importing both files together, since their supplied positions coincide.
The following files record the delivered comparison; T08 is preferred and T16
is now a rejected reference. These are
full-height parts, not the earlier wall probes. Use matching pads only.
**T16 here means 1.6 mm per upright skin**, not B16's tie size or S16's total
lining thickness. All geometry is in mm; import at 100% scale.

## Physical feedback — 2026-10-21

The user identifies the printed T08 and T16 pairs from this batch. Association:
delivered M1 batch at commit `2f56b7c`; exact printed hashes and runtime settings
are unknown. The user reports T16 feels too firm and produces a bit more sound;
T08 is good, effectively like earlier approved damping models, with much better
visual hiding of the structure than B/S, and explicitly calls T08 the new golden
standard. This is subjective physical feedback, not a calibrated sound or material
measurement. M1 readability, exact defects, individual corner integrity and
installation/durability details are not explicitly reported.

The user authorizes one or two thinner T08-derived full pairs for a quick print
comparison. [Thinner-gap follow-up](../thin_gap/README.md) preserves T08's 0.8 mm
skins while investigating the available core gap. T08 remains the control and
approved baseline; no thinner geometry is approved by this print report.

## Preserved interfaces and intentional changes

The shared [parametric builder](../../t_skin_design.py) retains the **34 × 34 ×
34 mm outer cup**, constant square insertion path, shell's nominal 0.2 mm lateral
clearance, and pad pocket with 0.2 mm lateral allowance per side. The rigid shell
is unchanged; do not reprint it. The pad is 1.8 mm thick as printed, including
the established 0.2 mm intended squeeze. Squeeze/insertion forces are uncalibrated.
The cup's pad-pocket step remains 1.6 mm below the rim. Flat object-contact
surfaces and both continuous skins remain on all six faces.

The **floor and lid panel retain B's horizontal construction**: 0.4 mm contact
skin / 0.8 mm post-supported air core / 0.4 mm backing; the pad's shell-side
backing additionally carries the 0.2 mm squeeze layer. These dimensions are the
same for T08/T16. The side skins and available panel area differ, so this does
not make damping a pure single-factor physical experiment.

Upright ties are **0.8 × 0.8 mm at 4.4 mm pitch**, crossing the 0.6 mm gap. Rows
remain centered at 3.2 + 4.4n mm (seven heights). Wall channels end 4 mm before
each outer tangent end, leaving solid corner regions. Five complete ties per
row remain in the air-channel region; no clipped sliver tie is left against a
solid end land. Floor/pad posts retain the established seven-by-seven center grid;
posts overlapping the local corner/label backing simply merge into it.
The four floor/pad corners retain solid 4 × 4 mm corner zones, clipped naturally
by the respective wall/rim geometry. Straight wall regions retain the air gap;
solid bends/end lands are deliberate, not claimed to have the same compliance.

## M1 marking without a large central label panel

Both parts carry the matching **T08** or **T16**, recessed **0.2 mm / one layer**
on the shell-facing underside, near the same corner. There is no separate R2
line and no raised text altering shell fit.

The selected [M1 concept](../marking_options.md) reserves **9 × 5.5 mm**, set 1 mm
in from the outer edges. The supporting corner seat extends **10 × 6.5 mm** to
connect the entire reserved region to the outer corner. It is solid through the
1.6 mm cup floor / 1.8 mm pad thickness, leaving 1.4 / 1.6 mm above the actual
recess. No letter cuts into a thin skin over the air core. The central floor
retains its original skins/posts and has no lettering or extra solid label panel.

The final monoline letters use **0.8 mm strokes**, 3.2 mm stroke-center height and
**0.6 mm material spacing between the broad T/0/8 outlines**. The final glyph
envelope is approximately 8.4 × 4.0 mm. This widens the original illustrative
7.4 mm envelope within the **same reserved 9 mm zone**, so ordinary first-layer
paths can preserve material between characters. Actual `1`/`6` shapes have their
own widths. Counters and gaps must be assessed in the retained slice, not inferred
from font size. The local solid seat is still a deliberate stiffness change;
its footprint/construction are the same for both variants and matching pads.

## Printing and checking the comparison

Use the supplied ordinary [Classic TPU process](../../profiles/tpu-support-classic-process.json),
[TPU 95A filament profile](../../profiles/tpu95a.json) and
[Qidi Q2C 0.4 mm printer](../../../../.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json).
The intended setup is **0.4 mm nozzle, 0.2 mm first and normal layers, Classic,
two requested wall loops, ordinary 0.42/0.45 mm widths, thin-wall detection off,
100% fill inside CAD material, thin bridges and no ironing**. The air spaces are
modeled voids; 100% fill does not fill them. Use the supplied flat placement and
keep labels bed-facing. No Arachne, scaling or thin-wall recovery is required.
The supplied pair centers are (60, 60) and (102, 60) mm. This moves the old
layout clear of the printer profile's front-left exclusion zone; the initial
preserved-layout slice rejected placement, while final placements are accepted.
The user-requested 9 mm³/s filament cap remains a preset limit, not a measured
TPU calibration. No printer job has been sent.

Print the M1 pairs instead of the old diagnostic wall plates. Read the small
underside ID in raking light and match cup/pad before installing them. Compare
object-facing finish, stringing, corner integrity, insertion damage and quietness
against the retained B/S parts using the same nut/shell and handling. The larger
T08 cavity allows more travel, so phone sound levels alone do not isolate material
damping. Reject a torn skin or detached tie; CAD/slicer evidence cannot predict
its physical survival or quietness.

## Evidence and limits

Native final receipts: [T08](T08_final.json), [T16](T16_final.json).
Actual path analysis: [JSON](paths.json), [wall paths](../../renders/print/t_skin_wall_paths.svg),
[M1 letter/counter/backing paths](../../renders/print/t_skin_m1_label_paths.svg).
Full G-code: [T08](T08_paths.gcode.gz), [T16](T16_paths.gcode.gz).
Product verification: [T08](T08_verification.json), [T16](T16_verification.json).
These files record the delivered artifact/settings identities and scoped outcomes;
T08 damping/appearance and T16 rejection now have subjective user evidence above.
Exact fit forces, label readability, calibrated sound/finish measures and durability
remain unmeasured.
The STL review does not verify Orca's separate GUI STEP import.
[Full-cup view](../../renders/print/t_skin_T16_m1_isometric.png) ·
[Underside IDs](../../renders/print/t_skin_T08_m1_bottom.png).

Both native exports are CAD-valid and both primary Classic slices complete with
no log notices. Their **automatic-support probe requests review**: it generates
only interface paths inside the floor/pad air cores at Z 1.0/1.2 mm. The
[headless support-location view](../../renders/print/t_skin_support_review.svg)
shows those locations. No interface is proposed on upright ties or M1 labels.
Retain supports **off**, as in the printed B horizontal post/roof construction;
internal support would be enclosed in the test core. Actual supports-off roof
paths cover the inspected central sections and bridge metadata stay at 0.2 mm
(with 0.000001 mm serialization roundoff). These are reviewed enclosed bridges,
not a claim that the probe reported no support or that printed sag is excluded.

The actual-path check covers both skins at six between-tie positions on all
four sides through **152 upright layers**, plus the outside boundary contour
through all **170 cup layers**, and solid end-land/tie/core witnesses. The
supplied 0.15 mm first-layer elephant-foot compensation is accounted for, rather
than interpreted as a missing wall. Tie checks require the full 0.6 mm core
crossing; they do not require every point of the surrounding skin's nominal
line-width envelope to be solid. Small local envelope gaps at turning joints
are retained in the JSON and do not establish a physical crack. The skin/gap
checks are geometric path evidence, not measured polymer density.

M1 first-layer paths retain the negative letter strokes, counters and inter-glyph
material, followed by backing paths at Z 0.4 mm. Exterior label-reading direction
and both full-pair CAD views were inspected. Full CAD checks also cover actual
shell/pad insertion clearances, continuous skins, floor/pad corner material,
discrete ties and solid backing under the entire reserved label seat.

Rebuild using `./evaluate_model.py model/tpu_damping_box/t_skin_T08_m1.py --export`
(or T16), and run the same complete supplied profile triplet above with `--slice`,
`--slice-placement preserve` and `--slice-keep-run` for native path reproduction.
Run `./execute.py model/tpu_damping_box/review_t_skin.py` after both final slice
receipts exist. The reader archives actual G-code, checks local core/skin/label
paths and produces the views. Retained raw directories are required to rerender;
the archived G-code remains inspectable after those directories are cleaned.
For example, reproduce the T08 native receipt with:

```sh
./evaluate_model.py model/tpu_damping_box/t_skin_T08_m1.py --slice \
  --slice-printer .codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json \
  --slice-process model/tpu_damping_box/profiles/tpu-support-classic-process.json \
  --slice-filament model/tpu_damping_box/profiles/tpu95a.json \
  --slice-placement preserve --slice-keep-run \
  --report model/tpu_damping_box/notes/t_skin/T08_final.json --summary
```

Substitute `T16` in the entry point and receipt name for the second pair.
Run product checks with `./execute.py model/tpu_damping_box/verification.py --variant T08`
(or T16); read the JSON outcomes, including physical UNKNOWN, rather than exit
status alone. `t_skin_checks.py` reuses established shell-overlap witnesses.

Final FDM rationale: broad flat bed contact; upright cup and flat separate pad;
ordinary-width skins and short 0.6 mm tie spans; solid corner transitions and
locally backed bed-side labels. The horizontal skins bridge between established
posts, while the pad remains separately printable without trapped support inside
the cup. Layer bonding, skin sag, first-layer relief and small-character visibility
remain physical properties, even where toolpaths are present.

| Item | Print status | Artifacts | User result / remaining physical checks |
| --- | --- | --- | --- |
| T08 M1 cup/pad | Yes — approved, earlier golden standard; now retained control | Paired Python / STEP / STL and retained native slice | User reports damping like prior approved models and much better appearance; exact print settings, label readability and long-term integrity remain unreported. |
| T16 M1 cup/pad | Yes — rejected for damping | Paired Python / STEP / STL and retained native slice | User reports too firm and somewhat noisier; retain files as rejected evidence, not a recommended reprint. |
| Final application liner | N/A | None new | These are existing-shell experiments, not qualified dental/sunglasses adaptations. |

Attribution, 2026-10-21: GPT-6 family; exact runtime identifier/reasoning effort not
exposed. Codex shared-workspace CLI/API agent, OpenAI; no subagents. User selects
T08/T16, M1 and full-box implementation; agent authors geometry, local checks and
path review. Existing B/S sources and supplied profile licensing remain attributed
to their original phases. Orca supplies the native slices, not physical approval.
