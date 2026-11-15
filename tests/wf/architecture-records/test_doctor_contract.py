from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3] / 'plugins/wf/skills/architecture-records'


def test_doctor_exposes_all_artifact_checks_and_evidence_verdicts():
    doctor = (ROOT / 'playbooks/doctor.md').read_text()
    checks = doctor.split('## Check records')[1].split('## Check index consistency')[0]
    assert set(re.findall(r'^\| ([^|]+) \|', checks, re.M)) >= {
        'ADR', 'Concept', 'Building block', 'Index prose/pointers'}
    verdicts = doctor.split('## Classify findings')[1].split('## Report')[0]
    assert set(re.findall(r'^\| `([^`]+)` \|', verdicts, re.M)) == {
        'current', 'drift', 'obsolete', 'unknown'}
    assert 'Clean requires complete coverage' in verdicts
    assert 'findings' in verdicts and 'incomplete' in verdicts


def test_doctor_keeps_report_only_writes_and_partial_coverage_visible():
    doctor = (ROOT / 'playbooks/doctor.md').read_text()
    assert 'authorizes only writing that report' in doctor
    assert 'otherwise return inline' in doctor
    assert 'approved decision awaiting implementation remains valid' in doctor
    assert 'unindexed record' in doctor and 'unlinked ADR rows' in doctor
    assert 'truncated/unconsumed rows' in doctor
    assert 'optional absent sections' in doctor
    assert 'empty repository clean' in doctor
    assert '_backup/' in doctor and '_in-progress/' in doctor
    final_section = doctor.split('## Closing completeness sweep')[1]
    assert 'inventoried = assessed + blocked' in final_section
    assert 'Run last' in final_section


def test_report_carries_evidence_coverage_and_failure_shape():
    report = (ROOT / 'templates/doctor-report.md').read_text()
    assert re.findall(r'^## (.+)$', report, re.M) == [
        'Summary', 'Scope', 'Coverage', 'Findings', 'Current records',
        'Unknowns and blockers', 'Recommended next actions']
    assert 'Total rows | Consumed rows' in report
    assert 'Documented statement | Observed evidence' in report
    assert 'Missing evidence or access | What resolves it' in report
    assert 'partially assessed artifact counts blocked' in report
