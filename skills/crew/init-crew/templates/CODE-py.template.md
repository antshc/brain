# CODE — Python

<!-- Read in full by crew-implement during IMPLEMENTATION. Hazard rules below are Python-general and ship with this template — kept even when repository practice differs; a conflict is recorded in the shared GOTCHAS.md instead of edited here. Style/Layer placement/Design principles/Tests describe this repo's own conventions — never invent or copy example values from another repo. -->

## Hazard rules (Python)
- A broad `except Exception` (or bare `except:`) hides the real failure — prefer the narrowest exception type that actually fixes the error.
- Mutable default arguments (`def f(x=[])`) are shared across every call — default to `None` and build the mutable value inside the function body.

## Style
<!-- Naming, formatting, and file organization conventions actually used in this repo. -->

## Layer placement
<!-- Where different kinds of Python code belong in this repo (folders/layers/modules) and how placement is decided. -->

## Design principles
<!-- Design rules this repo demonstrably follows for Python code (e.g. module depth, dependency direction, allowed/forbidden patterns). -->

## Tests
<!-- Where Python tests live, how they're structured/named, and when they're required in this repo. -->
