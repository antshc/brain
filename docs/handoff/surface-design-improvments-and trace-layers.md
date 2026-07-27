
The two below never was triggred, i think the Surface design improvements  covered with the existing concept deep module concept.
The Trace through the layers also need revision.
---
### Surface design improvements

When a proposed structure has a narrower/deeper alternative implied by a loaded Concept, name that Concept and surface it: "This Concept mandates deep modules — could this be one deep module with a narrow interface, instead of three shallow modules that leak their internals to each other?" Once a Concept rules an option out, don't present it as equally valid alongside the compliant one.

### Trace through the layers

When a new flow crosses a layer or a transaction/process/network boundary defined by a loaded Concept, read the relevant `Building blocks` section in `ARCHITECTURE.md` (and the specific service's full doc if one is open, per Load strategy guardrails), then select one representative scenario and trace it end-to-end, naming each layer from the loaded Concept as you go: "Trace 'place order' from the API down to persistence: which layer owns validation, which owns pricing, and where does the transaction boundary sit?" If a shortcut would skip a mandated layer, cite the Concept and surface the conflict rather than presenting the shortcut as equally valid.

When the trace needs to confirm what the code actually does at a layer (not just what `ARCHITECTURE.md` says), default that confirmation to `explore` (per *Delegate code lookups* above); reserve direct reads for anchoring the exact boundary line.

