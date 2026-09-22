"""Rear view of the seated two-piece coupon and its single recessed release port."""
import cadquery as cq
from components import coupon
left,right=coupon()
result=cq.Compound.makeCompound([left.val(),right.val()]).rotate((0,0,0),(1,0,0),180)
