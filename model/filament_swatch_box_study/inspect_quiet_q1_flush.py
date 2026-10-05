"""Inspection only: accepted A beside closed Q1F; open Q1F and detached insert."""
import quiet_q1_flush as q
base,jacket,hood=q.base(),q.jacket(),q.hood()
old=q.archive.base('continuous')
# Butted feet joined along Y; key sits on the actual seam.
parts=[old.translate((0,-q.FOOT_Y/2,0)),hood.translate((0,-q.FOOT_Y/2,0)),
       base.translate((0,q.FOOT_Y/2,0)),jacket.translate((0,q.FOOT_Y/2,0)),
       hood.translate((0,q.FOOT_Y/2,0)),q.keys.seated_key(3)]
parts += [p.translate((90,0,0)) for p in (base,jacket,*q.cards()[::7])]
parts.append(jacket.translate((165,0,-q.FOOT_TOP)))
result=q.g.compound(*parts)
