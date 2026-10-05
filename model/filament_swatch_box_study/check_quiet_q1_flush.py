"""Q1F closure/card/key checks plus the previously severed port connections.

The connectivity check addresses an observed rough-CAD defect: both key routes
cut the sleeve in two. Failure must reject a one-insert print/assembly claim.
"""
import quiet_q1_flush as q
import hashlib
import math
from pathlib import Path
from check_quiet_q1 import main
from quiet_assembly import QuietAssembly

def local_checks(model):
    """Q1F-only topology and thin-rim screens, using the shared actual insert."""
    assert model.model is q
    assert len(model.insert.Solids())==1, 'Port notches sever the one-piece TPU insert'
    p=q.archive.r1
    dx=q.CORE_X/2-q.CORE_R-(p.POCKET_WIDTH/2-p.POCKET_RADIUS)
    dy=q.CORE_Y/2-q.CORE_R-(p.POCKET_DEPTH/2-p.POCKET_RADIUS)
    corner_crest=q.CORE_R-p.POCKET_RADIUS-q.archive.ENTRY_EXPANSION-math.hypot(dx,dy)-2*q.RIM_RADIUS
    assert corner_crest>=.8, 'Flared and rounded corner crest becomes too thin for this plan'
    port_crest=(q.PORT_BYPASS_Y-q.PORT_BYPASS_DEPTH/2-q.SEAT_RECESS_GAP
                -p.POCKET_DEPTH/2-q.archive.ENTRY_EXPANSION-q.RIM_RADIUS-q.ACCESS_EDGE_BREAK)
    assert port_crest>=.8, 'Access channel and entrance flare leave too little rim'
    return dict(one_connected_insert_after_port_cuts=True,
        conservative_rounded_entrance_corner_crest_screen_mm=corner_crest,
        access_channel_entrance_crest_screen_mm=port_crest,
        existing_G_hood_builder_reused=True,
        unchanged_nominal_foot_mm=[q.FOOT_X,q.FOOT_Y],
        unchanged_nominal_hood_mm=[q.HOOD_X,q.HOOD_Y,q.g.ROOF_TOP],
        q1f_local_checks_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__=='__main__':
    model=QuietAssembly(q)
    main(q, 'quiet_q1_flush_checks.json',model=model,extra=local_checks(model))
