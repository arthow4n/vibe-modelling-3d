"""Inspection-only nominal swatch envelopes; never export this entry point.

0.04 mm drawing gaps reveal the twenty cards, not manufacturing clearances.
"""
from components import *
cards=[block(-CARD_X/2,-CARD_Y/2,STACK_Z+i*CARD_T,CARD_X,CARD_Y,CARD_T-.04).val() for i in range(COUNT)]
result=cq.Compound.makeCompound([body().val(),*cards])
