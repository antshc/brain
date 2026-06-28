---
name: csdroid-feedback
description: C# feedback loop — run LSP, build, test, and refactoring review against all changed files after implementation.
---

Run [feedback.md](feedback.md) against all files changed during the IMPLEMENTATION. All four feedback steps (LSP, build, test, refactoring review) must pass.

Do not suppress warnings (e.g., `#pragma warning disable`) to achieve a green build.

If feedback loops fail, fix the issues and re-run from Step 1 of feedback before proceeding. (Step 0 collection only re-runs if the set of changed files itself changed.)

If feedback returns STATUS: blocked or partial, stop immediately and emit that status in the STATUS REPORT after completing RECORD DECISIONS.
