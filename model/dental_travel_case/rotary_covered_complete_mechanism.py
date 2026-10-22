"""Complete solid control kit: keyed wheel, facecap, longer screw and printed nut."""
from rotary_covered_design import covered_case,mechanism_layout
result=mechanism_layout(covered_case(),include_nut=True)
