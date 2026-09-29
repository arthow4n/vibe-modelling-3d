"""Sampled CAD preflight for prescribed whole-part rigid translations.

These parts cannot deform to resolve mutual overlap. Partial-region constraints
and flexible parts are outside scope; this is not continuous collision proof.
"""
from itertools import combinations
import math
from .case import positive


def rigid_driver_clearance(case, *, max_relative_step_mm=.25, volume_tolerance_mm3=1e-7):
    positive(max_relative_step_mm,'Rigid motion sample step')
    positive(volume_tolerance_mm3,'Rigid overlap tolerance')
    drivers={}
    for name,part in case.parts.items():
        axes=[None]*3
        ambiguous=False
        for constraint in case.constraints:
            region=constraint.selection.region
            if constraint.selection.part!=name or region.lower!=(-math.inf,)*3 or region.upper!=(math.inf,)*3:
                continue
            for axis,value in enumerate(constraint.displacement_mm):
                if value is None: continue
                definition=(value,(constraint.progress or ((0.,0.),(1.,1.))) if value else ((0.,0.),(1.,0.)))
                if axes[axis] is not None and axes[axis]!=definition: ambiguous=True
                axes[axis]=definition
        if not ambiguous and all(axis is not None for axis in axes):
            shape=part.shape.val() if hasattr(part.shape,'val') else part.shape
            drivers[name]=(shape,axes)
    def position(axes,t):
        result=[]
        for value,progress in axes:
            multiplier=progress[-1][1]
            for (t0,v0),(t1,v1) in zip(progress,progress[1:]):
                if t<=t1:
                    multiplier=v0+(v1-v0)*(t-t0)/(t1-t0);break
            result.append(value*multiplier)
        return result
    pairs=[]
    for first,second in combinations(drivers,2):
        a,aa=drivers[first];b,ba=drivers[second]
        knots=sorted({t for axes in (aa,ba) for _,progress in axes for t,_ in progress})
        times={0.,1.};moving=False
        for t0,t1 in zip(knots,knots[1:]):
            rel0=[x-y for x,y in zip(position(aa,t0),position(ba,t0))]
            rel1=[x-y for x,y in zip(position(aa,t1),position(ba,t1))]
            travel=math.dist(rel0,rel1);moving|=travel>1e-12
            n=max(1,math.ceil(travel/max_relative_step_mm))
            times.update(t0+(t1-t0)*i/n for i in range(n+1))
        if not moving: continue
        hit=None;minimum_gap=math.inf
        for t in sorted(times):
            sa=a.translate(position(aa,t));sb=b.translate(position(ba,t))
            volume=sa.intersect(sb).Volume()
            if volume>volume_tolerance_mm3:
                hit=dict(time=t,intersection_mm3=volume);break
            minimum_gap=min(minimum_gap,sa.distance(sb))
        pairs.append(dict(first=first,second=second,samples_planned=len(times),
            first_sampled_overlap=hit,minimum_sampled_gap_mm=None if minimum_gap==math.inf else minimum_gap))
    return dict(ok=all(p['first_sampled_overlap'] is None for p in pairs),pairs=pairs,
        max_relative_step_mm=max_relative_step_mm,volume_tolerance_mm3=volume_tolerance_mm3,
        scope='Whole-part translations only; no overlap detected at sampled poses is not continuous-path proof. '
              'Static relative pairs and partial-region constraints are excluded. This does not test flexible contact.')
