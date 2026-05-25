# Plan: Align dev handler+CLI+tests with fix_prs format

## Phase 1 — dev/handler.py

1. Change signature: `owner: str, repo: str` → `github_repo: str`
2. Update exec_log init: `ExecutionLog(log_dir, github_repo)` (no f-string)
3. Add `owner, repo = github_repo.split("/", 1)` at top of body
4. Expand docstring with Args: section (fix_prs style)
5. Reorder imports to match fix_prs style

## Phase 2 — dev/cli.py (depends on Phase 1)

6. Rename `--github_repo` → `--github_repo_board`, remove `required=True`
7. main(): replace split + separate owner/repo call with:
   `dev(args.github_repo_board, args.log_dir, ...)`

## Phase 3 — handler_test.py (depends on Phase 1)

8. Remove `_OWNER` / `_REPO` constants; add `_GITHUB_REPO = "owner/repo"`
9. All `dev(_OWNER, _REPO, ...)` calls → `dev(_GITHUB_REPO, ...)`
10. vcs assert calls remain `("owner", "repo")` since handler splits internally

## Phase 4 — cli_test.py (depends on Phase 2)

11. `test_parser_applies_default_arguments_for_valid_repository`:
    - arg: `"--github_repo"` → `"--github_repo_board"`
    - assert: `args.github_repo` → `args.github_repo_board`
12. `test_parser_accepts_custom_arguments`: same arg+assert rename
13. `test_parser_requires_github_repo_argument`: DELETE (argument is no longer required)
    - ADD new test: `test_parser_accepts_no_arguments` → parse_args([]) succeeds, github_repo_board is None
14. `test_main_delegates_to_handler_with_info_logging`:
    - Namespace: `github_repo=` → `github_repo_board=`
    - monkeypatched dev lambda: `lambda owner, repo, ...` → `lambda github_repo, ...`
    - captured_dev_call assertions: remove `owner`/`repo`; add `github_repo="owner/repo"`
15. `test_main_uses_debug_logging_when_afk_debug_is_set`:
    - Namespace: `github_repo=` → `github_repo_board=`

## Files

- `tools/src/afk/features/dev/handler.py`
- `tools/src/afk/features/dev/cli.py`
- `tools/tests/unit/features/dev/handler_test.py`
- `tools/tests/unit/features/dev/cli_test.py`

## Verification

1. `pytest tools/tests/unit/features/dev/` — all pass
2. `python -m afk.features.dev.cli --help` → shows `--github_repo_board`, not marked required
3. `python -m afk.features.dev.cli` (no args) → no `SystemExit(2)`
4. `python -m afk.features.dev.cli --github_repo_board owner/repo` → accepted
5. `python -m afk.features.dev.cli --github_repo_board bad` → validation error
