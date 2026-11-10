# Deep modules

Vocabulary and rules for designing **deep modules**: much behaviour behind a small interface, placed at a clean seam, testable through that interface. Aim: leverage for callers, locality for maintainers, testability for everyone. Adapted from mattpocock/skills `codebase-design` (MIT).

## Contents

- Principle
- Vocabulary
- Relationships
- Deep vs shallow
- Rules
- Designing for testability
- Dependency categories
- Seam discipline
- Testing strategy
- Rejected framings

## Principle

Apply when shaping or changing a contract: interface, invariant, error mode, seam, or adapter.

Put much behaviour behind a small interface. Callers and tests cross the same seam. Add a seam only when two adapters vary across it. Delete-test every module: if complexity just moves to callers, it was earning its keep; if it vanishes, it was a pass-through.

**Why:** depth gives callers leverage and maintainers locality; shallow contracts leak complexity into every call site.

A broken contract found by Interrogate is resolved through `design deep-module`, not patched in place.

## Vocabulary

Use these terms exactly; never substitute "component", "service", "API", or "boundary". Repo glossary terms still name domain concepts.

- **Module**: anything with an interface and an implementation; scale-agnostic (function, class, package, tier-spanning slice). _Avoid_: unit, component, service.
- **Interface**: everything a caller must know to use the module correctly: type signature plus invariants, ordering constraints, error modes, required configuration, performance characteristics. _Avoid_: API, signature (type-level surface only).
- **Implementation**: the module's body of code. Distinct from **Adapter**: a small adapter may have a large implementation (Postgres repo) and vice versa (in-memory fake). Say "adapter" when the seam is the topic; "implementation" otherwise.
- **Depth**: leverage at the interface; behaviour a caller or test can exercise per unit of interface learned. **Deep**: much behaviour behind a small interface. **Shallow**: interface nearly as complex as the implementation.
- **Seam** (Feathers): a place where behaviour can change without editing in that place; the location where a module's interface lives. Seam placement is its own decision, distinct from what goes behind it.
- **Adapter**: concrete thing satisfying an interface at a seam. Describes role, not substance.
- **Port**: interface defined at a seam for a cross-seam dependency.
- **Leverage**: what callers get from depth; one implementation pays back across N call sites and M tests.
- **Locality**: what maintainers get from depth; change, bugs, knowledge, and verification concentrate in one place. Fix once, fixed everywhere.

## Relationships

- A **Module** has exactly one **Interface**.
- **Depth** is a property of a **Module**, measured against its **Interface**.
- A **Seam** is where a **Module**'s **Interface** lives.
- An **Adapter** sits at a **Seam** and satisfies the **Interface**.
- **Depth** produces **Leverage** for callers and **Locality** for maintainers.

## Deep vs shallow

```
Deep:     [ small interface ]          Shallow:  [     large interface     ]
          [                 ]                    [ thin pass-through impl  ]
          [ deep impl, much ]
          [ complexity hid  ]
```

When designing an interface, ask:

- Can I reduce the number of methods?
- Can I simplify the parameters?
- Can I hide more complexity inside?

## Rules

- **Depth is a property of the interface, not the implementation.** A deep module may be composed internally of small, mockable, swappable parts; they stay out of the interface.
- **Deletion test.** Imagine deleting the module. Complexity vanishes → it was a pass-through. Complexity reappears across N callers → it earns its keep.
- **The interface is the test surface.** Callers and tests cross the same seam. Wanting to test past the interface signals the wrong shape.

## Designing for testability

1. **Accept dependencies; don't create them.**
   ```typescript
   function processOrder(order, paymentGateway) {}          // testable
   function processOrder(order) { new StripeGateway(); }    // hard to test
   ```
2. **Return results; don't produce side effects.**
   ```typescript
   function calculateDiscount(cart): Discount {}            // testable
   function applyDiscount(cart): void { cart.total -= d; }  // hard to test
   ```
3. **Small surface area.** Fewer methods → fewer tests; fewer params → simpler setup.

## Dependency categories

Classify each dependency of a deepening candidate; the category decides how the deepened module is tested across its seam.

1. **In-process**: pure computation, in-memory state, no I/O. Always deepenable; merge modules and test through the new interface. No adapter.
2. **Local-substitutable**: has a local test stand-in (PGLite for Postgres, in-memory filesystem). Deepenable when the stand-in exists; tests run against the stand-in. Seam stays internal; no port on the external interface.
3. **Remote but owned (ports & adapters)**: own services across a network (microservices, internal APIs). Define a port at the seam; the deep module owns the logic; transport is an injected adapter. Tests use an in-memory adapter; production an HTTP/gRPC/queue adapter.
4. **True external (mock)**: third-party services (Stripe, Twilio). Inject as a port; tests provide a mock adapter.

## Seam discipline

- **One adapter = hypothetical seam; two adapters = real seam.** Introduce a port only when at least two adapters are justified (typically production + test). A single-adapter seam is indirection.
- **Internal vs external seams.** A deep module may have internal seams (private, used by its own tests) besides the external seam at its interface. Never expose internal seams through the interface because tests use them.

## Testing strategy

Replace, don't layer.

- Delete old unit tests on shallow modules once tests at the deepened module's interface exist.
- Write new tests at the deepened module's interface.
- Assert observable outcomes through the interface, never internal state.
- Tests survive internal refactors; a test that changes with the implementation tests past the interface.

## Rejected framings

- **Depth as implementation-lines / interface-lines ratio** (Ousterhout): rewards padding. Use depth-as-leverage.
- **Interface as a language `interface` keyword or a class's public methods**: too narrow; interface includes every fact a caller must know.
- **"Boundary" for a seam**: overloaded with DDD bounded context; say **seam** or **interface**. System boundary in *Boundary discipline* keeps its meaning.
