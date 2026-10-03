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

For retained evidence, add `--report model/<object>/notes/<run>.json --summary`:
the evaluator saves its complete native JSON and prints compact stage status,
errors, notices and support-probe results. The report path is relative to the
current directory; parent directories are created and existing reports replaced.
Without these options, console output and exit-status behavior stay unchanged.

Physical questions such as loaded deflection, flexure reaction force and contact
are available through the [physical analysis API](physical_analysis/README.md).
It wraps Gmsh and CalculiX, retains solver evidence, and distinguishes numerical
completion from design adequacy and physical validation.

Optional [local Codex latency capture](performance/WORKFLOW.md#optional-machine-setup-and-future-clones)
needs a separate machine setup for native telemetry and its filtered receiver,
including Remote Control startup. Cloning or moving this repository does not carry
that setup; future agents should check availability and discuss installation with
the user. Modeling and existing analysis remain usable without it.

## Models

| Object | Current use and print instructions | Model provenance | Test piece(s) printed | Final object printed |
| --- | --- | --- | --- | --- |
| Physical-analysis phone stand | [Compact table stand for viewing/reading, portrait/landscape and portrait charging under discussion; physical-analysis purpose retained](model/analysis_phone_stand/README.md) | [Record](model/analysis_phone_stand/README.md#attribution) | N/A — no separate coupon | No — user confirms unprinted; bulky exposed-gear product rejected before printing. Historical CAD/slice/local analysis retained; replacement architecture not yet agreed |
| Postcard displays | [Seven postcard displays: original through Orbit, Bolt and Pebble](model/postcard_display/README.md) | [Record](model/postcard_display/README.md#attribution) | N/A — full holder is the trial | Partial — Wave printed and works well; six other variants unreported |
| Book reading plate | [Final PETG plate and head-up screws](model/book_reading_plate/README.md) | [Record](model/book_reading_plate/README.md#attribution) | Yes — prior L sample worked; head/socket issue revised; no new coupon | Yes — user reports the complete plate printed with a really nice result |
| Decorative faceted tray | [Eight texture samples and retained tray exports](model/faceted_storage_tray/README.md) | [Record](model/faceted_storage_tray/README.md#attribution) | Unknown — eight coupons, no user report | Partial — variant H printed; user reports it works well; other variants unreported |
| Rounded storage tray | [220 mm interior tray](model/storage_tray/README.md) | [Record](model/storage_tray/README.md#attribution) | N/A — full tray is the trial | Unknown — no user report |
| CornerFlowTest | [Orca vase-mode calibration](model/corner_flow_test/README.md) | [Record](model/corner_flow_test/README.md#attribution) | N/A — full object is the trial | Unknown — no user report |
| Dental travel case | [Instructions](model/dental_travel_case/notes/README.md) | [Record](model/dental_travel_case/notes/provenance.md) | No — verification record | No — verification record |
| MacBook charger holder | [Instructions](model/macbook_charger_holder/notes/README.md) | [Record](model/macbook_charger_holder/notes/provenance.md) | No — optional coupon not used | Yes — user reports good print |
| Sunglasses case | [Accepted E production design](model/sunglasses_case/notes/printing_and_design.md) | [Record](model/sunglasses_case/notes/provenance.md) | Yes — D/E accepted | Yes — user reports it works really well |
| Glove drying insert | [Five-finger design](model/glove_drying_insert/README.md) | [Record](model/glove_drying_insert/README.md#attribution) | Unknown — no user report | Unknown — no user report |
| Vaseline container | [Screw-top jar](model/vaseline_container/README.md) | [Record](model/vaseline_container/README.md#attribution) | N/A — full pair is the trial | Yes — user reports good print |
| Vaseline transfer spatula | [Flat scrape-and-fill tool](model/vaseline_transfer_spatula/README.md) | [Record](model/vaseline_transfer_spatula/README.md#attribution) | N/A — complete tool is the first proposed trial | Unknown — no user report |
| Filament archive swatch | [SCAD instructions](model/filament_archive_swatch/README.md) | [Record](model/filament_archive_swatch/README.md#attribution) | N/A — full swatch is the trial | Yes — user reports previous print works as intended |
| Upright swatch box | [Five-card bases and accepted G hood](model/filament_swatch_box_study/README.md) | [Record](model/filament_swatch_box_study/README.md#attribution) | Yes — I keys work, 3 preferred. G hood accepted. V1 printed in PETG vase mode: holds base, but shell deforms/bulges with popping sounds; shape/feel rejected | J/K printed: J tilts cards; K fails dome engagement. J2/K2/J3/K3 explicitly unprinted; grips declined, J3/K3 flaps rejected before printing. Current J4/K4 use recessed upward-facing grips in original footprint with G hood and I key 3; targeted CAD checks/exports/slices passed, physical use unreported. No further hood exploration; complete-box durability unqualified |

These links identify current instructions; retained experiments are historical
unless the current instructions recommend them. The two print-status columns use
the [standard per-object status block](.codex/skills/cadquery-3d-design/references/physical-experiments.md#standard-per-object-print-status-record):
**Unknown** means no user print report is recorded, while **N/A** means no
printable item exists in that category for the current phase. Detailed results
and remaining physical checks are documented with each object.
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

Remixing is welcome under each object's applicable terms. For the charger
holder, sharing requires attribution, commercial use is not permitted by the
licence, and shared adaptations must use CC BY-NC-SA 4.0. Do not assume that
every model or printable export is MIT-licensed. New remixes should include
an object-level `LICENSE` and `ATTRIBUTION.md`, and an entry in this table.
