from swatch_book_case import body, lid_pose, cards, latch, hardware
import cadquery as cq
result=cq.Compound.makeCompound([body().val(),lid_pose(120).val(),latch().val(),cards(),hardware()])
