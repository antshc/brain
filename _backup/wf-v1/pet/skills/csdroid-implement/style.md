# C# Code Style

## General Rule

Before writing new code, look at existing files in the same project to match their style (namespace style, using placement, class layout). Follow what the codebase already does.

## Naming Conventions

| Scope | Style | Example |
|-------|-------|---------|
| Private fields | `m_camelCase` | `m_repository` |
| Private static fields | `s_camelCase` | `s_instance` |
| Private constants | `c_camelCase` | `c_maxRetries` |
| Protected constants | `c_camelCase` | `c_defaultTimeout` |
| Protected readonly fields | `PascalCase` | `BaseUrl` |
| Parameters | `camelCase` | `userId` |

## `var` Usage

- Built-in types: **never** use `var` → `int count = 0;`
- Type is apparent: **always** use `var` → `var service = new PaymentService();`
- Elsewhere: **never** use `var` → `IPaymentClient client = GetClient();`

## Expression-Bodied Methods

Always use block body. Do not use expression-bodied methods (`=>`).

## Formatting (enforced)

- **4-space indentation** for `.cs` files
- **CRLF** line endings
- **No trailing whitespace**
- **Always use braces** even for single-line `if`/`else`/`for`/`while` bodies
- **Allman style** — opening brace on its own line
- **Blank line between adjacent elements** (classes, methods, properties)
- **No blank line before closing brace**
- **No multiple consecutive blank lines**
- **Attributes on their own line**, not inline with the element
- **Operator spacing**: spaces around operators (`a + b`, not `a+b`)

## CancellationToken

- Always propagate `CancellationToken` through async call chains
- Add a `CancellationToken cancellationToken` parameter to every `async` method
- Pass it to all awaited calls that accept one

## Error Handling

- Handle exceptions at system boundaries (e.g., HTTP handlers, background workers, top-level entry points)
- Do not swallow exceptions silently — log or rethrow
- Use specific exception types over catching `Exception` unless re-throwing
- Do not add `try/catch` for scenarios that cannot happen

## Documentation

- Do not write XML doc comments or inline comments for newly added code unless explicitly asked

## Disabled / Relaxed

- `this.` qualifier: not required
- XML documentation: not required
- Ordering of members within a class: not enforced
- Using directive ordering/placement: not enforced
