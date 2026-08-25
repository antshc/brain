# Documentation template

Document public/protected .NET API contracts using standard XML documentation best practices.

- **Focus on:** contract, observable behavior, semantics, constraints, nullability, exceptions, cancellation, side effects, extension points.
- **Avoid:** implementation details, redundant comments, obvious restatements, incidental exceptions.
- **Cover:** interfaces, abstract classes, enums, extension methods, properties, methods, generic APIs.
- **`<summary>` must carry the terse "what it does" explanation, not just the contract:** the persisted output strips every method/property body, so `<summary>` is the only place a reader ever sees what a member actually does. One short clause of plain-language behavior is enough — never a body-length walkthrough, never implementation mechanics (which private field it sets, which helper it calls).

Implementing/overriding member with nothing to add → bare `<inheritdoc/>`, never mixed with new `<param>`/`<returns>`.

```csharp
/// <summary>Contract in one sentence — what it promises, not how.</summary>
/// <remarks>Non-obvious contract notes only (e.g. thread-safety, lifetime).</remarks>
public interface IWidgetStore<TKey>
{
    /// <summary>Looks up the widget for <paramref name="key"/>.</summary>
    /// <param name="key">Key to look up. Not <see langword="null"/>.</param>
    /// <param name="ct">Observed while the lookup is pending.</param>
    /// <returns>The matching widget, or <see langword="null"/> if none exists.</returns>
    /// <exception cref="OperationCanceledException"><paramref name="ct"/> was canceled.</exception>
    Task<Widget?> FindAsync(TKey key, CancellationToken ct);
}

public class BlobWidgetStore<TKey> : IWidgetStore<TKey>
{
    /// <inheritdoc/>
    public Task<Widget?> FindAsync(TKey key, CancellationToken ct);
}

/// <summary>Base pipeline stage; override <see cref="Process"/> to transform the input.</summary>
public abstract class PipelineStage
{
    /// <summary>Transforms <paramref name="input"/> for the next stage.</summary>
    public abstract object Process(object input);
}

/// <summary>Outcome of a widget validation attempt.</summary>
public enum ValidationResult
{
    /// <summary>Validation passed.</summary>
    Valid,
    /// <summary>A required field was missing.</summary>
    MissingFields,
}

public static class SettingExtensions
{
    /// <summary>Applies an override value, superseding the configured value until cleared.</summary>
    /// <returns>The same setting, for chaining.</returns>
    public static Setting<int> SetOverride(this Setting<int> setting, int value);
}

public class RequestOptions
{
    /// <summary>Time to wait before the request is canceled; &lt;= 0 falls back to the client's default.</summary>
    public TimeSpan Timeout { get; set; }
}
```

## Persisted fragment shape

One fragment per decompiled `.cs` file, written straight from that source — never by editing it. The fragment is exactly a `##` heading carrying the source path relative to its `src/` root, then one ```` ```csharp ```` block, and nothing else: namespace, type declarations with base lists and generic constraints, and each public/protected member reduced to its verbatim signature terminated by `;`, doc-commented as above. No `using` directives, no bodies, no private members, no `//IL_` comments, no `: base(...)` clauses.

````markdown
## Widgets/BlobWidgetStore.cs

```csharp
namespace Widgets;

/// <summary>Blob-backed widget store.</summary>
public class BlobWidgetStore<TKey> : IWidgetStore<TKey>
{
    /// <summary>Gets the container the widgets are read from.</summary>
    public string Container { get; }

    /// <inheritdoc/>
    public Task<Widget?> FindAsync(TKey key, CancellationToken ct);
}
```
````
