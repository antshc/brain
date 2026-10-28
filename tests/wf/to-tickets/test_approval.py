from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3] / 'plugins/wf/skills/to-tickets'
SKILL = (ROOT / 'SKILL.md').read_text()


def test_auto_rejected_without_approval_exception():
    assert 'Reject an explicit `auto` argument as unsupported' in SKILL
    assert '[auto]' not in SKILL
    assert 'auto` exception' not in SKILL
    assert 'non-interactive auto mode' not in SKILL
    assert SKILL.count('`auto`') == 1
    for reference in (ROOT / 'references').glob('*.md'):
        assert 'auto`' not in reference.read_text()


def test_online_offline_and_corrections_require_explicit_approval():
    for text in ('MUST NOT', 'until the user explicitly approves the current breakdown',
                 'Any slice change after approval', 'Before approval, only read and draft',
                 'MUST NOT** publish in the same turn as a correction',
                 'confirm the approval guard holds', 'save approved bodies',
                 'label `hitl,{{repoLabel}}`', 'labeled `hitl` and `{{repoLabel}}`'):
        assert text in SKILL
    assert 'Silence, partial feedback, corrections, and ambiguous replies are not approval' in SKILL
    assert 'Offline or partial' in SKILL


def test_publishes_blocker_graph_online_and_offline():
    assert 'acyclic **blocker graph**' in SKILL
    assert 'from blocker to dependent' in SKILL
    assert 'Reject cycles and missing blocker nodes' in SKILL
    assert '`Slice | Blocked by`' in SKILL
    assert '`Ticket | Blocked by`' in SKILL
    assert 'none` for roots' in SKILL
    assert 'fully qualified issue identities' in SKILL
    assert 'recompute the blocker graph and ready frontier' in SKILL
    assert 'symbolic blocker graph' in SKILL
    assert 'native link confirmed by reread' in SKILL
    github = (ROOT / 'references/github.md').read_text()
    assert 'symbolic blocker graph adjacency (including roots)' in github
    assert 'initial ready frontier' in github
