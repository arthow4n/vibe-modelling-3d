"""Actual exported left-half print placement; keep the outside end on the bed."""
from pathlib import Path
import cadquery as cq
result=cq.importers.importStep(str(Path(__file__).resolve().parent/'plate_left.step'))
