"""Inspection pose only: outside faces and four recessed screws."""
from pathlib import Path
import cadquery as cq
result=cq.importers.importStep(str(Path(__file__).resolve().parent/'book_reading_plate_assembled.step')).rotate((0,0,0),(1,0,0),180)
