"""Comparison of already completed evidence; never silently reruns a solver."""
import math
from .case import positive


def compare_results(coarse, refined, *, metrics, relative_tolerance=.05):
    """Compare explicitly chosen metric paths; convergence is not physical validation.

    Example metrics=['max_displacement_mm','peak_motion_force_N.thumb'].
    Both cases must represent the same physical question. This helper cannot
    infer that changed loads, geometry or material were intentional.
    """
    coarse.require_completed(); refined.require_completed()
    positive(relative_tolerance,'Relative tolerance')
    answer={}
    for path in metrics:
        a,b=coarse.metrics,refined.metrics
        for key in path.split('.'):
            a,b=a[key],b[key]
        if not isinstance(a,(int,float)) or not isinstance(b,(int,float)) or not math.isfinite(a+b):
            raise ValueError(f'{path} is not a finite scalar metric')
        change=abs(a-b)/max(abs(b),1e-12)
        answer[path]=dict(coarse=a,refined=b,relative_change=change,passes=change<=relative_tolerance)
    return answer
