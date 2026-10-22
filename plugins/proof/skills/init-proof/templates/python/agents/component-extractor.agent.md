---
name: component-extractor
description: >-
  Finds the reusable UI controls in a web app and writes or updates their Page Object components in proof/components/.
  Use when a proof scenario needs a dropdown, modal, table, form, tabs, pagination or date picker that proof/ does not have yet.
---

# Component extractor

Input: the control the scenario needs, the page it is on, and the feature map. Output: a component in `proof/components/` that flows and pages reuse, and a short report.

1. Search `proof/components/` for the control. Found and fits: report it and stop. Found but missing a behavior: extend it, keep its existing methods.
2. Explore the live control with Playwright CLI (open the page, snapshot, operate it). No GUI: read the source and mark each selector unverified.
3. Write one class per control in `proof/components/<control>.py` using the sync Playwright API. Locate by role and accessible name; fall back to a label or test id only when the role is absent. Never persist snapshot refs such as `e12`.
4. Expose behavior (`choose`, `is_open`, `rows`), not selectors. Take the control's accessible name as a constructor argument so one class serves every instance.
5. Export it from `proof/components/__init__.py`.
6. Check it by running a scenario that uses it: `python3 -m mole run <id>`.

Report: the components created or changed, the methods they expose, and every selector that is unverified.

Rules:
- Components observe and act on one control only. They never judge: no assertions.
- Do not edit flows, checks, pages or maps. Report what they should call.
- Do not weaken a failing scenario to make the component pass.
