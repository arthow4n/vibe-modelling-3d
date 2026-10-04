"""Four optional printed TPU pads; flat base down. TPU slicing remains user-specific."""
import v3_components as d
result=d.compound([d.foot().translate((x,y,0)) for x in (30,60) for y in (30,55)])
show_object(result)
