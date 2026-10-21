# Small liner IDs that preserve the test skins

[Object status](../README.md) · [Three-option SVG](../renders/concepts/liner_marking_options.svg) ·
[M1 compact text](../renders/concepts/liner_marking_m1.svg) ·
[M2 broad marks](../renders/concepts/liner_marking_m2.svg) ·
[M3 ink only](../renders/concepts/liner_marking_m3.svg)

**Implementation authorized:** the user selects **M1** and requests the full T08/T16 boxes for printing. The [implemented pairs](t_skin/README.md) own current exports and checks; the alternatives below preserve the preceding discussion.

**Earlier discussion:** the user intends to print **T08 and T16**, after settling
how to identify them without compromising the structure under test. At that phase this selected
the eventual pair while deferring the marking choice and full-box publication. Existing diagnostic probes are unchanged. T08/T16
mean 0.8/1.6 mm **per upright skin**, with a 0.6 mm wall gap and 2.2/3.8 mm total
wall depth. Their full-cup floor/pad/corner construction is not defined by those
wall probes. T12 remains historical research, outside this requested next pair.

The user reports that current bottom lettering is too big/deep and takes too much
of the skin's functional area. No new print is identified, and exact printed file
hashes are unknown. This adds a label-design objection to the retained A/B/C
physical feedback; it does not retract B08/B16 damping approval. Earlier labels
were also reported too small to read, so merely shrinking ordinary font text is
not an adequate solution.

## Existing labels and the actual interference

The current [B R2 source](../support_design.py) cuts a bold 12 mm font-size variant
ID plus an 8 mm font-size `R2`, offset 11 mm below the main line, into the
shell-facing underside of both cup and pad. Those are font sizes, not measured
capital heights. Its recess is **0.2 mm** deep. The cup has a **0.4 mm backing
skin**, so at a letter stroke the cut leaves only **0.2 mm** before the core.
That is one of the agreed 0.2 mm layers. The pad's additional 0.2 mm preload gives
it a 0.6 mm lower skin before the same cut, leaving 0.4 mm; its large footprint
still alters the face. [S source](../skin_design.py) uses 12 mm type, a 0.1 mm
recess and no R2 line. Thus the new objection must not be attributed to an
identical recess depth in every historical variant.

The user identifies lost functional area; thinner local material follows from
the B source. The extent of any resulting change in stiffness, sound or failure
probability is **unmeasured**. The SVG section illustrates the cup's B geometry,
not a measured section of the user's print.

## Three suggestions

All SVGs show underside views at the same nominal 34 mm cup size, with the ID
near one corner and the central area unlettered. The dashed central square is a
visual keep-clear guide, not a finalized floor/core boundary. The matching pad
receives the same identifier in its available corner, without shrinking strokes.
Orange is an explanatory color for a cut void; blue represents optional ink.
All printed material remains ordinary black TPU. These are drawn suggestions,
not CAD models or sliced paths.

| Option | Reserved marking zone | Identification | Consequence |
| --- | --- | --- | --- |
| **M1 — compact full ID** | 9 × 5.5 mm | Monoline `T08` / `T16`; 0.8 mm strokes, 3.2 mm stroke-center height, approximately 7.4 × 4.0 mm outer glyph envelope | Complete name on both parts; needs the largest local solid backing zone. Omit the separate revision line. |
| **M2 — broad corner marks** | 4 × 4 mm | One rectangular groove = T08, two = T16; each 0.8 × 2.4 mm, with 0.8 mm between grooves | Smallest integral choice; easy-to-count shapes avoid tiny enclosed letters. A full-name key is required with the batch. |
| **M3 — ink-only full ID** | No altered CAD area | Contrasting `T08` / `T16` written on both shell-facing undersides after printing | No recess, boss, support panel or extra printed part; adds manual marking, with adhesion/transfer untested. |

M1/M2 use a **0.2 mm recess**, one layer in the agreed setup. The improvement is
smaller area and relocating the entire cut over solid backing, rather than
leaving a thinner membrane above air. A nominal 0.05/0.1 mm CAD recess cannot be
assumed to produce equally shallow relief at 0.2 mm layers; that would need an
actual slice. No shallower cut is represented as qualified here.

The reserved zones are shown 1 mm in from the edge. Their dimensions describe
label placement, **not proof that an existing 4 mm corner fits them**. Final CAD
must establish the complete solid backing and its connection to the corner,
including that inset. The current B rim is not an established 4 mm solid label
land. M1/M2 are conditional on a suitable corner in the new design; do not add a
broad solid floor island merely to rescue a label. An added solid zone is itself
a local stiffness change, even if the center stays uncut. Compare its effect
honestly and keep corner treatment identical between the two variants and pads.

These IDs are batch-local. Do not reuse one/two-bar codes for another revision
without retaining a clear batch key. Preserve previous B/S markings and files;
no old label is edited or relabeled as T08/T16.

## Earlier recommendation for the SVG discussion

**M2 is the preferred integral marking:** countable broad bars in a suitable
solid corner, matching on cup and pad, with a full-name key kept with the batch.
Its reserved zone is 16 mm² versus M1's 49.5 mm²; those are zone areas, not a
prediction of damping or the actual amount of removed TPU. M1 is the alternative
if reading the full name directly is more valuable than the smaller footprint.
M3 preserves the geometry completely if a manual label is acceptable; no ink or
paint compatibility is assumed.

For the later model phase, inspect the actual Classic paths through the selected
mark on both parts, retaining the normal 0.4 mm nozzle / 0.2 mm layers and no
Arachne. The decision is whether the code survives slicing and remains wholly
backed by the solid corner, without intruding into the functional skins/core or
altering shell fit. Physical visibility remains a print question. No new trial
batch, pad, mesh, STEP or process profile was made in the SVG discussion; the later M1 implementation is linked above.

| Item | Print status | Artifacts | User result / remaining checks |
| --- | --- | --- | --- |
| Marking suggestions | N/A — SVG discussion | Overview and three option SVGs | User reports existing bottom text too large/deep; M1 subsequently selected; no option physically evaluated. |
| Implemented T08/T16 cup/pad pairs | Unknown — see implemented pair record | M1 implementation linked above | Full-box digital evidence belongs to the implementation; physical readability and damping remain unmeasured. |

Attribution, 2026-10-21: GPT-6 family; exact runtime identifier and reasoning
effort not exposed. Codex shared-workspace CLI/API agent, OpenAI; no subagents.
User supplies the label objection, structure-preservation priority and eventual
T08/T16 pair. Agent authors the SVG options and comparison. Existing source and
physical approvals retain their original attribution.
