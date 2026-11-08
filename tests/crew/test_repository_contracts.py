from pathlib import Path


CREW_ROOT = Path(__file__).resolve().parents[2] / "plugins" / "crew"


def test_chorey_passes_manifest_stacks_without_reinferring_them():
    agent = (CREW_ROOT / "agents" / "chorey.agent.md").read_text(encoding="utf-8")

    assert "pass it unchanged to `/crew-chore` as `STACKS`" in agent
    assert "Do not independently infer stacks" in agent
    assert "an empty array loads every configured stack file" in agent


def test_crew_chore_loads_named_stacks_or_all_stacks_for_an_empty_array():
    template = (
        CREW_ROOT / "install" / "templates" / "chore.SKILL.template.md"
    ).read_text(encoding="utf-8")

    assert "When `STACKS` is nonempty" in template
    assert "`stacks/<stack>.md`" in template
    assert "When `STACKS` is empty" in template
    assert "every configured `stacks/*.md` file in filename order" in template
    assert "Do not infer stacks from the review scope" in template

def test_codey_agents_require_focused_integration_tests_for_external_boundaries():
    for name in ("codey-py.agent.md",):
        agent = (CREW_ROOT / "agents" / name).read_text(encoding="utf-8")

        assert "repository/accessor/proxy" in agent
        assert "existing integration/functional-slice tests" in agent
        assert "*run `testing-integrations` skill" in agent
        assert "source of truth" in agent
        assert "smallest existing test subset" in agent


def test_chorey_uses_testing_integrations_skill_and_minimal_existing_boundary_tests():
    agent = (CREW_ROOT / "agents" / "chorey.agent.md").read_text(encoding="utf-8")

    assert "repository/accessor/proxy" in agent
    assert "existing integration/functional-slice tests" in agent
    assert "*run `testing-integrations` skill" in agent
    assert "source of truth" in agent
    assert "smallest matching existing boundary-test subset" in agent


def test_crew_reports_gotchas_without_a_memory_dependency():
    for path in (CREW_ROOT / 'agents').glob('*.agent.md'):
        agent = path.read_text()
        assert 'GOTCHAS' in agent
        assert 'crew-memory' not in agent
        assert 'GOTCHAS UPDATED' not in agent
    assert not (CREW_ROOT / 'skills/crew-gotchas/SKILL.md').exists()
    installer = CREW_ROOT / 'install'
    assert not (installer / 'templates/crew-memory.SKILL.template.md').exists()
    assert 'crew-memory' not in (installer / 'install.md').read_text()


def test_crew_codey_dotnet_uses_the_original_task_and_workspace_contract():
    agent = (CREW_ROOT / 'agents/codey-dotnet.agent.md').read_text()
    assert 'name: codey-dotnet' in agent
    assert '`## TASK`' in agent
    assert '`/memories/session/plan.md`' in agent
    assert 'Work in cwd' in agent
    assert 'leave changes uncommitted for the caller' in agent
    assert 'ticket-commit' not in agent
