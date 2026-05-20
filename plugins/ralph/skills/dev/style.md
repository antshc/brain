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
| Public methods (test files) | `PascalCase_With_Underscores` | `Checkout_WithValidCart_ReturnsConfirmed` |

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

## Disabled / Relaxed

- `this.` qualifier: not required
- XML documentation: not required
- Ordering of members within a class: not enforced
- Using directive ordering/placement: not enforced
