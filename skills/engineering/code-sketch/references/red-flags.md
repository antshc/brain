# Design red flags

Screen the sketch before finishing. A red flag is a reason to revise or reject the shape.

## Shallow module

A large interface hiding little complexity. Judge depth by the capability and policy hidden behind the public surface relative to its size; prefer a simple interface backed by substantial behavior.

A deep call chain scatters understanding across layers; a deep module concentrates capability behind one interface.

Signs:

- Callers coordinate several methods to complete one operation.
- Public options expose internal stages or implementation choices.
- Learning the interface does not save the caller from learning the implementation.

## Information leakage

Multiple modules depend on the same internal decision: a representation, policy, or protocol detail appears in more than one place, so a change needs coordinated edits.

Public re-exports of transport or wire types leak. Parse external data into domain types behind the interface; keep storage schemas, framework objects, and protocol details private.

## Temporal decomposition

Modules organized by execution order instead of owned knowledge. Separate load, validate, transform, and save stages often repeat one representation and its invariants across several boundaries.

Group code around domain knowledge and ownership. Methods that run at different times can share a module when they protect the same decisions.

## Pass-through method

A method forwards the same arguments to another method with the same shape, adding a layer without hiding complexity.

Remove it or move responsibility to the module that can complete the operation. Keep a forwarding boundary only when it adds policy, adaptation, or a distinct abstraction.

## Split ownership

More than one module writes the same state or keeps its own copy. An agent editing one writer cannot see the others, so their rules diverge.

Give each piece of state one owner. Other modules read it or ask the owner to change it.

## Two ways to do one task

The design supports more than one way to do the same task. An agent copies whichever it finds first, so every way keeps gaining callers.

Keep one way. Move callers off the others and delete them in the same change.

## Importable internals

A caller can import a module's internals. An agent takes the shortest path that compiles, so internals become part of the interface.

Make internals unreachable from outside the module, so an outside import fails the build.

## Hand-synced list

Two or more places list the same items, and adding an item means editing every list. An agent that sees one list updates only that one.

Keep one list and derive the others from it. If a list cannot be derived, fail the build when the lists disagree.
