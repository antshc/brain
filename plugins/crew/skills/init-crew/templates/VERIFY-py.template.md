# VERIFY — Python

<!-- Followed in order by crew-feedback Step 1 during FEEDBACK LOOPS. Hazard rules below are Python-general and ship with this template — kept even when repository practice differs; a conflict is recorded in the shared GOTCHAS.md instead of edited here. Verify steps list this repo's own commands — never invent or copy example values from another repo. When this file exists it replaces the skill's inline default for this Stack's files. -->

## Hazard rules (Python)
- Module and test-discovery boundaries follow the project's own build marker (`pyproject.toml`, `setup.cfg`, `tox.ini`) — never assume `pytest`/`unittest` without checking which one this repo actually declares.

## Verify steps
<!--
1.  Diagnostics: e.g. run the language server / linter over changed files.
2.  Build: the command(s), if any, that build this repo's Python code.
3.  Test: the command(s) that run this repo's Python test suite.
4.  Project-specific checks: anything else this repo requires before a Python change is considered verified.
-->
