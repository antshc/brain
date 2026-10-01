<!-- @: terse; every claim traces to the investigation log; no placeholder left unresolved -->
# {{title|symptom + affected component, one line}}

## Summary of issue

{{2-3 sentences|what was reported vs what actually happened, and the observable impact}}

## Root cause & mechanism

{{1-2 sentences|setup facts the mechanism depends on — config, data shape, versions}}

<!-- @: optional bullet list of concrete facts (resources, positions, values) the mechanism hinges on; omit if none -->
- {{fact}} ← {{why it matters}}

**Why this fails:**

<!-- @: one item per mechanism-chain link, cause first; cite path:line or probe -->
1. **{{label|short mechanism name}}:** {{one line}} (`{{path:line}}`)

## Evidence

<!-- @: one row per deciding check; Source = path:line, log excerpt location, command, or doc URL -->
|  Metric / Check | Finding | Source / Reference |
|---|---|---|
| {{what was checked}} | {{observed value}} | {{citation}} |

## Ruled out

<!-- @: one line per falsified hypothesis; omit section if none -->
- **{{hypothesis}}** — {{what killed it}} ({{citation}})

## Known gap / tracking

<!-- @: omit section if no ticket, TODO, or upstream issue exists -->
{{ticket id, `// TODO` at path:line, or upstream issue URL}}
