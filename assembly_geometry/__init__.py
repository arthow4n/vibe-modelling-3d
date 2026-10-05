"""Optional native-assembly snapshots and explicit geometric intent. See README.md."""
from .configuration import Configuration, Resolution, solve, rigid_location, constrain
from .queries import PairRequirement, PairResult, MotionResult, check_pair, sample_motion

__all__ = ['Configuration', 'Resolution', 'solve', 'PairRequirement', 'PairResult',
           'MotionResult', 'check_pair', 'sample_motion', 'rigid_location', 'constrain']
