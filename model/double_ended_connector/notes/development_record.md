# Connector development record

## D: first sequential CAD increment

The user authorizes CAD modelling D, E, F sequentially, including assembled views
so mechanism and assembly are understandable. Current first increment is D only;
E and then F remain the next authorized increments. Generic sizing is delegated.
The original SVGs are conceptual: they are not assembly-fit evidence.

### Assembly and negative cases

An integral threaded stem with a later keeper tip was the initial interpretation.
Putting its halves in split frame pieces does not by itself solve installation:
the upper half-stem must cross the closed sleeve wall as the frame approaches.
The actual CAD assembly-path check rejected this arrangement. The revised eight
parts are two frame halves, two independent keyed stems, two barrels and two
printed hand screws. Each barrel threads onto its stem from the small root end
first; the assembled units are captured in the split frame afterward. Their root
grooves engage socket ribs, blocking direct axial withdrawal. The flat/keyed
section prevents free stem rotation.

The frame closes with barrels retracted. Requiring a closed-barrel frame
approach falsely tested a different sequence: the barrel then cups the fixed
nose that is still on the approaching frame. The checker was corrected to the
explicit retracted-barrel assembly sequence, not to a larger collision tolerance.
The closed state remains checked along the operating screw path after assembly.

A first closed operating pose also collided with the outer crown. Moving the
crown clear of the two-mm nose overlap fixed that collision. Keeper shoulder
and threaded-skirt heights were aligned at the declared closing stop. A narrow
roof over each root socket was thickened during print review: the central block
is eight mm thick around 4.3 mm-high sockets, leaving 1.85 mm nominal above and
below rather than a marginal skin. This changes the central body, not the slim
free horn or the screw travel.

### Digital intent and remaining physical questions

The explicit helical path samples 0..8 mm in one-mm increments, with 360 degrees
per two-mm travel. Pair overlaps must be below 0.001 mm³ (kernel roundoff screen,
not a print tolerance). A direct 0.7 mm axial pull from closed must obstruct;
a 3.2 × 3.2 × 4 mm box witnesses the nominal open mouth; the other mouth stays
bridged. The free-nose diameter is below the nominal cord bore. This is not a
complete articulated ring-loading sweep or a physical pull test.

The upper frame approaches the open gate/stem units at Z offsets12,6,3,1,0.2,0.
Before that, each barrel is checked on the separate stem at helical offsets
-18,-12,-8,-4,0 mm. A 0.6 mm axial stem withdrawal is obstructed by the socket
ribs. Each delivered assembly screw has six actual axial material witnesses to
protect the known hollow-thread failure pattern from other repository work.
Screw/frame forbidden overlaps are checked in the assembled pose.

The shared product-verification CLI reports CAD passes while hand assembly,
opening effort and shaking remain UNKNOWN. A geometric obstacle does not prove
shake resistance, force, fatigue or load capacity. The planned four turns are a
control motion, not a calibrated vibration lock. The frame seam, sockets and
small printed assembly screws are experimental load paths.

### Views and publication

The ordinary exported result is the eight-piece print layout. Native CadQuery
assembly configurations supply fully closed, upper-open and exploded/assembly
views from the same actual components. No display scene is exported as the
print layout. Frame halves lie on their split plane, sleeves upright, stems on
their keyed roots, screws on their broad heads.

A full two-ended solid cutaway was interrupted while its rendering continued
without a usable sectional image; the completed outer views were already useful.
The section recipe was narrowed to one actual stem and sleeve with a planar
section and labelled frame omission. The repeated lower end contributes no new
internal relationship. The native artifact cache may reuse unchanged completed
images, but interrupted jobs are not completion receipts. The final native
receipt owns delivered export/view/slice status and input association.

The existing architecture guidance was adequate: actual whole-assembly approach
checks exposed flaws that a static assembly image alone would not reveal. No
shared framework change or physical-property inference is justified by this
prototype. All-printable and no tools are object requirements; normal opening
removes no components.
