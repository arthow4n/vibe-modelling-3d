from pathlib import Path
import cadquery as cq
root=Path(__file__).resolve().parent
result=cq.importers.importStep(str(root/'joint_test_assembled.step')).rotate((0,0,0),(1,0,0),180)
