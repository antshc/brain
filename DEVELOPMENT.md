# Development

## Git Hooks

This repo ships hooks in `.githooks/`. After cloning, activate them once:

```bash
git config core.hooksPath .githooks
```

### pre-commit

Syncs `tools/src/modules/github/` → `plugins/ralph/skills/fix/github/` and stages the result before every commit.

## Markdown and skill checks

Use Node.js 24 and Python 3.10 or later:

```bash
npm ci --ignore-scripts
npm run lint:markdown
npm run lint:links
npm run test:markdown
python3 -m pip install -e '.[dev]'
python3 .github/scripts/lint_skill_descriptions.py
python3 -m pytest .github/scripts/test_lint_skill_descriptions.py tools/tests/unit/repo_consistency -q
```

Run `npm run lint:markdown:fix` to apply supported formatting fixes; review the diff before committing. The lockfile pins the formatter and parser versions used locally and in CI.

`.markdownlint.json` configures Markdown syntax and formatting. Table cells retain their existing padding; the custom `brain-table-separator` rule requires separator rows without spaces, such as `|---|---|`. MD060 is disabled because it also enforces cell padding. MD041 and MD025 are disabled globally: Markdown files may omit a title or contain multiple H1 headings. Existing headings are preserved; linting does not add titles. Use bold labels ending with a colon, such as `**Actions:**` or `**Optional:**`, for short blocks that do not need headings. Keep MD036 enabled instead of adding per-file suppression comments. `.markdownlint-cli2.jsonc` selects files and excludes archived folders, dependencies, and captured regression fixtures. Prompt XML, embedded fragments, and language alternatives use documented local rule exceptions. New standalone documents follow the root rules.

The local-link check parses Markdown links, images, and reference definitions, including route-to-playbook links. It skips code, URLs, anchors, absolute runtime paths, and templated destinations; it does not validate remote availability or cross-file heading fragments. Exact example and installation-time destinations are documented in `.github/scripts/markdown-link-exceptions.json`; add an exception only when the destination is intentionally unavailable in this checkout.

Skill validation checks YAML front matter across tracked skills, WF description length, trigger overlap, redirects, required agent metadata, and skill invocations. Description quality checks retain their WF scope.

### Require checks before merging

After the workflow has run once, open **Settings → Rules → Rulesets**, create or edit the rule targeting `main`, and enable **Require status checks to pass**. Select **Markdown lint**, **Skill validation**, and **Python tests**, then save the ruleset.

All three checks run for every PR targeting `main` and for merge queues. Keep their job names stable and avoid workflow path filters or branch-name conditions that skip required checks. Workflow files provide the checks; repository rules enforce the merge gate.
