"""Finger-contact finishing, leaving functional snap/guide faces alone."""
import cadquery as cq
import m1_design as base

GRIP_EDGE_RADIUS = .4


def finish(parts):
    d = parts['dimensions']
    edges = []
    for edge in parts['cap'].val().Edges():
        bounds = edge.BoundingBox()
        center = edge.Center()
        if (bounds.xmin < -10.001 or bounds.xmax > 10.001 or
                bounds.zmax > d.seam+3.001 or abs(center.y) < 20):
            continue
        # Both cut contours, plus the sharp inward junctions with the open rim.
        # Omit smooth seams joining the cutter's rounded profile faces.
        if bounds.ylen < 1e-6 or (abs(abs(center.x)-10) < 1e-5 and bounds.zmax < d.seam+.601):
            edges.append(edge)
    assert len(edges) == 28, 'Both complete inside/outside finger-notch boundaries required'
    cap = parts['cap'].newObject(edges).fillet(GRIP_EDGE_RADIUS).clean()
    result = cq.Assembly(name='comfortable_short_lap_pair')
    result.add(parts['body'],name='body')
    result.add(base.print_cap(cap,d.length),name='cap')
    return dict(parts,cap=cap,result=result)
