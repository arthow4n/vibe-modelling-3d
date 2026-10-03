import cadquery as cq
shape=cq.Workplane('XY').box(10,10,10).cut(cq.Workplane('XY').sphere(4)).val()
assert shape.isValid()
print(round(shape.Volume(),6))
