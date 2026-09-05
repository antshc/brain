# Logic Prototype

A lightweight, minimal .NET console app that lets you drive a state model or data shape by hand before committing real code. Use this when the question is about business logic, state transitions, or data shape — the kind of thing that looks reasonable on paper but only feels wrong once you push it through real cases.

If the question is "does this SDK call behave as expected" — wrong branch. Use [SDK.md](SDK.md).

## Process

1. **State the question.** Before writing code, write down what state model and what question you're prototyping — one paragraph, printed at the top of the console app's output, not just a comment. A prototype that answers the wrong question is pure waste.

2. **Isolate the logic in a portable type.** Put the actual logic — the bit that's answering the question — in a small, pure class or set of functions that could be lifted out and dropped into the real codebase later. The `Main` method around it is throwaway; this type isn't.

   The right shape depends on the question:
   - A pure reducer — `(state, action) => state`. Good when actions are discrete events and state is a single value.
   - A state machine — explicit states and transitions. Good when "which actions are even legal right now" is part of the question.
   - A small set of pure functions over a plain record/DTO. Good when there's no implicit current state — just transformations or a data shape to validate.

   Keep it pure: no console I/O, no file access, reaching inside it. The console shell calls into it; nothing flows the other direction — that's what makes the validated type liftable into the real module once the question's answered.

3. **Build the console shell.** One scratch console project (`dotnet run`), no external dependencies beyond what the question needs. Lay it out top to bottom:
   1. Title and one-line explanation of what this lets you explore (the question from step 1).
   2. Current state — the full relevant state, printed as labelled fields (not a raw object dump), reprinted after every action so the change is visible.
   3. Free-play menu — one option per action, always available, so you can poke at the model in any order.
   4. A couple of guided scenarios — hard-coded sequences of actions that demonstrate the awkward cases (the happy path, a tricky edge case, an attempt at something that should be illegal), each printing its state after every step.

4. **Hand it over.** Run through the guided scenarios, then free-play. The interesting moments are "wait, that shouldn't be possible" or "huh, I assumed X would be different" — those are the bugs in the idea, which is the whole point.

5. **Capture the answer and the prototype**, the way [SKILL.md](SKILL.md) describes: the validated reducer/machine/function set lifts into the real module (the decision, absorbed); the console shell rides along to the throwaway branch that keeps the prototype as a primary source.

## Anti-patterns

- Don't add tests. A prototype that needs tests is no longer a prototype.
- Don't wire it to a real database or SDK call. Use in-memory state — that's the Logic branch; a real call is [SDK.md](SDK.md).
- Don't generalise. No "what if we wanted to support X later." The prototype answers one question.
- Don't blur the logic and the shell together. If the pure type references console I/O, it's no longer liftable.
