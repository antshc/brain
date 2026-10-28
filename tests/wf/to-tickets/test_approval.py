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
