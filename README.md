# vibe-modelling-3d

Parametric 3D-printable objects and engineering experiments in CadQuery, mainly for single-material FDM printing. Each object directory in `model/` owns its Python source, printable `.step`/`.stl` exports, current decisions, and supporting evidence.

> **Note:** A model file being in the repository does **not** mean it has been physically printed or validated. Check the status in each model entry below or at the top of its `README.md`.

## Start here

- **Browse & print models:** Use the [Models catalog](#models) below. Every model's `README.md` starts with **At a Glance** (what works, which exact file to print, slicer settings, and what old variants to ignore).
- **Build or slice from source:** Use [Modelling tools](#modelling-tools) and the [execution guide](execution/README.md#running-scripts).
- **Explore engineering lessons:** Each object's `README.md` links to its deeper `notes/` and solver reports; transferable lessons are indexed in [reusable model lessons](.codex/skills/cadquery-3d-design/references/reusable-model-lessons.md).
- **Agent rules & documentation style:** See [AGENTS.md](AGENTS.md) and [Documentation writing](.codex/skills/documentation-writing/SKILL.md).

## Models

Models are grouped by their real-world physical print status. In the standard status lines:
- **Yes / Partial / Printed** = physically printed by the user with reported results.
- **Unknown** = CAD and smoke slice pass, awaiting physical print report (not a failure).
- **N/A** = separate sample coupons do not apply (or object is a sample study only).

Full status definitions live in [physical-experiments.md](.codex/skills/cadquery-3d-design/references/physical-experiments.md#standard-per-object-print-status-record).

---

### 1. Printed & Working Objects (Ready to Print)

#### Book reading plate — [`model/book_reading_plate/`](model/book_reading_plate/README.md)
Two-piece L-profile PETG book reading stand (`400 × 260 × 50 mm` assembled) joined by four printed head-up hex-socket screws (`8 mm` Allen key).
- **Action / Print:** Ready to print — [`plate_left.step`](model/book_reading_plate/plate_left.step) ([`.stl`](model/book_reading_plate/plate_left.stl)), [`plate_right.step`](model/book_reading_plate/plate_right.step) ([`.stl`](model/book_reading_plate/plate_right.stl)), and [`screws.step`](model/book_reading_plate/screws.step) ([`.stl`](model/book_reading_plate/screws.stl)).
- **Test pieces:** Yes — prior `L` thread sample worked; head/socket revised; no new coupon.
- **Final object:** Yes — user reports the complete plate printed with a really nice result.
- **Provenance:** [Record](model/book_reading_plate/README.md#attribution) · **Agent effort:** [Selected token/timing record](model/book_reading_plate/notes/agent_effort.md)

#### Sunglasses case (Variant E) — [`model/sunglasses_case/`](model/sunglasses_case/notes/printing_and_design.md)
Reduced-interior (`158 × 78 × 63 mm`) captive-hinged PETG travel case with the accepted `Variant E` loop-and-keeper snap latch.
- **Action / Print:** Ready to print — [`sunglasses_case.step`](model/sunglasses_case/sunglasses_case.step) ([`.stl`](model/sunglasses_case/sunglasses_case.stl)). Optional TPU liner available below.
- **Test pieces:** Yes — `D`/`E` joint samples accepted (`D_firm_side_printed_keeper.stl`, `E_extra_firm_side_printed_keeper.stl`).
- **Final object:** Yes — user reports the case works really well.
- **Provenance:** [Record](model/sunglasses_case/notes/provenance.md) · **Agent effort:** [Selected token/timing record](model/sunglasses_case/notes/agent_effort.md)

#### Sunglasses-case S16 TPU liner — [`model/sunglasses_case_liner/`](model/sunglasses_case_liner/README.md)
Two-cup flexible TPU 95A sound-damping insert for the printed Variant E sunglasses case.
- **Action / Print:** Ready to print — [`sunglasses_case_liner.step`](model/sunglasses_case_liner/sunglasses_case_liner.step) ([`.stl`](model/sunglasses_case_liner/sunglasses_case_liner.stl)) at `0.2 mm` layers with `50%` top-surface ironing flow.
- **Test pieces:** Yes — ironing sample ([`bottom_sample_18p5mm.step`](model/sunglasses_case_liner/bottom_sample_18p5mm.step)) printed at `0.2 mm` layers; `50%` flow preferred ("perfect"), `10%`/`30%` leave gaps, `100%` raises bumps.
- **Final object:** Yes — successful fit and damping (2026-10-17); confirmed intact walls with no dental-style breakage (2026-10-19). Long-term wear and optional tape adhesion not separately assessed.
- **Provenance:** [Record](model/sunglasses_case_liner/README.md#attribution) · **Agent effort:** N/A — no performance study requested

#### MacBook charger holder — [`model/macbook_charger_holder/`](model/macbook_charger_holder/notes/README.md)
One-piece PETG cable-wrap ring with an integrated slide-in MagSafe 3 cradle for the 96W MacBook charger.
- **Action / Print:** Ready to print — [`macbook_charger_holder.step`](model/macbook_charger_holder/macbook_charger_holder.step) ([`.stl`](model/macbook_charger_holder/macbook_charger_holder.stl)).
- **Test pieces:** No — optional `cradle_test` coupon not used.
- **Final object:** Yes — user reports good print.
- **Provenance:** [Record](model/macbook_charger_holder/notes/provenance.md) · **Agent effort:** [Selected token/timing record](model/macbook_charger_holder/notes/agent_effort.md)

#### Vaseline container — [`model/vaseline_container/`](model/vaseline_container/README.md)
Scalloped `50 × 25 mm` screw-top travel jar (`38 mm` mouth, `3 mm` pitch thread) for petroleum jelly.
- **Action / Print:** Ready to print — [`vaseline_container.step`](model/vaseline_container/vaseline_container.step) ([`.stl`](model/vaseline_container/vaseline_container.stl)).
- **Test pieces:** N/A — full pair is the trial.
- **Final object:** Yes — user reports good print.
- **Provenance:** [Record](model/vaseline_container/README.md#attribution) · **Agent effort:** [Selected token/timing record](model/vaseline_container/notes/agent_effort.md)

#### Vaseline transfer spatula — [`model/vaseline_transfer_spatula/`](model/vaseline_transfer_spatula/README.md)
Flat `30 × 141 mm` scrape-and-fill hand tool matched to the `38 mm` Vaseline jar mouth.
- **Action / Print:** Ready to print — [`vaseline_transfer_spatula.step`](model/vaseline_transfer_spatula/vaseline_transfer_spatula.step) ([`.stl`](model/vaseline_transfer_spatula/vaseline_transfer_spatula.stl)).
- **Test pieces:** N/A — complete tool is the trial.
- **Final object:** Yes — user reports the print works well and has the right handle size (future compact storage revision noted as optional).
- **Provenance:** [Record](model/vaseline_transfer_spatula/README.md#attribution) · **Agent effort:** [Selected token/timing record](model/vaseline_transfer_spatula/notes/agent_effort.md)

#### Filament archive swatch — [`model/filament_archive_swatch/`](model/filament_archive_swatch/README.md)
OpenSCAD parametric filament sample card (`52.9 × 35.6 × 2.8 mm`) with thickness steps.
- **Action / Print:** Ready to print — see [SCAD instructions](model/filament_archive_swatch/README.md).
- **Test pieces:** N/A — full swatch is the trial.
- **Final object:** Yes — user reports previous print works as intended.
- **Provenance:** [Record](model/filament_archive_swatch/README.md#attribution) · **Agent effort:** [Selected token/timing record](model/filament_archive_swatch/notes/agent_effort.md)

#### Swatch display & archive box — [`model/filament_swatch_box_study/`](model/filament_swatch_box_study/README.md)
Modular 5-card display bases and 15-card compact archival box sharing a clear PETG lift-off hood (`G`) and joiner key (`I3`).
- **Action / Print:**
  - **15-card Archive Box (Accepted):** Print **Archive R2 A** ([`archive_r2_walled_15.step`](model/filament_swatch_box_study/archive_r2_walled_15.step) / [`.stl`](model/filament_swatch_box_study/archive_r2_walled_15.stl)) + **G Hood** ([`cap_g_hood_5.step`](model/filament_swatch_box_study/cap_g_hood_5.step) / [`.stl`](model/filament_swatch_box_study/cap_g_hood_5.stl)) + **I3 Key** ([`cap_i_grip_keys.step`](model/filament_swatch_box_study/cap_i_grip_keys.step) / [`.stl`](model/filament_swatch_box_study/cap_i_grip_keys.stl)). Ignore `R1` and unprinted `B`/`C`/`D`.
  - **5-card Display Base (Partial / Deferred):** `J4` ([`cap_j4_base_5.step`](model/filament_swatch_box_study/cap_j4_base_5.step) / [`.stl`](model/filament_swatch_box_study/cap_j4_base_5.stl)) is preferred over `K4` ([`cap_k4_base_5.step`](model/filament_swatch_box_study/cap_k4_base_5.step)), though cards still tilt slightly; user deferred further display-base and `K4` stop fixes.
  - **Do NOT print:** TPU quiet variants (`Q1`, `Q1F`, `V1`) — **TPU damping for this box was discontinued (2026-10-06)** due to sliding noise and fit issues.
- **Test pieces:** N/A — complete boxes/modules are the trials.
- **Final object:** Archive R2 A: Yes (printed and accepted — holds all 15 cards on hood lift). Display J4/K4: Partial (printed; fixes deferred). TPU Q1F/G-TPU: Discontinued.
- **Provenance:** [Record](model/filament_swatch_box_study/README.md#attribution) · [Named assembly investigation](model/filament_swatch_box_study/notes/development_record.md#named-assembly-engineering-2026-10-06) · **Agent effort:** [Selected token/timing record](model/filament_swatch_box_study/notes/agent_effort.md)

---

### 2. Active Prototypes, Print Trials & Partial Results

#### Dental travel case (Smooth C seam-grip box) — [`model/dental_travel_case/`](model/dental_travel_case/README.md)
Slim two-piece PETG box (`75.8 × 52.8 × 264 mm`) for an electric toothbrush (`255 mm`) and toothpaste tube (`160 × 55 × 40 mm`).
- **Action / Print:** Smooth C **unprinted prototype** — [STEP](model/dental_travel_case/short_lap_case_smooth.step) · [STL](model/dental_travel_case/short_lap_case_smooth.stl). Smooth aligned sides, `3 mm` exposed seam grip, 2 mm main walls/sleeve; modeled aligned pull about 11 N, physically unmeasured; use the matching pair. PETG, `0.4 mm` nozzle, `0.2 mm` layers, 3 configured loops, no supports ([setup / evidence](model/dental_travel_case/README.md)).
- **Do not print / Closed:** Closed `_assembled` inspection pose, superseded wrap-grip and deep-sleeve variants, and discarded hinged designs. Old coupled-impact analysis remains closed; fresh C force/side screens are scoped separately, with bag retention still a physical check.
- **Test pieces:** Short **PLA C2 ring trial**, print status **Unknown** — [STEP](model/dental_travel_case/smooth_joint_test.step) · [STL](model/dental_travel_case/smooth_joint_test.stl). 46/37 mm heights; preserves full-width catches/stop, tests local fit/action/recovery, not full-case force or bag retention. [Instructions](model/dental_travel_case/notes/smooth_exterior.md#short-pla-joint-trial). Earlier short wall snaps had high effort/noise (variants unknown); C7 rejected before print, C8 loop broke on first push and its TPU strips were unprinted.
- **Final object:** Smooth C **Unknown** (no reported print); seam grip, stop and snap feel need testing. Previous three-line wrap-grip pair unprinted. Printed M1 was usable as a shell but had inadequate retention.
- **Provenance:** [Smooth C](model/dental_travel_case/notes/smooth_exterior.md#phase-evidence-and-attribution), [short lap](model/dental_travel_case/notes/short_lap.md#attribution), [historical](model/dental_travel_case/notes/provenance.md) · **Agent effort:** [Historical record](model/dental_travel_case/notes/agent_effort.md)

#### TPU damping box & wall-support research — [`model/tpu_damping_box/`](model/tpu_damping_box/README.md)
30–34 mm TPU 95A test coupons used to qualify impact damping, tall-wall support durability, and surface finish before full liner prints.
- **Action / Print:** **L20 is preferred** — [STEP](model/tpu_damping_box/thin_gap_L20.step) / [STL](model/tpu_damping_box/thin_gap_L20.stl), `2.0 mm` wall versus T08's `2.2 mm`. L18, L20 and T08 all damp similarly well; L20 has print quality almost equal to T08 and slightly fewer bottom defects with ironing on (cause unknown). [Physical report](model/tpu_damping_box/notes/thin_gap/README.md#physical-feedback--2026-10-21).
- **Test pieces:** Yes — L20, L18 and T08 printed and approved; T08 remains a comparison control, B08/B16 and S16/S12 historical references. **Do not reprint** rejected T16 (too firm/noisy), A16/A20, solid C12/C16, R1 or torn I10. F0–F7 surface coupons have no print report (`Unknown`).
- **Final object:** N/A — research samples feeding the sunglasses and dental liners.
- **Provenance:** [Record](model/tpu_damping_box/README.md#attribution) · **Agent effort:** N/A — no performance study requested

#### Slim dental box S16 TPU liner — [`model/dental_travel_case_liner/`](model/dental_travel_case_liner/README.md)
Full two-cup `S16` TPU 95A sound-damping retrofit for the printed M1 slim dental travel box.
- **Action / Print:** **Hold / Wait for T08 / L20 transfer.** The first `S16` print suffered local inner/outer wall skin tears (2026-10-19) and tore further during insertion into the tight deep box (2026-10-20). Small-box TPU research has now approved `T08 M1` (`0.8 mm` skins + separated ties + solid corners) and now prefers printed `L20` over `T08`, with `L18` also accepted; transfer to this tall dental liner remains unqualified.
- **Test pieces:** N/A — uses the `S16` profile; see [TPU damping box](model/tpu_damping_box/README.md) for active wall-support replacements (`T08`, `L20`/`L18`).
- **Final object:** Printed — wall and installation integrity **not accepted** (skins broke during print and insertion; cause unresolved).
- **Provenance:** [Record](model/dental_travel_case_liner/README.md#attribution) · **Agent effort:** N/A — no performance study requested

#### Postcard displays — [`model/postcard_display/`](model/postcard_display/README.md)
Seven stand-alone A6 / `100 × 150 mm` postcard holders (`Original`, `Outline`, `Wave`, `Prism`, `Orbit`, `Bolt`, `Pebble`).
- **Action / Print:** `Wave` ([`postcard_wave.step`](model/postcard_display/postcard_wave.step) / [`.stl`](model/postcard_display/postcard_wave.stl)) is printed and confirmed working; six other stylistic variants ([`postcard_display.step`](model/postcard_display/postcard_display.step), `postcard_outline.step`, `postcard_prism.step`, `postcard_orbit.step`, `postcard_bolt.step`, `postcard_pebble.step`) are ready to print.
- **Test pieces:** N/A — full holder is the trial.
- **Final object:** Partial — `Wave` printed and works well; six other variants unreported (`Unknown`).
- **Provenance:** [Record](model/postcard_display/README.md#attribution) · **Agent effort:** [Selected token/timing record](model/postcard_display/notes/agent_effort.md)

#### Decorative faceted tray — [`model/faceted_storage_tray/`](model/faceted_storage_tray/README.md)
`220 × 220 mm` interior square trays with eight outer faceted wall patterns (`A`–`H`).
- **Action / Print:** Variant `H Soft` ([`variants/h_soft/h_soft.step`](model/faceted_storage_tray/variants/h_soft/h_soft.step) / [`.stl`](model/faceted_storage_tray/variants/h_soft/h_soft.stl)) is printed and works well; root default `C Slender` ([`faceted_storage_tray.step`](model/faceted_storage_tray/faceted_storage_tray.step) / [`.stl`](model/faceted_storage_tray/faceted_storage_tray.stl)) and variants `A`–`G` are ready to print.
- **Test pieces:** Unknown — eight 1:1 wall coupons (`test_pieces/*/*_coupon.step`/`.stl`), no user report.
- **Final object:** Partial — variant `H` printed and works well; other full tray variants unreported.
- **Provenance:** [Record](model/faceted_storage_tray/README.md#attribution) · **Agent effort:** [Selected token/timing record](model/faceted_storage_tray/notes/agent_effort.md)

#### One-sided dental latch study — [`model/dental_latch_study/`](model/dental_latch_study/README.md)
Standalone mechanical study comparing an upright catch (`A`) vs. a flat lower-travel PLA flexure latch (`B`).
- **Action / Print:** Optional standalone sample coupons ([`a_original.step`](model/dental_latch_study/a_original.step) / [`.stl`](model/dental_latch_study/a_original.stl), [`b_flat_pla.step`](model/dental_latch_study/b_flat_pla.step) / [`.stl`](model/dental_latch_study/b_flat_pla.stl)); does not modify the dental case.
- **Test pieces:** No — unprinted A/B samples; CAD, path checks, and diagnostic slices complete; PLA behavior untested.
- **Final object:** N/A — samples only.
- **Provenance:** [Record](model/dental_latch_study/README.md#attribution) · **Agent effort:** N/A — no performance study requested

---

### 3. Unprinted Prototypes & Calibration Objects

#### Physical-analysis phone stand (V3) — [`model/analysis_phone_stand/`](model/analysis_phone_stand/README.md)
Compact `105 × 140 mm` fully printed pedestal phone stand with a concealed three-angle (`45°`/`60°`/`75°`) spring-latch lock.
- **Action / Print:** Unprinted prototype — [`phone_stand_v3.step`](model/analysis_phone_stand/phone_stand_v3.step) ([`.stl`](model/analysis_phone_stand/phone_stand_v3.stl)) + optional TPU feet [`phone_stand_v3_feet.step`](model/analysis_phone_stand/phone_stand_v3_feet.step) ([`.stl`](model/analysis_phone_stand/phone_stand_v3_feet.stl)). Ignore rejected `V1`/`V2`.
- **Test pieces:** N/A — complete prototype; miniatures are exploratory.
- **Final object:** Unknown — unprinted 4-part core prototype. CAD, conditional mechanics, MyoArm reach screen, and reference slice checked; physical fit, tapping stability, desk grip, and PETG spring recovery require printing.
- **Provenance:** [Record](model/analysis_phone_stand/README.md#attribution) · **Agent effort:** [Selected token/timing record](model/analysis_phone_stand/notes/agent_effort.md)

#### Rounded storage tray — [`model/storage_tray/`](model/storage_tray/README.md)
Simple `220 × 150 × 45 mm` rounded rectangular tray with `3 mm` walls.
- **Action / Print:** Unprinted — [`storage_tray.step`](model/storage_tray/storage_tray.step) ([`.stl`](model/storage_tray/storage_tray.stl)).
- **Test pieces:** N/A — full tray is the trial.
- **Final object:** Unknown — no user report.
- **Provenance:** [Record](model/storage_tray/README.md#attribution) · **Agent effort:** [Selected token/timing record](model/storage_tray/notes/agent_effort.md)

#### CornerFlowTest — [`model/corner_flow_test/`](model/corner_flow_test/README.md)
OrcaSlicer spiral vase-mode corner calibration shell.
- **Action / Print:** Unprinted — [`corner_flow_test.step`](model/corner_flow_test/corner_flow_test.step) ([`.stl`](model/corner_flow_test/corner_flow_test.stl)).
- **Test pieces:** N/A — full object is the trial.
- **Final object:** Unknown — no user report.
- **Provenance:** [Record](model/corner_flow_test/README.md#attribution) · **Agent effort:** [Selected token/timing record](model/corner_flow_test/notes/agent_effort.md)

#### Glove drying insert — [`model/glove_drying_insert/`](model/glove_drying_insert/README.md)
Open-lattice five-finger insert for airing and drying gloves.
- **Action / Print:** Unprinted — [`glove_drying_insert.step`](model/glove_drying_insert/glove_drying_insert.step) ([`.stl`](model/glove_drying_insert/glove_drying_insert.stl)).
- **Test pieces:** Unknown — no user report.
- **Final object:** Unknown — no user report.
- **Provenance:** [Record](model/glove_drying_insert/README.md#attribution) · **Agent effort:** [Selected token/timing record](model/glove_drying_insert/notes/agent_effort.md)

---

### How to interpret the records

- **Agent effort records:** Linked `agent_effort.md` files give historical token categories and timing samples with explicit scopes; they supplement creator provenance and do not measure product quality.
- **Reusable lessons:** See [reusable model lessons](.codex/skills/cadquery-3d-design/references/reusable-model-lessons.md) for tested interfaces and transfer limits.
- **Removed early swatch concepts:** Three early swatch-storage concepts (sliding, lift-off, upright) were removed after user feedback showed product-architecture flaws (preserved in Git history through `d37763c`, with a minimal solver regression fixture in [`rounded_snap`](physical_analysis/experiments/ipc/fixtures/rounded_snap/README.md)). The [product architecture gate](.codex/skills/cadquery-3d-design/references/design-decisions.md#product-architecture-gate) now precedes mechanism refinement.

## Modelling tools

This repository is a locked `uv` Python project ([`pyproject.toml`](pyproject.toml), [`uv.lock`](uv.lock)). Run `uv sync --locked` once, then use:
- **CAD build, views & exports:** `./evaluate_model.py model/<object>/<object>.py --export` (add `--slice` for a reference OrcaSlicer STL smoke check; see [CAD operation details](execution/README.md#cad-evaluation-and-exports) and [execution contracts](execution/README.md)).
- **Physical analysis (Gmsh / CalculiX):** [physical_analysis/README.md](physical_analysis/README.md) for deflection, flexure force, and contact studies.
- **Assembly geometry:** [assembly_geometry/README.md](assembly_geometry/README.md) for named multi-part placement, clearance, and rigid-path checks.
- **Product verification:** [product_verification/README.md](product_verification/README.md) links user intent, variant checks, and scoped physical evidence via `model/<object>/verification.py`.
- **Articulated human interaction:** [.codex/skills/articulated-human-interaction/SKILL.md](.codex/skills/articulated-human-interaction/SKILL.md) for MuJoCo/SciPy kinematic reach and collision screening.
- **Optional latency telemetry:** [performance/WORKFLOW.md](performance/WORKFLOW.md#optional-machine-setup-and-future-clones) documents optional local Codex telemetry setup.

## Licensing

This is a mixed-license repository. [MIT](LICENSE) is the default for repository-owned material; object-specific licences and third-party notices take precedence for their stated files.

| Object | Licence | Attribution |
| --- | --- | --- |
| [Integrated MacBook charger holder](model/macbook_charger_holder/) | [CC BY-NC-SA 4.0](model/macbook_charger_holder/LICENSE) | [Original model and modifications](model/macbook_charger_holder/ATTRIBUTION.md) |
| [TPU damping-box Orca snapshots](model/tpu_damping_box/profiles/) — profile JSONs only | [AGPL-3.0](model/tpu_damping_box/profiles/LICENSE.txt) | [Orca/Qidi sources and changes](model/tpu_damping_box/profiles/ATTRIBUTION.md); model geometry retains the default licence |
| [Dental S16 Orca process](model/dental_travel_case_liner/profiles/) — profile JSON only | [AGPL-3.0](model/dental_travel_case_liner/profiles/LICENSE.txt) | [Source and layer-height changes](model/dental_travel_case_liner/profiles/ATTRIBUTION.md); liner geometry retains the default licence |
| [Dental short-lap Orca process](model/dental_travel_case/notes/short_lap/profiles/) — profile JSON only | [AGPL-3.0](model/dental_travel_case/notes/short_lap/profiles/LICENSE.txt) | [Source and three-wall change](model/dental_travel_case/notes/short_lap/profiles/ATTRIBUTION.md); geometry retains the default licence |
| [Swatch Q1 Orca profile snapshots](model/filament_swatch_box_study/notes/quiet_q1_profiles/) — profile JSONs only | [AGPL-3.0](model/filament_swatch_box_study/notes/quiet_q1_profiles/LICENSE.txt) | [Orca/Qidi source and snapshot changes](model/filament_swatch_box_study/notes/quiet_q1_profiles/ATTRIBUTION.md); Q1 model geometry retains the default licence |

Remixing is welcome under each object's applicable terms. For the charger holder, sharing requires attribution, commercial use is not permitted by the licence, and shared adaptations must use CC BY-NC-SA 4.0. Do not assume that every model or printable export is MIT-licensed. New remixes should include an object-level `LICENSE` and `ATTRIBUTION.md`, and an entry in this table.
