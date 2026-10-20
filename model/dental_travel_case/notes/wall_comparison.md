# Full-case print comparison: 2 mm and three-line walls

Two complete body/cap pairs are ready for a practical print comparison. The
existing thick model is preserved. The new thin pair has **1.2 mm ordinary walls**;
Orca actually generates **three extrusion strokes across them**, rather than
relying on the nominal nozzle diameter. Both pairs sliced without supports.
Neither has a reported physical result for this comparison.

![Wall sections, actual sliced strokes and material comparison](wall_comparison/comparison.svg)

[SVG](wall_comparison/comparison.svg) · [PNG](wall_comparison/comparison.png) ·
[Previous overlap/force investigation and physical history](short_lap.md)

## Choose a matching pair

| Complete case | Authoritative Python entry | STEP (primary print file) | STL |
| --- | --- | --- | --- |
| Preserved 2 mm control | [short_lap_case.py](../short_lap_case.py) | [short_lap_case.step](../short_lap_case.step) | [short_lap_case.stl](../short_lap_case.stl) |
| Three-line thin pair | [short_lap_case_three_line.py](../short_lap_case_three_line.py) | [short_lap_case_three_line.step](../short_lap_case_three_line.step) | [short_lap_case_three_line.stl](../short_lap_case_three_line.stl) |

Each export contains the complete body and cap, separated in print placement.
You can select only the cap in your slicer. **Use the thin cap with the thin body**:
their mating surfaces move together. The caps are not interchangeable with the
other version. Printing caps alone can compare flexibility, but testing fit and
retention requires the corresponding body.

## Authorized comparison

On 2026-10-20 the user questioned the material cost of 2 mm walls and requested
three extrusion lines instead, allowing a catch opening if needed. They asked
to retain the current iteration and deliver complete cases for both thicknesses,
so they can choose to print only the cap themselves. They clarified that total
width need not be exact, then selected **the same general outside size with a
matching thin body/cap pair**. These are user directions; 1.2 mm and local pad
dimensions are implementation choices checked below.

The finish line is two usable print candidates, checked for fit and actual sliced
wall construction. No new force or impact simulation is needed to deliver this
comparison. The prior side-hit investigation remains closed and inconclusive;
its results do not establish a safe bag-knock load for either pair.

## What changed and why

| Feature | Preserved control | Thin comparison |
| --- | --- | --- |
| Ordinary body/cap walls | 2 mm | 1.2 mm |
| Body overlap wall | 2 mm | 1.2 mm |
| Cap receiving band | 2.7 mm | 1.2 mm away from pads; 1.85 mm at uncut pads |
| Backing at pocket/runout peak | 2.05 mm | 1.2 mm at pad center |
| Floor and roof | 2 mm | 1.2 mm: six 0.2 mm layers |
| Overlap / bite / nominal guide gap per side | 30 / 0.6 / 0.1 mm | Same |
| Main exterior width × depth × length | 74.2 × 51.2 × 264 mm | Same |
| Maximum width at cap pads | 74.2 mm | 75.5 mm |
| Central sleeve mouth | 64.6 × 41.6 mm | 69.2 × 46.2 mm |

Simply thinning the existing cap would leave only 0.55 mm behind its catch
recesses and the long relief tracks. Instead, two small outside pads add 0.65 mm
per side over a 14 mm wide region, preserving 1.2 mm of backing at the deepest
cuts. They taper back into the shell above the overlap. This avoids cutting long
open slots or adding separate cantilever arms. Between recessed regions a pad
is intentionally thicker than three lines; the whole cap is not uniformly 1.2 mm.
The main thin builder is [short_lap_thin.py](../short_lap_thin.py).

The same small-bite wall-snap profile and recovery track remain. Thinner walls
will flex more easily; their printed holding force, return, rubbing and durability
are unknown. The old conditional 11.22 N pull estimate belongs to the reinforced
control geometry and must not be applied to the thin pair.

## Actual slicing and fit evidence

Both full pairs were sliced with **OrcaSlicer 2.4.2**, Qidi Q2C, 0.4 mm nozzle,
PETG, 0.2 mm layers, three wall loops and 7% adaptive cubic infill. The ordinary
wall is a narrow shell with two boundary contours: the three-loop setting does
not itself mean three lines total across that shell.

The actual paths contain five strokes in the 2 mm wall: two boundary lines, two
inner lines and a center gap-fill line. The 1.2 mm wall contains two boundary
lines and one center gap-fill line. This is **three total lines**, without sparse
infill between them. Boundary widths are 0.42 mm; the middle thin gap-fill line
is about 0.43 mm. Slicer spacing accounts for overlap between bead sections;
adding nozzle diameters is not the width calculation.

| Same-profile full-pair estimate | Control | Thin |
| --- | --- | --- |
| Filament | 183.27 g | 108.43 g |
| Print time | 5 h 2 m 21 s | 4 h 5 m 27 s |
| Saving | — | 74.84 g (40.8%); 56 m 54 s (18.8%) |

These are slicer estimates, not weighed prints. They include the full pair under
this profile. Different settings, caps alone and real printing can differ.

The focused checks passed:

- Thin body and cap fit seated without interference; each end catch independently
  obstructs a 1 mm opening even with ±0.1 mm sideways guide play.
- Sampled axial opening positions have no guide interference; from 6 mm lift
  onward the snap clears. Pushing below the seated position meets the hard stop.
- Individual brush/tube passage gauges clear, recessed grips remain accessible,
  and the actual R4 end surfaces remain. Integrated packing still needs the real
  items; individual gauges do not prove simultaneous loading.
- Actual sampled main body, main cap, sleeve, runout backing and pocket backing
  sections have five control strokes or three thin strokes. The path-width
  approximation leaves under 0.05 mm total uncovered width and under 0.01 mm
  internal gap at each section. These are local fill checks, not calibration of
  deposited polymer, bonding or every curved corner.
- Native evaluation/export succeeded for both; the original exports were reused
  unchanged. Both diagnostic slices and automatic-support probes succeeded,
  with no generated supports and no log notices.

Reproducible local inspection and SVG source:
[short_lap_wall_comparison.py](../short_lap_wall_comparison.py), run with
`./execute.py --threads 1 model/dental_travel_case/short_lap_wall_comparison.py`.
It reads the kept Orca runs identified in the receipts. The committed result is
[checks.json](wall_comparison/checks.json), including source/artifact hashes,
rigid capture/path results and actual section strokes.
Native slice receipts: [control](wall_comparison/control_slice.json),
[thin](wall_comparison/thin_slice.json).

Verification uses the shared interface, with explicit variants:

```sh
./execute.py --threads 1 model/dental_travel_case/verification.py --variant slim-short-lap-three-line
./execute.py --threads 1 model/dental_travel_case/verification.py --variant slim-short-lap
```

The thin plan preserves inherited user intent and physical unknowns while
replacing geometry-dependent evidence. No thick-shell numerical force or impact
claim is inherited. Current reports: [thin](wall_comparison/thin_verification.json),
[control](wall_comparison/control_verification.json).

## Print and compare

Use the same filament and settings for both versions. The exported body stands
on its bottom; the cap stands on its roof. Heights are 204 and 90 mm. Keep that
placement and the diagnostic profile's automatic brim for the tall body. Both
parts fit the selected Q2C layout. The R4 tangent feet and pad tapers were reviewed
for this orientation; the selected support probe generated no supports. The
1.2 mm floor/roof are layers across a closed end, not three horizontal wall lines.
Fit gaps, seams, shrinkage and layer adhesion still depend on the actual printer.
The CLI smoke slice used STL; it does not verify Orca's separate GUI STEP importer.

Compare how the broad walls feel in the hand, whether both bites return after
opening, and whether closing/rubbing/noise are acceptable. Inspect for whitening
or cracks around the pockets. Try the real packed items and ordinary handling.
This direct comparison can decide whether the saved material is worthwhile;
there is no new computational campaign queued before printing. Resistance to
travel-bag knocks and long-term closure life remain physical questions.

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | N/A | No additional coupon; user requested full cases | Cap-only selection is available in each paired export |
| Final printable object(s) | Unknown | `short_lap_case.step/.stl`, `short_lap_case_three_line.step/.stl` | No print report for these pairs; compare feel, fit, snap return, packed retention and wear |

## Handoff lesson and attribution

Actual toolpaths answered the thickness question directly: three configured wall
loops produced five total strokes in the control shell, while the thin shell
produced three. The catch recess required a local backing decision; it did not
justify keeping every wall thick. This evidence stays local to this geometry and
profile; it does not establish a universal minimum PETG wall or a new mandatory
solver/check workflow. Earlier practical stopping and explanation lessons remain
in [their existing owning records](short_lap.md#practical-stopping-and-explanation-feedback).

Primary language model: GPT-6 (exact runtime model variant and reasoning effort
not exposed). Harness: Codex agent, shared local repository; provider: OpenAI.
No subagents contributed to this comparison. Historical model attribution remains
in [short_lap.md](short_lap.md#attribution). Existing Orca process profile attribution
and AGPL-3.0 licensing remain in [profiles](short_lap/profiles/ATTRIBUTION.md);
no third-party geometry was added.
