"""Inspection only: accepted A beside closed Q1F; open Q1F and detached insert."""
from quiet_assembly import QuietAssembly
import quiet_q1_flush
configuration=QuietAssembly(quiet_q1_flush).inspection()
result=configuration.assembly()
