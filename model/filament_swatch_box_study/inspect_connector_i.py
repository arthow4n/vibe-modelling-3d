"""I key seated in actual H sample geometry; intentional relaxed pad overlap."""
import cap_i_grip_keys as i
h=i.h
parent=h.base().val()
ends=[]
for end in (1,-1):
    lo,hi=(h.FOOT_DEPTH/2-h.FIXTURE_DEPTH,h.FOOT_DEPTH/2+.1) if end>0 else (-h.FOOT_DEPTH/2-.1,-h.FOOT_DEPTH/2+h.FIXTURE_DEPTH)
    crop=parent.intersect(h.block(-h.FOOT_X/2-.1,h.FOOT_X/2+.1,lo,hi,0,h.SEAM_Z).val())
    ends.append(crop.translate((0,-end*h.FOOT_DEPTH/2,0)))
result=h.compound(*ends,i.seated_key(2))
