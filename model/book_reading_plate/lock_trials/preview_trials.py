import cadquery as cq
from lock_trials import parts,box
items=[]
for i,letter in enumerate('AB'):
    a,b=parts(letter)
    items.extend([a.translate((0,i*110+50,0)).val(),b.translate((0,i*110,0)).val()])
result=cq.Compound.makeCompound(items)
