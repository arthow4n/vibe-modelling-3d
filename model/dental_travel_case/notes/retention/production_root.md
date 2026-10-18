# M2B production-root operation study

The 3.2 N per-pad traction fixture produces a retracting pose with a positive
leaf/liner separation bound on the actual production-root mesh. Its local peak
strain is **not yet mesh qualified**. These results do not establish pull-off
resistance, insertion, printed elasticity or finger comfort. The product decision
remains in [the M2 record](../m2.md).

The earlier isolated tongue omitted the production R0.8 blend. This experiment
instead crops `m2b_design.build()['body']`, retaining both roots, guards, liners
and the complete circumference. Only the annular cut 12 mm below the nominal
beam roots has all translations fixed. Equal opposite inward global-X loads act
as tractions initially normal to the actual 15.5609 mm² rounded pad faces (0.205643 MPa at
3.2 N); the pads may rotate and deform. The selection's 28 mm² rectangle is
only its bounding region, not the loaded CAD face area. These are fixed world
directions, not follower pressure or a finger-contact law.
There is no imposed target travel, rigid pad constraint, cap or self-contact.
The material is an uncalibrated homogeneous isotropic elastic hypothesis:
E = 1200 MPa, ν = 0.38, geometrically nonlinear static response. No material
strain limit is supplied.

Both runs use the same guarded mesh: 90,470 nodes and 46,254 C3D10 tetrahedra,
maximum size 3 mm, minimum size 0.5 mm and curvature count 8. The native minimum
Jacobian is positive (0.00069362). CalculiX 2.21 uses its default direct solver.
The complete case, native input, load selections, material and solver identity
are retained with each result.

| Quantity | 4 N per pad, retained overtravel counterexample | 3.2 N per pad |
| --- | ---: | ---: |
| Minimum inward tooth displacement, negative/positive side | 2.76104 / 2.77314 mm | 2.20762 / 2.21731 mm |
| Mean tip displacement, negative/positive side | 3.34961 / 3.36413 mm | 2.67672 / 2.68835 mm |
| Mean pad displacement, negative/positive side | 1.74823 / 1.75716 mm | 1.39462 / 1.40176 mm |
| Maximum absolute principal strain | 0.98178% | 0.78719% |
| Maximum von Mises stress | 11.5689 MPa | 9.26296 MPa |
| Minimum continuous quadratic-face gap lower bound | −0.34056 mm | +0.32938 mm |
| Contact-free interpretation | Blocked | Selected channel faces separated at saved frames |

The 4 N run completed numerically, but its contact-free representation cannot
support an operation conclusion: the leaf can reach the liner. Its negative
conservative bound does not itself prove intersection. It is preserved as a
counterexample to interpreting solver completion or a low strain as sufficient
evidence. See its [native result](dental_m2b_production_root_direct/result.json)
and [face witness](dental_m2b_production_root_direct/channel_witness.json).

The 3.2 N run converged in ten load increments. Its peak strain occurs at
element 69545, integration point 3, centroid (32.5746, −6.74735, 151.03087) mm:
0.631 mm from the nominal root, about 12.63 mm from the annular clamp. Both
leaves participate. These are finite-element estimates, not measured printed
strength or recovery. See the [native result](dental_m2b_production_root_32/result.json)
and [continuous-face witness](dental_m2b_production_root_32/channel_witness.json).

The witness uses the actual quadratic triangular faces from the native C3D10
mesh. For a degree-two face, its Bernstein controls are its three vertex
coordinates and `2 × mid-edge − (endpoint A + endpoint B) / 2`. The complete
face lies inside their convex hull. The minimum inward coordinate of every
liner-front control minus the maximum inward coordinate of every inner-leaf
control therefore bounds separation of these faces, including possible
overshoot between nodes. Every saved displacement frame is checked against the
native input/case identities and extracted observation summaries. A positive
bound excludes intersection of these selected FEM faces. It does not certify
other faces, continuous load time between frames, the omitted cap, exact
deformed CAD, or a physical print.

The [face-bound regressions](../../../../tests/test_dental_root_channel.py) include
an actual quadratic edge that crosses a liner between clear nodes: endpoint
coordinates 0 and 1 with midpoint 1 give a coordinate of 1.125 at three-quarters
of the edge. A liner at 1.1 therefore defeats the nodal screen, while the
quadratic bound rejects the claimed separation. A separated linear-face control
preserves its independently specified 0.3 mm gap. Both tests passed.

The existing 4 N run at fraction 0.8 already supplies the same 3.2 N equilibrium
under a coarser absolute increment. Comparing its 0.4 N steps with the new
0.32 N steps gives a 20% increment refinement, with relative changes of
6.29×10⁻¹¹ in maximum displacement and 1.24×10⁻⁷ in peak strain. The largest
observation-summary component difference is 0.000001 mm. Both compared
subpaths have positive continuous-face bounds. The [reproducible comparison](dental_m2b_production_root_32/increment_comparison.json)
uses the shared metric comparison helper; its 1% diagnostic tolerance concerns
increment resolution only. No 0.05-increment root run was performed. The later
unrepresented-contact portion of the 4 N run does not change its earlier saved
equilibrium. Mesh sensitivity is assessed separately below.

Because this particular model contains only elastic stiffness, zero support
translations and these tractions, scaling E and both forces together preserves
its equilibrium deformation and strain. Thus E = 800–2200 MPa corresponds
theoretically to 2.133–5.867 N per pad for the same pose; stress scales with E.
This is an equilibrium rescaling, not extra native simulations, a measured
operating-force range, or a substitute for anisotropy and strength evidence.
The equal opposite forces have zero net resultant and moment, so the reported
global force balance mainly checks cancellation and cannot independently verify
each leaf's local force transfer.

Reproduce from the repository root:

```bash
./execute.py --threads 1 model/dental_travel_case/retention_root_study.py solve --load 3.2 --modulus 1200 --linear-solver default --mesh-from /tmp/dental_m2b_production_root_direct --destination /tmp/new_root32
./execute.py --threads 1 model/dental_travel_case/retention_root_study.py witness --destination /tmp/new_root32
./execute.py --threads 1 model/dental_travel_case/retention_root_study.py compare --destination /tmp/new_root32 --reference /tmp/dental_m2b_production_root_direct
```

Omit `--mesh-from` for fresh meshing; retained compressed decks can also be
restored to a raw directory through the established native evidence workflow.
The finer actual-root mesh (maximum 2.1 mm, minimum 0.35 mm, curvature count 12)
has been generated with 182,772 nodes and 96,588 tetrahedra, with positive
minimum Jacobian 0.0000906400. Its standalone direct solve completed. The [mesh comparison](dental_m2b_production_root_fine/mesh_comparison.json)
finds maximum travel 2.73042 mm (1.36% change), minimum tooth retraction
2.26292/2.26082 mm (2.44%/1.92% change), and selected whole-face channel gap
≥0.29270 mm. The final selected tooth patch clears the frozen receiver plane
by ≥0.28619 mm even at each separately adverse 0.25 mm guide offset. This is a
released geometric pose of the selected FEM patch, not a loaded moving cap or
continuous withdrawal simulation.

Peak strain rises from 0.78719% to **0.88618%** (11.17% normalized change), while
maximum von Mises stress rises from 9.26296 to 10.20730 MPa (9.25%). The peak
moves along the actual root blend to (32.6569, −1.4921, 150.9718) mm. Displacement
and radial clearance are stable under this refinement; local strain does not meet
the declared 10% numerical comparison. Keep the strain range visible rather than
calling it mesh-converged or using an uncalibrated material threshold to pass it.
No further root refinement is claimed. Numerical uncertainty and unknown printed
recovery remain distinct from the demonstrated retracting pose.
