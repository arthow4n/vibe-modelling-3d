"""Nominal grip-zone layout and prescribed cap travel, independent of grasp IK.

This selects a concept location. It does not model skin, force or finished band
CAD. Dimensions use the same constructor/overlap as build_three_line; its local
backing ends lap+9 mm above the seam (short_lap_thin.py's axial pad blend).
"""
from dataclasses import dataclass, asdict
import math
import short_lap_design
from short_lap_thin import OVERLAP, WALL


@dataclass(frozen=True)
class GripLayout:
    cap_center_mm: float
    body_center_mm: float
    band_width_mm: float
    depth_mm: float

    def __post_init__(self):
        if not all(math.isfinite(v) for v in asdict(self).values()):
            raise ValueError('Finite layout dimensions required')
        if self.band_width_mm<=0 or self.depth_mm<=0:
            raise ValueError('Positive band width/depth required')


LAYOUTS={
    'near':GripLayout(40.,-15.,20.,.7),
    'previous':GripLayout(50.,-30.,20.,.7),
    'selected':GripLayout(55.,-30.,20.,.7),
    'far':GripLayout(65.,-50.,20.,.7),
}


def dimensions():
    # The thin builder overrides wall/fit details, but retains these external
    # dimensions, end radius, cap length and selected overlap unchanged.
    return short_lap_design.dimensions(OVERLAP)


def describe(layout,d):
    half=layout.band_width_mm/2
    cap=(layout.cap_center_mm-half,layout.cap_center_mm+half)
    body=(layout.body_center_mm-half,layout.body_center_mm+half)
    cap_length=d.length-d.seam
    backing_end=d.lap+9.
    gap=cap[0]-body[1]
    metrics=dict(cap_extent_mm=cap,body_extent_mm=body,
        sleeve_end_mm=d.lap,backing_end_mm=backing_end,cap_length_mm=cap_length,
        cap_backing_gap_mm=cap[0]-backing_end,cap_sleeve_gap_mm=cap[0]-d.lap,
        cap_closed_end_gap_mm=cap_length-cap[1],
        cap_end_round_gap_mm=cap_length-d.end_radius-cap[1],
        body_seam_gap_mm=-body[1],body_bottom_round_gap_mm=d.seam+body[0]-d.end_radius,
        axial_band_gap_mm=gap,center_separation_mm=layout.cap_center_mm-layout.body_center_mm,
        local_inner_width_mm=d.width-2*WALL-2*layout.depth_mm,
        local_inner_depth_mm=d.depth-2*WALL-2*layout.depth_mm)
    checks=dict(cap_beyond_backing=metrics['cap_backing_gap_mm']>=0.,
        cap_beyond_sleeve=metrics['cap_sleeve_gap_mm']>=0.,
        cap_before_end_round=metrics['cap_end_round_gap_mm']>=0.,
        body_below_seam=metrics['body_seam_gap_mm']>=0.,
        body_above_bottom_round=metrics['body_bottom_round_gap_mm']>=0.,
        distinct_band_zones=gap>=0.,
        positive_inward_section=min(metrics['local_inner_width_mm'],metrics['local_inner_depth_mm'],d.corner-WALL-layout.depth_mm)>0.)
    # Body stays still and the cap hand follows the cap. The zones separate
    # analytically by gap+lift; these are nominal zone positions, not hand poses.
    travel=[dict(cap_lift_mm=t,axial_band_gap_mm=gap+t,
        cap_center_mm=layout.cap_center_mm+t,body_center_mm=layout.body_center_mm)
        for t in (0.,6.,d.lap,cap_length)]
    return dict(layout=asdict(layout),metrics=metrics,checks=checks,travel=travel,
        accepted=all(checks.values()),scope='Nominal band zones and prescribed axial motion; no anatomical grasp, force, packing or print qualification')


def selected_layout():
    return describe(LAYOUTS['selected'],dimensions())
