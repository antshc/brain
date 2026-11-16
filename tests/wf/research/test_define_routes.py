"""Research Wayfinder ownership, isolation and resumable lifecycle contracts."""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / 'plugins/wf/skills/research'
ENTRY = (ROOT / 'SKILL.md').read_text()
WAYFINDER = (ROOT / 'wayfinder/wayfinder.md').read_text()
MAP = (ROOT / 'wayfinder/research-map.template.md').read_text()
DOCUMENT = (ROOT / 'wayfinder/research-document.template.md').read_text()
LIVING = (ROOT / 'wayfinder/living-document.md').read_text()


def test_wayfinder_route_resources_and_migration():
    assert 'wayfinder' not in ENTRY.split('---')[1].lower()
    assert '/research wayfinder <prompt-or-map-path>' in ENTRY
    assert 'Route: Wayfinder' in ENTRY
    for name in ('wayfinder.md', 'questioning.md', 'living-document.md',
                 'research-map.template.md', 'research-document.template.md'):
        assert f'](wayfinder/{name})' in ENTRY
    for removed in ('playbooks/define.md', 'references/define-questioning.md', 'templates/research-map.md'):
        assert not (ROOT / removed).exists()
    assert not (ROOT / 'playbooks').exists()
    assert not (ROOT / 'templates').exists()
    assert 'legacy map as inactive' in WAYFINDER
    assert 'preserve files/history' in WAYFINDER


def test_root_owns_coarse_fog_and_children_own_precise_work():
    assert re.findall(r'^## (.+)', MAP.split('```markdown\n')[1].split('```')[0], re.M) == [
        'Destination', 'Notes', 'Document and branches', 'Findings so far', 'Not yet specified', 'Out of scope']
    for field in ('Question', 'Unknowns', 'Work', 'Research scope', 'Blocked by', 'Part of', 'Result'):
        assert f'## {field}' in MAP
    assert 'all unresolved unknowns and risks' not in WAYFINDER
    assert 'including those with active children' not in WAYFINDER
    assert 'no live root fog row required' in MAP
    assert 'Pending proposals:' in MAP
    assert 'Transfer stable IDs, provenance, consequence, criteria' in WAYFINDER
    assert 'Do not maintain another active Markdown research map' in WAYFINDER
    assert 'native parent/sub-issue edges' in WAYFINDER
    assert 'reject cycles' in WAYFINDER


def test_shared_mechanics_and_exact_proposal_approval():
    shared = REPO / 'plugins/wf/skills/github/references/wayfinder.md'
    design = (REPO / 'plugins/wf/skills/design/references/github.md').read_text()
    assert 'using **Wayfinder operations**' in design
    assert '### Create Wayfinder sub-ticket' in shared.read_text()
    assert '### Create Wayfinder sub-ticket' not in design
    assert '`github` skill' in WAYFINDER and '`git` skill' in WAYFINDER
    assert '**Ticket approval** and **Prototype approval**' in WAYFINDER
    assert 'temporary clickable Markdown drafts' in WAYFINDER
    assert 'Changed proposals require fresh review' in WAYFINDER
    assert 'without another dispatch question' in WAYFINDER
    assert 'Do not start Design' in WAYFINDER


def test_owned_worktrees_pinned_dependencies_and_payload_gate():
    for prefix in ('wayfinder/<slug>', 'research/<slug>', 'prove/<slug>'):
        assert prefix in WAYFINDER
    assert 'outside disposable worktrees' in WAYFINDER
    assert 'leave the caller\'s working branch untouched' in WAYFINDER
    assert 'pinned current integration HEAD' in WAYFINDER
    assert 'prerequisite evidence is integrated' in WAYFINDER
    assert 'research report-only payloads integrate automatically' in WAYFINDER
    assert 'explicit user approval before any payload commit/merge' in WAYFINDER
    assert 'actual payload content identity' in WAYFINDER
    assert 'revised payloads require fresh approval' in WAYFINDER
    assert 'Restore unrelated production-source edits' in WAYFINDER
    assert 'No automatic push, PR, merge into session base' in WAYFINDER
    assert 'Retain blocked, rejected or approval-pending worktrees' in WAYFINDER


def test_evidence_pipeline_and_standalone_delivery_are_preserved():
    assert 'Frame, Routing and Spawning agents' in WAYFINDER
    assert 'Never recursively invoke Research or select Wayfinder for a topic' in WAYFINDER
    assert 'Save Explore verdicts unabridged' in WAYFINDER
    assert 'Batch independent research' in WAYFINDER
    assert 'only the Research router writes reports' in WAYFINDER
    for field in ('@question', '@criteria', '@repoFacts', '@outputPath', '@outputBase'):
        assert field in WAYFINDER
    assert 'retention through reproduction and human review' in WAYFINDER
    assert 'Report-only delivery below applies to standalone evidence routes' in ENTRY
    assert 'route `define-concept`' in ENTRY


def test_incremental_synthesis_keeps_evidence_and_status_separate():
    assert re.findall(r'^## (.+)', DOCUMENT.split('```markdown\n')[1].split('```')[0], re.M) == [
        'Bottom line', 'What we did', 'Open questions / decisions', 'Remaining work', 'Next steps', 'References']
    for contract in ('Update matching subjects and sections in place',
                     'Preserve verified findings and human decisions',
                     'Avoid duplicate findings, references and outcome rows',
                     '**Not confirmed**', 'references/bottom-line.md',
                     'repository-relative links', 'first unconfirmed synchronization step',
                     'A no-change rerun creates no commit'):
        assert contract in LIVING
    assert 'pending proof is not integrated evidence' in LIVING
    assert 'not a competing fog register' in LIVING


def test_resume_retains_incomplete_work_without_unblocking_dependents():
    for contract in ('their dependents remain blocked',
                     'without restarting the destination interview',
                     'Never regenerate an unchanged approval candidate',
                     'Missing refs or local evidence are blockers',
                     'never invent remote artifact links',
                     'a synchronized document needs remaining tracker writes only',
                     'Every unresolved claim stays explicit'):
        assert contract in WAYFINDER
