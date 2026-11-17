# Model the Domain

Encode the domain in a data structure instead of scattering it across conditionals. The right structure makes invalid states unrepresentable and deletes branches.

Reach for a state machine instead of scattered booleans or phase checks, a typed model instead of loose parameters, a map, registry, or discriminated union instead of branching spread across files, a reducer instead of ad hoc mutations, and an index, queue, or normalized collection where the access pattern calls for it.

Organize modules around domain knowledge, ownership and invariants, not load/validate/save phases. If no familiar structure fits, derive it from invariants and access patterns.

Do not force it. Keep boring code when the shape is clear, local, and unlikely to grow, and distrust an abstraction that adds indirection without removing branches, duplicated rules, invalid states or lifecycle risk.

The sign that you skipped this: a feature that grows an if/else chain by one more branch, or a second boolean that must stay in sync with the first.
