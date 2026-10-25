"""D print layout, with separate native assembled/open/cutaway inspections."""
from d_design import print_layout, inspection
inspections={state:(lambda state=state:inspection(state))
             for state in ('closed','open','assembly','section')}
if __name__ in ('__main__','__cqgi__'):
    result=print_layout()
