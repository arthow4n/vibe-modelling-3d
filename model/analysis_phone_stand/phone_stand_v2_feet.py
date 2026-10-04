from v2_components import soft_foot,compound
result=compound([soft_foot().translate((x,y,0)) for x in (30,60) for y in (30,56)])
