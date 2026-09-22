# Inspect System

Prompt examples and recommendations for getting precise, evidence-backed results from the `inspect-system` skill.

## Write a strong instruction

A useful instruction names the **unit to inspect**, the **question to settle**, and the **boundary of the answer**.

Use this shape:

> Inspect **{{unit}}** to determine **{{question}}**. Start at **{{entry point}}** and stop at **{{observable outcome or terminal system}}**. Cover **{{important branches or concerns}}**. Write the result to **{{optional output path}}**.

Include the details that materially change the investigation:

- Name the capability, behavior, deployable, message, item type, store, route, job, or configuration key you already know.
- Ask one concrete question that the inspection must answer, not a broad request to "document the system."
- State where the trace starts and what observable outcome, process boundary, or external system ends it.
- Name important branches such as feature flags, provider selection, retries, failures, fallbacks, or asynchronous paths.
- Ask for current **as-built** behavior. Use a design or review skill when the goal is a proposed change or a before-and-after delta.
- Mention suspected mocks, emulators, or development-only stores so the inspection can distinguish wiring from production behavior.
- Request a probe when static code cannot settle a runtime claim, and say which commands or environments are safe to use.
- Provide an output path only when the default location under `docs/ongoing/` is unsuitable.
- Keep one inspection unit per instruction. Split unrelated behaviors, flows, or data boundaries into separate requests.

The skill selects the inspection axis and appropriate diagram from the question. Describe what you need to understand rather than prescribing a diagram type.

## Behavior instruction examples

Use the Behavior axis for implementation behavior inside one deployable.

**Focused call chain**

> Inspect how `OrderApi` submits an order. Start at `POST /orders` and stop when the API returns a response or schedules downstream work. Explain validation, payment-provider selection, persistence, failure branches, and which concrete implementations serve the calls. Document the current as-built behavior with filename-only file links followed by visible line numbers.

**Configuration decision**

> Inspect how the billing worker chooses a payment provider. Start where the worker reads the provider configuration and stop at the selected provider call or terminal failure. Cover missing configuration, feature flags, fallback behavior, and test doubles. Determine which provider production configuration selects.

**Weak instruction**

> Inspect order processing.

This leaves the entry point, outcome, deployable, and deciding question undefined, so the result is likely to be broad or based on assumptions.

## Flow instruction examples

Use the Flow axis when the behavior crosses independently runnable or deployed processes.

**End-to-end message path**

> Inspect the deployable chain for an accepted order. Start when `OrderApi` publishes `OrderAccepted` and stop when every outcome-relevant branch reaches a system whose source is unavailable or outside the order-confirmation outcome. For each boundary, identify the emitted contract, receiving trigger, transport binding, retries, and terminal failures. Include all deployables whose executing source is available.

**Known starting contract**

> Inspect what handles the `customer.deleted.v2` event after `CustomerService` emits it. Trace every in-repo deployable that receives or forwards the event, including dead-letter and retry paths, and stop at external systems. Settle whether deletion of analytics and notification data is synchronous, asynchronous, or absent.

## Data instruction examples

Use the Data axis when the answer turns on one item type and its store.

**Ownership and consistency**

> Inspect the `Session` item and its production store. Determine the key design, authoritative writer, readers, serialization shape, consistency guarantees, concurrent-write behavior, expiry, and deletion path. Distinguish production configuration from local emulators and identify any claim that requires a runtime probe.

**Migration safety**

> Inspect how `Order.status` is stored and migrated. Identify every writer and reader, the serialized values, backward-compatibility handling, migration or backfill behavior, and what happens when old and new application versions run concurrently. Settle whether adding a new status is safe during a rolling deployment.

## Recommendations

- Prefer a question with a decision at the end: "Which implementation runs?", "Where does this message terminate?", or "Can this read be stale?"
- Supply greppable anchors such as symbols, routes, queue names, table names, event types, and configuration keys.
- Define success in observable terms: a response, persisted record, emitted event, scheduled job, or terminal external call.
- Explicitly request failure and fallback paths when they matter; otherwise a happy-path trace may answer too little.
- Separate facts you need proved from suspicions you want checked. For example: "Verify whether `InMemoryOrderStore` is development-only."
- State access constraints before inspection begins, including unavailable repositories, prohibited environments, or commands that must not run.
- Let evidence determine the conclusion. Avoid embedding the expected answer as if it were already true.
- Ask for unknowns to be named as concrete next probes instead of filled with inference.

## It is working if

- Every repository file mention uses `[filename](relative/path#Lstart):Lstart-end`; each behavioral claim has the deciding file reference nearby.
- Facts, assumptions, unknowns, and conclusions are visibly distinct.
- The trace has a named entry point and a defensible stopping boundary.
- Real implementations are separated from mocks, stubs, emulators, and local-only configuration.
- Cross-process boundaries identify both sides of the contract.
- Unsettled runtime behavior ends in a concrete probe, not a guess.