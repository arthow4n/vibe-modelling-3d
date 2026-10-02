"""Inspection only: closed/open twenty-card C with realistic sparse contents."""
from cap_c_hinged_5 import *

count=FULL_COUNT
shift=105
closed=compound(frame(count),cap(count),axle(count),key(count),*contents(count))
opened_box=compound(frame(count),opened(cap(count),count,OPEN_STOP_ANGLE),axle(count),key(count),
                    *contents(count,sparse=True)).translate((shift,0,0))
result=compound(closed,opened_box)
