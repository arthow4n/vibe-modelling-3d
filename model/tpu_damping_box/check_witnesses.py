"""Negative CAD controls: missing skins, shifted fit and filled channels fail."""
import cadquery as cq
import design as d
from checks import candidate, fit_checks, skin_checks, core_checks, closure_checks, no_overlap


def must_reject(label, run):
    try:
        run()
    except AssertionError:
        print(f'{label}: correctly rejected')
    else:
        raise AssertionError(f'Broken fixture accepted: {label}')


def main():
    body,cup,pad=candidate('C')
    parts=(body,cup,pad)
    fit_checks(parts)
    skin_checks(parts)
    core_checks('C',parts)
    closure_checks(body)
    wrong_lid=d.lid_print().rotate((0,0,0),(1,0,0),180).translate((0,0,d.BODY_HEIGHT+d.LID_THICKNESS))
    x,y=d.SCREW_CENTRES[0]
    shaft=cq.Workplane('XY').center(x,y).circle(1.5).extrude(12).translate((0,0,d.BODY_HEIGHT-8.8))
    must_reject('lid flipped onto wrong screw diagonal',lambda:no_overlap(shaft,wrong_lid))
    must_reject('cup shifted into PETG', lambda:fit_checks((body,cup.translate((1,0,0)),pad)))
    missing_floor=cup.cut(d.block(26,26,0.8,3.2))
    must_reject('floor skin missing',lambda:skin_checks((body,missing_floor,pad)))
    missing_roof=pad.cut(d.block(26,26,0.8,d.FLOOR+30))
    must_reject('ceiling skin missing',lambda:skin_checks((body,cup,missing_roof)))
    filled=cup.union(d.block(26,26,2.4,0.8))
    must_reject('CAD channels filled',lambda:core_checks('C',(body,filled,pad)))
    try:
        d.variant_named('typo')
    except ValueError:
        print('unknown variant: correctly rejected')
    else:
        raise AssertionError('Unknown variant silently selected a design')


if __name__=='__main__':
    main()
