---
name: hunt-deepmodule
description: Hunt shallow modules in a code diff — flag a public surface that grows without matching depth (redundant entry points, thin pass-through wrappers, leaked stream/disposable ownership, classitis, upward or cross-module reach). Use when reviewing a diff that adds or widens a public member: a new method or property on an interface, a new public method/property/type, added parameters, a changed return type, or visibility widened to public. Cross-references the C# LSP.
---

# Hunt deep modules

A **deep module** hides a lot behind a little: a small public **surface** (few members, few parameters, no leaked internals) over a rich implementation. A **shallow** module inverts that ratio — wide surface, thin depth. This skill hunts the shallow ones a diff introduces and turns each into a review finding.

`deep` and `shallow` are the leading words: judge every changed public member by which way its surface-to-depth ratio points.

## When this fires

Run the hunt when a reviewed diff touches a **public surface** — any of:

- a new method or property on an `interface`;
- a new `public` method, property, or type on a class;
- new parameters added to an existing public member;
- a changed return type on a public member (especially one now handing back `Stream`, `IDisposable`/`IAsyncDisposable`, a collection, or an internal type);
- visibility widened to `public`.

Each such change grows the surface; the hunt decides whether depth grew with it.

## The hunt

The C# LSP is the instrument — use it for every semantic hop; fall back to text search only when the LSP cannot answer. Work one changed public member at a time.

1. **Enumerate the new surface.** **List all symbols in each changed file** to collect the added/widened public members. This is the worklist.
2. **Weigh the surface.** **Get the type info and signature** of each member. Surface cost rises with parameter count, out/ref params, returned lifecycle-owning types (streams, disposables, handles the caller must manage), and leaked internal types.
3. **Weigh the depth.** From the interface member, **jump to its implementation**, then **look at what that body calls**. Rich fan-out into private helpers/accessors/engines = depth. A single forwarded call = **thin pass-through**; forwarding straight back out a layer = **middle-man**. **Follow the calls** one level into private helpers to tell real hidden logic from relay.
4. **Catch redundant entry points.** For near-twin members (same parameters, adjacent names — **search the workspace by name** to find siblings), **jump to each implementation** and **look at what each calls**. If they converge on the **same** private helper and differ only by one argument or one delegated call, they are one operation split in two → collapse into a single parameterized member.
5. **Catch leaked ownership.** For members returning a lifecycle-owning type, **find all references** and read every caller. If callers must remember to dispose, null-check, or order calls just so, the abstraction leaks internal responsibility → prefer a member that does the work internally over one that hands back the open resource.
6. **Catch classitis and dead surface.** **Find who calls each added member** (its callers / references). Zero in-repo callers = dead surface; a lone caller that could inline it, or a new type only constructed and immediately delegated to, is an unnecessary layer.
7. **Check the boundary.** **Go to the definition** of each dependency reached in step 3. A call that reaches **up** a layer, or into another feature module's concrete (non-`*.Abstractions`) project, is both a layering breach (SSR 0003/0009) and a leaky surface.

## LSP cheat-sheet

| Question | What to ask the LSP | Input |
|---|---|---|
| What public members changed? | **List all symbols in the file** | file |
| Full signature / surface cost? | **Get type info and signature** of the member | member |
| Interface → concrete body? | **Go to the implementation** of the member | interface member |
| Depth vs. pass-through? | **Show what the method calls** | method |
| Who depends on this? Dead / single-caller? | **Find callers / all references** of the member | member |
| Does a type leak internals or cross a layer? | **Go to the definition** of the type | type/symbol |
| Find near-twin members elsewhere | **Search the workspace for symbols by name** | name |

## Verdict

Judge **every** member on the worklist — the hunt is done only when each has a verdict, not when the first smell is found.

- Small surface + self-contained depth + no leak + clean boundary → **deep; nothing to flag.**
- Redundant entry points (4), thin pass-through / middle-man (3), leaked ownership (5), classitis / dead surface (6), or upward/cross-module reach (7) → raise a finding naming the specific narrowing, merge, or inversion. Confirmed shallowness worth fixing is `suggest`; minor polish is `nit`.
