from __future__ import annotations

import pytest

from conftest import FakeGitHub

REPO = "acme/work"


def design_args(body, **overrides):
    values = {"--profile": "design", "--tracker-repository": REPO, "--source-repository": REPO,
              "--base-branch": "main", "--initiative-id": "PAY-12", "--summary": "Refunds",
              "--body-file": body("Spec body\n"), **overrides}
    return ["spec", "create", *[part for item in values.items() for part in item]]


@pytest.fixture
def tracker(fake: FakeGitHub) -> FakeGitHub:
    fake.labels["spec"] = {"name": "spec", "color": "ffffff"}
    return fake


def test_design_spec_creates_routing_labels_and_the_issue(run, tracker, body):
    result = run(*design_args(body), gh=tracker)
    assert result.code == 0 and result.data["created"] is True
    issue = tracker.issues[result.data["number"]]
    assert issue["title"] == "PAY-12: Refunds" and issue["body"] == "Spec body\n"
    assert sorted(label["name"] for label in issue["labels"]) == ["repo:base:main", "repo:target:acme/work", "spec"]
    assert {"repo:base:main", "repo:target:acme/work"} <= tracker.labels.keys()


def test_design_spec_requires_the_spec_label_from_workflow_setup(run, fake, body):
    result = run(*design_args(body), gh=fake)
    assert result.code == 2 and "lacks the spec label" in result.err and fake.writes() == []


def test_design_spec_refuses_a_second_spec_for_the_same_initiative(run, tracker, body):
    tracker.add_issue("PAY-12: Other", labels=("spec", "repo:target:acme/work"))
    result = run(*design_args(body), gh=tracker)
    assert result.code == 2 and "spec already exists" in result.err and tracker.writes() == []


def test_design_spec_allows_other_initiatives_in_the_same_tracker(run, tracker, body):
    tracker.add_issue("PAY-99: Other", labels=("spec", "repo:target:acme/work"))
    assert run(*design_args(body), gh=tracker).code == 0


@pytest.mark.parametrize("overrides", [
    {"--tracker-repository": "noslash"}, {"--source-repository": "noslash"},
    {"--initiative-id": "../x"}, {"--initiative-id": ".hidden"}, {"--initiative-id": "a/b"}, {"--initiative-id": " "},
])
def test_design_spec_validates_inputs_before_writing(run, tracker, body, overrides):
    assert run(*design_args(body, **overrides), gh=tracker).code == 2
    assert tracker.writes() == []


def test_design_spec_requires_a_tracker_repository(run, tracker, body):
    args = design_args(body)
    index = args.index("--tracker-repository")
    del args[index:index + 2]
    assert run(*args, gh=tracker).code == 2


def test_implement_spec_profile_requires_a_source_note(run, tracker, body):
    args = design_args(body, **{"--profile": "implement-spec"})
    result = run(*args, gh=tracker)
    assert result.code == 2 and "--source-note" in result.err


def artifact(number: int, name: str, kind: str = "generic", text: str = "body") -> dict:
    return {"number": number, "name": name, "type": kind, "body": text, "html_url": f"https://x/{number}", "updated_at": "t"}


@pytest.fixture
def issue_ref(fake: FakeGitHub) -> str:
    return f"{REPO}#{fake.add_issue('spec')}"


def test_artifact_list_and_get(run, fake, issue_ref):
    fake.artifacts = [artifact(1, "plan"), artifact(2, "notes")]
    assert [a["name"] for a in run("artifact", "list", issue_ref, gh=fake).data["artifacts"]] == ["plan", "notes"]
    assert run("artifact", "get", issue_ref, "2", gh=fake).data["name"] == "notes"
    missing = run("artifact", "get", issue_ref, "9", gh=fake)
    assert missing.code == 2 and "not found" in missing.err


def test_artifact_list_follows_pages_until_a_short_page(run, fake, issue_ref):
    fake.artifacts = [artifact(n, f"a{n}") for n in range(1, 102)]
    assert len(run("artifact", "list", issue_ref, gh=fake).data["artifacts"]) == 101


def test_artifact_read_reports_unavailable_preview_as_failure(run, fake, issue_ref):
    fake.fail("GET", r"artifacts", "gh: Not Found (HTTP 404)")
    result = run("artifact", "list", issue_ref, gh=fake)
    assert result.code == 1 and "unavailable" in result.err


def writer(fake, *, applies: bool = True):
    def handle(argv):
        if applies:
            name = argv[argv.index("--name") + 1] if "--name" in argv else None
            text = open(argv[argv.index("--body-file") + 1], encoding="utf-8").read()
            if argv[3] == "create":
                kind = argv[argv.index("--type") + 1]
                fake.artifacts.append(artifact(len(fake.artifacts) + 1, name, kind, text))
            else:
                next(a for a in fake.artifacts if a["number"] == int(argv[5]))["body"] = text
        return 0, "", ""
    fake.stub(("gh", "issue", "artifact"), handle)


def put(run, fake, issue_ref, body, text="new\n", name="plan", kind="generic"):
    return run("artifact", "put", issue_ref, "--name", name, "--type", kind, "--body-file", body(text), gh=fake)


def test_artifact_put_creates_then_edits_then_skips_identical_content(run, fake, issue_ref, body):
    fake.stub(("gh", "--version"), (0, "gh version 2.103.3 (2026-10-26)\n", ""))
    writer(fake)
    assert put(run, fake, issue_ref, body).data["body"] == "new\n"
    assert put(run, fake, issue_ref, body, "changed\n").data["body"] == "changed\n"
    before = len(fake.calls)
    put(run, fake, issue_ref, body, "changed\n")
    assert not any(call[:3] == ["gh", "issue", "artifact"] for call in fake.calls[before:])
    assert len(fake.artifacts) == 1


def test_artifact_put_refuses_old_gh_versions(run, fake, issue_ref, body):
    fake.stub(("gh", "--version"), (0, "gh version 2.103.1 (2026-01-01)\n", ""))
    result = put(run, fake, issue_ref, body)
    assert result.code == 2 and "2.103.2" in result.err


def test_artifact_put_refuses_a_type_conflict(run, fake, issue_ref, body):
    fake.artifacts = [artifact(1, "plan", "embedded_html")]
    fake.stub(("gh", "--version"), (0, "gh version 2.103.3\n", ""))
    assert put(run, fake, issue_ref, body, kind="generic").code == 2


def test_artifact_put_does_not_claim_success_when_the_write_does_not_stick(run, fake, issue_ref, body):
    fake.stub(("gh", "--version"), (0, "gh version 2.103.3\n", ""))
    writer(fake, applies=False)
    result = put(run, fake, issue_ref, body)
    assert result.code == 1 and "unconfirmed" in result.err
