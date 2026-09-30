"""Question-oriented engineering analysis. Units: mm, N, MPa."""
from .case import AnalysisCase, Region
from .materials import Material, PETG_SCREEN
from .results import AnalysisResult
from .questions import (SnapFitQuestion, FlexureQuestion, StructuralQuestion,
                        Support, Motion, SurfaceForce, MatingPart,
                        BeamApproximation, ManufacturingAssumption)
from .studies import QuestionStudy

__all__ = ['AnalysisCase', 'Region', 'Material', 'PETG_SCREEN', 'AnalysisResult',
           'SnapFitQuestion', 'FlexureQuestion', 'StructuralQuestion', 'Support',
           'Motion', 'SurfaceForce', 'MatingPart', 'BeamApproximation', 'ManufacturingAssumption', 'QuestionStudy']
