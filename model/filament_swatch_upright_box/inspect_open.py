"""Open card file; conservative envelopes are references, never print geometry."""
from components import *
result=cq.Compound.makeCompound([body().val(),*[card(i,CARD_T-.08).val() for i in range(COUNT)]])
