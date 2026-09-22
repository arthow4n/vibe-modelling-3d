"""Rear view of the locked full-size test joint; inspection only."""
import cadquery as cq
from components import P, coupon
left, right, locking_key = coupon()
result = cq.Compound.makeCompound([
    left.val(), right.val(),
    locking_key.translate((0,0,P.key_lock_advance)).val(),
]).rotate((0,0,0),(1,0,0),180)
