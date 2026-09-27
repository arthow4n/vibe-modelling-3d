"""Inspection-only scene, card clearance checks and native vector comparison.
Never export/print result: it includes reference postcards.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import cadquery as cq
from cadquery.occ_impl.exporters.svg import getSVG
import cairosvg
from postcard_display import BASE_HEIGHT, SLOT_GAP, LEAN_DEG, SLOPE
from style_variants import wave
from sculptural_variants import BUILDERS


def card(w,h,t):
    return (cq.Workplane('XY').box(w,t,h).translate((0,-t/2,h/2))
            .rotate((0,0,0),(1,0,0),-LEAN_DEG)
            .translate((0,SLOT_GAP,BASE_HEIGHT))).val()


models = {name.title():builder().val() for name,builder in BUILDERS.items()}
scene = []
for i,(name,shape) in enumerate(models.items()):
    for w,h in [(105,148),(148,105),(100,150),(150,100)]:
        for t in [0.2,0.8]:
            assert shape.intersect(card(w,h,t)).Volume() < 1e-7,(name,w,h,t)
    for j,(w,h) in enumerate([(105,148),(148,105)]):
        offset = (i*180,0,j*180)
        scene.extend([shape.translate(offset),card(w,h,0.4).translate(offset)])
result = cq.Compound.makeCompound(scene)


def comparison():
    shapes = {'Wave (existing)':wave().val(),**models}
    captions = ['Reference: slender curved arms','Circular body / crowned opening',
                'Single folded lightning spine','Low, broad rounded body']
    board = ['<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="540" viewBox="0 0 1280 540">',
             '<rect width="1280" height="540" fill="#f8f7f3"/>',
             '<g font-family="sans-serif" fill="#263c40"><text x="32" y="42" font-size="25">Three new silhouettes</text>',
             '<text x="32" y="70" font-size="15">Wave shown for comparison · front is left · same scale · dashed line indicates card plane</text></g>']
    for i,((name,shape),caption) in enumerate(zip(shapes.items(),captions)):
        drawing = ET.fromstring(getSVG(shape.rotate((0,0,0),(1,0,0),90),opts={
            'projectionDir':(1,0,0),'showHidden':False,'showAxes':False}))
        paths = drawing.findall('.//{http://www.w3.org/2000/svg}path')
        board.append(f'<g transform="translate({40+i*315},400) scale(4,-4)" fill="none" stroke="#263c40" stroke-width="0.45">')
        board.append(f'<path d="M {SLOT_GAP} {BASE_HEIGHT} L {SLOT_GAP+(70-BASE_HEIGHT)*SLOPE} 70" stroke="#9caaa9" stroke-width="0.3" stroke-dasharray="1.4,1.4"/>')
        for path in paths:
            board.append(f'<path d="{path.attrib["d"]}"/>')
        board.append('</g>')
        board.append(f'<g font-family="sans-serif" fill="#263c40"><text x="{32+i*315}" y="457" font-size="22">{name}</text><text x="{32+i*315}" y="485" font-size="14">{caption}</text></g>')
    board.append('</svg>')
    output = Path(__file__).parent/'renders'/'sculptural_comparison.svg'
    output.write_text('\n'.join(line.rstrip() for line in '\n'.join(board).splitlines())+'\n')
    cairosvg.svg2png(url=str(output),write_to=str(output.with_suffix('.png')))


comparison()
