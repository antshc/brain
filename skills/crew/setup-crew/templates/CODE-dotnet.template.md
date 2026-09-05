# CODE — .NET

<!-- Read in full by crew-implement during IMPLEMENTATION. Hazard rules below are .NET-general and ship with this template — kept even when repository practice differs; a conflict is recorded in the shared GOTCHAS.md instead of edited here. Style/Layer placement/Design principles/Tests describe this repo's own conventions — never invent or copy example values from another repo. -->

## Hazard rules (.NET)
- A `.csproj` (or the `.sln` that groups several) is the Module boundary — a change belongs to its nearest `.csproj`, never a folder without one.
- An `IDisposable` resource acquired in a method must be disposed (`using`) on every exit path, including exceptions — leaking one silently degrades the process over time.

## Style
<!-- Naming, formatting, and file organization conventions actually used in this repo. -->

## Layer placement
<!-- Where different kinds of .NET code belong in this repo (folders/layers/projects) and how placement is decided. -->

## Design principles
<!-- Design rules this repo demonstrably follows for .NET code (e.g. module depth, dependency direction, allowed/forbidden patterns). -->

## Tests
<!-- Where .NET tests live, how they're structured/named, and when they're required in this repo. -->
