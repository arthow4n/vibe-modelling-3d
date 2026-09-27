"""Inspection scene and reproducible side-profile comparison, never print this scene.
Checks seated-card clearance at the supported size/thickness extremes.
"""
from pathlib import Path
import cadquery as cq
from cadquery.occ_impl.exporters.svg import getSVG
import cairosvg
from postcard_display import build, BASE_HEIGHT, SLOT_GAP, LEAN_DEG
from style_variants import BUILDERS


def card(width, height, thickness):
    return (cq.Workplane('XY').box(width,thickness,height)
            .translate((0,-thickness/2,height/2))
            .rotate((0,0,0),(1,0,0),-LEAN_DEG)
            .translate((0,SLOT_GAP,BASE_HEIGHT))).val()


models = {'Original':build().val()}
models.update({name.title():builder().val() for name,builder in BUILDERS.items()})
scene = []
for i,(name,shape) in enumerate(models.items()):
    if name != 'Original':
        for w,h in [(105,148),(148,105),(100,150),(150,100)]:
            for t in [0.2,0.8]:
                assert shape.intersect(card(w,h,t)).Volume() < 1e-7, (name,w,h,t)
    # Portrait above landscape in the renderer's front projection.
    for j,(w,h) in enumerate([(105,148),(148,105)]):
        offset = (i*180,0,j*180)
        scene.extend([shape.translate(offset),card(w,h,0.4).translate(offset)])
result = cq.Compound.makeCompound(scene)

if __name__ == '__main__':
    # Native vector side views, rolled upright for a readable comparison board.
    # This transform affects illustration geometry only, never print geometry.
    captions = ['Solid practical gusset','Open architectural frame',
                'Soft curved arms','Tapered sculptural facets']
    board = ['<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="580" viewBox="0 0 1280 580">',
             '<rect width="1280" height="580" fill="#f8f7f3"/>',
             '<g font-family="sans-serif" fill="#263c40"><text x="32" y="42" font-size="25">Postcard display — four side profiles</text>',
             '<text x="32" y="70" font-size="15">Original retained + three printable alternatives · front is left · same scale</text></g>']
    for i,((name,shape),caption) in enumerate(zip(models.items(),captions)):
        svg = getSVG(shape.rotate((0,0,0),(1,0,0),90),opts={
            'width':280,'height':370,'projectionDir':(1,0,0),'showHidden':False,
            'showAxes':False,'strokeWidth':0.6,'strokeColor':(38,60,64),
            'marginLeft':15,'marginTop':15})
        svg = svg[svg.index('<svg'):]
        board.append(f'<g transform="translate({20+i*315},110)">{svg}</g>')
        board.append(f'<g font-family="sans-serif" fill="#263c40"><text x="{32+i*315}" y="510" font-size="22">{name}</text><text x="{32+i*315}" y="537" font-size="14">{caption}</text></g>')
    board.append('</svg>')
    folder = Path(__file__).parent/'renders'
    vector = folder/'style_comparison.svg'
    vector.write_text('\n'.join(line.rstrip() for line in '\n'.join(board).splitlines())+'\n')
    cairosvg.svg2png(url=str(vector),write_to=str(folder/'style_comparison.png'))
