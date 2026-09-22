"""Inspection only: transverse structural section away from the catch."""
import cadquery as cq
from lock_trials import parts,box
items=[]
for i,letter in enumerate('AB'):
    a,b=parts(letter,labels=False)
    crop=box(-9,13,10,12,-1,11)
    items.extend([a.intersect(crop).rotate((0,0,0),(1,0,0),90).translate((0,i*16,0)).val(),b.intersect(crop).rotate((0,0,0),(1,0,0),90).translate((0,i*16,0)).val()])
result=cq.Compound.makeCompound(items)
