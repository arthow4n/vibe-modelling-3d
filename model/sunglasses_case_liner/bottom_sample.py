"""Rib-bounded S16 bottom-panel crop for ironing off/on comparison.

The approximately 2 cm square finishes at the outer faces of two complete ribs,
so the top skin has no cut-edge cantilever. Keep the supplied orientation.
"""
import design as d

RIB_INTERVALS = 4
SAMPLE_SIZE = RIB_INTERVALS*d.PITCH+d.WEB  # 18.5 mm: four complete air pockets.
result = d.cup().intersect(d.block(SAMPLE_SIZE,SAMPLE_SIZE,d.THICKNESS)).clean()

# Check the actual crop's two bridge-end ribs, rather than only a nominal size.
for sign in (-1,1):
    edge_rib=d.block(d.WEB-.1,SAMPLE_SIZE-.2,d.CORE-.1,
        x=sign*(SAMPLE_SIZE/2-d.WEB/2),z=d.BACKING+.05)
    assert edge_rib.cut(result).val().Volume()<1e-6, 'Sample edge lacks continuous rib support'
