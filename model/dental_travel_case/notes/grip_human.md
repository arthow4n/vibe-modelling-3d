# Three-line case with wraparound grips

> **Navigation:** Back to the main [**Dental Travel Case README**](../README.md).

**Selected grip design:** Two smooth full-wrap bands — **cap centre `+55 mm`, body centre `-30 mm` from the seam**, each **`20 mm` wide and `0.7 mm` deep**. The cap band sits beyond the joint backing with room toward the closed end; the body band lets the lower hand support the case while the upper hand lifts the cap. Printed grip feel is a physical observation during use, not an open layout calculation.

**Print this version:** [STEP — matching body and cap](../short_lap_case_three_line_grip.step)
· [STL](../short_lap_case_three_line_grip.stl)
· [Python entry point](../short_lap_case_three_line_grip.py).
The 2 mm version and earlier thin pair are retained unchanged.
[Actual finished CAD sections](grip_human/finished_band_sections.svg)
([PNG](grip_human/finished_band_sections.png)) show the continuous thin shell;
[print-placement preview](../renders/print/grip/short_lap_case_three_line_grip_isometric.png)
shows the separate named body and cap.

[Selected opening sequence — SVG](grip_human/selected_opening.svg)
([PNG](grip_human/selected_opening.png)) shows the supported half, moving half
and useful curved shoulders. [Location comparison](grip_human/placement_comparison.svg)
([PNG](grip_human/placement_comparison.png)) explains the alternatives.
Contact ovals are schematic suggested zones, not simulated anatomical hands.

## User direction

The user selected recessed saddles, accepted exploration of a shallow smooth
full-wrap band, and requested investigation of useful hand placement with
recorded visualizations. They specified **upright/diagonal opening because the
toothbrush must not fall out**. The lower hand supports the body; the upper
hand lifts the cap. The latest feedback rejects treating an unsuccessful
optional computation as an inconclusive product decision and requests a
practical conclusion and a lasting workflow correction.

The user has not supplied numerical hand-force or comfort thresholds. The
band size, location and comparison criteria are engineering choices. The latest
instruction authorizes implementing this design **only in the three-line
version**, since the user does not expect to print the 2 mm case. Earlier
instructions authorize removal of the unhelpful seam finger notches.

## Why this location

The selected cap band spans **+45 to +65 mm**. The sleeve ends at +30 mm;
the exterior backing blend ends at +39 mm. That leaves **15 mm beyond the
sleeve and 6 mm beyond the backing**, while retaining **25 mm to the cap's
closed end** (21 mm before its nominal 4 mm end-round region). The previous
+50 mm centre was geometrically clear, but left only 1 mm beyond the backing.
Moving it up 5 mm buys more separation from that blend without pushing the
band to the cap tip. Six millimetres is the resulting nominal distance, not a
new mandatory safety allowance.

The body band spans **−40 to −20 mm**, leaving **20 mm to the seam**. It
gives the supporting hand a zone on the main body rather than over the guide
walls. The two band centres are **85 mm apart**, with **65 mm between their
nearest edges**. These are band dimensions, not a claim that complete hands
occupy only 20 mm or never touch. The other fingers can wrap or rest farther
along their own part. Full wrap permits the person to choose faces and corners;
there is no need to land four particular fingertips on predefined points.

| Layout | Cap/body centres | Cap band beyond backing | Cap band to closed end | Decision |
| --- | --- | --- | --- | --- |
| Near | +40 / −15 mm | −9 mm: overlaps backing | 40 mm | Discard: conflicts with the existing exterior blend |
| Previous | +50 / −30 mm | 1 mm | 30 mm | Viable; revised to give more room from the blend |
| **Selected** | **+55 / −30 mm** | **6 mm** | **25 mm** | **Implemented in the new thin pair** |
| Far | +65 / −50 mm | 16 mm | 15 mm | Viable alternative; consumes more cap-end space without a demonstrated need |

This is a reasoned selection among usable alternatives, not a claim of a
unique ergonomic optimum. The depth/profile choice and local interior cost
remain in the [shape comparison](wall_comparison.md#continuous-band-and-shallow-profile):
the inner and outer skins move inward together to retain nominal wall
thickness. The resulting thin-wall interior at the band's flat regions is
70.4 × 47.4 mm. Finished-corner construction and actual passage are checked below.

## Implemented three-line case

[The builder](../short_lap_grip.py) reuses the original thin pair, restores the
cap-rim material removed by the old front/back notches, and replaces each grip
zone with a continuous recessed shell. The end-wall catch pockets and runouts
lie outside the notch-restoration cut and remain unchanged. The old 2 mm and
thin builders/exports are preserved; the new wrapper has the explicit
`_three_line_grip` filename so it cannot be confused with the old trial.

Both skins follow **exact quintic Bezier ramps**, with zero slope and curvature
at their joins. Rounded corners use the same radial profile. Each horizontal
wall section remains **1.2 mm**, verified in 66 actual CAD sections across faces,
corners, ramps and joins. Normal thickness on the sloping ramp falls slightly
to approximately **1.172 mm**; “1.2 mm” describes the horizontal section that
determines extrusion count, not a constant normal offset everywhere.

The joint-region symmetric differences against the previous thin case are zero
for the body guide/catches and both cap end-wall receiver regions. The hard
seat, both snap obstructions and guide path remain present. Sampled opening
positions 0…90 mm have no guide interference; snap geometry clears after 6 mm.
This preserves geometric function without inferring unchanged elastic stiffness
or a measured release force.

Individual passage gauges clear the narrowed shell: the 30 mm brush-handle
gauge at its retained offset has at least **3.1 mm body / 3.7 mm cap-band
clearance**; the 55 × 40 mm tube gauge has **1.8 / 3.7 mm**, respectively.
This checks the new band apertures and body passage, not simultaneous packing
of both actual items. Cap-band gauges stop before the intentionally closed roof.

**Print placement:** body upright on its base, 204 mm high including the sleeve;
cap on its closed roof, 90 mm high, beside the body. STEP and STL use this same
millimetre placement, with separately named components. Select just the cap in
STEP if desired. Use the retained Q2C PETG profile: 0.4 mm nozzle, 0.2 mm layers,
three walls, automatic 5 mm brim. The 1.2 mm floor/roof remain six nominal layers.

The maximum outward increment at a band is approximately **0.044 mm per 0.2 mm
layer**, leaving substantial support from the preceding wall. Closed-end feet,
R4 end rounds, backing blends and overlap are retained. OrcaSlicer 2.4.2 accepted
the delivered layout with no notices and no generated automatic supports.
Native toolpaths show **three strokes** with continuous coverage through both
landings and ramps: body print Z 137/144/151 mm, cap 28/35/42 mm. Estimated pair
mass is **108.54 g** in this profile. This STL review does not qualify Orca's
separate GUI STEP importer or predict printed grip feel.

- [Actual CAD checks](grip_human/finished_checks.json).
- [Native export/slice report](grip_human/finished_slice.json).
- [Export association and toolpath sections](grip_human/finished_publication.json).
- [Printable-case verification](grip_human/finished_verification.json): CAD and
  publication checks PASS; print observations remain separate.

Print the matched thin pair and use the bands during upright/diagonal opening.
Check grip feel, actual contents passage, cap fit and snap return. No separate
coupon or additional numerical investigation is required before this full-case trial.

## How the hands use it

1. Keep the case upright or modestly diagonal, with the body underneath.
   Wrap the lower hand around the body band; let the other fingers support
   the body wherever they naturally land.
2. Pinch or wrap the cap band with the other hand. The cap's **upper curved
   shoulder** gives a surface to press against while pulling upward. The body's
   **lower curved shoulder** provides the opposite bearing direction. The
   selected G2 profile has two smooth 6 mm ramps and an 8 mm central landing.
3. Lift the cap along the case axis while keeping the body supported. The
   grip zones move farther apart: their edge gap is **65 mm + cap travel**.
   At 6 mm lift it is 71 mm; at 30 mm it is 95 mm. The zone layout therefore
   introduces no need to switch grips during the initial release or sleeve exit.
4. Continue lifting past the contents. A 30 mm lift clears the nominal sleeve
   length but can leave the toothbrush inside the cap. At **90 mm lift**, the
   cap mouth reaches the old closed top, so that axial travel clears contents
   that were fully enclosed. The body and lower hand stay underneath throughout.

That last result follows from the 90 mm cap length; it is a nominal opening
walkthrough, not a new collision simulation or prediction of snap force. The
shallow ramp supplies a bearing direction, with traction also depending on skin
and print surface. Actual pull effort and comfort remain unmeasured. Those
limits do not prevent selecting this layout.

## Decision evidence

[The layout calculation](../grip_placement.py) uses the external dimensions from
the same constructor and 30 mm overlap as the thin builder; the local backing
end is `lap + 9 mm` from that builder's axial pad blend. It checks bands against
the sleeve, backing, end-round regions and seam, and calculates the prescribed
opening positions. This earlier layout calculation is supplemented by the
finished-CAD and publication evidence above.

- [Current dimensions and alternative results](grip_human/layout.json).
- [Current shared verification report](grip_human/verification.json):
  **grip.layout PASS**, scoped to nominal placement and prescribed motion.
  Printed usefulness remains a physical question; inherited product requirements
  remain visible. The implemented case has its separate report linked above.
- [Historical native-hand investigation](grip_human/native_search.md), including
  replayable anatomy, unsuccessful poses, source/tool identities and its old
  verification report. Its results are preserved without turning them into
  passing grasps or product failure.

Reproduce the layout exploration from the repository root:

```sh
./execute.py --threads 1 model/dental_travel_case/grip_placement_diagram.py
./execute.py --threads 1 model/dental_travel_case/verification.py --variant grip-band-placement
```

For the implemented case, run `short_lap_grip_checks.py` through `./execute.py`,
evaluate/export the `_three_line_grip.py` wrapper with the retained three-profile
slice setup, then run `short_lap_grip_publication.py`. Select
`--variant slim-short-lap-three-line-grip` in the shared verification CLI.

The layout verifier recomputes the layout; it does not trust `accepted` flags in the
saved JSON. Regression controls include a band overlapping the backing, a
band reaching the cap-end round, an invalid body position, and preservation
of the user requirement when the verification strategy changes.

## Working-approach correction

The previous study used a precise, simultaneous four-contact rigid-skin grasp
as the answer to a broad band-location question. It fixed wrist coordinates,
selected distal-capsule contacts and required point/normal tolerances. Those
were agent choices, not user requirements. Real use permits different digits,
proximal contacts, distributed soft-skin contact and freely chosen positions
around the band. We have not established which factor caused the optimizer
failure; we **have** established that its narrow success criterion was not
necessary to choose a useful exterior zone.

Stopping the search but still presenting placement as inconclusive did not
correct that mismatch. This revision changes the active verification strategy
and delivers the missing use walkthrough and selected location. It does not
loosen the native model's screens or rename its unsuccessful result PASS.

The transferable lesson belongs in method selection: identify the decision
before selecting the calculation, test only what can change that decision,
and retire a mismatched agent-created question while preserving user intent
and historical results. A useful design choice can be complete without claiming
a measured force, physical trial or universal optimum. The human-interaction
skill now explicitly distinguishes broad grip layout from precise reach/contact
problems. This is implemented in the current consumer, not just a reminder to
“be practical.”

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test pieces | N/A | No separate coupon; full matched pair provided | User can choose only the cap from STEP |
| Final printable objects | Unknown | `short_lap_case_three_line_grip.step/.stl` | No user print report yet; compare grip feel, actual contents, cap fit and snap return |

Primary model: GPT-6; exact runtime variant and reasoning effort not exposed.
Harness: Codex in the shared local repository. Provider: OpenAI. No subagents.
Historical attribution and MyoSim evidence remain in
[the retained investigation](grip_human/native_search.md).
