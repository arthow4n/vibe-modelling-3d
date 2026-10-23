# Uniform L20 liner for the printed rotary dental box

Print the revised two-cup [STEP](../rotary_l20_uniform_liner.step) / [STL](../rotary_l20_uniform_liner.stl) / [Python](../rotary_l20_uniform_liner.py). **Both walls and floors now use 0.8 / 0.4 air / 0.8 mm, totaling 2 mm.** Keep the printed hard box, wheel, cap and screw. The user reselects this updated L20 recipe after printing G08/G16: G16 has a modest perceptible damping benefit, but L20 is sufficient for most uses. This full-size application still has no physical print report; the earlier thin-floor print was canceled.

Use the same [L20 standard and process as the experiment](../../tpu_damping_box/notes/l20_standard.md). The long body cup and short lid cup are the complete liner: no new inserts, adhesive or fasteners. Keep both closed ends down and openings up, at supplied centres (60,60) and (142,60).

![Uniform panel section shared with the experiment](../../tpu_damping_box/renders/print/uniform_l20/profile.png)

## User direction

After printing the G08 and G16 experimental cups, the user reports G16 meaningfully but only slightly better than L20 in damping, with G08 less meaningfully different. They explicitly select **updated L20** for the dental liner, not the older thin-floor recipe with visible defects. The authoritative dental source already imports SKIN=0.8, CORE=0.4 and TOTAL=2.0 from the shared standard, aliases both floor skins/core to those same values, and the matched native exports retain that construction. No model/export alteration or repeat slice is needed for this selection. [Recorded comparison](../../tpu_damping_box/notes/gap_comparison.md#physical-comparison-and-application-selection).

The user requires the same sandwich in walls and bottoms in both the TPU experiment and dental liner, and requires updating the reusable standard so future models cannot inherit the old inconsistency. This replaces the earlier 0.4/0.8/0.4 floors; their poor interior surface is recorded in the [prior application report](rotary_l20.md) and [floor explanation](floor_surface_review.md). Early wall regions looked okay, but a canceled print did not qualify completed tall walls or insertion.

## What changed and how it fits

Both floors grow from 1.6 to **2.0 mm**, with **0.8 mm skins** and a **0.4 mm post-supported gap**. Dimensions and floor pattern come from the experiment's [shared source](../../tpu_damping_box/l20_standard.py). Wall skins/gap retain the selected 0.8/0.4/0.8 section. The same 0.8 mm ties/posts and 4.4 mm grid are retained; the body floor's six-millimetre flare begins above the new floor height. Corners, shape transitions, end lands and rim closures remain solid boundaries of the active sandwich.

| Interface | Current geometry |
| --- | --- |
| Body / lid cup heights | 201.3 / 57.3 mm, unchanged |
| Installation allowance | 0.3 mm per side and at hard closed ends, unchanged |
| Cup-rim separation | 0.8 mm, unchanged |
| Body lined cavity / throat | 67.2 × 44.2 / 62.6 × 39.6 mm, unchanged |
| Clear length between interior floors | **255.4 mm**, previously 256.2 mm |
| Contents gauge | Separate 30 × 255 mm brush gauge clears; 0.4 mm nominal spare axial length |
| Lid seating | Existing four shallow ramped TPU pads, 0.1 mm intended local compression |

The 0.4 mm axial spare length is small. It is nominal CAD clearance, not permission to force a longer brush or proof of combined brush/paste packing. No hard shell was enlarged. The complete 2 mm leading body floor still fits rigidly through the sleeve mouth. The wider lower walls still need gentle elastic pinching during insertion; exact effort remains unmeasured. A nominal 40 mm toothpaste thickness also exceeds the 39.6 mm mouth, so actual tube deformation/packing remains a physical check.

## Printing and installation

Use the shared [uniform L20 process](../../tpu_damping_box/profiles/l20-uniform-process.json), [TPU 95A filament](../../tpu_damping_box/profiles/tpu95a.json) and [Q2C 0.4 mm printer](../../../.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json). **0.2 mm layers, Classic, thin-wall detection off, two walls, 100% rectilinear fill, four top and bottom layers, supports off, 9 mm³/s maximum flow.** Both current models retain the same 50% / 30 mm/s / 0.15 mm ironing starting recipe. Its actual finish effect is unqualified.

The four-layer backing is bed-supported; the two-layer-high core remains empty between posts; the four-layer contact skin closes over it. The first roof still bridges. Keep supplied orientation and placement. Broad backing gives stable bed contact, and the tall body remains below the Q2C's 256 mm build height. The gradual outer transitions preserve the previous approximately 0.077 mm outward movement per 0.2 mm layer. Internal supports would be trapped in the damping core.

Inspect the floor after all ten nominal floor layers, and stop for torn skins rather than completing a defective tall print. Insert the narrow closed end first, gently pinch the broader walls through the mouth, and stop if it needs force. Seat the lid cup on its shallow pads. Confirm the empty box opens/closes freely, then check actual contents and quietness. Do not infer installation durability from early wall appearance.

## Verification, limits and print status

Both current native layouts are valid, export paired STEP/STL successfully, and complete OrcaSlicer 2.4.2 slicing with the supplied TPU profile, no notices and **no automatic-support generation**. Actual local paths retain four-layer floor skins and the 0.4 mm core. This is digital evidence; the revised floor has no physical print report.

[CAD report](uniform_l20/cad.json) retains shell/hardware clearance, cap-withdrawal, complete-floor entry and lid-pad contact checks. Actual material/air probes inspect the added backing/contact layers and the 0.4 mm floor core; separate individual contents gauges are checked. [Native export/slice](uniform_l20/print_review.json), [local skin/core/floor paths](uniform_l20/paths.json), [publication association](uniform_l20/publication.json) and [product verification](uniform_l20/verification.json) identify the delivered files and TPU setup. Physical gap openness, floor finish, long-wall survival, installation force, seating and quietness remain untested for this revision.

| Item | Print status | Artifacts / user observation |
| --- | --- | --- |
| Prior small L20 experiment | **Yes — walls/damping preferred; floor fragile** | Historical recipe, not physical validation of this revised floor |
| Prior dental L20 print | **Partial — canceled for broken/cracking interior floor** | `rotary_l20_liner` files retained for identification |
| Uniform L20 dental liner | **Unknown — no print report** | `rotary_l20_uniform_liner.py` / `.step` / `.stl`; new two-cup application trial |
| Printed rigid box and revised controls | **Yes — user reports everything works well** | Existing case and matte-repair cap/screw remain unchanged |

## Engineering notes and attribution

One shared standard owns skin thickness, gap, total, post/tie dimensions and floor-core construction. Application geometry owns installation and contents clearances. The historical models and source-guarded receipts remain intact, and their successful walls are not promoted to new floor approval. New variant `rotary-l20-uniform` preserves earlier user intent while recording the explicit orientation-consistency requirement.

Primary language model: GPT-6 family; exact identifier and reasoning effort not exposed. Harness: Codex shared-workspace coding agent, OpenAI. No subagents. User supplies physical feedback and selects the uniform standard. Existing model and third-party profile attribution are preserved.
