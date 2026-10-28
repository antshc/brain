from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / 'plugins/wf/skills/implement-spec'
MAIN = (ROOT / 'SKILL.md').read_text()
GITHUB_FILES = ('setup', 'graph', 'publication', 'finalize')


def _joined(folder: str, names: tuple[str, ...]) -> str:
    return '\n'.join((ROOT / f'references/{folder}_{name}.md').read_text() for name in names)


BREAKDOWN = (ROOT / 'references/breakdown.md').read_text() + (ROOT / 'references/ticket-body-template.md').read_text()
GITHUB = _joined('github', GITHUB_FILES)


def test_exact_layout_and_local_links():
    assert {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()} == {
        'SKILL.md', *(f'agents/{role}.md' for role in ('planner', 'implementer', 'verifier', 'chore')),
        *(f'references/{name}.md' for name in ('breakdown', 'ticket-body-template', 'sequential', 'parallel', 'fetch-diff', 'worktrees')),
        *(f'references/github_{name}.md' for name in GITHUB_FILES),
    }
    for path in ROOT.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if ':' in target or '{{' in target or target.startswith('docs/'):
                continue
            assert (path.parent / target.split('#')[0]).exists(), (path, target)


def test_input_detection_modes_and_existing_graph_bypass():
    workflow = MAIN.split('## Workflow')[1].split('## Subagent launch contract')[0]
    assert workflow.index('Detect input type first') < workflow.index('Prepare input')
    assert 'mode=plan' not in MAIN
    assert 'Validate `mode` and `MAX_PARALLEL` before creating any branch or worktree' in workflow
    assert '`sequential` (default) | `parallel`' in MAIN
    prepare = BREAKDOWN.split('## Prepare Spec')[1].split('## Breakdown Initiative')[0]
    assert 'Existing sub-issues' in prepare and 'MUST NOT' in prepare
    assert 'run the planner or create tickets' in prepare
    assert 'Zero sub-issues' in prepare
    assert '(./references/sequential.md#sequential-implementation)' in MAIN
    assert '(./references/parallel.md#parallel-implementation)' in MAIN


def test_plan_branch_is_answered_validated_persisted_and_read_back():
    create = GITHUB.split('## Create spec')[1].split('## Read the task graph')[0]
    for text in ('target/base branch', 'all three answers', 'branches/BASE_BRANCH',
                 'Fetch that exact remote branch', 'source checkout',
                 'repo:base:BASE_BRANCH', 'Read back title, labels, body', 'MUST NOT'):
        assert text in create
    assert 'BASE_BRANCH` = `gh repo view' not in create


@pytest.mark.parametrize('role,old,required', [
    ('planner', 'plan', ('breakdown', 'ticket-body-template', 'github_setup')),
    ('implementer', 'implement', ('github_setup',)),
    ('verifier', 'verify', ('github_setup',)),
    ('chore', 'chore', ('fetch-diff',)),
])
def test_agent_migration_and_absolute_load_contract(role, old, required):
    body = (ROOT / f'agents/{role}.md').read_text()
    assert not body.startswith('---')
    for value in ('Before taking task actions', 'requiredReferences', 'referenceManifest',
                  'referencesRoot', 'absolute', 'unreadable', 'failed', 'Never launch another subagent'):
        assert value in body
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
    assert 'REFERENCES_ROOT/github_setup.md' in handoff
    assert 'REFERENCES_ROOT/fetch-diff.md' in handoff
    for role in ('planner', 'implementer', 'verifier', 'chore'):
        assert f'agents/{role}.md' in handoff
    for phrase in ('before changing', 'before taking task actions', 'all six reference files',
                   'never infer', 'never create subagents', 'absolute paths'):
        assert phrase in handoff


def test_embedded_breakdown_is_self_contained_and_non_interactive():
    for text in ('Online-only, non-interactive', 'Never invoke `/to-tickets`',
                 'Ask nothing', 'only missing', 'closed', 'unlinked', 'lost response',
                 'numeric internal IDs', 'native blocker', 'Read back', 'partial publication',
                 'Concepts/ADRs', 'Functional Requirements', 'Business Rules', 'Edge Cases',
                 'COMPLETE', 'every touched integration layer'):
        assert text in BREAKDOWN
    assert '/to-tickets auto' not in MAIN + BREAKDOWN
    assert '## Breakdown ticket operations' in GITHUB
    for endpoint in ('/sub_issues --method POST -F sub_issue_id=', '/dependencies/blocked_by --method POST -F issue_id='):
        assert endpoint in GITHUB


def test_artifacts_fetched_before_slicing_mapped_both_directions_and_reconciled():
    for text in ('body and every comment', 'Read actual contents', 'untrusted source data',
                 'BEFORE publishing', 'source pointer/anchor', 'page ranges', 'diagram regions',
                 'Repeat a shared piece in every related ticket', 'exclude unrelated pieces',
                 'no relevant piece omitted', 'no included piece lacking',
                 'With no artifacts, omit', 'without duplicates', 'without', 'user-authored',
                 'Related Spec Artifacts', 'canonical source/anchor'):
        assert text in BREAKDOWN
    assert BREAKDOWN.index('## 2. Discover and fetch') < BREAKDOWN.index('## 4. Draft vertical')
    assert 'no suitable reader' in GITHUB


def test_template_parity_except_intentional_artifact_section():
    standalone = (REPO / 'plugins/wf/skills/to-tickets/references/issue-template.md').read_text()
    embedded = BREAKDOWN[BREAKDOWN.index('<issue-template>'):]
    embedded = re.sub(r'## Related Spec Artifacts\n.*?(?=## Implementation Decisions)', '', embedded, flags=re.S)
    assert embedded == standalone


def test_downstream_order_and_guards():
    workflow = MAIN.split('## Workflow')[1].split('## Subagent launch contract')[0]
    positions = [workflow.index(text) for text in (
        '6. Check the remaining frontier', '7. Launch chore', '8. Launch verifier',
        '9. Verify pushed commits', '10. Run code review', '11. Actualize and remove', '12. Finalize',
    )]
    assert positions == sorted(positions)
    for text in ('git revert --no-edit', 'exactly one commit', 'at most two rounds',
                 'PR remains draft', 'one quick confirmation', 'never reset'):
        assert text in MAIN
    for text in ('no `hitl` ticket is open', 'posting failures', 'Review completed at the current head'):
        assert text in GITHUB
    worktrees = (ROOT / 'references/worktrees.md').read_text()
    for text in ('Commit pending changes', 'merge --no-edit', 'Resolve conflicts', 'without force',
                 '**MUST NOT** rebase, reset, or force'):
        assert text in worktrees
    for path in (ROOT / 'references').glob('*.md'):
        assert not re.search(r'\]\(\./[a-z-]+\.md', path.read_text()), path
    parallel = (ROOT / 'references/parallel.md').read_text()
    assert 'no `conflicts`, paths `-`' not in parallel
    assert 'serialize overlapping tickets' in parallel
    assert 'mode=plan' not in parallel


def test_planner_has_no_empty_ticket_or_breakdown_switch_input():
    planner = (ROOT / 'agents/planner.md').read_text()
    placeholders = set(re.findall(r"\{\{([^}|]+)(?:\|[^}]*)?\}\}", planner))
    assert not {'ticketsJson', 'breakdown'} & placeholders
    assert 'zero native sub-issues' in planner
    assert 'initial invocation' in planner and 'return `failed` without ticket writes' in planner
    assert 'reconcile only the prior run' in planner
    assert 'internal `ticketGraph`' in planner
    assert 'from the fetched `ticketGraph`' in planner
    caller = MAIN.split('Launch planner')[1].split('2. Read the complete ticket graph')[0]
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
                 'do not wait for unrelated in-flight tickets', 'After each merge',
                 'after each validated integration', 'while B still runs',
                 'A finished worker alone does not satisfy its dependants',
                 'no ticket is ready but workers remain in flight',
                 'Keep a completed worker', 'until integration settles'):
        assert text in parallel
    assert 'schedule' not in MAIN + parallel
    assert '| Ticket | Blocked by |' in GITHUB
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
    assert examples[1]['status'] == 'failed'
