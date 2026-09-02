# Coding Policy

## Purpose and Scope

This file defines coding rules for production C# code and tests used by the agent workflow.

- MUST follow this policy unless a higher-priority instruction conflicts.
- MUST prefer deep modules and avoid speculative features.
- SHOULD match existing style in the touched project (namespace style, using placement, class layout).

## Rule Priority

When rules conflict, apply this order:

1. Direct user task instructions.
2. Existing local project conventions in touched files.
3. This policy.

<!--
Ordering contract for actionable rule sections:
- MUST
- MUST NOT
- SHOULD
- MAY
-->

## Production C# Rules (MUST)

### Style Source of Truth

- `workspace/zerto-zic/.editorconfig` is the build-enforced source of truth for naming and formatting (`dotnet_analyzer_diagnostic.category-Style.severity = error`, `category-Naming.severity = warning`); violations of its `error`-severity rules fail the build.
- MUST treat this policy as a summary of the `.editorconfig` rules most relevant to hand-written code, not a replacement for it — when in doubt, check `.editorconfig` directly rather than relying on this section from memory.
- Where this policy is stricter than `.editorconfig` (noted inline below), MUST follow this policy; it will not break the build but is still required.

### Naming

- MUST apply the naming styles defined in this table (mirrors `.editorconfig` `dotnet_naming_rule.*`, enforced as build errors).

| Scope | Style | Example |
|-------|-------|---------|
| Private fields | `m_camelCase` | `m_repository` |
| Private static fields | `s_camelCase` | `s_instance` |
| Private constants | `c_camelCase` | `c_maxRetries` |
| Protected constants | `c_camelCase` | `c_defaultTimeout` |
| Protected readonly fields | `PascalCase` | `BaseUrl` |
| Parameters | `camelCase` | `userId` |
| Test methods (`*Tests.cs`, `*TestsBase.cs`) | `PascalCase_With_Underscore` | `Read_WhenNoData_Empty` |

- MUST mark fields `readonly` when never reassigned outside the constructor (`.editorconfig` `IDE0044 = error`).
- MUST use the same parameter/argument name for the same semantic value across an entire call chain.

### var Usage

- MUST use `var` when the type is immediately apparent from the right-hand side (`.editorconfig` `csharp_style_var_when_type_is_apparent = true:error`).
- MUST NOT use `var` for built-in types (`.editorconfig` `csharp_style_var_for_built_in_types = false:error`).
- MUST NOT use `var` in other cases. Note: `.editorconfig` only marks this a `suggestion` (`csharp_style_var_elsewhere = false`), so the build will not catch a violation — this policy is stricter and still applies.

### Collection Emptiness Checks

- MUST use `.Any()` to check emptiness of a computed/lazy `IEnumerable<T>`, not `.Count()`/materialization.

### Method Form

- MUST use block bodies.
- MUST make private helper methods instance methods by default.
- MUST NOT use expression-bodied methods (`=>`), including single-line cases. Note: `.editorconfig` allows single-line expression bodies (`csharp_style_expression_bodied_methods = when_on_single_line`) and won't flag them at build time — this policy is stricter and still applies.
- MUST remove a private/internal methods,parameters,fields as soon as it has no remaining callers; do not leave dead code behind a refactor "just in case".

### Formatting

All rules below are enforced as build errors by `.editorconfig` (`IDE0055` formatting rule plus the listed StyleCop diagnostics); a violation fails the build, not just a style nit.

- MUST use 4-space indentation for `.cs` files (`indent_size = 4`).
- MUST use CRLF line endings for `.cs` files (`end_of_line = crlf`, `SA1518`).
- MUST save new `.cs` files as UTF-8 with a BOM, matching existing files in this repo (`.editorconfig` `charset = utf-8-bom`; applied by editors on save, not currently a build-enforced diagnostic).
- MUST verify a newly created `.cs` file actually has real CRLF bytes and a BOM, not just LF or literal `\r\n` text — some file-creation tools silently write a literal backslash-r/backslash-n when the content string contains explicit `\r\n` escape sequences. Check with `od -c path | head` (real CRLF, not `\ r \ n` as separate chars) and `head -c3 path | od -An -tx1` (expect `ef bb bf`). If wrong, recreate the file using real newlines and fix up with `sed -i 's/\r$//; s/$/\r/' path`.
- MUST always use braces, including single-line `if`/`else`/`for`/`while` bodies.
- MUST use Allman style (opening brace on its own line).
- MUST keep one blank line between adjacent elements (classes, methods, properties) (`SA1516`).
- MUST place attributes on their own line (`SA1134`).
- MUST keep spaces around operators (for example `a + b`) (`SA1003`).
- MUST NOT leave trailing whitespace (`SA1028`).
- MUST NOT add a blank line before closing braces (`SA1508`).
- MUST NOT add multiple consecutive blank lines (`SA1507`).

### CancellationToken

- MUST propagate `CancellationToken` through async call chains.
- MUST add `CancellationToken cancellationToken` to every async method.
- MUST pass `cancellationToken` to awaited calls that accept one.

### Error Handling

- MUST handle exceptions at system boundaries (for example HTTP handlers, background workers, top-level entry points).
- MUST log or rethrow caught exceptions.
- MUST NOT swallow exceptions silently.
- MUST NOT add `try/catch` for scenarios that cannot happen.
- SHOULD catch specific exception types instead of `Exception`, unless immediately rethrowing.

### Zerto.Infrastructure.Utils Usage

- MUST validate constructor/method arguments with `Zerto.Infrastructure.Utils.Arguments.ArgumentsValidator` (`ValidateIsNotNull`, `ValidateStringIsNotNullOrEmpty`, `ValidateCollectionIsNotNull`) instead of hand-rolled `if (x == null) throw ...` checks — this is the dominant argument-validation pattern across `main/src` (300+ call sites).
- MUST use `Zerto.Infrastructure.Utils.Extensions.EnumerableExtensions.IsNullOrEmpty()` to check whether an `IEnumerable<T>` is null or empty, rather than `x == null || !x.Any()`.
- MUST use `Zerto.Infrastructure.Utils.System.IClock` (injected), not `DateTime.Now`/`DateTime.UtcNow` directly, for any time value that needs to be testable/mockable.
- SHOULD use `Zerto.Infrastructure.Utils.Threading.AsyncHelper.RunSync()` only at the few existing synchronous-bridge call sites (for example entry points that cannot be made `async`); do not introduce new sync-over-async code paths elsewhere.
- SHOULD use `Zerto.Infrastructure.Utils.Extensions.StringExtensions.Truncate()` when bounding a string to a max length, instead of manual `Substring` length checks.
- SHOULD use `Zerto.Infrastructure.Utils.Extensions.SafeExtensions.SafeEquals<T>()`/`SafeEqualCollections<T>()` for null-safe equality (for example inside `Equals()` overrides), instead of a manual `x == null ? y == null : x.Equals(y)` check.
- SHOULD use `Zerto.Infrastructure.Utils.Extensions.EnumerableExtensions.EnumerableAsString()` (any `IEnumerable<T>`, including lists/arrays) and `Zerto.Infrastructure.Utils.Extensions.DictionaryExtensions.DictionaryAsString()` for logging/diagnostics rendering of collections and dictionaries, instead of hand-rolled `string.Join`. The package has no separate `ListAsString`/`ArrayAsString` — `EnumerableAsString()` covers those cases too.
- SHOULD use `Zerto.Infrastructure.Utils.Extensions.EnumsExtensions.GetAttribute<TAttribute>()`/`ParseEnumFromAttributeValue<TEnum>()` for enum-attribute lookups (for example resolving a display name or an external-value mapping from a custom attribute), instead of hand-rolled `GetCustomAttribute`/`GetMember` reflection.
- MUST NOT re-implement helpers already provided by `Zerto.Infrastructure.Utils` (argument validation, null-or-empty collection checks, clock abstraction, safe equality, collection/dictionary-to-string, enum-attribute lookup) — search for an existing extension/utility before adding a new one.

### Serialization

- MUST add new fields on `[JsonConstructor]` types as trailing constructor parameters with safe defaults (for example `= null`) and matching init/get-only properties.
- MUST preserve backward deserialization for legacy serialized blobs that do not contain new fields.

### REST API Query Parameters

- MUST validate optional numeric/paging query parameters (for example `top`, `limit`) at the controller boundary and return `400 Bad Request` for out-of-range values (for example `<= 0`), rather than silently ignoring them and returning `200` with a default/full result.
- MUST cap any user-supplied result-count parameter with a configuration-tweak ceiling (see [Concept 0007](../docs/concepts/0007-operational-parameters-via-configuration-tweaks.md)); the request value may only narrow the ceiling, never exceed it.

### Response Model Collections

- MUST default collection-typed response-model properties to an empty collection, never `null`.

### Documentation in Code

- MUST NOT add XML doc comments unless explicitly requested.
- MUST NOT add inline comments that restate what code already says.
- MUST NOT add short comments for non-obvious rationale.

## Test Rules

### Unit Tests (MUST)

- MUST test through public API (verify what, not how).
- MUST mock only system boundaries (external APIs, databases, time/randomness, file system).
- MUST use dependency injection for external dependencies.
- MUST use `// Arrange`, `// Act`, `// Assert` sections.
- MUST keep one logical assertion per test.
- MUST verify behavior through public interfaces, not internals.
- MUST create the SUT in test constructor via `new`.
- MUST use `MockBehavior.Strict` by default.
- MUST use behavior-oriented test names in the form `MethodOrBehavior_Condition_ExpectedResult` (for example `Read_WhenNoData_ReturnsEmpty`), in plain English, with the expected result always last (`.editorconfig` `test_methods` naming rule for `*Tests.cs`/`*TestsBase.cs` enforces `PascalCase_With_Underscore` as a build error).
- MUST write a single-case test as a `[Fact]`; use `[Theory]`/`[InlineData]` only for two or more distinct cases.
- MUST NOT mock internal collaborators or classes you control.
- MUST NOT use switch expressions inside `Mock.Setup()` when `.ReturnsAsync()` is required; use switch statements or per-branch setup calls.
- MUST NOT use `if` in tests, except to reduce excessive duplication.
- MUST name reusable mock setup helper methods with a `Setup` prefix and `Mock` suffix (ex: `SetupConfigurationMock`).
- SHOULD use factory methods when setup varies.
- SHOULD wrap reusable mock setup in named helper methods.
- SHOULD use `Setup` + `ReturnsAsync` for happy paths.
- SHOULD use `SetupSequence` for varying call results.
- SHOULD use `ThrowsAsync` for failures.
- SHOULD use `Callback` for argument capture when needed.

### Integration and Framework Tests

- SHOULD extend an existing test when adding a new field assertion, instead of creating a new test.

## Fakes and Test-Data Reuse Policy

- MUST search for an existing fake/helper for the same domain type or purpose before adding a new one.
- MUST delegate new overloads to existing constructors/methods.
- MUST create a new fake/helper only when the domain contract or purpose is genuinely different.
- MUST NOT reorder existing constructor or method parameters when adding overloads.
- SHOULD extend existing fake/test-data helpers by adding overloads or optional/nullable parameters.

## Red Flags (Reject During Review)

- MUST treat each item below as a review failure.
- MUST NOT mock internal collaborators.
- MUST NOT use `Times.Exactly(N)` call-count assertions.
- MUST NOT test private methods directly.
- MUST NOT verify behavior by internal DB/state inspection instead of public API.
- MUST NOT accept tests that break on refactor with no behavior change.
- MUST NOT accept a `[Theory]` with a single `[InlineData]` case.
- MUST NOT accept a leftover unused private/internal method.


## Agent Final Checklist

Before finalizing changes:

1. MUST confirm touched files follow local style patterns.
2. MUST confirm async call chains propagate `CancellationToken`.
3. MUST confirm test changes follow public-API testing and strict mocking rules.
4. MUST confirm no duplicate fake/test-data helpers were introduced when extension was possible.
5. MUST confirm naming and formatting rules were applied.