"""Actual insertion alignment: slide the raised male sample downward in Y."""
import cadquery as cq
from components import coupon
left,right=coupon()
result=cq.Compound.makeCompound([left.translate((0,80,0)).val(),right.val()])
