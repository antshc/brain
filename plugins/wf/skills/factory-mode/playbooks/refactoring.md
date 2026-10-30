### Refactoring

**You own the contract. The structure changes; the behavior does not.** Feature development adds behavior; bug fixing corrects it.

Cleanup reveals a missing feature or real bug → report it separately; ship the structural change first against the pinned contract. A behavior-preserving redesign is allowed; name it.

1. Pin the behavior contract. Research current behavior and callers through Non-negotiables, then write a characterization test, snapshot, or equivalence harness capturing current behavior before structure moves. Type check and lint are not a pin. Done when the pin runs green on the untouched code.
2. Name the structure the code is missing (**Model the domain**). Boring code stays when the shape is already clear and local. The reshape must delete branches or invalid states, not add indirection.
3. Name the target shape: module layout, types, call graph if built today (**Foundational thinking**, **Redesign from first principles**). Crosses a function boundary → `architect`. Seam or interface depth question → *run `codebase-design` skill to find deepening opportunities and decide where the seam goes.*
4. Subtract before you add. Delete dead code, collapse one-caller wrappers, drop redundant validators (**Subtract before you add**). Smallest change reaching the target ships (**Laziness protocol**).
5. Move in small behavior-preserving steps, each keeping the pin green. API reshape → migrate every caller and delete the old API in the same wave; no shims (**Migrate callers, then delete**). Spot-check renames against strings, docs, and back-references. C# → *run `csharp-refactoring` skill to safely rename, move, extract, or inline C# code without changing behavior.* Delegate mechanical edits with a specific scope: files, names moved, behavior to hold.
6. Prove behavior unchanged on the real artifact (**Prove it works**). Larger reshapes → equivalence check: diff old vs new outputs, replay a recorded baseline, or smoke-run the matching surface.
7. Confirm it earns its place. Success measure is reduced reader load (**Minimize reader load**); no reduction → revert.
8. Rebase into ordered commits: subtraction, reshape, follow-on cleanup; each green (**Verifiable units**). Run Opening a PR.

**Reply:** the structure that changed, the pin, the equivalence proof, the reader-load delta, what shipped and what got reverted. No new behavior.
