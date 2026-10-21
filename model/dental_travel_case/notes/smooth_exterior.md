# Smooth exterior exploration

Discuss the [closed-shape comparison](../renders/concepts/smooth_exterior_comparison.svg) and [enlarged grip / catch sections](../renders/concepts/smooth_exterior_details.svg) before changing the printable case. PNG previews accompany both SVGs. These are editable schematic proposals, not CAD projections or new printable variants. The existing three-line files retain their previous digital evidence, but printing is on hold for this appearance discussion. No new print result was reported.

The user reviewed the unprinted three-line wrap-grip case and found the exterior too conspicuously interrupted. They proposed keeping only the useful side of the body grip, making the remaining upper surface straight, reducing or removing the cap band, and exposing some recessed overlap as a natural grip. A small body/cap size difference is acceptable to explore; neither a dimension nor a design was selected. “Button case” is interpreted here as the bottom/body piece. Flat means a continuous side profile with the established rounded corners and ends retained.

| Drawing | Exterior change | Unresolved consequence |
| --- | --- | --- |
| NOW | Existing 0.7 mm recessed wrap bands and 0.65 mm local cap backing pads | Existing physical grip, retention and loaded packing remain untested. |
| A | Body has one lower shoulder, then stays about 0.4 mm inset per side up to the seam; cap band removed, catch pads retained | Insetting the body needs a deliberate transition into the sleeve. Smooth-cap grip and any packing loss need review. |
| B | Both bands removed; shorten the cap rim to expose about 3 mm of the continuous sleeve | The shallow collar may give little finger purchase. Shortening the rim must preserve the catch position and useful guidance. Pads still interrupt the cap outline. |
| C | B's seam reveal plus a continuous cap envelope out to the old pad maximum; align body exterior to it | About 1.3 mm extra nominal width (75.5 rather than 74.2 mm) if using the outward route; affected cap end walls become about 1.85 mm away from recesses. Changed wall stiffness affects the snap. Other walls can remain 1.2 mm. |

C is the agent's suggested starting direction for discussion, not a user selection. The second sheet also shows an inward alternative: keep the original exterior size and move the sleeve/catches inward. That is a mating-region redesign, not simple uniform body scaling, and may reduce contents clearance. Do not shrink the whole body without preserving brush and toothpaste space.

The cap's raised pads are not grip decoration. `short_lap_thin.py` adds 0.65 mm locally so the recess/runout retains 1.2 mm of backing. Removing this material alone would leave about 0.55 mm. A flat exterior must carry that thickness across a larger area, relocate the mating geometry inward, or adopt another justified catch design. There is no basis here for claiming that a smaller catch alone retains the previous retention behavior.

The comparison uses the current 264 mm closed length, 174 mm body seam, 90 mm cap and 74.2 mm nominal width as its visual baseline. B/C illustrate a shortened cap rim while keeping the roof at the same height, not lifting the existing cap out of its seated catch. Their visible overlap remains an inner sleeve, not a hole into the case; this is not a sealing claim. Colors distinguish body, cap and visible sleeve made from the same PETG. Detail depths are exaggerated for legibility.

Before developing a selected direction, check the affected catch seat and release path, sleeve guidance/overlap, wall thickness and contents space. Any new printable geometry needs its own affected CAD/print evidence. Grip effectiveness and feel remain physical questions. No new CAD, simulation or slice was warranted for this drawing phase.

## Phase evidence and attribution

- Both SVGs parsed and rendered through the locked CairoSVG dependency; both PNGs were visually inspected for legibility and intended differences.
- Test-piece print status: N/A — SVG-only exploration. Final-object print status for these proposals: N/A — no printable revision. The previous three-line pair remains Unknown / unprinted.
- Primary language model: GPT-6 family; exact model identifier and reasoning effort not exposed. Harness: Codex coding-agent environment. Provider: OpenAI. New drawings and interpretation are agent-authored from the current source and user feedback; historical model attribution remains in the existing records.
