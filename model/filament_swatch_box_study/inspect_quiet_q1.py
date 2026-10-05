"""Q1 inspection only: closed shell, open loaded jacketed base, detached jacket.

Reference cards and operating poses must never enter printable exports.
"""
import quiet_q1 as q
base,jacket,hood=q.base(),q.jacket(),q.hood()
parts=[base,jacket,hood]
parts += [part.translate((95,0,0)) for part in (base,jacket,*q.cards()[::7])]
parts.append(jacket.translate((175,0,-q.FOOT_TOP)))
result=q.g.compound(*parts)
