"""Exact unchanged G hood on archive R1; no reference geometry in output."""
import archive_r1_base_15 as a
result = a.g.compound(a.base(),a.g.cap())
