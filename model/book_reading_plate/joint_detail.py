"""Exploded joint illustration; not a printable layout. Same coupon builders."""
import cadquery as cq
from components import coupon
left, right, locking_key = coupon()
result = cq.Compound.makeCompound([
    left.translate((-22,0,0)).val(),
    right.translate((22,0,0)).val(),
    locking_key.translate((22,-46,-8)).val(),
])
