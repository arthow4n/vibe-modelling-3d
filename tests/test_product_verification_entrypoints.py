"""Adopted products must follow one shared command contract, including new ones."""
import ast
import inspect
import json
from pathlib import Path
import runpy
import sys

import pytest
import product_verification as pv

ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINTS = tuple(sorted((ROOT / 'model').glob('*/verification.py')))
assert ENTRYPOINTS, 'No adopted product entry points found'


@pytest.mark.parametrize('entrypoint', ENTRYPOINTS, ids=lambda p: p.parent.name)
def test_plan_factory_requires_explicit_variant(entrypoint):
    make_plan = runpy.run_path(str(entrypoint))['make_plan']
    assert inspect.signature(make_plan).parameters['variant'].default is inspect.Parameter.empty
    with pytest.raises(TypeError, match='variant'):
        make_plan()


@pytest.mark.parametrize('entrypoint', ENTRYPOINTS, ids=lambda p: p.parent.name)
def test_entrypoint_delegates_directly_to_shared_cli(entrypoint):
    tree = ast.parse(entrypoint.read_text())
    main_blocks = [node for node in tree.body if isinstance(node, ast.If)
                   and ast.dump(node.test) == ast.dump(ast.parse(
                       "__name__ == '__main__'", mode='eval').body)]
    assert len(main_blocks) == 1, 'Require one standard __main__ entry point'
    block = main_blocks[0]
    assert not block.orelse and len(block.body) == 1
    statement = block.body[0]
    assert isinstance(statement, ast.Raise) and statement.cause is None
    exit_call = statement.exc
    assert isinstance(exit_call, ast.Call) and isinstance(exit_call.func, ast.Name)
    assert exit_call.func.id == 'SystemExit' and len(exit_call.args) == 1 and not exit_call.keywords
    call = exit_call.args[0]
    assert isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
    assert call.func.id == 'cli' and len(call.args) == 2 and not call.keywords
    assert isinstance(call.args[0], ast.Name) and call.args[0].id == 'make_plan'
    assert any(isinstance(node, ast.ImportFrom) and node.module == 'product_verification'
               and any(alias.name == 'cli' and alias.asname is None for alias in node.names)
               for node in tree.body), 'Import the shared cli, without a local wrapper'


def assert_common_protocol(entrypoint, invocation, reason, code, monkeypatch, capsys):
    shared_cli = pv.cli
    calls = []
    builds = []

    # Discover each product's declared names without constructing its plan.
    # A separate probe avoids coupling this guard to a fixed product inventory.
    declarations = []
    def declared(make_plan, variants):
        declarations.append(tuple(variants))
        return 0
    monkeypatch.setattr(pv, 'cli', declared)
    monkeypatch.setattr(sys, 'argv', [str(entrypoint), '--help'])
    with pytest.raises(SystemExit) as probe:
        runpy.run_path(str(entrypoint), run_name='__main__')
    assert probe.value.code == 0 and len(declarations) == 1
    assert not capsys.readouterr().out, 'Only the shared helper may write stdout'
    variants = declarations[0]
    base = ['--variant', variants[0]]
    argv = {'help': ['--help'], 'variant-help': base + ['--help'],
            'missing-variant': [], 'complete': base,
            'failed': base, 'physical-unknown': base, 'inconclusive': base,
            'focused': base + ['--check', 'contract.check'],
            'unknown-check': base + ['--check', 'nonexistent'],
            'extra-option': base + ['--product-specific-option']}[invocation]
    requested_argv = [str(entrypoint), *argv]
    monkeypatch.setattr(sys, 'argv', requested_argv.copy())

    def command(make_plan, declared_variants):
        assert sys.argv == requested_argv, 'Product code must not rewrite shared command arguments'
        assert tuple(declared_variants) == variants
        calls.append((make_plan, declared_variants))

        def lightweight_plan(selected):
            builds.append(selected)
            requirement = pv.UserRequirement('contract.use', 'Contract fixture',
                pv.UserSource(__file__, 'Synthetic conformance fixture; not product intent'))
            scope = {'design': selected}
            evidence = pv.Evidence('contract.check', (('contract.use', 'check'),),
                {'failed': pv.Status.FAIL, 'inconclusive': pv.Status.INCONCLUSIVE}.get(
                    invocation, pv.Status.PASS), 'Fixture result', __file__, scope)
            questions = (pv.Question('check', requirement.id, 'Fixture check succeeds', 'CAD'),)
            checks = (pv.Check('contract.check', evidence.targets, lambda: (evidence,)),)
            if invocation == 'physical-unknown':
                questions += (pv.Question('use', requirement.id, 'Physical use accepted', 'physical'),)
            if invocation == 'focused':
                questions += (pv.Question('other', requirement.id, 'Other obligation', 'CAD'),)
                checks += (pv.Check('contract.omitted', ((requirement.id, 'other'),),
                    lambda: pytest.fail('Focused selection must not run omitted checks')),)
            return pv.Plan(selected, (requirement,), scope, checks, questions=questions)

        return shared_cli(lightweight_plan, declared_variants)

    monkeypatch.setattr(pv, 'cli', command)
    with pytest.raises(SystemExit) as exit:
        runpy.run_path(str(entrypoint), run_name='__main__')
    assert exit.value.code == code
    assert len(calls) == 1 and callable(calls[0][0])
    assert calls[0][0].__name__ == 'make_plan'
    result = json.loads(capsys.readouterr().out)
    assert result['exit_reason'] == reason
    assert result['available_variants'] == list(calls[0][1])
    assert builds == ([] if invocation in ('help', 'missing-variant', 'extra-option')
                      else [calls[0][1][0]])
    assert result['selected_checks'] == (['contract.check'] if invocation == 'focused'
        else ['nonexistent'] if invocation == 'unknown-check' else None)
    if invocation in ('variant-help', 'unknown-check'):
        assert result['available_checks'] == ['contract.check']
    if invocation in ('complete', 'focused', 'failed', 'physical-unknown', 'inconclusive'):
        assert result['report']['variant'] == calls[0][1][0]
        assert result['error'] is None
        expected = {'complete': ['PASS'], 'focused': ['PASS', 'UNKNOWN'],
                    'failed': ['FAIL'], 'physical-unknown': ['PASS', 'UNKNOWN'],
                    'inconclusive': ['INCONCLUSIVE']}[invocation]
        assert [q['status'] for q in result['report']['requirements'][0]['questions']] == expected
        assert result['report']['focused'] == (invocation == 'focused')


@pytest.mark.parametrize('entrypoint', ENTRYPOINTS, ids=lambda p: p.parent.name)
@pytest.mark.parametrize('invocation,reason,code', [
    ('help', 'help_requested', 0),
    ('variant-help', 'help_requested', 0),
    ('missing-variant', 'argument_error', 1),
    ('complete', 'verification_complete', 0),
    ('focused', 'unresolved_evidence', 0),
    ('failed', 'criterion_failed', 0),
    ('physical-unknown', 'unresolved_evidence', 0),
    ('inconclusive', 'unresolved_evidence', 0),
    ('unknown-check', 'argument_error', 1),
    ('extra-option', 'argument_error', 1),
])
def test_entrypoints_follow_common_protocol(entrypoint, invocation, reason, code, monkeypatch, capsys):
    assert_common_protocol(entrypoint, invocation, reason, code, monkeypatch, capsys)


@pytest.mark.parametrize('local_code,invocation,message', [
    ("if len(sys.argv) == 1: sys.argv += ['--variant', 'candidate']",
     'missing-variant', 'must not rewrite'),
    ("sys.argv[:] = [arg for arg in sys.argv if arg != '--product-specific-option']",
     'extra-option', 'must not rewrite'),
    ("print('local output prefix')", 'help', 'Only the shared helper'),
])
def test_conformance_rejects_local_argument_and_output_overrides(local_code, invocation, message,
                                                               tmp_path, monkeypatch, capsys):
    entrypoint = tmp_path / 'verification.py'
    entrypoint.write_text("import sys\nfrom product_verification import cli\n"
        "def make_plan(variant): pass\n" + local_code + "\n"
        "if __name__ == '__main__':\n"
        "    raise SystemExit(cli(make_plan, ('candidate',)))\n")
    with pytest.raises(AssertionError, match=message):
        assert_common_protocol(entrypoint, invocation, 'argument_error', 1, monkeypatch, capsys)
