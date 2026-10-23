"""Shared verification contract for the full slim-M1 S16 accessory."""
from product_verification import UserRequirement as U, UserSource as S, Question as Q, Plan, DesignDecision, assertion_check, cli

REQUIREMENTS=(
    U('liner.retrofit','Line the existing printed slim dental travel box',S('README.md#intent','User requests a sound damping liner for the recently printed slim dental box')),
    U('liner.full','Use full S16 coverage',S('README.md#intent','User confirms there is room and selects the full S16 liner')),
    U('liner.quiet','Reduce contents impact noise',S('README.md#intent','User requests sound damping')),
)
QUESTIONS=(
    Q('fit','liner.retrofit','Installed liners clear the complete rigid cups, moving catches and sampled cap withdrawal','CAD'),
    Q('installation','liner.retrofit','Flexible insertion, retention, access and actual contents fit work in the printed box','physical'),
    Q('profile','liner.full','Preserve S16 flat profile and continuous end skins in two connected cups','CAD'),
    Q('corners','liner.full','Ordinary wall bends and guard-region perimeters retain air cores','CAD'),
    Q('noise','liner.quiet','User finds the lined box sufficiently quieter','subjective'),
)


def make_plan(variant):
    if variant=='rotary-l20-uniform':
        from rotary_l20_uniform_verification import make_plan as uniform_plan
        return uniform_plan(variant)
    if variant=='rotary-l20':
        from rotary_l20_verification import make_plan as current_plan
        return current_plan(variant)
    if variant!='slim-m1-s16':
        raise ValueError(variant)
    import checks
    scope={'design':variant,'rigid_case':'narrow-m1-74.2mm','material':'TPU95A-assumed','print':'unreported'}
    groups=(('fit','liner.retrofit','fit',checks.check_fit),
            ('profile','liner.full','profile',checks.check_profile),
            ('corners','liner.full','corners',checks.check_perimeters))
    return Plan(variant,REQUIREMENTS,scope,
        tuple(assertion_check(id,((req,q),),run,'checks.py#'+run.__name__,scope) for id,req,q,run in groups),
        questions=QUESTIONS,decisions=(DesignDecision('attachment','Two conformal cups; flexible installation and thin removable tape remain physical checks','README.md#installation'),))


if __name__=='__main__':
    raise SystemExit(cli(make_plan,('slim-m1-s16','rotary-l20','rotary-l20-uniform')))
