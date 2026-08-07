---
name: prototype
description: Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether an SDK call or integration behaves as expected, or whether a state model or data shape feels right, before committing real code.
---

# Prototype

A prototype is throwaway code that answers a question. The question decides the shape.

## Pick a branch

Identify which question is being answered — from the user's prompt, the surrounding code, or by asking if the user is around:

- "Does this SDK call / integration behave as expected?" → [SDK.md](SDK.md). Write a throwaway integration test that exercises the real cloud SDK call and asserts on its actual response shape.
- "Does this logic / state model / data shape feel right?" → [LOGIC.md](LOGIC.md). Build a small, runnable console app that pushes the model through cases that are hard to reason about on paper.

The two branches produce very different artifacts — getting this wrong wastes the whole prototype. If the question is genuinely ambiguous and the user isn't reachable, default to whichever branch better matches the surrounding code (a repository/proxy wrapping a cloud call → SDK; a pure domain model or data shape → Logic) and state the assumption at the top of the prototype.

## Rules that apply to both

1. Throwaway from day one, and clearly marked as such. Locate the prototype code close to where it will actually be used (next to the module it's prototyping for) so context is obvious — but name it so a casual reader can see it's a prototype, not production.
2. Trivial to run. One command, no thinking required to start it — `dotnet test` for the SDK branch, `dotnet run` for the Logic branch.
3. No persistence beyond what the question is checking. If the question is about persistence, hit a scratch/sandbox resource with a clear "PROTOTYPE — wipe me" name, never a real one.
4. Skip the polish. No unrelated tests, no error handling beyond what makes the prototype runnable, no abstractions. The point is to learn something fast.
5. Surface the state. After every action, print or render the full relevant state (or response) so the reader can see what changed.
6. Capture it when done. Fold any validated decision into the real code, then capture the prototype itself as a primary source: commit it to a throwaway branch, out of main, and leave a context pointer to that branch on the implementation issue. Capture the answer too — the verdict and the question it settled — in the issue or a commit. The main branch keeps only the validated decision.
