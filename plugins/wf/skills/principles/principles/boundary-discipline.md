# Boundary Discipline

Validate, narrow types, and handle errors where data crosses a system boundary (CLI args, config files, external APIs, network). Inside, trust the types: no re-validation and no redundant nil checks. Parse raw data into domain types at the boundary, and keep transport, storage, wire and framework types out of the public surface. Business logic lives in pure functions with no framework dependencies. The shell that calls them is thin. Keep general-purpose mechanism inside and special-purpose policy at the edge.

Two tests. Is this data crossing a boundary right now? If not, the validation is redundant. Can this be a pure function the shell just calls? If yes, extract it.
