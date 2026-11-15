"""Research-map ownership, disclosure, and resumable lifecycle regressions."""
import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / 'plugins/wf/skills/research'
ENTRY = (ROOT / 'SKILL.md').read_text()
DEFINE = (ROOT / 'playbooks/define.md').read_text()
TEMPLATE = (ROOT / 'templates/research-map.md').read_text()
QUESTIONING = (ROOT / 'references/define-questioning.md').read_text()


def test_define_is_body_only_and_old_owner_is_removed():
    frontmatter = ENTRY.split('---')[1]
    assert 'define' not in frontmatter.lower()
    assert '/research define <prompt-or-map-path>' in ENTRY
    assert 'Route: Define' in ENTRY
    assert 'Select Define before requiring a factual question' in ENTRY
    assert not (ROOT.parent / 'define').exists()
    for resource in ('playbooks/define.md', 'references/define-questioning.md', 'templates/research-map.md'):
        assert f']({resource})' in ENTRY
        assert (ROOT / resource).is_file()
    assert 'both required in full before charting/resuming' in ENTRY


def test_map_and_topics_keep_the_persistent_contract():
    assert re.findall(r'^## (.+)', TEMPLATE.split('```markdown\n')[1].split('```')[0], re.M) == [
        'Destination', 'Notes', 'Topics', 'Findings so far', 'Not yet specified', 'Out of scope']
    for field in ('Type', 'Question', 'Claim', 'Resolve via', 'Blocked by'):
        assert f'**{field}:**' in TEMPLATE
    assert 'confirmed when' in TEMPLATE and 'refuted when' in TEMPLATE
    assert 'docs/ongoing/{{destinationSlug}}-research-map.md' in DEFINE
    assert 'docs/research/{{destinationSlug}}-{{topicSlug}}.md' in DEFINE
    assert 'or an explicit caller destination' in DEFINE
    assert 'explicit paths override session defaults' in DEFINE


def test_resume_and_chart_preserve_user_checkpoints():
    assert 'without restarting the destination interview' in DEFINE
    assert 'Missing or unreadable map' in DEFINE
    assert 'overwrite it or resume it' in DEFINE
    assert 'the user confirms the destination' in DEFINE
    assert 'Ask the user to confirm or correct the map' in DEFINE
    assert 'On decline, stop' in DEFINE
    assert 'one at a time; on acceptance' in DEFINE
    assert 'The decision itself and any implementation belong to the caller' in DEFINE
    assert 'Ask the whole frontier in one round' in QUESTIONING


def test_evidence_uses_existing_pipeline_without_recursive_dispatch():
    assert 'Frame, Routing and Spawning agents' in DEFINE
    assert 'Never recursively invoke Research or select Define for a topic' in DEFINE
    assert 'Batch independent topics in parallel' in DEFINE
    assert 'sequence dependent topics' in DEFINE
    assert 'built-in `explore` subagent' not in DEFINE
    assert 'Frame, Routing and Spawning agents' in QUESTIONING
    assert 'Save Explore verdicts unabridged to the topic path' in DEFINE
    assert 'Report-only delivery below applies to standalone evidence routes' in ENTRY
    assert 'route `define-concept`' in ENTRY


def test_incomplete_work_remains_resumable_and_does_not_unblock_dependants():
    assert 'Keep partial, blocked, declined and inconclusive topics open' in DEFINE
    assert 'their dependants remain blocked' in DEFINE
    assert 'hand back their status and the resumable map' in DEFINE
    assert 'Check closure before offering more work' in DEFINE
    assert 'Graduate any fog' in DEFINE
    assert 'Out of scope' in DEFINE
    assert 're-rank Topics by risk' in DEFINE
    assert 'Topics and Not yet specified are both empty' in DEFINE
    assert 'user confirms the remaining topics cannot change the destination' in DEFINE
    for field in ('@question', '@criteria', '@repoFacts', '@outputPath', '@outputBase'):
        assert field in DEFINE
    assert 'request retention through any human review; read its returned report in full' in DEFINE
