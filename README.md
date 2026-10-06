# vibe-modelling-3d
Experiment field for random vibe-modelled 3D objects. Mainly for 3D printing.

## Modelling tools

The repository is a uv Python project. Run `uv sync --locked` once, then use the
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

## Models

| Object | Current use and print instructions | Model provenance | Test piece(s) printed | Final object printed | Agent effort |
| --- | --- | --- | --- | --- | --- |
| Physical-analysis phone stand | [V3: compact fully printed pedestal, concealed three-angle lock](model/analysis_phone_stand/README.md) | [Record](model/analysis_phone_stand/README.md#attribution) | N/A — complete prototype; miniatures are exploratory | Unknown — V3 CAD, conditional mechanics and reference slice checked; fit, ring/cable use, tapping, grip and PETG recovery unprinted. 105 × 140 mm base; four solid core parts. V1/V2 rejected before printing | [Selected token/timing record](model/analysis_phone_stand/notes/agent_effort.md) |
| Postcard displays | [Seven postcard displays: original through Orbit, Bolt and Pebble](model/postcard_display/README.md) | [Record](model/postcard_display/README.md#attribution) | N/A — full holder is the trial | Partial — Wave printed and works well; six other variants unreported | [Selected token/timing record](model/postcard_display/notes/agent_effort.md) |
| Book reading plate | [Final PETG plate and head-up screws](model/book_reading_plate/README.md) | [Record](model/book_reading_plate/README.md#attribution) | Yes — prior L sample worked; head/socket issue revised; no new coupon | Yes — user reports the complete plate printed with a really nice result | [Selected token/timing record](model/book_reading_plate/notes/agent_effort.md) |
| Decorative faceted tray | [Eight texture samples and retained tray exports](model/faceted_storage_tray/README.md) | [Record](model/faceted_storage_tray/README.md#attribution) | Unknown — eight coupons, no user report | Partial — variant H printed; user reports it works well; other variants unreported | [Selected token/timing record](model/faceted_storage_tray/notes/agent_effort.md) |
| Rounded storage tray | [220 mm interior tray](model/storage_tray/README.md) | [Record](model/storage_tray/README.md#attribution) | N/A — full tray is the trial | Unknown — no user report | [Selected token/timing record](model/storage_tray/notes/agent_effort.md) |
| CornerFlowTest | [Orca vase-mode calibration](model/corner_flow_test/README.md) | [Record](model/corner_flow_test/README.md#attribution) | N/A — full object is the trial | Unknown — no user report | [Selected token/timing record](model/corner_flow_test/notes/agent_effort.md) |
| Dental travel case | [Instructions](model/dental_travel_case/notes/README.md) | [Record](model/dental_travel_case/notes/provenance.md) | No — verification record | No — verification record | [Selected token/timing record](model/dental_travel_case/notes/agent_effort.md) |
| MacBook charger holder | [Instructions](model/macbook_charger_holder/notes/README.md) | [Record](model/macbook_charger_holder/notes/provenance.md) | No — optional coupon not used | Yes — user reports good print | [Selected token/timing record](model/macbook_charger_holder/notes/agent_effort.md) |
| Sunglasses case | [Accepted E production design](model/sunglasses_case/notes/printing_and_design.md) | [Record](model/sunglasses_case/notes/provenance.md) | Yes — D/E accepted | Yes — user reports it works really well | [Selected token/timing record](model/sunglasses_case/notes/agent_effort.md) |
| Glove drying insert | [Five-finger design](model/glove_drying_insert/README.md) | [Record](model/glove_drying_insert/README.md#attribution) | Unknown — no user report | Unknown — no user report | [Selected token/timing record](model/glove_drying_insert/notes/agent_effort.md) |
| Vaseline container | [Screw-top jar](model/vaseline_container/README.md) | [Record](model/vaseline_container/README.md#attribution) | N/A — full pair is the trial | Yes — user reports good print | [Selected token/timing record](model/vaseline_container/notes/agent_effort.md) |
| Vaseline transfer spatula | [Flat scrape-and-fill tool](model/vaseline_transfer_spatula/README.md) | [Record](model/vaseline_transfer_spatula/README.md#attribution) | N/A — complete tool is the trial | Yes — user reports the existing print works well, does its job and has the right handle size; storage bulk motivates a compact revision | [Selected token/timing record](model/vaseline_transfer_spatula/notes/agent_effort.md) |
| Filament archive swatch | [SCAD instructions](model/filament_archive_swatch/README.md) | [Record](model/filament_archive_swatch/README.md#attribution) | N/A — full swatch is the trial | Yes — user reports previous print works as intended | [Selected token/timing record](model/filament_archive_swatch/notes/agent_effort.md) |
| Swatch display / archive box | [Accepted A/G baseline; TPU damping discontinued with retained lessons](model/filament_swatch_box_study/README.md) | [Record](model/filament_swatch_box_study/README.md#attribution) | Archive and Q1F: N/A — complete box is the trial. R1 rejected before printing. Display J4/K4 printed; J4 preferred, K4 missing key stop at one end. G hood and I3 key retained; V1 shell rejected | TPU damping discontinued by user, 2026-10-06. Q1F printed: joining works, contrasting coverage/upper fit/sliding noise unsatisfactory. Unchanged G hood printed fully in TPU: TPU-on-TPU rubbing somewhat quieter but unacceptable; upper shell locally distorted/movable, still usable. Layer-line cause is user hypothesis; files/settings unknown. Q1 has no print report; follow-up SVGs are superseded history. Archive R2 A: Yes — accepted storage, J4 joining/G hood fit, full 15-card load retained on hood lift; rigid-contact sound unresolved. B/C/D: No — only A printed. J4 tilt and K4 two-ended joining fixes remain deferred | [Named assembly engineering](model/filament_swatch_box_study/README.md#named-assembly-engineering-2026-10-06) · [Selected token/timing record](model/filament_swatch_box_study/notes/agent_effort.md) |

These links identify current instructions; retained experiments are historical
unless the current instructions recommend them. The two print-status columns use
the [standard per-object status block](.codex/skills/cadquery-3d-design/references/physical-experiments.md#standard-per-object-print-status-record):
**Unknown** means no user print report is recorded, while **N/A** means no
printable item exists in that category for the current phase. Detailed results
and remaining physical checks are documented with each object.
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

## Licensing

This is a mixed-license repository. [MIT](LICENSE) is the default for
repository-owned material; object-specific licences and third-party notices
take precedence for their stated files.

| Object | Licence | Attribution |
| --- | --- | --- |
| [Integrated MacBook charger holder](model/macbook_charger_holder/) | [CC BY-NC-SA 4.0](model/macbook_charger_holder/LICENSE) | [Original model and modifications](model/macbook_charger_holder/ATTRIBUTION.md) |
| [Swatch Q1 Orca profile snapshots](model/filament_swatch_box_study/notes/quiet_q1_profiles/) — profile JSONs only | [AGPL-3.0](model/filament_swatch_box_study/notes/quiet_q1_profiles/LICENSE.txt) | [Orca/Qidi source and snapshot changes](model/filament_swatch_box_study/notes/quiet_q1_profiles/ATTRIBUTION.md); Q1 model geometry retains the default licence |

Remixing is welcome under each object's applicable terms. For the charger
holder, sharing requires attribution, commercial use is not permitted by the
licence, and shared adaptations must use CC BY-NC-SA 4.0. Do not assume that
every model or printable export is MIT-licensed. New remixes should include
an object-level `LICENSE` and `ATTRIBUTION.md`, and an entry in this table.
