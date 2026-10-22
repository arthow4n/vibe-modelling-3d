# Rotary closure with a solid custom printed screw and nut

**The complete quick PLA trial is now reported successful.** Its idea works and stays together, with slightly loose fit at the corrected temperature. The user authorizes modest tightening, a wheel-width cap keeper and full-size adoption. [Current full-box print files and instructions](rotary_case.md).

This record preserves the mechanism, hollow-thread correction and earlier binding investigation. Those observations preceded the successful [50 mm quick trial](quick_rotary.md). The suspected overheating cause remains unconfirmed; the revised full box has its own first-print status.


![Replacement screw and keyed printed nut](../renders/tests/printed_fasteners/rotary_printed_fasteners_isometric.png)

## What the user requires and what changed

The latest instruction explicitly favors an **all-printed screw and matching nut**, with a custom thread sized for ordinary FDM rather than forced compatibility with a stock metal nut. It supersedes the earlier stock-only hardware approach. Installed hardware must remain recessed and outside storage, and the wheel must resist accidental opening independently of pivot tightening. Existing sample compatibility is desirable, not mandatory; it is achieved here.

The replacement has a **6 mm major diameter, 4.6 mm solid root diameter and 2.4 mm pitch**. This is a custom coarse thread, **not M6**. Its broad 0.5 mm crest and 0.6 mm flank rise replace the old 1 mm pitch / approximately 0.126 mm crest. The female thread is cut with 0.24 mm radial and 0.08 mm additional axial allowance per flank. The book-reading plate's successful coarse printed thread informed the profile and clearance; its larger diameter and strength are not transferred as validation of this pair.

The nut is a **10 × 11 × 5.2 mm keyed printed block**. Its flat sides fit the existing 10.4 mm slot. The screw retains the original **8 mm shoulder diameter**, **2 mm shoulder length**, recessed **8 mm external hex**, and total **10.6 mm length**. The unchanged body bore is 6.4 mm. The same shoulder seats against the body, leaving **0.5 mm axial wheel freedom**, rather than clamping the wheel for resistance. The detent, capture nose, keeper, 30 mm sleeve, 3 mm seam reveal and continuous storage walls are unchanged. Maximum local projection remains 10.4 mm.

## The old thread really was hollow

The user correctly identified an **empty centre in the model's threaded section**. A direct material witness through the old source and delivered `rotary_refinement_axle.step` confirms the entire 3 mm-diameter core witness is absent between 5 and 9 mm above the bed. This is a CAD defect, not merely sparse infill. The intended root cylinder initially existed; the following helical union/trim returned a hollow thread while the final shape still passed validity and connectivity checks. The precise kernel/sweep cause is not isolated.

The agent initially asserted the core was solid from reading the intended cylinder, then attributed the issue to printing before checking the exported geometry. Both statements were wrong. The corrected check tests material after the complete construction and in the actual exported STEP. The replacement retains an extended root cylinder during the sweep union and then trims the combined geometry; its complete axial-core witness passes. The old hollow geometry is retained as a negative control so the check must catch the known defect.

[Actual CAD thread sections: old and replacement](../renders/tests/printed_fasteners/thread_sections.svg).

The old diagnostic process also used sparse infill through parts of the head and shoulder. The new pair is explicitly **100% infill** and its sampled toolpaths fill the centre through head, shoulder and thread. Increasing infill alone could never repair the old CAD hole. [Actual old/new paths](../renders/tests/printed_fasteners/core_paths.svg) · [path evidence](printed_fasteners/core_paths.json).

## PLA guide-binding feedback — 2026-10-22

The user has printed the previous indexed sample and finds its PLA body and cap very tight and hard to pull apart. They explicitly confirm the problem persists with the **wheel completely removed**. At that point the replacement screw had not been printed; the later complete quick trial is now reported successful. They are exploring PLA first; PETG is untested and may be explored later. The user expects the approximately 30 mm overlap to guide the case adequately once it releases; that expectation is not a measured retention result. The model has **30 mm sleeve height (3 cm), with 27 mm actually engaged** because of the 3 mm seam reveal.

A targeted inspection of the actual delivered `rotary_index_test.step`, identified in [guide evidence](printed_fasteners/guide_review.json), finds **0.30 mm nominal clearance per side** at the four flats and a rounded-corner witness: sleeve outside 71.2 × 48.2 mm, cap inside 71.8 × 48.8 mm. Sampled straight withdrawal has no body/cap solid overlap. There are no shell snap teeth in this rotary sample. This establishes intended geometry only; it does not override the physical binding report or establish low sliding effort.

The guide is nearly continuous around the perimeter and over the engaged length. Its tight nominal allowance leaves little room for printed surface error or misalignment. Which surfaces rub, the actual part dimensions and pull force are unknown; roughness, seams, shape error and cocking are plausible contributors rather than measured causes. The closed-ended sample also differs in stiffness from open R1a, whose qualitative success does not qualify the newer guide. The entry has no dedicated lead-in chamfer. Printed contact or end effects have not been isolated.

The initial diagnosis proposed more guide clearance, a lead-in and relieved bearing surfaces. **The latest user instruction supersedes that proposal:** the user recalls unintentionally closing the chamber for the tight later PLA print, suspects overheating, and says R1a fitted nicely. Its guide dimensions were the same. The [new shorter open-ended sample](quick_rotary.md) therefore keeps the 0.30 mm fit unchanged and is intended for the corrected PLA setup. This does not erase the observed binding or prove its thermal cause. A replacement screw alone cannot change that particular printed guide fit.

[Prusa's tolerance guidance](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135#tolerances) treats nominal clearance as a starting choice dependent on geometry, orientation, settings and material. Its generic 0.3 mm starting point is not qualification of this long rectangular PLA joint. Prior rigid-clearance checks answered geometric obstruction, not printed friction or comfortable operation.

## Assemble using the current sample

These are preserved assembly steps for the compatible fastener pair. Use the current [short sample instructions](quick_rotary.md) for the next print; the tight earlier shell remains a historical result.

1. Retain the existing body, cap and wheel for reference. Set aside the old fine-thread screw and metal M6 nut; neither mates with this new pair. Remove the pair's brim and any first-layer burrs without sanding away thread flanks.
2. Try the new screw and nut **loose in your hands first**. Start square, back-turn until the lead finds its start, then turn gently. They should engage for about two turns without forcing, whitening or cracking. The nut is shallow to preserve compatibility; fit, stripping and durability remain untested.
3. With the cap off, drop the printed nut into the existing top-loading pocket. Its **10 mm side runs across the slot**, its 11 mm dimension is vertical, and its threaded hole points out toward the wheel. The pocket's flat walls keep it from spinning; backing separates it from storage.
4. Place the wheel over the body pins in LOCK and pass the new screw through it. Start the printed nut gently, then seat the shoulder using an **8 mm socket, maximum 12.8 mm outside diameter**. Do not tighten beyond light seating. The recessed head and protected interior remain as before.
5. Check that the wheel turns independently of screw tightness, rests in LOCK and OPEN, and needs a deliberate turn to leave LOCK. Seat the cap in OPEN, turn to LOCK and try a gentle straight tug; release pulling before unlocking. Watch for loosening, wear, strings, cracks or spring whitening over several cycles.

If the loose pair binds, stop and report where; do not force it in the sample. If the wheel binds only after assembly, distinguish shoulder seating, brim residue and pin rubbing from thread fit. A freely spinning wheel requires detent revision, not extra screw clamping. Shortened shells do not qualify full-case peel, loaded handling or bag shaking.

## Verification, limits and print status

[CAD evidence](printed_fasteners/cad.json) checks the replacement's complete solid core and the known hollow negative control, the exported old/new STEP thread centres, **25 helical insertion/removal poses**, straight withdrawal obstruction, nut drop-in access, and unchanged body/cap/wheel material. It also reuses the full and short sample checks for protected storage skins, shoulder seating, recessed head and socket access, detent-before-release, journal play, capture, stops, withdrawal and individual full-size contents passage. No measured torque, strength, wear or shake resistance is claimed.

[Native export/slice report](printed_fasteners/print_review.json): CadQuery 2.8.0 exports the matching pair; **OrcaSlicer 2.4.2 completes with no notices and no automatic-support paths**. Actual paths at head/shoulder/thread sections fill the central witness. The Q2C 0.4 mm diagnostic setup uses 0.2 mm layers, four walls and 100% rectilinear infill. Its filament preset is **PETG diagnostic**, so use your own PLA preset. This establishes selected-profile path generation, not physical print quality or the separate GUI STEP importer. [Source/export association](printed_fasteners/publication.json).

The compatible body/cap/wheel are those in [`rotary_index_test.step`](../rotary_index_test.step) / [STL](../rotary_index_test.stl) from `d2e367c`. Those exports are deliberately preserved to identify the earlier print. For a new trial use `rotary_quick_test.step` / `.stl` and the same replacement pair with solid fastener settings, as described in [the current sample record](quick_rotary.md). Existing old sample/export reports are historical; current model/check calls explicitly select `printed-coarse`.

| Item | Print status | Artifact(s) | User result / remaining observation |
| --- | --- | --- | --- |
| R1a action sample | **Yes** | Unchanged `rotary_r1_test.step` / `.stl` | User reports “kind of works” / “okay” on 2026-10-22; quantitative effort, durability and bag security unknown. Exposed final appearance remains rejected. |
| Indexed spring sample, old M6 fastener revision | **Partial — shells printed and tested; sliding fit rejected** | `rotary_index_test.step` / `.stl` at `d2e367c` | PLA body/cap very hard to separate with wheel removed. User later recalls unintended closed chamber and suspects overheating; unconfirmed. No successful complete closure result. Hollow old thread confirmed; actual screw breakage not reported. |
| Coarse printed replacement pair | **Yes — included in successful complete PLA quick trial** | `rotary_printed_fasteners.py` / `.step` / `.stl` | Assembly works; separate strength/torque/wear remain unmeasured. Reused unchanged for the full case. |
| Full rotary case | **N/A — study only** | No new production print release | Full case on hold; retention force, far-edge peel and bag shaking unqualified. |

## History, references and attribution

[Previous M6 revision and evidence](rotary_refinement_m6_history.md) preserve its dimensions, hardware packaging, support diagnosis, research links and attribution. Its original source/export reports describe `d2e367c`; they do not qualify the new pair. The earlier exposed-hardware study is preserved there at `4229ddb`. [R1a action record](rotary_r1.md) retains the newly reported qualitative success. Its hardware and geometry remain unchanged.

[Book-reading plate](../../book_reading_plate/README.md#what-changed-after-the-successful-l-sample) is positive physical evidence for that larger custom printed thread. It supports choosing a coarse, printable pair as a starting point rather than forcing an ISO interface; it does not calibrate this reduced 6 mm thread. The useful lesson is to co-design both mating parts and the intended solid print, then verify actual root material after all sweep/boolean operations. Stock hardware availability is an option, not a requirement to recreate metal-scale detail in plastic.

Primary language model: GPT-6 family; exact model identifier and reasoning effort not exposed. Harness: Codex coding-agent environment. Provider: OpenAI. User supplied the print feedback, identified the hollow model, and requested the fully printed custom pair and solid fasteners. Prior attribution is preserved in the historical record.
