# Sunglasses closure history

Historical trials and diagnostic slices are retained in Git; use
[current print instructions](printing_and_design.md) for the delivered case.
The notes below preserve the observations that changed the design, not a print
recommendation for the older samples.

- The standing case had an unsupported cavity roof. A historical PrusaSlicer
  review found bridge-role paths about 87 mm long at Z=171.2 mm, including
  anchors. Printing the case open with both broad panels on the bed removed that
  roof from the print plan. The earlier orientation is at Git `9b8af79`.
- The flat-print conical hinges initially produced degenerate STL triangles at
  exact cone tips despite valid CAD and a clean slice. Small flat tips fixed the
  mesh. The user later reported that the full case's shape and hinge operation
  were acceptable, but hinge play and latch retention were weak. The flat-print
  revision is at `c2fe963`.
- A tighter 0.20 mm radial / 0.20 mm axial hinge sample still tilted. Moving
  both latch surfaces in the supposed deeper version left the nominal projected
  bite at 1.0 mm; both retaining faces were ramps. These samples are at
  `1c6b8c3`. A/B/C trials then used spaced hinges and a positive loop shoulder
  (`578bc5d`). The user found all three similar; C's locating tabs gave no
  noticeable improvement. The keeper underside drooped into the loop's seating
  path even though the diagnostic slices reported no warning.
- D/E moved the keeper tooth to a separate side-printed insert. Both used a
  0.20 mm seated rail gap and 3.20 mm outward release travel. D used 2.20 mm
  loop leaves; E used 2.80 mm leaves. The user printed both, found both
  satisfactory, and slightly preferred E (`bca684e`). E was integrated without
  scaling its local mating geometry. The user subsequently printed the reduced
  full case and reported that it works well; see its current print-status block.

The historical PrusaSlicer profiles, layer images, hashes and reports remain
recoverable at those revisions. Their former 260 × 260 × 250 mm review limit is
not the repository's current Qidi Q2C default. Print success of one fixture
does not establish fatigue or backpack durability of the full case.
The original loop-latch reasoning also cited the
[Formlabs snap-fit guide](https://formlabs.com/uk/blog/designing-3d-printed-snap-fit-enclosures/)
for general undercut and cantilever principles, without adopting its
material-specific dimensions as PETG limits.
