from __future__ import annotations

import re
import hashlib
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / 'plugins/wf/skills/implement-spec'
MAIN = (ROOT / 'SKILL.md').read_text()
BREAKDOWN = (ROOT / 'references/breakdown.md').read_text()
GITHUB = (ROOT / 'references/github.md').read_text()


def test_exact_layout_and_local_links():
    assert {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()} == {
        'SKILL.md', *(f'agents/{role}.md' for role in ('planner', 'implementer', 'verifier', 'chore')),
        *(f'references/{name}.md' for name in ('breakdown', 'sequential', 'parallel', 'github', 'fetch-diff')),
    }
    for path in ROOT.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if ':' in target or '{{' in target or target.startswith('docs/'):
                continue
            assert (path.parent / target.split('#')[0]).exists(), (path, target)


def test_input_detection_modes_and_existing_graph_bypass():
    workflow = MAIN.split('## Workflow')[1].split('## Prepare Plan')[0]
    assert workflow.index('Detect input type first') < workflow.index('Prepare input')
    assert 'reject `mode=plan`' in workflow
    assert 'before writes, execution worktrees, or PR creation' in workflow
    assert '`sequential` (default) | `parallel`' in MAIN
    prepare = MAIN.split('## Prepare Spec')[1].split('## Breakdown Initiative')[0]
    assert 'Existing sub-issues' in prepare and 'MUST NOT' in prepare
    assert 'run the planner or create tickets' in prepare
    assert 'Zero sub-issues' in prepare
    assert '[sequential.md](./references/sequential.md)' in MAIN


def test_plan_branch_is_answered_validated_persisted_and_read_back():
    create = GITHUB.split('## Create spec')[1].split('## Read the task graph')[0]
    for text in ('target/base branch', 'all three answers', 'branches/BASE_BRANCH',
                 'Fetch that exact remote branch', 'source checkout',
                 'repo:base:BASE_BRANCH', 'Read back title, labels, body', 'MUST NOT'):
        assert text in create
    assert 'BASE_BRANCH` = `gh repo view' not in create


@pytest.mark.parametrize('role,old,required', [
    ('planner', 'plan', ('breakdown', 'github')),
    ('implementer', 'implement', ('github',)),
    ('verifier', 'verify', ('github',)),
    ('chore', 'chore', ('fetchDiff',)),
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
                  'maxParallel',
                  'notesDir',
                  'sourceRoot',
                  'specJson',
                  'specRef'],
                 '554906fb5eb68990beff72e23d961b4b34bf47fe92e78584cea9d42c7b7c4759'),
     'implementer': (['commitSubjectPrefix',
                      'featureBranch',
                      'initiativeCommits',
                      'targetBranch',
                      'ticketJson',
                      'worktreePath'],
                     'cc6785dae95427f44940c45b9f6fdc5f8a1390d3651876252043c2dc40cfcce4'),
     'verifier': (['branchCommits',
                   'commitSubjectPrefix',
                   'evidenceDir',
                   'featureBranch',
                   'pullRequestUrl',
                   'specJson',
                   'targetBranch',
                   'ticketsJson',
                   'verificationSkills',
                   'worktreePath'],
                  'bf82dd8421283a88d6a5f27a9ad31d4dfb259c5920b162b111832bbdaa58aaa9'),
     'chore': (['branchCommits',
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
    assert hashlib.sha256(responses.encode()).hexdigest() == response_hash


def test_launch_manifest_has_every_reference_and_role():
    handoff = MAIN.split('## Subagent launch contract')[1].split('## Implementer prompt')[0]
    for name in ('breakdown', 'sequential', 'parallel', 'github', 'fetch-diff'):
        assert f'REFERENCES_ROOT/{name}.md' in handoff
    for role in ('planner', 'implementer', 'verifier', 'chore'):
        assert f'agents/{role}.md' in handoff
    for phrase in ('before changing', 'before taking task actions', 'all five reference files',
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
    workflow = MAIN.split('## Workflow')[1].split('## Prepare Plan')[0]
    positions = [workflow.index(text) for text in (
        '8. **Verify the app', '9. **Chore pass', '10. **Publish and remove worktree',
        '11. **Code review', '12. **Finalize',
    )]
    assert positions == sorted(positions)
    for text in ('git revert --no-edit', 'exactly one commit', 'at most two rounds',
                 'no `hitl` ticket is open', 'posting failures', 'review completed at the current head',
                 'PR remains draft', 'one quick confirmation', 'never reset'):
        assert text in MAIN
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
    caller = MAIN.split('## Breakdown Initiative')[1].split('## Constraints')[0]
    assert '{{ticketsJson}}' not in caller
    assert '{{breakdown}}' not in caller
    assert '{{ticketsJson}}' in (ROOT / 'agents/verifier.md').read_text()
    assert '`{{ticketsJson}}` = spec and integrated tickets' in MAIN
