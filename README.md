# vibe-modelling-3d

Parametric objects and engineering experiments, mainly for single-material FDM
printing. Each object owns its source, printable files, current decisions and
supporting evidence. **A model being available does not mean it has been printed
or physically validated.**

## Start here

- To choose an object or find its print files, use [models](#models). Each linked
  current record explains setup, evidence, limitations and any deferred work.
- To build/export or inspect a model, use [modelling tools](#modelling-tools) and
  the [execution guide](execution/README.md#running-scripts).
- To understand an engineering result, start at its object record, then follow
  its investigation/native report links. [Reusable lessons](.codex/skills/cadquery-3d-design/references/reusable-model-lessons.md)
  index transferable findings with limits.
- For agent task routing and repository ownership, read [AGENTS.md](AGENTS.md).
  [Documentation writing](.codex/skills/documentation-writing/SKILL.md) explains
  how current state, detailed investigations and reproducible evidence fit together.

## Models

The grouped entries below distinguish successful prints, unreported prototypes
and research. Each retains separate sample/final status, attribution and any
selected effort record. **Unknown** means no user print report; **N/A** means the
category does not apply to that phase. Neither means a failed print. Detailed
[status conventions](.codex/skills/cadquery-3d-design/references/physical-experiments.md#standard-per-object-print-status-record)
remain with the engineering workflow.

### Reported working objects and accepted baselines

#### Book reading plate

[Final PETG plate and head-up screws](model/book_reading_plate/README.md)

- Test pieces: Yes — prior L sample worked; head/socket issue revised; no new coupon
- Final object: Yes — user reports the complete plate printed with a really nice result
- Provenance: [Record](model/book_reading_plate/README.md#attribution) · Agent effort: [Selected token/timing record](model/book_reading_plate/notes/agent_effort.md)

#### MacBook charger holder

[Instructions](model/macbook_charger_holder/notes/README.md)

- Test pieces: No — optional coupon not used
- Final object: Yes — user reports good print
- Provenance: [Record](model/macbook_charger_holder/notes/provenance.md) · Agent effort: [Selected token/timing record](model/macbook_charger_holder/notes/agent_effort.md)

#### Sunglasses case

[Accepted E production design](model/sunglasses_case/notes/printing_and_design.md)

- Test pieces: Yes — D/E accepted
- Final object: Yes — user reports it works really well
- Provenance: [Record](model/sunglasses_case/notes/provenance.md) · Agent effort: [Selected token/timing record](model/sunglasses_case/notes/agent_effort.md)

#### Vaseline container

[Screw-top jar](model/vaseline_container/README.md)

- Test pieces: N/A — full pair is the trial
- Final object: Yes — user reports good print
- Provenance: [Record](model/vaseline_container/README.md#attribution) · Agent effort: [Selected token/timing record](model/vaseline_container/notes/agent_effort.md)

#### Vaseline transfer spatula

[Flat scrape-and-fill tool](model/vaseline_transfer_spatula/README.md)

- Test pieces: N/A — complete tool is the trial
- Final object: Yes — user reports the existing print works well, does its job and has the right handle size; storage bulk motivates a compact revision
- Provenance: [Record](model/vaseline_transfer_spatula/README.md#attribution) · Agent effort: [Selected token/timing record](model/vaseline_transfer_spatula/notes/agent_effort.md)

#### Filament archive swatch

[SCAD instructions](model/filament_archive_swatch/README.md)

- Test pieces: N/A — full swatch is the trial
- Final object: Yes — user reports previous print works as intended
- Provenance: [Record](model/filament_archive_swatch/README.md#attribution) · Agent effort: [Selected token/timing record](model/filament_archive_swatch/notes/agent_effort.md)

#### Swatch display / archive box

[Current designs, deliverables and decisions](model/filament_swatch_box_study/README.md).
**Archive R2 A is printed and accepted**, with J4 joining, G hood fit and full
15-card retention on hood lift. B/C/D were not printed; R1 was rejected before
printing. Archive trials use complete boxes, so separate samples are N/A.

**Display is partial:** J4/K4 were printed; J4 is preferred but cards still tilt.
K4 lacks a working key stop at one end. G hood and I3 remain selected; V1 shell
was rejected. J4 alignment and K4 joining fixes are deferred by the user.

**TPU damping is discontinued (2026-10-06).** Q1F was printed: joining works,
but contrasting coverage, upper fit and sliding noise are unsatisfactory. Unchanged
G geometry printed fully in TPU was somewhat quieter but still unacceptable;
the movable/distorted upper shell remains usable. Layer-line causation is the
user's hypothesis; printed files/settings are unknown. Q1 has no print report;
follow-up SVGs are superseded history. Complete damping trials have no separate
coupon (N/A).

[Provenance](model/filament_swatch_box_study/README.md#attribution) ·
[Named assembly investigation](model/filament_swatch_box_study/notes/development_record.md#named-assembly-engineering-2026-10-06) ·
[Selected effort record](model/filament_swatch_box_study/notes/agent_effort.md)

### Partial results and stopped development

#### Postcard displays

[Seven postcard displays: original through Orbit, Bolt and Pebble](model/postcard_display/README.md)

- Test pieces: N/A — full holder is the trial
- Final object: Partial — Wave printed and works well; six other variants unreported
- Provenance: [Record](model/postcard_display/README.md#attribution) · Agent effort: [Selected token/timing record](model/postcard_display/notes/agent_effort.md)

#### Decorative faceted tray

[Eight texture samples and retained tray exports](model/faceted_storage_tray/README.md)

- Test pieces: Unknown — eight coupons, no user report
- Final object: Partial — variant H printed; user reports it works well; other variants unreported
- Provenance: [Record](model/faceted_storage_tray/README.md#attribution) · Agent effort: [Selected token/timing record](model/faceted_storage_tray/notes/agent_effort.md)

#### Dental travel containers — short-lap slim wall-snap box

**Current grip exploration:** the user prefers recessed saddles (B).
[Band placement and native-hand investigation](model/dental_travel_case/notes/grip_human.md)
compares three locations for upright/diagonal opening, with recorded SVGs.
Cap +50 / body −30 mm from the seam is a dimensional starting proposal;
the hand search has not validated a usable grasp or comfort.
[Full-wrap band and shallow-profile SVGs](model/dental_travel_case/notes/wall_comparison.md#continuous-band-and-shallow-profile)
now compare grip coverage and smooth 0.4/0.7 mm recesses; a 0.7 × 20 mm band is
the proposed starting shape, with printed usefulness unverified.
[Three B-family SVG suggestions](model/dental_travel_case/renders/concepts/grip_b_family_comparison.svg)
compare oval dimples, longer corner saddles and directional scoops. The
[earlier comparison](model/dental_travel_case/renders/concepts/grip_comparison.svg)
is retained. CAD is unchanged; the rejected seam notches will be removed after
the visual exploration.

[Current print comparison: full 2 mm and three-line (1.2 mm) body/cap pairs](model/dental_travel_case/notes/wall_comparison.md).
Both pairs slice without supports. The thin pair uses about 41% less material
in the same profile, with local catch backing; use matching bodies and caps.
No physical comparison is reported. [Wall and toolpath drawing](model/dental_travel_case/notes/wall_comparison/comparison.svg).
Both caps now have rounded inner/outer finger-slot edges; the thin cap's raised
joint backing blends into the shell. [Comfort details](model/dental_travel_case/notes/wall_comparison/comfort.svg).
Retained force/contact studies describe the earlier cap geometry.

[Current full prototype, production joint test and overlap comparison](model/dental_travel_case/notes/short_lap.md).
**2026-10-19:** the user discards the hinged box and reopens small wall snaps.
Opening noise is potentially acceptable; priority is much shorter overlap with
strong retention and sideways stability. Current geometry and computational
screens are prototypes; printed retention/effort/packing remain unqualified.
The selected model uses **30 mm overlap**, reinforced bearing walls and small
.6 mm bumps, preserving the printed slim box's exterior size.
**2026-10-20 clarification:** knocks and bumps inside a travel bag must not open
the box. Deformable contact snapshots show that widthwise loading can consume
almost all capture at one bite while the other remains engaged. The coupled
release investigation is **INCONCLUSIVE**; impact resistance remains unverified.
The 30 mm prototype remains unprinted; do not infer a safe
side-hit force from the static stiffness or straight-pull screens.
[Visual test map](model/dental_travel_case/notes/short_lap/sideways_test_map.svg) ·
[12.6 N result in everyday terms](model/dental_travel_case/notes/short_lap/sideways_result_explained.svg).
The [workflow feedback](model/dental_travel_case/notes/short_lap.md#practical-stopping-and-explanation-feedback)
closes this numerical branch and records practical stopping and visual-explanation lessons.

[M1 full-box feedback and retained files](model/dental_travel_case/notes/m1.md) · [Separate M2B retention investigation](model/dental_travel_case/notes/m2.md)

[Historical M5 space-recovery prototype and test](model/dental_travel_case/notes/m5.md) · [M4 motion investigation](model/dental_travel_case/notes/m4.md) · [Superseded M3 investigation](model/dental_travel_case/notes/m3.md)

[Historical research: four minimal wall-flexure/slide closure specimens](model/dental_travel_case/notes/closure_research.md), including the user's free-rim idea. These long specimens were not adopted as a full case; subsequent short samples were printed and rejected as recorded below.
[Conditional R1/R2 straight-pull force and equivalent-weight investigation](model/dental_travel_case/notes/closure_pull.md); R3 bead and R4 rail-lifting forces remain unresolved.
[Earlier short wall-snap trials and their print report](model/dental_travel_case/notes/closure_short.md).

**2026-10-19:** two short samples printed (exact variants unknown); user reports
high engagement effort and noisy opening, and initially discontinues these trials;
the later direction above reopens them with revised priorities.
[Discarded C8: clear interior and a flat-opening flexible spine](model/dental_travel_case/notes/spine.md).
C7's internal pivot shelves were rejected before printing. C8 replaces them with
flush-mounted TPU spines and a continuous rear wall (.8 mm thicker), with a CAD
folding path to 180°. The complete mini box uses separate PETG and TPU plates;
**latest print feedback: the shortened loop broke immediately on its first push;
TPU strips have not been printed. Hinged direction now discarded.**
Mount pullout, hinge life and integrated operation remain untested. A small exterior
pin hinge remains historical CAD. [C7](model/dental_travel_case/notes/internal_hinge.md)
and [C6](model/dental_travel_case/notes/clamshell_exploration.md) remain historical.

- Test pieces: New production-joint prototype unprinted. Earlier two short wall snaps had high effort/noise, exact variants unknown. C7 rejected before printing for intrusive shelves; C8-context shortened loop broke on first push, TPU strips unprinted; hinged work discarded
- Final object: New short-lap wall-snap prototype unprinted. M1 printed and usable, retention inadequate; source/exports preserved. Current packing, integrated retention, sideways stiffness and durability require physical assessment
- Provenance: [Current](model/dental_travel_case/notes/short_lap.md#attribution), [historical](model/dental_travel_case/notes/provenance.md) · Agent effort: [Historical selected token/timing record](model/dental_travel_case/notes/agent_effort.md)

#### Slim dental box S16 liner

[Full two-cup TPU retrofit](model/dental_travel_case_liner/README.md)

- Test pieces: N/A — uses the preferred printed S16 starting profile
- Final object: Printed — inner and outer wall skins locally broken (2026-10-19); further breakage while pushing the liner into the old box (2026-10-20). Wall and installation integrity not accepted; cause unresolved. Reported 0.4 mm nozzle / 0.2 mm layers and 9 mm³/s limit; actual speeds unknown. Completed seating, contents fit and quietness unreported
- Provenance: [Record](model/dental_travel_case_liner/README.md#attribution) · Agent effort: N/A — no performance study requested

### Samples and application research

#### TPU damping box research

[Preferred printed S16 profile](model/tpu_damping_box/README.md)

- Test pieces: Yes — prior liners at 0.2 mm layers; S16/S12 work, S16 preferred; I10 rejected. Latest report: surface waviness remains despite 50% ironing. New [eight 30 mm finish coupons](model/tpu_damping_box/README.md#surface-finish-coupons--2026-10-17): not yet printed; surface and damping comparison pending. Other exact prior settings unknown
- Final object: N/A — samples; S16 approved starting profile for rigid-shell/TPU damping; application fit/quietness require review
- Current follow-up: [R2 support-test pairs](model/tpu_damping_box/README.md#ordinary-classic-repair--r2) replace R1, which the user rejected before printing for missing sliced walls. R2 retains A at 1.6/2.0 mm and both B tie sizes at 1.6 mm, with 0.5 mm skins and engraved R2 IDs. One ordinary Classic profile, thin-wall detection OFF; R1 loses walls/produces empty-layer errors under that setup. Physical installation survival and damping remain untested. F0–F7 do not qualify tall walls
- Provenance: [Record](model/tpu_damping_box/README.md#attribution) · Agent effort: N/A — no performance study requested

#### One-sided dental latch research

[A: original upright catch; B: flat lower-travel PLA concept](model/dental_latch_study/README.md)

- Test pieces: No — new A/B samples; CAD/path checks and diagnostic slices complete; A support reviewed; PLA behavior untested
- Final object: N/A — samples only; dental case unchanged
- Provenance: [Record](model/dental_latch_study/README.md#attribution) · Agent effort: N/A — no performance study requested

#### Sunglasses-case S16 liner

[Two-cup retrofit and setup](model/sunglasses_case_liner/README.md)

- Test pieces: Yes — ironing sample printed at 0.2 mm layers; 50% flow preferred (“perfect”), 10%/30% leave gaps, 100% raises/bumps the top. Other exact settings unknown; S16 damping samples approved separately
- Final object: Yes — successful fit and damping (2026-10-17); 2026-10-19 comparison confirms no dental-style wall breakage, with a recalled earlier 80 mm/s setting whose role/attained speeds are unverified. Exact printed revision/full settings unknown; long-term wear and tape adhesion not separately assessed
- Provenance: [Record](model/sunglasses_case_liner/README.md#attribution) · Agent effort: N/A — no performance study requested

### Unreported prototypes and calibration objects

#### Physical-analysis phone stand

[V3: compact fully printed pedestal, concealed three-angle lock](model/analysis_phone_stand/README.md)

- Test pieces: N/A — complete prototype; miniatures are exploratory
- Final object: Unknown — V3 is an unprinted 105 × 140 mm, four-core-part prototype. CAD, conditional mechanics and reference slice checked; fit, ring/cable use, tapping, desk grip and PETG recovery remain physical unknowns. Current MyoArm sampled access depends on assumed shoulder placement and incomplete collision coverage; integrated operation is UNKNOWN. V1/V2 rejected before printing.
- Provenance: [Record](model/analysis_phone_stand/README.md#attribution) · Agent effort: [Selected token/timing record](model/analysis_phone_stand/notes/agent_effort.md)

#### Rounded storage tray

[220 mm interior tray](model/storage_tray/README.md)

- Test pieces: N/A — full tray is the trial
- Final object: Unknown — no user report
- Provenance: [Record](model/storage_tray/README.md#attribution) · Agent effort: [Selected token/timing record](model/storage_tray/notes/agent_effort.md)

#### CornerFlowTest

[Orca vase-mode calibration](model/corner_flow_test/README.md)

- Test pieces: N/A — full object is the trial
- Final object: Unknown — no user report
- Provenance: [Record](model/corner_flow_test/README.md#attribution) · Agent effort: [Selected token/timing record](model/corner_flow_test/notes/agent_effort.md)

#### Glove drying insert

[Five-finger design](model/glove_drying_insert/README.md)

- Test pieces: Unknown — no user report
- Final object: Unknown — no user report
- Provenance: [Record](model/glove_drying_insert/README.md#attribution) · Agent effort: [Selected token/timing record](model/glove_drying_insert/notes/agent_effort.md)

### How to interpret the records

Agent-effort links give selected historical token categories and qualified timing
samples, with shared/import/follow-up scopes kept explicit. They supplement creator
provenance; coverage is partial and token counts do not establish product quality.
For a new design, the design skill's
[reusable model evidence](.codex/skills/cadquery-3d-design/references/reusable-model-lessons.md)
points to tested interfaces and their transfer limits.

The three former swatch-storage concepts were removed after authoritative user
feedback: the sliding box was physically printed and rejected as an incoherent
product; the lift-off and upright concepts were also rejected visually and
functionally. This was a product-architecture failure, not an established tolerance
or print-process defect. Git history (through `d37763c`) preserves the designs.
The successful archive swatch remains supported. A minimal
[local numerical contact fixture](physical_analysis/experiments/ipc/fixtures/rounded_snap/README.md)
preserves useful solver regressions without serving as a product precedent.
The [architecture gate](.codex/skills/cadquery-3d-design/references/design-decisions.md#product-architecture-gate)
now precedes mechanism refinement.

## Modelling tools

The repository is a uv Python project. Current runtime requirements are in
[pyproject.toml](pyproject.toml) and [uv.lock](uv.lock); older version lists in
model and performance records identify historical runs. Run `uv sync --locked` once, then use the
shared [CadQuery evaluation command](evaluate_model.py) to build, inspect,
render and export matching STEP/STL files with `--export`; `--slice` also runs a
reference OrcaSlicer smoke review on the STL. Invoke it directly as
`./evaluate_model.py`; `--help` lists its options and defaults. No MCP server
configuration is needed. CairoSVG in the uv environment produces PNG views;
OrcaSlicer is installed from Flathub for reference-profile CLI print review.

[Agent instructions](AGENTS.md) route task methodology and required evidence.
[CAD operation details](execution/README.md#cad-evaluation-and-exports) cover
selection, exports, views and retained native reports (`--report ... --summary`);
[execution contracts](execution/README.md) cover reuse, resources and recovery.

Physical questions such as loaded deflection, flexure reaction force and contact
are available through the [physical analysis API](physical_analysis/README.md).
It wraps Gmsh and CalculiX, retains solver evidence, and distinguishes numerical
completion from design adequacy and physical validation.

Optional [assembly geometry](assembly_geometry/README.md) keeps native named
CadQuery components in stable operating/print configurations and evaluates
explicit contact, clearance, obstruction and sampled rigid-path requirements.
Its qualified native constraint solves retain independent residuals; positioned
component shapes feed the existing evaluator and physical questions directly.

Optional [local Codex latency capture](performance/WORKFLOW.md#optional-machine-setup-and-future-clones)
needs a separate machine setup for native telemetry and its filtered receiver,
including Remote Control startup. Cloning or moving this repository does not carry
that setup; future agents should check availability and discuss installation with
the user. Modeling and existing analysis remain usable without it.

[Product verification](product_verification/README.md) links declared user intent,
variant checks and scoped physical evidence without a product score. Q1/Q1F,
the sunglasses case, book plate and Vaseline jar are initial consumers; simple
objects can retain local checks. It does not change their print status.

Optional [articulated human-interaction guidance](.codex/skills/articulated-human-interaction/SKILL.md)
starts product-local with [V3 rear-button reach and sampled access](model/analysis_phone_stand/README.md#articulated-release-access).
MuJoCo/SciPy kinematic evidence keeps assumed human geometry, endpoint/path outcomes
and physical UNKNOWN distinct; it adds no ergonomic score or print qualification.

## Licensing

This is a mixed-license repository. [MIT](LICENSE) is the default for
repository-owned material; object-specific licences and third-party notices
take precedence for their stated files.

| Object | Licence | Attribution |
| --- | --- | --- |
| [Integrated MacBook charger holder](model/macbook_charger_holder/) | [CC BY-NC-SA 4.0](model/macbook_charger_holder/LICENSE) | [Original model and modifications](model/macbook_charger_holder/ATTRIBUTION.md) |
| [TPU damping-box Orca snapshots](model/tpu_damping_box/profiles/) — profile JSONs only | [AGPL-3.0](model/tpu_damping_box/profiles/LICENSE.txt) | [Orca/Qidi sources and changes](model/tpu_damping_box/profiles/ATTRIBUTION.md); model geometry retains the default licence |
| [Dental S16 Orca process](model/dental_travel_case_liner/profiles/) — profile JSON only | [AGPL-3.0](model/dental_travel_case_liner/profiles/LICENSE.txt) | [Source and layer-height changes](model/dental_travel_case_liner/profiles/ATTRIBUTION.md); liner geometry retains the default licence |
| [Dental short-lap Orca process](model/dental_travel_case/notes/short_lap/profiles/) — profile JSON only | [AGPL-3.0](model/dental_travel_case/notes/short_lap/profiles/LICENSE.txt) | [Source and three-wall change](model/dental_travel_case/notes/short_lap/profiles/ATTRIBUTION.md); geometry retains the default licence |
| [Swatch Q1 Orca profile snapshots](model/filament_swatch_box_study/notes/quiet_q1_profiles/) — profile JSONs only | [AGPL-3.0](model/filament_swatch_box_study/notes/quiet_q1_profiles/LICENSE.txt) | [Orca/Qidi source and snapshot changes](model/filament_swatch_box_study/notes/quiet_q1_profiles/ATTRIBUTION.md); Q1 model geometry retains the default licence |

Remixing is welcome under each object's applicable terms. For the charger
holder, sharing requires attribution, commercial use is not permitted by the
licence, and shared adaptations must use CC BY-NC-SA 4.0. Do not assume that
every model or printable export is MIT-licensed. New remixes should include
an object-level `LICENSE` and `ATTRIBUTION.md`, and an entry in this table.
