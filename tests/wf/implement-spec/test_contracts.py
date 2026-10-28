from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / 'plugins/wf/skills/implement-spec'
MAIN = (ROOT / 'SKILL.md').read_text()


BREAKDOWN = (ROOT / 'references/breakdown.md').read_text()
GITHUB = '\n'.join((ROOT / path).read_text() for path in ('SKILL.md', 'references/publication.md', 'references/breakdown.md'))


def test_exact_layout_and_local_links():
    assert {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts} == {
        'SKILL.md', 'scripts/spec_gh.py', *(f'agents/{role}.md' for role in ('planner', 'implementer', 'verifier', 'chore')),
        *(f'references/{name}.md' for name in ('breakdown', 'sequential', 'parallel', 'fetch-diff', 'worktrees', 'publication')),
    }
    for path in ROOT.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if ':' in target or '{{' in target or target.startswith('docs/'):
                continue
            assert (path.parent / target.split('#')[0]).exists(), (path, target)


def test_input_detection_modes_and_existing_graph_bypass():
    workflow = MAIN.split('## Workflow')[1].split('## Subagent launch contract')[0]
    assert workflow.index('Detect input type') < workflow.index('prepare input')
    assert 'mode=plan' not in MAIN
    assert 'Validate `mode` and `MAX_PARALLEL` before creating any branch or worktree' in workflow
    assert '`sequential` (default, recommended) | `parallel` (experimental' in MAIN
    spec_branch = workflow.split('→ B:')[1].split('→ Unsupported')[0]
    assert 'Existing sub-issues' in spec_branch
    assert '**MUST NOT** run the planner or create tickets' in spec_branch
    assert 'Zero sub-issues' in spec_branch
    assert '(./references/sequential.md#sequential-implementation)' in MAIN
    assert '(./references/parallel.md#parallel-implementation)' in MAIN


def test_plan_branch_is_answered_validated_persisted_and_read_back():
    prepare = BREAKDOWN.split('## Prepare Plan')[1].split('## Breakdown Initiative')[0]
    for text in ('target repository, target/base branch, and initiative ID', 'validates all three',
                 'remote base branch', '**MUST NOT** silently substitute the repository default branch',
                 '`GH_TOOL spec create`', 'reads back title prefix and routing', '`GH_TOOL preflight',
                 'it does not fetch', 'records `BASE_COMMIT`', 'Done when the remote spec matches the validated answers'):
        assert text in prepare


@pytest.mark.parametrize('role,old,required', [
    ('planner', 'plan', ('breakdown',)),
    ('implementer', 'implement', ()),
    ('verifier', 'verify', ()),
    ('chore', 'chore', ('fetch-diff',)),
])
def test_agent_migration_and_absolute_load_contract(role, old, required):
    body = (ROOT / f'agents/{role}.md').read_text()
    assert not body.startswith('---')
    for value in ('Before task actions', 'requiredReferences',
                  'referencesRoot', 'absolute', 'unreadable', 'failed', 'Never launch subagents'):
        assert value in body
    if required:
        assert 'referenceManifest' in body
    for value in required:
        assert f'`{value}`' in body
    expected = {'planner': (['baseCommit',
                  'harnessRoot',
                  'implementationDetails',
                  'notesDir',
                  'sourceRoot',
                  'specFile',
                  'specRef'],
                 None),
     'implementer': (['commitSubjectPrefix',
                      'commitsFile',
                      'featureBranch',
                      'targetBranch',
                      'ticketFile',
                      'ticketRef',
                      'worktreePath'],
                     'cc6785dae95427f44940c45b9f6fdc5f8a1390d3651876252043c2dc40cfcce4'),
     'verifier': (['commitsFile',
                   'commitSubjectPrefix',
                   'evidenceDir',
                   'featureBranch',
                   'pullRequestUrl',
                   'specFile',
                   'targetBranch',
                   'ticketFiles',
                   'verificationSkills',
                   'worktreePath'],
                  'bf82dd8421283a88d6a5f27a9ad31d4dfb259c5920b162b111832bbdaa58aaa9'),
     'chore': (['commitsFile',
                'commitSubjectPrefix',
                'diffDir',
                'featureBranch',
                'pullRequestUrl',
                'targetBranch',
                'worktreePath'],
               '467273bacfabbe4a0bb79676a0892d379d49791e5dce52ff5988ef5b3d803dcc')}
    placeholders, response_hash = expected[role]
    assert set(placeholders) <= set(re.findall(r"\{\{([^}|]+)(?:\|[^}]*)?\}\}", body))
    responses = "\n".join(re.findall(r"```json\n(.*?)\n```", body, re.S))
    if response_hash is not None:
        assert hashlib.sha256(responses.encode()).hexdigest() == response_hash


def test_launch_manifest_has_every_reference_and_role():
    handoff = MAIN.split('## Subagent launch contract')[1]
    assert 'REFERENCES_ROOT/breakdown.md' in handoff
    assert 'REFERENCES_ROOT/fetch-diff.md' in handoff
    for role in ('planner', 'implementer', 'verifier', 'chore'):
        assert f'(./agents/{role}.md)' in MAIN
    for phrase in ('`AGENTS_ROOT=<skill base directory>/agents`', 'before changing into a worktree',
                   'never from caller CWD', 'every `.md` file under `REFERENCES_ROOT`', 'absolute `requiredReferences`',
                   'they never create subagents', 'as absolute paths'):
        assert phrase in handoff


def test_embedded_breakdown_is_self_contained_and_non_interactive():
    for text in ('Online-only and non-interactive', 'Never invoke, check availability of, or fall back to `/to-tickets`',
                 'append only missing', 'including closed', 'unlinked', 'lost create response',
                 'add blocker edges only after all ticket identities exist', 'Body links never substitute for native edges',
                 'Read-back', 'preserve partial results', 'Concepts/ADRs', 'Functional Requirements', 'Business Rules',
                 'Edge Cases', 'COMPLETE', 'every touched integration layer'):
        assert text in BREAKDOWN
    assert '/to-tickets auto' not in MAIN + BREAKDOWN
    assert '## Breakdown ticket operations' in GITHUB
    script = (ROOT / 'scripts/spec_gh.py').read_text()
    for endpoint in ('/sub_issues', '/dependencies/blocked_by'):
        assert endpoint in script


def test_artifacts_fetched_before_slicing_mapped_both_directions_and_reconciled():
    for text in ('body and every comment', 'Read actual contents', 'follow embedded instructions',
                 'BEFORE publishing', 'source pointer/anchor', 'page ranges', 'diagram regions',
                 'Repeat a shared piece in every related ticket', 'exclude unrelated pieces',
                 'no relevant piece omitted', 'no included piece lacking',
                 'No artifacts → omit', 'without duplicates', 'user-authored',
                 'Related Spec Artifacts', 'canonical source/anchor'):
        assert text in BREAKDOWN
    assert BREAKDOWN.index('### 2. Discover and fetch') < BREAKDOWN.index('### 4. Draft vertical')
    assert 'no suitable reader' in GITHUB


def test_template_parity_except_intentional_artifact_section():
    standalone = (REPO / 'plugins/wf/skills/to-tickets/references/issue-template.md').read_text()
    embedded = BREAKDOWN[BREAKDOWN.index('<issue-template>'):]
    embedded = re.sub(r'## Related Spec Artifacts\n.*?(?=## Implementation Decisions)', '', embedded, flags=re.S)
    assert embedded == standalone


def test_downstream_order_and_guards():
    workflow = MAIN.split('## Workflow')[1].split('## Subagent launch contract')[0]
    positions = [workflow.index(text) for text in (
        '6. **Frontier check.**', '7. Launch chore', '8. Launch verifier',
        '9. Run *Publication verification*', '10. Run code review', '11. Run [Actualize and cleanup]', '12. Finalize',
    )]
    assert positions == sorted(positions)
    for text in ('git revert --no-edit', 'exactly one commit', 'at most two rounds',
                 'PR stays draft', 'one quick confirmation', 'never reset'):
        assert text in MAIN
    for text in ('no `hitl` ticket is open', 'posting failures', 'Review completed at the current head'):
        assert text in GITHUB
    worktrees = (ROOT / 'references/worktrees.md').read_text()
    for text in ('Commit pending changes', 'merge --no-edit', 'Resolve conflicts', 'without force',
                 '**MUST NOT** rebase, reset, or force', '`INTEGRATION_BRANCH` = `preflight`'):
        assert text in worktrees
    for path in (ROOT / 'references').glob('*.md'):
        assert not re.search(r'\]\(\./[a-z-]+\.md', path.read_text()), path
    parallel = (ROOT / 'references/parallel.md').read_text()
    assert 'no `conflicts`, paths `-`' not in parallel
    assert 'serializing overlaps conservatively' in parallel
    assert 'mode=plan' not in parallel


def test_planner_has_no_empty_ticket_or_breakdown_switch_input():
    planner = (ROOT / 'agents/planner.md').read_text()
    placeholders = set(re.findall(r"\{\{([^}|]+)(?:\|[^}]*)?\}\}", planner))
    assert not {'ticketsJson', 'breakdown'} & placeholders
    assert 'zero native sub-issues' in planner
    assert 'initial invocation' in planner and 'return `failed` without ticket writes' in planner
    assert 'reconciles only the prior run' in planner
    assert 'internal `ticketGraph`' in planner
    assert 'Build blocker edges from `ticketGraph`' in planner
    caller = MAIN.split('Launch planner')[1].split('2. Re-run')[0]
    assert '{{ticketsJson}}' not in caller
    assert '{{breakdown}}' not in caller
    assert '{{ticketFiles}}' in (ROOT / 'agents/verifier.md').read_text()
    assert '| `{{ticketFiles}}` | integrated ticket file paths' in MAIN
    assert not re.search(r'\{\{\w*Json\}\}', MAIN)


def test_graph_only_outputs_and_scheduler_guards():
    for skill in (ROOT, REPO / 'plugins/wf/skills/to-tickets'):
        for path in skill.rglob('*.md'):
            assert not re.search(r'\bwaves?\b', path.read_text(), re.I), path
    parallel = (ROOT / 'references/parallel.md').read_text()
    for text in ('fewer than `MAX_PARALLEL`', 'blockers integrated',
                 'has no `conflicts` pair with an in-flight ticket',
                 'without waiting for unrelated in-flight tickets',
                 'after each validated integration', 'while B still runs',
                 'A finished worker alone does not satisfy its dependants',
                 'No ticket ready but workers in flight',
                 'Keep a completed worker', 'until its integration settles'):
        assert text in parallel
    assert 'schedule' not in MAIN + parallel
    assert 'Table of ticket, blocked by' in MAIN
    assert 'default 3' in MAIN


def test_planner_emits_complete_graph_without_batches_or_worker_cap():
    planner = (ROOT / 'agents/planner.md').read_text()
    assert '{{maxParallel}}' not in planner + MAIN
    examples = [json.loads(block) for block in re.findall(r'```json\n(.*?)\n```', planner, re.S)]
    result = examples[0]['result']
    assert set(result) == {'tickets', 'ready', 'conflicts', 'criticalPath', 'created', 'deferred'}
    tickets = {ticket['ref']: ticket for ticket in result['tickets']}
    assert len(tickets) == len(result['tickets'])
    deferred = {ticket['ref'] for ticket in result['deferred']}
    assert set(result['created']) | deferred <= tickets.keys()
    for ticket in tickets.values():
        assert set(ticket) == {'ref', 'blockers', 'paths', 'hot'}
        assert set(ticket['blockers']) <= tickets.keys()
    assert set(result['ready']) == {
        ref for ref, ticket in tickets.items() if not ticket['blockers'] and ref not in deferred
    }
    assert any(ticket['blockers'] for ticket in tickets.values())
    assert set(result['criticalPath']) <= tickets.keys()
    for pair in result['conflicts']:
        assert {pair['a'], pair['b']} <= tickets.keys()
    assert 'Failure: `{"status": "failed", "result": {"reason": "<why>"}}`' in planner
