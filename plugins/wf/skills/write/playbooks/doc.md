# Doc

Write or update one standalone Markdown page from supplied facts. Use `draft` or `update`; `normalize` returns a scope gap. Read the Doc template disclosed by the router in full before rendering. It owns section order, mode blocks, optionality and troubleshooting structure.

## Workflow

1. **Resolve scope.** Identify purpose, audience, mode, operation, destination and renderer from the request and existing page. Apply the router's mode policy; preserve supplied scope and output constraints. Done when the page's purpose and format are known, or a material ambiguity has been returned to the caller.
2. **Map facts.** Read the supplied content and permitted local sources. Keep facts, source conflicts and unknowns distinct. Return missing evidence or decisions as gaps; do not dispatch investigation or invent defaults, failures, causes or fixes. Done when each included claim has support or an explicit gap.
3. **Render.** Fill only the selected template mode block and applicable sections. For updates, preserve unaffected content and existing structure unless restructuring was requested; use the template to check applicable obligations. Retain exact code, commands, logs, error messages, identifiers, citations, confidence and caller-required markers. Done when the draft covers the requested scope without unused scaffolding.
4. **Refine page prose.** Apply the `guide` route per the router's Internal hand-offs to the full page, with its selected mode and template constraints; keep the selected structure and protected text. Done when page prose follows the writing route, with change notes separate from the body.
5. **Refine actions.** When instructions or troubleshooting actions exist, apply the `steps` route per the router's Internal hand-offs to only the procedural blocks with their conditions and expected results; preserve surrounding structure. Done when every procedural block follows the writing route, or the page has none.
6. **Check and return.** Check against the template's Rules and section conditions. Return the page, with update notes, conflicts and gaps separately. Use the router's output-path policy; no default path or publication is implied. Missing evidence yields an explicitly incomplete draft, not a fabricated complete page. Done when every requested page is returned or its blocker is named.
