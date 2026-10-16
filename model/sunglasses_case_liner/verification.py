"""Shared verification command for the S16 accessory; no inherited print PASS."""
from product_verification import (UserRequirement as U, UserSource as S, Question as Q,
    Plan, DesignDecision, assertion_check, cli)

RECORD = 'README.md'
REQUIREMENTS = (
    U('liner.retrofit','Add a liner to the already printed sunglasses case',
      S(RECORD+'#intent','User reports existing case printed with sufficient room and requests a printable damping liner adapter')),
    U('liner.profile','Use the user-preferred printed S16 damping profile',
      S(RECORD+'#intent','User selects S16 and requests its adaptation to the sunglasses case')),
    U('liner.damping','Damp sunglasses contact in the existing box',
      S(RECORD+'#intent','User requests damping of the already printed sunglasses box')),
)
QUESTIONS = (
    Q('fit','liner.retrofit','Nominal inserts clear the complete existing case and have a sampled installation route','CAD'),
    Q('motion','liner.retrofit','Installed inserts clear one another and rigid mechanisms during sampled opening/closing','CAD'),
    Q('use','liner.retrofit','Actual inserts fit, remain attached, permit closure and leave room for the user glasses','physical'),
    Q('profile','liner.profile','Preserve S16 local skins/core/ribs/pitch and continuous floor/wall contact faces','CAD'),
    Q('quiet','liner.damping','User finds the lined sunglasses case sufficiently quiet in use','subjective'),
)


def make_plan(variant):
    if variant != 's16-retrofit':
        raise ValueError(variant)
    import checks
    scope = {'design':variant,'shell':'accepted-e-158x78x63','liner':'TPU','physical':'unreported'}
    runs = (('liner.profile','liner.profile','profile',checks.check_profile),
            ('liner.fit','liner.retrofit','fit',checks.check_fit),
            ('liner.motion','liner.retrofit','motion',checks.check_motion))
    return Plan(variant,REQUIREMENTS,scope,
        tuple(assertion_check(id,((req,q),),run,'checks.py#'+run.__name__,scope)
              for id,req,q,run in runs), questions=QUESTIONS,
        decisions=(DesignDecision('liner.attachment',
            'Two identical rounded cups, 0.2 mm lateral allowance, thin removable tape under flat backing; physical adhesion remains unqualified',RECORD+'#installation'),))


if __name__ == '__main__':
    raise SystemExit(cli(make_plan,('s16-retrofit',)))
