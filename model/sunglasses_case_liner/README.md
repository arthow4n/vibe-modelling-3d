# S16 TPU Damping Liner for the Printed Sunglasses Case

Two identical flexible TPU 95A cups (`157.6 × 77.6 × 30.8 mm` each) that line both halves of the printed [Variant E sunglasses case](../sunglasses_case/notes/printing_and_design.md) using the `1.6 mm` **`S16`** ribbed air-core damping profile across the floor, straight walls, and all four rounded corners.

![Retained solid corner left; current revised corner right](renders/corner_study/corner_study_top.png)

---

## At a Glance: Current Status & What to Print

- **Current Status:** **PRINTED, WORKING & ACCEPTED (2026-10-17 / 2026-10-19)**
  - **User result:** Fits cleanly inside the printed Variant E sunglasses case, damps rattling well, and has **no wall breakage** (unlike the much taller dental liner). No further geometry changes are needed.
- **Files to Print:**
  - **Full two-cup liner:** [`sunglasses_case_liner.step`](sunglasses_case_liner.step) · [`sunglasses_case_liner.stl`](sunglasses_case_liner.stl) · [Python source](sunglasses_case_liner.py)
  - **Optional `18.5 × 18.5 mm` ironing test coupon:** [`bottom_sample_18p5mm.step`](bottom_sample_18p5mm.step) · [`bottom_sample_18p5mm.stl`](bottom_sample_18p5mm.stl) · [Python source](bottom_sample_18p5mm.py) (printed and used to select `50%` ironing flow; no need to reprint unless testing a new TPU spool).
- **Recommended Slicer Setup:**
  - **Material & Layers:** TPU 95A ([`../tpu_damping_box/profiles/tpu95a.json`](../tpu_damping_box/profiles/tpu95a.json)), `0.4 mm` nozzle, **`0.20 mm` layers** (including first layer).
  - **Process:** [`../tpu_damping_box/profiles/tpu-closed-process.json`](../tpu_damping_box/profiles/tpu-closed-process.json) — Arachne, 2 walls, 100% rectilinear fill (CAD voids form the air channels), thin bridges, `180°` bridge angle, **supports OFF**.
  - **Top-Surface Ironing:** Enable top-surface ironing at **`50%` ironing flow** (established by the printed coupon comparison below).

---

## Design & Geometry Summary

<a id="intent"></a>

### Intent & Corner Air-Core Upgrade
After approving the **`S16`** damping profile in the [TPU damping box study](../tpu_damping_box/README.md#s16--s12-print-feedback--2026-10-16), the user requested a full two-cup liner for the printed Variant E sunglasses case (`158 × 78 × 63 mm` interior, `R7 mm` inner corners).
- Before printing the first draft (`60784df`), the user noticed its rounded corners were solid TPU and asked for air channels through the corners as well.
- The current design adds **three curved vertical air pockets and radial `0.9 mm` ribs (`30°` sector pitch) around each of the four corners** (12 corner pockets per cup) while keeping the outer envelope and clearances unchanged.

| Feature | Dimension / Specification |
| --- | --- |
| **Cup exterior & clearances** | `157.6 × 77.6 × 30.8 mm`, `R6.8 mm` outer corners (`0.2 mm` per-side lateral clearance, `0.2 mm` backing allowance for thin tape, `0.5 mm` below each rigid rim leaving a `1.0 mm` unpinched seam gap) |
| **Remaining lined interior** | `154.4 × 74.4 × 59.4 mm` |
| **Floor & wall sandwich (`S16`)** | `0.4 mm` shell backing + `0.8 mm` air core + `0.4 mm` inner contact skin (`1.6 mm` total) |
| **Straight-wall & floor ribs** | `0.9 mm` wide ribs at `4.4 mm` pitch (`3.5 mm` open channels); floor ribs run across the short axis with `180°` bridges crossing them |
| **Curved-corner pockets** | 3 curved vertical pockets per corner (`30°` pitch, `~3.14 mm` arc spacing, `≥ 0.9 mm` radial rib chord), closed at the top by a `0.4 mm` cap |

<a id="installation"></a>

### Installation
1. Print both cups backing-down, openings up (`157.6 × 161.2 × 30.8 mm` combined plate). Remove any stringing and clean the inner contact surfaces.
2. Dry-fit each cup into one half of the Variant E sunglasses case; each rim sits `0.5 mm` below the rigid seam lip so the latch closes without pinching.
3. For the upper lid cup (and optionally the base), apply small perimeter strips of **thin removable double-sided tape (`≤ 0.2 mm` thick)** under the flat backing. Do not use thick foam tape.

---

## Physical Print Reports & Lessons

<a id="full-liner-print-feedback--2026-10-17"></a>

### 1. Full Liner Print Report (2026-10-17 & 2026-10-19 Comparison)
- **Fit & Damping (2026-10-17):** The user printed the full sunglasses-case liner and reported that it **fits inside cleanly, provides good damping, and works well with no problems**.
- **Wall Integrity Comparison (2026-10-19):** When the taller [dental travel case liner](../dental_travel_case_liner/README.md#wall-print-feedback--2026-10-19) (`183.4 mm` tall) later exhibited local wall-skin tears, the user confirmed this `30.8 mm`-tall sunglasses liner had **no wall breakage**, recalling an `80 mm/s` speed setting on this earlier print.

<a id="ironing-flow-print-feedback--2026-10-16"></a>

### 2. Bottom-Panel Ironing Coupon (`bottom_sample_18p5mm`) & Flow Selection (2026-10-16)
To test top-surface ironing over `S16` bridged air channels without printing a full case liner, we created an **`18.5 × 18.5 × 1.6 mm` rib-bounded crop** of the actual liner bottom ([`bottom_sample_18p5mm.step`](bottom_sample_18p5mm.step) / [`.stl`](bottom_sample_18p5mm.stl), trimmed flush to the outer faces of two complete ribs so there are no unsupported `0.75 mm` edge lips; verified by [`inspect_sample_exports.py`](inspect_sample_exports.py)).

The user printed the sample at **`0.2 mm` layer height** across four **top-surface ironing flow** levels:

| Ironing Flow | User Observation on Printed Coupon | Decision |
| --- | --- | --- |
| `10%` (default) | Visible gaps remain between surface lines after ironing | Rejected |
| `30%` | Visible gaps remain between surface lines after ironing | Rejected |
| **`50%`** | **Described as "perfect" smooth top finish** | **Selected starting ironing flow for TPU `S16` skins** |
| `100%` | Top surface bulges/bumps upward instead of staying flat | Rejected |

*(Note: A later 2026-10-17 report on larger panels noted some remaining periodic waviness even at `50%` flow, which is being explored separately via the [`F0`–`F7` surface coupons](../tpu_damping_box/README.md#surface-finish-coupons--2026-10-17) in `model/tpu_damping_box/`.)*

---

## Print Status, Verification & Attribution

<a id="printing-and-manufacturing-review"></a>
<a id="corner-coverage-investigation--2026-10-16"></a>
<a id="print-status"></a>

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| **Test piece (Ironing coupon)** | **Yes — Printed & Accepted** (2026-10-16) | `bottom_sample_18p5mm.step` / `.stl` | Printed at `0.2 mm` layers. **`50%` ironing flow preferred ("perfect")**; `10%`/`30%` leave gaps; `100%` bulges upward. |
| **Final printable object (Full liner)** | **Yes — Printed & Accepted** (2026-10-17 / 2026-10-19) | `sunglasses_case_liner.step` / `.stl` | Fits cleanly inside Variant E case and damps well; confirmed free of the wall tears seen on the tall dental liner. Long-term wear and tape adhesion not separately rated. |

### Digital Verification, Full Agent Logs & Historical Receipts
- **Full Historical Agent & Engineering Log:** [`notes/development_record.md`](notes/development_record.md) (preserves the complete verbatim phase-by-phase engineering, corner-coverage, and print-feedback record; write detailed future agent logs here).
- **Automated Verification (`s16-retrofit`):**
  ```sh
  ./execute.py --threads 1 model/sunglasses_case_liner/verification.py --variant s16-retrofit
  ```
  Verifies `S16` profile dimensions, 36 corner air-pocket witnesses + 24 radial-rib witnesses (rejecting the historical solid-corner baseline in [`notes/corner_coverage_solid.json`](notes/corner_coverage_solid.json)), case installation/closing clearance, and sampled hinge opening ([`notes/verification.json`](notes/verification.json)).
- **Toolpath & Slice Receipts:** Retained `0.1 mm` diagnostic receipts ([`notes/final_review.json`](notes/final_review.json), [`notes/path_review.json`](notes/path_review.json), [`renders/path_review.png`](renders/path_review.png), [`renders/corner_paths.png`](renders/corner_paths.png), and sample receipts [`notes/bottom_sample_final.json`](notes/bottom_sample_final.json), [`notes/bottom_sample_paths.json`](notes/bottom_sample_paths.json)) verify open straight and curved corner air channels and multi-track ribs. Actual prints use the `0.2 mm` layer setup above ([layer-height correction](../tpu_damping_box/README.md#actual-liner-layer-height-correction--2026-10-16)).

<a id="attribution"></a>

### Attribution
- **Model & Verification:** Primary model GPT-6-based Codex (exact runtime variant and reasoning effort not exposed); Codex shared-workspace API agent; provider OpenAI; no subagents. Adapts the accepted [Variant E sunglasses case](../sunglasses_case/notes/provenance.md) and user-approved [`S16` TPU profile](../tpu_damping_box/README.md#attribution).
