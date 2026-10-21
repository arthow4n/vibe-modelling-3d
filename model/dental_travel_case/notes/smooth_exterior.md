# Smooth C travel case

C is implemented as a complete matching body/cap pair: [print STEP](../short_lap_case_smooth.step), [STL](../short_lap_case_smooth.stl), and [Python entry point](../short_lap_case_smooth.py). Use this pair for the next physical trial. The separate [closed STEP](../short_lap_case_smooth_assembled.step) is an inspection pose, not a print layout.

![Closed smooth C case](../renders/assembled/smooth/short_lap_case_smooth_assembled_isometric.png)

## Authorized C implementation

The user selected C after the SVG discussion and explicitly authorized remodelling with engineering judgment. Small dimension increases and more than three extrusion lines are acceptable; exact overall dimensions and a strict three-line wall limit are not requirements for this revision. This supersedes the earlier thin-only / three-line restriction for the selected C pair while preserving the historical files and their evidence. No new print result was reported.

The implemented exterior is `75.5 × 51.2 × 264 mm`: only width grows, by `1.3 mm`. Both main end walls are `1.85 mm`; broad walls and the sleeve remain `1.2 mm`. The original main-body cavity, sleeve, catch profiles and matching cap clearance are retained. The new cap's tapered stop locally reduces the upper cavity passage; actual individual brush/tube gauges still clear it by at least `2.8 mm`. The supplied item envelopes are not a simultaneous packing test.

There are no wrap bands, local exterior pads or seam finger notches. The cap rim ends `3 mm` above the body shoulder, leaving a continuous inner sleeve exposed with rounded opposing rim contacts. Cap coverage is `27 mm` over the unchanged `30 mm` sleeve. A continuous internal seat contacts the sleeve tip at `Z=204 mm`; this is necessary to stop the cap being pushed down until the exposed collar disappears. The seat projects inward `1 mm`, with a `1.5 mm` taper above it. It remains above the end catches and has no sampled opening-path interference.

![Actual CAD sections](../renders/assembled/smooth_case_sections.png)

### Verification and manufacturing

[CAD checks](smooth_case/cad.json) cover 20 actual outline/wall sections, unchanged sleeve and catch geometry above the collar, seated clearance, hard-seat contact, overclosing obstruction, six independent-catch obstruction witnesses across lateral play, 13 sampled axial poses, individual brush/tube passages and retained R4 handled ends. Numerical intersection screen: `1e-5 mm³`; individual passage screen: at least `0.8 mm`. The stop contacts within numerical tolerance and obstructs `0.1 mm` excess closing. No new force or impact analysis was run; the changed end-wall stiffness and stop invalidate transfer of historical force predictions.

[OrcaSlicer 2.4.2 review](smooth_case/print_review.json) passed with no notices and no generated support. The [source/export association](smooth_case/publication.json) uses the source snapshot taken before native evaluator publication, checks unchanged inputs afterward and identifies the delivered paired exports and slice receipt. STEP/STL came from the same selected geometry and placement; the native publication guards completed successfully. [Product verification](smooth_case/verification.json) preserves inherited user intent, records the latest wall/form authorization and leaves physical obligations UNKNOWN.

Print the body upright on its floor (`204 mm` tall), cap inverted on its roof (`87 mm` tall), with the established PETG / `0.4 mm` nozzle / `0.2 mm` layers / 3 configured loops / `7%` adaptive cubic / `5 mm` automatic brim process. The width change stays well inside the Q2C layout envelope; the selected-profile slice accepts the paired placement. The broad walls remain the previously qualified nominal thickness; thicker end walls need no strict path-count promise. The R4 end blends retain the established chamfered bed-contact foot. The cap seat grows inward by `1 mm` over `1.5 mm` of print height (about `0.13 mm` radial movement per `0.2 mm` layer), then ends in its sleeve-bearing face. The small snap ramps/runouts retain the earlier geometry and print directions. No trapped supports or new unsupported islands are planned; the automatic-support probe generated none. Exterior/rim rounding preserves the functional sleeve and catch surfaces.

The STL review does not qualify Orca's separate GUI STEP importer. Actual seam-grip purchase, snap closing/opening effort, recovery and durability, stop seating under hand pressure, simultaneous loaded packing and bag-bump retention need a physical trial. A shallow collar is not a claim of reliable finger purchase or sealing. Keep the body underneath when opening so loose contents remain supported.

## Earlier SVG exploration (historical)

The [closed-shape comparison](../renders/concepts/smooth_exterior_comparison.svg) and [enlarged grip / catch sections](../renders/concepts/smooth_exterior_details.svg) record the alternatives before C was selected. PNG previews accompany both. They are schematic proposals; the actual CAD sections above govern the implemented geometry.

The user reviewed the unprinted three-line wrap-grip case and found the exterior too conspicuously interrupted. They proposed keeping only the useful side of the body grip, making the remaining upper surface straight, reducing or removing the cap band, and exposing some recessed overlap as a natural grip. At the drawing stage, a small body/cap size difference was acceptable to explore; no dimension or design had yet been selected. “Button case” is interpreted here as the bottom/body piece. Flat means a continuous side profile with the established rounded corners and ends retained.

| Drawing | Exterior change | Unresolved consequence |
| --- | --- | --- |
| NOW | Existing 0.7 mm recessed wrap bands and 0.65 mm local cap backing pads | Existing physical grip, retention and loaded packing remain untested. |
| A | Body has one lower shoulder, then stays about 0.4 mm inset per side up to the seam; cap band removed, catch pads retained | Insetting the body needs a deliberate transition into the sleeve. Smooth-cap grip and any packing loss need review. |
| B | Both bands removed; shorten the cap rim to expose about 3 mm of the continuous sleeve | The shallow collar may give little finger purchase. Shortening the rim must preserve the catch position and useful guidance. Pads still interrupt the cap outline. |
| C | B's seam reveal plus a continuous cap envelope out to the old pad maximum; align body exterior to it | About 1.3 mm extra nominal width (75.5 rather than 74.2 mm) if using the outward route; affected cap end walls become about 1.85 mm away from recesses. Changed wall stiffness affects the snap. Other walls can remain 1.2 mm. |

C was the agent's suggested starting direction in the drawing phase; the later authorization above selects it. The second sheet also shows an inward alternative: keep the original exterior size and move the sleeve/catches inward. That is a mating-region redesign, not simple uniform body scaling, and may reduce contents clearance. Do not shrink the whole body without preserving brush and toothpaste space.

The cap's raised pads are not grip decoration. `short_lap_thin.py` adds 0.65 mm locally so the recess/runout retains 1.2 mm of backing. Removing this material alone would leave about 0.55 mm. A flat exterior must carry that thickness across a larger area, relocate the mating geometry inward, or adopt another justified catch design. There is no basis here for claiming that a smaller catch alone retains the previous retention behavior.

The comparison uses the current 264 mm closed length, 174 mm body seam, 90 mm cap and 74.2 mm nominal width as its visual baseline. B/C illustrate a shortened cap rim while keeping the roof at the same height, not lifting the existing cap out of its seated catch. Their visible overlap remains an inner sleeve, not a hole into the case; this is not a sealing claim. Colors distinguish body, cap and visible sleeve made from the same PETG. Detail depths are exaggerated for legibility.

Before developing a selected direction, check the affected catch seat and release path, sleeve guidance/overlap, wall thickness and contents space. Those questions are now addressed by the C records above where geometric. Grip effectiveness and feel remain physical questions. No CAD, simulation or slice was run during the earlier drawing phase.

## Phase evidence and attribution

- The proposal SVGs were parsed/rendered and both PNGs visually inspected. Implemented CAD print/closed views and enlarged actual sections were also visually inspected.

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test pieces | N/A | No new coupon | Full matching pair is the next trial. Historical joint samples remain recorded in the object README. |
| Final printable object | Unknown | `short_lap_case_smooth.step` / `.stl` | No reported print. Check seam grip, snap effort/return, internal seat, actual loaded packing and bag retention. Earlier wrap-grip pair remains Unknown / unprinted. |

- Primary language model: GPT-6 family; exact model identifier and reasoning effort not exposed. Harness: Codex coding-agent environment. Provider: OpenAI. New drawings, implementation and checks are agent-authored from the current source and user feedback; historical model attribution remains in the existing records.
