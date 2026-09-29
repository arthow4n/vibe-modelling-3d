"""Question-oriented engineering analysis. Units: mm, N, MPa."""
from .case import AnalysisCase, Region
from .materials import Material, PETG_SCREEN
from .results import AnalysisResult

__all__ = ['AnalysisCase', 'Region', 'Material', 'PETG_SCREEN', 'AnalysisResult']
