from swatch_book_case import body, lid, latch, block, BEAD_X0, BEAD_WIDTH, FRONT_Y, LEAF_Z
import cadquery as cq
window=block(-25,FRONT_Y-6,LEAF_Z-3,45,17,18)
result=cq.Compound.makeCompound([s.intersect(window).val() for s in (body(),lid(),latch())])
