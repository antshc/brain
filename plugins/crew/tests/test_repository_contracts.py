from pathlib import Path


CREW_ROOT = Path(__file__).resolve().parents[1]


def test_chorey_passes_manifest_stacks_without_reinferring_them():
    agent = (CREW_ROOT / "agents" / "chorey.agent.md").read_text(encoding="utf-8")

    assert "pass it unchanged to `/crew-chore` as `STACKS`" in agent
    assert "Do not independently infer stacks" in agent
    assert "an empty array loads every configured stack file" in agent


def test_crew_chore_loads_named_stacks_or_all_stacks_for_an_empty_array():
    template = (
        CREW_ROOT / "skills" / "init-crew" / "templates" / "chore.SKILL.template.md"
    ).read_text(encoding="utf-8")

    assert "When `STACKS` is nonempty" in template
    assert "`stacks/<stack>.md`" in template
    assert "When `STACKS` is empty" in template
    assert "every configured `stacks/*.md` file in filename order" in template
    assert "Do not infer stacks from the review scope" in template
