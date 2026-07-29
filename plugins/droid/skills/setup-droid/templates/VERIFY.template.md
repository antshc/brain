# VERIFY

<!-- Followed in order by droid-feedback Step 1 during FEEDBACK LOOPS. When this file exists it replaces the skill's inline default — list every step needed to verify a change in this repo. -->


## Verify steps
<!-- 
1.  Diagnostics: e.g. run the language server / linter over changed files.
2.  Build: the command(s) that build this repo. 
3.  Test: the command(s) that run this repo's test suite. 
4.  Project-specific checks: anything else this repo requires before a change is considered verified. 
-->


## Refactoring review
<!-- optional section: 
if the repo has a specific toolchain, list it here. 
If not, leave this section out and droid-feedback will discover the toolchain from the repo's own project files. 
-->
After the Verify phase passes, review all changed files together for refactoring candidates:
- **Duplication** → extract function/class
- **Long methods** → break into private helpers (keep tests on public interface)
- **Shallow modules** → combine or deepen
- **Feature envy** → move logic to where data lives
- **Primitive obsession** → introduce value objects
- **Existing code** the new code reveals as problematic

