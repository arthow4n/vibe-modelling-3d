"""Slice-only N1 straight wall proxy: 60 × 6 × 16 mm, long edge on bed.

No box/corners/lid or print qualification. The solid CAD volume lets the selected
ordinary infill process generate its internal core; it is not an all-solid print.
"""
import cadquery as cq

result = cq.Workplane('XY').box(60, 6, 16, centered=(False, False, False))
