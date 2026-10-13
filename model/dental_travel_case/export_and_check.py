"""Explicit publication boundary; checks geometry before writing paired exports.

Run through evaluate_model.py. Building/importing the production modules never
exports. STL settings match the shared evaluator absolute-deflection contract.
"""
from pathlib import Path
import cadquery as cq
from design import build
from samples import samples
from components import clip
from checks import contents_check, shells_check, clips_check, construction_check, latch_check, compliance_check

root = Path(__file__).resolve().parent
case = build()
construction_check(case)
contents_check(case)
shells_check(case)
clips_check(case)
latch_check(case)
compliance_check()
layouts = {"dental_travel_case": case["result"], "accessories": case["accessories"],
           "handle_clip": clip(), **samples(case)}
for name, part in layouts.items():
    shape = part.val() if isinstance(part, cq.Workplane) else part
    assert shape.isValid(), name
    cq.exporters.export(shape, str(root / (name + ".step")))
    written = shape.exportStl(str(root / (name + ".stl")), tolerance=0.003,
                    angularTolerance=0.5, relative=False)
    assert written, (name, "STL conversion failed")
cq.exporters.export(case["closed"], str(root / "dental_travel_case_assembled.step"))
result = case["opened"]
