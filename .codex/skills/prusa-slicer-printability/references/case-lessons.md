# Verified case lessons

These are scoped observations, not universal printability limits.

## Long bridge-role paths can lie over internal infill

In the revised flat case, a diagnostic profile with 6 top and 6 bottom layers
at 0.2 mm left a sparse infill band inside the 3 mm floor. At Z=2.0 mm,
PrusaSlicer emitted bridge-role paths up to about 184 mm long over that infill,
without the earlier long-bridge warning. Their full length was not an empty
span. Inspect preceding material before classifying such paths as failures.

Using 8 top and 8 bottom layers made those 3 mm panels solid throughout; the
final case and coupon had no Bridge infill or support roles and no stability
warnings. That setting is specific to these panel thicknesses and layer height,
not a general instruction to eliminate all infill or bridge roles. Evidence:
[flat-print review](../../../../model/sunglasses_case/notes/support_free_review/report.md).

## Recorded case: standing sunglasses case

Evidence: [report](../../../../model/sunglasses_case/notes/slicer_review/report.md)
and [measurements](../../../../model/sunglasses_case/notes/slicer_review/measurements.json).
The tested geometry and analysis are retained in Git at `9b8af79`; future model
revisions may no longer reproduce these numbers.

With supports disabled, PrusaSlicer explicitly reported:

> Detected print stability issues:
> Long bridging extrusions
> Consider enabling supports.

At Z=171.2 mm, the upper cavity wall closed with `Bridge infill` segments up to
87.186 mm long, including anchors. Mapping that layer back to the standing case
identified the overhead wall. The completed G-code therefore supplied evidence
against accepting that orientation for the user's no-support requirement.

The support comparison added support/interface paths below the wall. It still
used bridge-role paths at Z=171.2 mm, illustrating why role labels need spatial
context. It was a diagnostic comparison, not an approved support-based solution.

## Clean slicing does not prove clean mesh topology

The rounded sunglasses hinge exported a few degenerate triangles at exact cone
apices even though its CAD solids were valid and PrusaSlicer emitted no warning.
Small flat tips eliminated the degenerate facets; final exported meshes were
checked independently for paired triangle edges, component count and bed contact.
When moving-part reliability matters, retain these mesh checks alongside slicer
warnings and path inspection. A clean slice alone did not reveal this defect.

## Role labels can hide a bridge or suggest unsupported anchors

Verified 2026-09-07 with PrusaSlicer 2.9.6, 0.2 mm layers and supports off:
the sunglasses closure trial's 12 mm loop bridge was represented by
`Overhang perimeter` paths (about 11.6 mm centerline segments). Meanwhile,
roughly 6.2 mm `Bridge infill` paths appeared on a keeper lip whose outer
edges were themselves unsupported. Neither the longest Bridge infill segment
nor its presence established the actual free-air span or two sound anchors.
Compare the previous layer with the first spanning layer, including perimeter
roles, and distinguish one-sided overhangs from bridges. See the
[closure review and layer windows](../../../../model/sunglasses_case/notes/closure_review/report.md).
No automatic anchor classifier was implemented; these were visual inspections.

Subsequent physical A/B/C tests confirmed keeper droop despite the clean slices.
The D/E revision uses a separate side-printed keeper; checking its local paths
and first layers showed the full tooth profile on the bed and only perimeter
roles thereafter. Record both the removal of that local overhang and the added
assembly/fit tradeoff, rather than labeling the whole model bridge-free. See
[D/E evidence](../../../../model/sunglasses_case/notes/keeper_review/report.md).

When transferring a tested mechanism to a different height, inspect its new
layers even if CAD comparison shows identical translated geometry. In the
[reduced full case](../../../../model/sunglasses_case/notes/production_e_review/report.md),
the first loop bridge moved from Z=36.2 to 40.8 mm after a 4.5 mm CAD translation
on a 0.2 mm layer grid. Preserve dimensions, but do not assume layer registration
or printed clearance stays identical. This was observed with PrusaSlicer 2.9.6.


## Remaining limitations

Selected layer-window SVGs are supported by the review helper. Automatic
free-air span measurement, support-removal accessibility checking and a reliable
pass/fail printability score remain unimplemented here. No universal safe bridge length or overhang-angle limit
has been established; behavior depends on geometry, anchors, process and material.
Slicer evidence does not physically measure sag, surface finish or hinge freedom.

## Check the actual brim and deposited-path footprint

Verified 2026-09-06 with PrusaSlicer 2.9.6 on the dental travel case, using the
existing `read_paths` helper and a centered 260 × 260 mm bed with 3 mm brim:
[object summary script](../../../../model/dental_travel_case/notes/slicer_review/summarize.py).
For each deposited straight segment, extend both endpoints in X/Y by half its
reported extrusion width, then take global min/max. Include `Skirt/Brim` paths.
Check maximum layer Z independently against the **250 mm** safe height.

The final case had X 3.122–256.876 and Y 11.202–248.220 mm, with Z up to 61.8 mm.
This checks generated paths rather than relying only on model bounds plus nominal
brim width. It is conservative for straight segments of the reported width, but
not a prediction of ooze/flow spread or a check of travel/start/end machine moves.
The parser's existing limits (absolute XYZ, relative E, linear ASCII moves) apply.

In the same investigation, a circular-bottom clip produced a `Loose extrusions`
warning on the accessories plate but not on a mixed coupon plate. Inspecting the
lower-arc layers identified abrupt lateral growth; adding a supporting pedestal
removed the accessory warning. Replacing small grip bumps alone did not. Do not
assume a clean mixed-plate warning result validates the same part in every layout;
inspect the production plate's paths. See the object's review report and layer
images for geometry and profile scope, rather than treating the fix as universal.
