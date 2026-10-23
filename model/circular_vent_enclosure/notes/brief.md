# User brief and measured-interface updates

Source: user design brief in this conversation, 2026-10-23. These are user
requirements; V1 implementation choices and test assumptions live in the README.

- Reduce perceived inlet airflow noise while preserving as much ventilation as
  possible. Passive shield/diffuser, without guaranteed attenuation or assumed
  broadband benefit from chamber volume. No V1 foam, fibers, resonators or tuned
  cavities. No additional internal baffle.
- Existing approximately Ø130 mm valve projects approximately 35 mm. Air emerges
  around its disc, never through the disc. Preserve the gap, adjustment and function.
- Maximum radial extension 50 mm; absolute OD approximately 230 mm. Preferred OD
  210–215 mm and total wall projection 80–90 mm.
- Solid room-facing front, hollow chamber, smaller rear mounting interface,
  rounded smooth transitions, shell approximately 2.0–2.4 mm and front 2.4–3.0 mm.
  Optional shallow internal front ribs; lightweight, unobtrusive and cleanable.
- Six to eight broad peripheral windows, rounded lips/corners, structural
  continuity and printable roof geometry. Start near 80–100 cm² nominal exit
  area. Check minimum passages throughout; exit area alone proves no flow rating.
  Adapt angular placement to nearby obstacles. Avoid narrow passages, long
  spirals, labyrinths, abrupt airflow edges and whistle-producing features.
- Prefer removable slip/friction fit to a stationary rim, never the disc.
  No drilling, destructive modifications, disc loading or interference with
  adjustment. Mount geometry is provisional until the stationary rim is measured.
  Parameterize diameter, clearance and engagement. Optional compliant contact
  material or a separate mounting ring may be considered if needed. Do not
  overload the original attachment.
- Prefer one support-free PETG FDM part, solid front against bed and collar up.
  Two parts acceptable if materially better. Do not trade away airflow/mount
  function for one-piece manufacture. Avoid unsupported window bridges and
  contraction overhangs; prevent panel flex/rattle and inaccessible debris or
  condensation traps.
- Parameterize OD/depth, thicknesses, mounting fit/engagement, disc clearance,
  outlet count/width/height/phase/shape, taper/curvature and optional ribs.
- Evaluate whole fit, disc/gap clearance, minimum passage sizes, print orientation,
  overhangs, mount feasibility, weight/stiffness and basic manufacture. Deliver a
  simple functional V1 using repository conventions; actual airflow remains
  unqualified without testing.

User clarification in the same conversation: **“rim is about 2 cm height, then
1.5 cm gap to the disc, adding up to 3.5 cm we mentioned above”**. Treat the
stationary rim as approximately wall heights 0–20 mm and the annular emission
region as approximately 20–35 mm. This supplies axial layout, not rim diameter,
profile, grip suitability, attachment strength or calibrated effective flow area.

Additional user direction in this conversation: **“I don't know if you can minimise
the material usage somehow while keeping the functionality but try think about it”**.
The selected thinner shell/front and extended ribs implement this direction; the
comparison and remaining stiffness uncertainty are recorded in the object README.

## Follow-up directions

User: “Do you think it's possible to further reduce the material usage while
keeping the functionality? If possible go do it”.

User: “Btw I think you need a bit more contact area with the rim to ensure the
mounting is stable, consider also making the mechanism a bit clamping so it's
both compliant and clamping so I can mount easily without worrying about slightly
wrong measuring”.

These authorize the material/mount revision. The selected 1.4 mm curved sidewall,
16.7 mm contact span, 129–132 mm geometric adjustment range, two-piece arrangement
and chosen fasteners are engineering decisions, not user-supplied dimensions or
validated fit/holding-force requirements. Preserve the initial approximate wall
and front preferences above as historical user guidance; the front remains 2.4 mm.
