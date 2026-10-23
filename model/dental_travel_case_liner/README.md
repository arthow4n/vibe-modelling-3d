# TPU Liners for the Dental Travel Case

Two preformed **L20 TPU 95A cups** for the latest [wraparound-wheel rotary box](../dental_travel_case/README.md). The long cup lines the body and sleeve; the short cup lines the lid above the sleeve.

<a id="what-to-print-now"></a>

## Current action: floor review before another full print

- **Existing files, hold repeat printing:** [STEP](rotary_l20_liner.step) · [matching STL](rotary_l20_liner.stl) · [Python](rotary_l20_liner.py). Both cups are on one plate, closed ends down and openings up. Two printed cups total.
- **Settings:** TPU 95A, **0.4 mm nozzle / 0.2 mm layers**, Classic walls, thin-wall detection off, **2 walls / 100% rectilinear fill / supports off**, **9 mm³/s** maximum volumetric flow. The [process preset](profiles/rotary-l20-process.json) uses **50% top-surface ironing**, drawing on the earlier accepted floor coupon. [Filament preset](../tpu_damping_box/profiles/tpu95a.json).
- **Status:** Full-size L20 printing was **canceled after the early layers**: printed wall regions look okay, but the contents-facing floor has broken/cracking surface regions. Earlier small-cup damping preference remains; floor robustness is unresolved across the experiment and application. See the [floor explanation and proposals](notes/floor_surface_review.md). [Design, installation and current evidence](notes/rotary_l20.md).
- **Do not reprint the old M1 S16 liner** (`dental_travel_case_liner.step` / `.stl`): it was damaged during printing and insertion and belongs to a different box.

![L20 cups for the rotary box](renders/rotary_l20/rotary_l20_liner_isometric.png)

## How this version fits

The walls retain **0.8 mm outer skin / 0.4 mm air gap / 0.8 mm inner skin**, with discrete **0.8 × 0.8 mm ties at 4.4 mm pitch**. Floors retain the **1.6 mm** post-supported sandwich. Corners and short shape transitions have solid backing, following the accepted L20 construction.

The body cup is **201.3 mm** tall; the lid cup **57.3 mm**. A **0.3 mm per-side installation allowance**, **0.3 mm at each closed end** and **0.8 mm between liner rims** keep the hard seating stops and rotary mechanism clear. Four shallow ramped TPU pads on the lid cup have **0.1 mm intended local interference** to help keep it seated, without tape. Their actual holding force is unmeasured. The leading body floor fits through the sleeve opening; the wider body walls still require a gentle pinch during installation. Do not force a reluctant cup.

The narrowest lined passage is **62.6 × 39.6 mm**, opening to **67.2 × 44.2 mm** in the main body. Clear length is **256.2 mm**. The 255 mm toothbrush has little spare length; a nominal 40 mm-thick toothpaste tube may need slight deformation through the mouth. Simultaneous packing remains a physical check.

![Installed outline and enlarged L20 wall section](renders/rotary_l20/liner_sections.png)

[Editable section SVG](renders/rotary_l20/liner_sections.svg).

## Print status and evidence

| Item | Status | Evidence / next observation |
| --- | --- | --- |
| L20 small damping cups | **Yes — walls/damping preferred; floor unresolved** | [User print comparison](../tpu_damping_box/notes/thin_gap/README.md#physical-feedback--2026-10-21): damping like L18/T08, preferred thickness/finish. |
| Rotary L20 full liner | **Partial — canceled for interior-floor defects** | [Raw STEP](rotary_l20_liner.step) / [STL](rotary_l20_liner.stl); early wall regions look okay; floor surface breaks/cracks. Do not repeat the full print unchanged. Tall-wall completion and installation remain untested. |
| Old M1 S16 full liner | **Printed — damaged / rejected** | Both skins broke locally and damage increased during insertion. Historical record below. |

[Current CAD/slice records and limits](notes/rotary_l20.md#verification-and-limits). The old S16 observations remain historical evidence, not acceptance of these new taller cups.

## Historical M1 S16 liner — retained evidence

The following dimensions, print reports and receipts describe the old M1 retrofit. The R2/T08/L20 experiments mentioned here are now complete; the current rotary adaptation is above. Historical recommendations to wait for R2 are superseded.

That earlier liner fitted the **264 × 74.2 × 51.2 mm** M1 shell, with **183.4 mm body / 75.4 mm cap** inserts. Its [original entry point](dental_travel_case_liner.py), [design source](design.py), [process](profiles/tpu-s16-0p2-process.json) and [cutaway](renders/assembled/inspection_isometric.png) are retained for identification and historical reproduction.

## Design & Geometry Summary

<a id="intent"></a>

### Intent & Starting `S16` Profile
On 2026-10-16, the user requested a sound-damping liner for the printed `M1` slim dental box and confirmed there was enough room to use the full **`S16`** sandwich profile ([approved in the TPU damping box study](../tpu_damping_box/README.md#s16--s12-print-feedback--2026-10-16)):
- **Sandwich structure:** `0.4 mm` shell-facing backing + `0.8 mm` air core + `0.4 mm` contents-facing skin (`1.6 mm` total thickness), supported by **`0.9 mm` straight ribs at `≤ 4.4 mm` pitch** (`~3.5 mm` open channels).
- **Note on rigid box closure:** This soft insert cushions contents inside the `M1` shell; it does not fix `M1`'s weak cap retention (which is addressed separately by the [`30 mm` short-lap dental case](../dental_travel_case/README.md)).

### Key Dimensions & Clearances
- **Clearances:** `0.2 mm` per-side lateral installation clearance; `0.2 mm` reserved at each closed end for optional thin double-sided tape; `0.8 mm` axial gap between the two liner rims at the seam (`Z = 185.6` to `186.4 mm`).
- **Print heights:** Body insert is **`183.4 mm`** tall (`Z = 2.2–185.6 mm` assembled); cap insert is **`75.4 mm`** tall (`Z = 186.4–261.8 mm` assembled).
- **Internal lined space:** `66.6 × 43.6 mm` in the main lower body; `61.5 × 38.5 mm` in the overlap sleeve (`51.5 mm` between the indented internal catch-guard detours).
- **Corner core preservation:** Sleeve corners use an inner **`R3.0 mm`** radius (rather than following the rigid shell's tight `R1.45 mm` bend) so curved corner air channels remain open rather than filling solid with rib material.

<a id="installation"></a>

### Installation & Reference Print Setup
1. **Print setup (for reference):** Both cups sit closed-end down, openings up (cap at `X = +82 mm`), `0.4 mm` nozzle, `0.2 mm` layers ([layer-height correction](../tpu_damping_box/README.md#actual-liner-layer-height-correction--2026-10-16)), 2 walls, 100% rectilinear fill (CAD voids form the air channels), **supports OFF**. For upward floor contact surfaces, `50%` ironing flow is the starting trial setting from the [sunglasses liner coupon](../sunglasses_case_liner/README.md#ironing-flow-print-feedback--2026-10-16).
2. **Installation:** With the rigid `M1` halves separated, gently fold/collapse the flexible TPU walls past the narrower sleeve mouth and catch guards, then unfold to seat against the walls (optional `≤ 0.2 mm` removable double-sided tape under the end backing; never tuck TPU into the rigid snap channels).

---

## Physical Print Feedback & Failure Diagnosis (Oct 19–20, 2026)

<a id="wall-print-feedback--2026-10-19"></a>
<a id="installation-breakage--2026-10-20"></a>

### 1. As-Printed Wall Breakage (2026-10-19) & Installation Breakage (2026-10-20)
- **What broke:** Both the interior (contents-side) and exterior (shell-side) `0.4 mm` vertical skins showed locally broken areas after printing (2026-10-19), and **broke further while being pushed into the tight `M1` dental box** (2026-10-20).
- **Comparison with the working Sunglasses Case Liner:**
  | Feature | Dental Travel Case Liner (Broke) | Sunglasses Case Liner (Worked cleanly) |
  | --- | --- | --- |
  | **Sandwich & Ribs** | `0.4 / 0.8 / 0.4 mm`, `0.9 mm` ribs at `≤ 4.4 mm` pitch | Identical (`0.4 / 0.8 / 0.4 mm`, `0.9 mm` ribs at `4.4 mm` pitch) |
  | **Cup Print Height** | **Body `183.4 mm`, Cap `75.4 mm`** | **Both `30.8 mm`** |
  | **Wall Geometry** | Split into height zones by `0.4 mm` solid bands; concave catch-guard detours, sleeve step, and deep narrow insertion path | Uniform vertical walls (`30.8 mm` tall); open drop-in clamshell tray |
  | **User-Recalled Speed / Flow Setting** | `9 mm³/s` max volumetric speed (`0.4 mm` nozzle / `0.2 mm` layers) | Recalled `80 mm/s` speed setting on earlier print (`~6.4 mm³/s` at `0.4 × 0.2 mm`) |

- **Why the cause was not simple channel width:** The nominal air channel width (`3.5 mm`) is identical in both liners, and vertical walls build layer-on-layer rather than bridging horizontally. However, the dental liner is **6× taller (`183.4 mm` vs. `30.8 mm`)**, has concave guard detours, and must be folded/pushed past a narrower sleeve mouth during installation.
- **Next step taken:** Rather than guessing or immediately re-printing a 22-hour tall liner, the user authorized the **[R2 Wall-Support Experiments (`A16`, `A20`, `B08`, `B16`)](../tpu_damping_box/README.md#ordinary-classic-repair--r2)** in `model/tpu_damping_box/` (`0.5 mm` skins, square frames vs. staggered ties, ordinary Classic slicing without Arachne).

---

## Print Status, Verification & Attribution

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| **Test pieces** | N/A — see [`model/tpu_damping_box/`](../tpu_damping_box/README.md) | S16 baseline approved; R2 support coupons (`support_A16`..`B16`) ready to print | Small R2 coupons test Classic wall continuity and installation survival before revising this tall liner. |
| **Final printable object** | **Printed — Rejected / Damaged** (2026-10-19 & 2026-10-20) | `dental_travel_case_liner.step` / `.stl` | Both inner and outer wall skins locally broken as printed; broke further during insertion into the old `M1` box. Wall and installation integrity not accepted; awaiting R2 support coupon results. |

### Digital Verification, Full Agent Logs & Receipts
- **Full Historical Agent & Engineering Log:** [`notes/development_record.md`](notes/development_record.md) (preserves the complete verbatim phase-by-phase engineering and print-feedback record; write detailed future agent logs here).
- **Automated Checks:** `./execute.py model/dental_travel_case_liner/verification.py --variant slim-m1-s16` checks CAD fit, catch clearance, continuous `S16` skins, and corner air cores ([`notes/verification.json`](notes/verification.json), [`notes/inspection.json`](notes/inspection.json)).
- **Slicer & Path Receipts:** OrcaSlicer 2.4.2 smoke slice (`0.2 mm` layers, `0` notices, estimated `80.50 g` / `21 h 58 m` at the old `4 mm³/s` cap; [`notes/final_review.json`](notes/final_review.json)) and 56-region toolpath review (`≥ 0.577 mm` skin separation, `≥ 2` rib tracks; [`notes/path_review.json`](notes/path_review.json), [`renders/path_review.png`](renders/path_review.png)). Historical `0.1 mm` draft receipt before the guard-ramp fix is preserved in [`notes/initial_0p1_review.json`](notes/initial_0p1_review.json).
- **Lesson:** Passing CAD and Arachne toolpath-presence checks did **not** guarantee physical thin-wall continuity or installation survival on a `183 mm` tall flexible print.

<a id="attribution"></a>

### Attribution
- **Model & Verification:** Primary model GPT-6 family (exact runtime ID and reasoning effort not exposed); Codex shared-workspace agent; provider OpenAI; no subagents.
- **Licensing:** Geometry and scripts are MIT-licensed; derived Orca process profile in [`profiles/`](profiles/ATTRIBUTION.md) is [AGPL-3.0](profiles/LICENSE.txt).
