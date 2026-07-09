---
name: to-spec
description: Create a spec from codebase context and submit as a GitHub issue. Use when user wants to write a spec or plan a new feature.
argument-hint: '<feature description>'
disable-model-invocation: true
---

Ask the user: _"What is the target branch and feature ID? (e.g. `release/1.1.10`, `PROJ-1234`)"_

You may skip steps if you don't consider them necessary.

1. Explore the repo to understand the current state of the codebase, if you haven't already. If `grill-design` ran, use the project's domain glossary vocabulary throughout the spec and respect any ADRs, SDRs in the area you're touching.

2. Sketch out the major modules you will need to build or modify to complete the implementation. Actively look for opportunities to extract deep modules that can be tested in isolation.

A deep module (as opposed to a shallow module) is one which encapsulates a lot of functionality in a simple, testable interface which rarely changes.

Check with the user that these modules match their expectations. Check with the user which modules they want tests written for.

3. Write the spec using the template and writing style defined in `references/spec-format.md`.

4. Save to GitHub — see `references/create-github-issue.md`.

5. Report the spec location, milestone title, and URLs to the user.
