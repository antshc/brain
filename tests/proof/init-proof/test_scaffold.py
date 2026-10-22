"""Proof init-proof scaffold script behavior tests.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[3] / "plugins" / "proof" / "skills" / "init-proof"
SCRIPT_PATH = SKILL_DIR / "scripts" / "scaffold.py"

spec = importlib.util.spec_from_file_location("proof_scaffold", SCRIPT_PATH)
assert spec and spec.loader
scaffold_module = importlib.util.module_from_spec(spec)
sys.modules["proof_scaffold"] = scaffold_module
spec.loader.exec_module(scaffold_module)

PACKAGE = {"name": "demo", "private": True, "scripts": {"dev": "node server.js"}}


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / "package.json").write_text(json.dumps(PACKAGE, indent=2) + "\n")
    (tmp_path / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\n")
    return tmp_path


def run(repo: Path, surfaces: str = "both", name: str = "Demo shop") -> dict:
    return scaffold_module.scaffold(repo, scaffold_module.parse_surfaces(surfaces), name, install=False)


def text_files(repo: Path) -> list[Path]:
    roots = [repo / "proof", repo / ".github"]
    return [p for root in roots for p in root.rglob("*") if p.is_file()]


class TestSurfaceSelection:
    """Feature: Proof Surface Selection"""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [("web", ["web"]), ("api", ["api"]), ("both", ["web", "api"]), ("api,web", ["web", "api"]), (" Web , API ", ["web", "api"])],
    )
    def test_surface_choice_is_normalised_to_canonical_order(self, value: str, expected: list[str]) -> None:
        assert scaffold_module.parse_surfaces(value) == expected

    @pytest.mark.parametrize("value", ["", "cli", "web,ftp"])
    def test_unknown_or_empty_surface_choice_is_refused(self, value: str) -> None:
        with pytest.raises(scaffold_module.ScaffoldError):
            scaffold_module.parse_surfaces(value)


class TestRepositoryGate:
    """Feature: Proof Repository Gate"""

    def test_repo_without_package_json_is_refused(self, tmp_path: Path) -> None:
        with pytest.raises(scaffold_module.ScaffoldError, match="not a pnpm repository"):
            run(tmp_path)

    def test_npm_repo_is_refused_and_untouched(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").write_text("{}")
        (tmp_path / "package-lock.json").write_text("{}")
        with pytest.raises(scaffold_module.ScaffoldError, match="Choose python"):
            run(tmp_path)
        assert not (tmp_path / "proof").exists()

    def test_package_manager_field_marks_a_pnpm_repo(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").write_text(json.dumps({"packageManager": "pnpm@10.0.0"}))
        assert scaffold_module.is_pnpm_repo(tmp_path)

    def test_cli_exits_2_with_error_for_non_pnpm_repo(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        code = scaffold_module.main(["--repo", str(tmp_path), "--surfaces", "web", "--app-name", "x", "--no-install"])
        assert code == 2
        assert json.loads(capsys.readouterr().err)["ok"] is False


class TestScaffoldedFiles:
    """Feature: Proof Scaffold Output"""

    def test_both_surfaces_create_the_api_adapter_and_the_web_page_object(self, repo: Path) -> None:
        result = run(repo, "both")
        for created in ("proof/adapters/api.ts", "proof/pages/app-page.ts", "proof/flows/open-app.ts", "proof/checks/example-web.ts", "proof/checks/example-api.ts"):
            assert created in result["created"]
        assert (repo / ".github/skills/verify-demo-shop/SKILL.md").is_file()
        assert (repo / "mole/mole.ts").is_file()
        assert (repo / "proof/kit/run.ts").is_file()
        assert not (repo / "proof/engine").exists()
        assert not (repo / "proof/features/surfaces").exists()

    def test_scaffold_creates_the_scenario_model_layout(self, repo: Path) -> None:
        run(repo, "both")
        for path in ("proof/features/index.ts", "proof/features/example.ts", "proof/adapters/index.ts", "proof/components/README.md", "proof/features.test.ts"):
            assert (repo / path).is_file(), path
        for path in ("features/README.md", "features/example.md", "references/component-extractor.md"):
            assert (repo / ".github/skills/verify-demo-shop" / path).is_file(), path
        assert (repo / "proof/AGENT.md").is_file()
        assert not (repo / ".github/skills/verify-demo-shop/scripts").exists()

    def test_web_only_has_no_api_adapter_or_api_config(self, repo: Path) -> None:
        run(repo, "web")
        assert not (repo / "proof/adapters/api.ts").exists()
        assert not (repo / "proof/checks/example-api.ts").exists()
        app = (repo / "proof/app.ts").read_text()
        assert 'surfaces: ["web"]' in app
        assert "api: {" not in app and "web: {" in app
        assert "apiResponse" not in (repo / "proof/adapters/index.ts").read_text()
        assert "apiAnswers" not in (repo / "proof/features/example.ts").read_text()

    def test_api_only_has_no_web_adapter_or_web_config(self, repo: Path) -> None:
        run(repo, "api")
        for absent in ("proof/pages/app-page.ts", "proof/flows/open-app.ts", "proof/checks/example-web.ts"):
            assert not (repo / absent).exists(), absent
        app = (repo / "proof/app.ts").read_text()
        assert 'surfaces: ["api"]' in app
        assert "web: {" not in app and "api: {" in app
        assert "openApp" not in (repo / "proof/features/example.ts").read_text()
        skill = (repo / ".github/skills/verify-demo-shop/SKILL.md").read_text()
        assert "screenshot" not in skill and "over HTTP" in skill

    @pytest.mark.parametrize("surfaces", ["web", "api", "both"])
    def test_no_marker_or_placeholder_is_left_in_any_file(self, repo: Path, surfaces: str) -> None:
        run(repo, surfaces)
        for path in text_files(repo):
            body = path.read_text()
            for leftover in ("<surface:", "</surface:", "<!-- surface", "<!-- /surface", "{{", "}}"):
                assert leftover not in body, f"{leftover!r} left in {path.relative_to(repo)}"

    def test_skill_drives_the_scenario_loop_with_run_flow_and_receipts(self, repo: Path) -> None:
        run(repo, "both")
        skill = (repo / ".github/skills/verify-demo-shop/SKILL.md").read_text()
        for command in ("pnpm mole run", "pnpm mole flow", "pnpm mole receipts", "proof/AGENT.md", "references/component-extractor.md"):
            assert command in skill
        assert "prove --feature" not in skill and "--surface" not in skill

    def test_app_name_is_json_escaped_in_app_ts_and_plain_in_the_skill(self, repo: Path) -> None:
        run(repo, "web", name='Shop "Pro"')
        assert 'name: "Shop \\"Pro\\""' in (repo / "proof/app.ts").read_text()
        assert "name: verify-shop-pro\n" in (repo / ".github/skills/verify-shop-pro/SKILL.md").read_text()
        assert 'Verify Shop "Pro"' in (repo / ".github/skills/verify-shop-pro/SKILL.md").read_text()

    def test_example_map_has_one_scenario_paragraph_per_chosen_surface(self, repo: Path) -> None:
        run(repo, "api")
        map_text = (repo / ".github/skills/verify-demo-shop/features/example.md").read_text()
        for section in ("## Sub-features", "## How to get to it (user POV)", "## Driving it with Mole", "## Gotchas"):
            assert section in map_text
        assert "**(app-answers | api):**" in map_text and "(API response)" in map_text
        assert "(app-answers | web)" not in map_text and "(DOM assertion)" not in map_text

    def test_kit_and_mole_are_copied_byte_for_byte(self, repo: Path) -> None:
        run(repo, "both")
        for folder, target in (("kit", "proof/kit"), ("mole", "mole")):
            for source in (SKILL_DIR / "templates" / "typescript" / folder).iterdir():
                assert (repo / target / source.name).read_bytes() == source.read_bytes()

    def test_unresolved_todo_markers_remain_for_the_research_step(self, repo: Path) -> None:
        run(repo, "both")
        assert "TODO(proof)" in (repo / "proof/app.ts").read_text()


class TestNoOverwrite:
    """Feature: Proof Scaffold No Overwrite"""

    def test_existing_files_are_kept_and_reported_as_skipped(self, repo: Path) -> None:
        (repo / "proof").mkdir()
        (repo / "proof/app.ts").write_text("// mine\n")
        result = run(repo, "both")
        assert (repo / "proof/app.ts").read_text() == "// mine\n"
        assert "proof/app.ts" in result["skipped"]
        assert "proof/app.ts" not in result["created"]

    def test_second_run_creates_nothing(self, repo: Path) -> None:
        first = run(repo, "both")
        second = run(repo, "both")
        assert second["created"] == []
        assert sorted(second["skipped"]) == sorted(first["created"])


class TestPackageJson:
    """Feature: Proof Package Setup"""

    def test_scripts_are_added_and_indent_is_preserved(self, repo: Path) -> None:
        result = run(repo)
        data = json.loads((repo / "package.json").read_text())
        assert data["scripts"]["mole"] == "tsx mole/mole.ts"
        assert data["scripts"]["dev"] == "node server.js"
        assert set(result["scripts_added"]) == {"mole", "prove", "test:proof", "typecheck:proof"}
        assert (repo / "package.json").read_text().startswith('{\n  "name"')

    def test_conflicting_script_is_kept_and_reported(self, repo: Path) -> None:
        package = dict(PACKAGE, scripts={"mole": "something else"})
        (repo / "package.json").write_text(json.dumps(package))
        result = run(repo)
        assert json.loads((repo / "package.json").read_text())["scripts"]["mole"] == "something else"
        assert result["scripts_conflicting"] == ["mole"]

    def test_declared_dev_dependencies_are_not_reinstalled(self, repo: Path) -> None:
        package = dict(PACKAGE, devDependencies={"tsx": "^4", "typescript": "^5"})
        (repo / "package.json").write_text(json.dumps(package))
        result = run(repo)
        assert result["dev_dependencies_missing"] == ["@playwright/test", "@types/node"]
        assert result["install"] == "skipped"

    def test_workspace_root_installs_with_dash_w(self, repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        (repo / "pnpm-workspace.yaml").write_text("packages: []\n")
        calls: list[tuple[str, ...]] = []

        class Done:
            returncode, stdout, stderr = 0, "", ""

        monkeypatch.setattr(scaffold_module.shutil, "which", lambda _: "/usr/bin/pnpm")
        monkeypatch.setattr(scaffold_module, "_pnpm", lambda _repo, *args: calls.append(args) or Done())
        assert scaffold_module._install(repo, ["tsx"]) == "installed"
        assert calls == [("add", "-D", "-w", "tsx")]

    def test_ignored_build_scripts_are_approved(self, repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        calls: list[tuple[str, ...]] = []

        class Blocked:
            returncode = 1
            stdout = ""
            stderr = "Error: ERR_PNPM_IGNORED_BUILDS\n  Ignored build scripts: esbuild@0.28.2, @scope/pkg@1.0.0\n"

        class Done:
            returncode, stdout, stderr = 0, "", ""

        monkeypatch.setattr(scaffold_module.shutil, "which", lambda _: "/usr/bin/pnpm")
        monkeypatch.setattr(scaffold_module, "_pnpm", lambda _repo, *args: calls.append(args) or (Blocked() if args[0] == "add" else Done()))
        status = scaffold_module._install(repo, ["tsx"])
        assert status.startswith("installed (approved build scripts: esbuild, @scope/pkg")
        assert calls[1] == ("approve-builds", "esbuild", "@scope/pkg")


class TestGitignore:
    """Feature: Proof Gitignore"""

    def test_missing_gitignore_is_created(self, repo: Path) -> None:
        assert run(repo)["gitignore"] == "created"
        assert (repo / ".gitignore").read_text() == "/proof/.runs/\n"

    def test_line_is_appended_once_to_an_existing_file(self, repo: Path) -> None:
        (repo / ".gitignore").write_text("node_modules")
        assert run(repo)["gitignore"] == "added"
        assert (repo / ".gitignore").read_text() == "node_modules\n/proof/.runs/\n"
        assert run(repo)["gitignore"] == "present"

    def test_equivalent_existing_entry_is_respected(self, repo: Path) -> None:
        (repo / ".gitignore").write_text("proof/.runs/\n")
        assert run(repo)["gitignore"] == "present"


class TestRenderMarkers:
    """Feature: Proof Surface Markers"""

    def test_ts_block_markers(self) -> None:
        text = "a\n  // <surface: api>\n  b\n  // </surface: api>\nc\n"
        assert scaffold_module.render(text, ["web"], "x") == "a\nc\n"
        assert scaffold_module.render(text, ["api"], "x") == "a\n  b\nc\n"

    def test_markdown_inline_and_block_markers(self) -> None:
        text = "x <!-- surface: web+api -->both<!-- /surface: web+api --> y\n<!-- surface: web-only -->\nonly\n<!-- /surface: web-only -->\nz\n"
        assert scaffold_module.render(text, ["web", "api"], "n") == "x both y\nz\n"
        assert scaffold_module.render(text, ["web"], "n") == "x  y\nonly\nz\n"

    def test_language_block_and_inline_markers(self) -> None:
        text = "a <!-- lang: python -->py<!-- /lang: python --><!-- lang: typescript -->ts<!-- /lang: typescript --> b\n<!-- lang: python -->\nonly py\n<!-- /lang: python -->\nz\n"
        assert scaffold_module.render(text, ["web"], "n", "python") == "a py b\nonly py\nz\n"
        assert scaffold_module.render(text, ["web"], "n", "typescript") == "a ts b\nz\n"

    def test_unknown_language_marker_is_an_error(self) -> None:
        with pytest.raises(scaffold_module.ScaffoldError, match="Unknown language marker"):
            scaffold_module.render("<!-- lang: ruby -->x<!-- /lang: ruby -->", ["web"], "n")

    def test_unknown_marker_expression_is_an_error(self) -> None:
        with pytest.raises(scaffold_module.ScaffoldError, match="Unknown surface marker"):
            scaffold_module.render("<!-- surface: cli -->x<!-- /surface: cli -->", ["web"], "n")

    def test_unresolved_placeholder_is_an_error(self) -> None:
        with pytest.raises(scaffold_module.ScaffoldError, match="Unresolved"):
            scaffold_module.render("{{NOPE}}", ["web"], "n")


PLUGIN_DIR = SKILL_DIR.parents[1]
REPO_ROOT = PLUGIN_DIR.parents[1]


class TestPluginLayout:
    """Feature: Proof Plugin Layout"""

    def test_only_the_three_skills_carry_a_skill_md(self) -> None:
        found = sorted(p.parent.name for p in PLUGIN_DIR.rglob("SKILL.md"))
        assert found == ["init-proof", "maintain-proof", "playwright-cli"]

    def test_plugin_manifest_points_at_the_skills_folder(self) -> None:
        manifest = json.loads((PLUGIN_DIR / "plugin.json").read_text())
        assert manifest["name"] == "proof"
        assert manifest["skills"] == ["./skills"]

    def test_marketplace_lists_the_plugin(self) -> None:
        marketplace = json.loads((REPO_ROOT / ".github" / "plugin" / "marketplace.json").read_text())
        entry = next(p for p in marketplace["plugins"] if p["name"] == "proof")
        assert entry["source"] == "./plugins/proof"

    def test_template_skill_is_renamed_on_scaffold(self, repo: Path) -> None:
        run(repo)
        assert not list((repo / ".github/skills/verify-demo-shop").glob("*.template.md"))
        assert (repo / ".github/skills/verify-demo-shop/SKILL.md").is_file()

    def test_one_shared_verify_mole_template_serves_both_languages(self, repo: Path) -> None:
        templates = SKILL_DIR / "templates"
        assert (templates / "verify-mole" / "AGENT.md").is_file()
        assert (templates / "verify-mole" / "references" / "component-extractor.md").is_file()
        assert not (templates / "python" / "verify-mole").exists() and not (templates / "typescript" / "verify-mole").exists()
        run(repo)
        agent_doc = (repo / "proof/AGENT.md").read_text()
        assert "defineFeature" in agent_doc and "@flow" not in agent_doc
        prompt = (repo / ".github/skills/verify-demo-shop/references/component-extractor.md").read_text()
        assert "<control>.ts" in prompt and "<control>.py" not in prompt

    @pytest.mark.parametrize("skill", ["init-proof", "maintain-proof", "playwright-cli"])
    def test_every_skill_has_name_and_description_frontmatter(self, skill: str) -> None:
        head = (PLUGIN_DIR / "skills" / skill / "SKILL.md").read_text().split("---")[1]
        assert f"name: {skill}" in head and "description:" in head
