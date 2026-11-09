# Panel Alternatives

Each section shows the same message written a different way. The **Confluence result** line says what `map-markdown-adf` produces from it.

## 1. Plain blockquote

**Confluence result:** `blockquote`

> Quoted line for the blockquote check.

## 2. Panels — `map-markdown-adf` syntax

**Confluence result:** `panel` (`attrs.panelType`). Marker on its own line; text on the next line.

> [!INFO]
> Info panel text.

> [!NOTE]
> Note panel text.

> [!WARNING]
> Warning panel text.

> [!SUCCESS]
> Success panel text.

> [!ERROR]
> Error panel text.

## 3. GitHub alerts

**Confluence result:** `panel` for `NOTE` and `WARNING`; `blockquote` with the literal `[!TIP]` / `[!IMPORTANT]` / `[!CAUTION]` text for the rest. GitHub renders all five as alerts but not `INFO`, `SUCCESS`, or `ERROR`.

> [!NOTE]
> Useful information.

> [!TIP]
> Helpful advice.

> [!IMPORTANT]
> Key information.

> [!WARNING]
> Urgent information.

> [!CAUTION]
> Risky action.

## 4. Bold label paragraph

**Confluence result:** `paragraph`. Portable everywhere; no panel styling.

**Info:** Info panel text.

**Note:** Note panel text.

⚠️ **Warning:** Warning panel text.

✅ **Success:** Success panel text.

❌ **Error:** Error panel text.

## 5. Admonitions (MkDocs / Docusaurus)

**Confluence result:** `codeBlock` as fenced below; unfenced, plain `paragraph` text. Rendered only by the owning tool.

```text
!!! note "Note"
    Note panel text.
```

```text
:::warning
Warning panel text.
:::
```

## 6. HTML block

**Confluence result:** `paragraph` with the raw HTML as literal text; many Markdown renderers strip or escape it too.

<div class="note">Note panel text.</div>

## 7. Collapsible section

**Confluence result:** `expand`, not a panel.

<details>
<summary>Expandable note</summary>

Note panel text.
</details>

## Summary

| Form | GitHub | Confluence via `map-markdown-adf` |
|---|---|---|
| `> text` | Quote | `blockquote` |
| `> [!INFO\|NOTE\|WARNING\|SUCCESS\|ERROR]` | Alert for `NOTE`, `WARNING`; quote otherwise | `panel` |
| `> [!TIP\|IMPORTANT\|CAUTION]` | Alert | `blockquote` with literal marker |
| `**Label:** text` | Bold paragraph | `paragraph` |
| `!!! note` / `:::note` | Plain text | `paragraph` (or `codeBlock` if fenced) |
| `<div>` | Stripped or plain | `paragraph` with literal HTML |
| `<details>` | Collapsible | `expand` |
