# Help Playbook

**Trigger:** Invocation args start with `help`. `help` alone → usage examples. `help <request>` → 3 options to test the request. Never runs tests or touches cloud.

## help (no request)

Skip Discover. Print the block below verbatim, then stop.

```text
/testing-integrations <request>          test <request>: pick a kind (+ optional strategy)
/testing-integrations help               this help
/testing-integrations help <request>     3 ranked options to test <request>, with reasoning; runs nothing

KINDS — what runs; ladder: lowest seam first
 component          one accessor vs its real dependency: DB emulator, then cloud SDK
  /testing-integrations run the repository integration test for <Repository>
  /testing-integrations add a DB integration test reproducing <bug>

 functional-slice   integration testing framework: mock / fake config → in-process → real cloud
  /testing-integrations run <Class.Method>
  /testing-integrations run tests for ticket <TICKET-ID> on mock
  /testing-integrations smoke test the full flow
  /testing-integrations run <Class.Method> on real cloud with image <image-id>
  /testing-integrations run <Class.Method> against the deployment at <url>

 local-runtime      last rung: running local app, REST API first, web GUI last
  /testing-integrations call <endpoint> on the local instance and show the stored record
  /testing-integrations start the app locally and check <feature> in the UI

 experiment         off ladder: one uncertain question via the experiment skill
                    options: logic / runtime / integration (local or cloud) / ui
  /testing-integrations check whether the test role can <cloud action> in the dev account
  /testing-integrations does <serializer / middleware> handle <case>

STRATEGIES — how to test, combine with any kind
 reproduce          red → root cause → green
  /testing-integrations reproduce flaky <Class.Method>
  /testing-integrations why does <feature> break on the local instance

 regression         breadth run, delta vs baseline
  /testing-integrations regression for my branch changes
  /testing-integrations run all <area> tests, compare with main

Repo commands, environments, and filters are discovered from the repo docs at run time.
```

**Done when:** block printed; nothing executed.

## help <request>

1. **Discover.** Run **Discover (automatic, always first)**. **Done when:** `suites` table built.
2. **Locate the behavior.** Map the request to code and tests: existing tests covering it (names via search), owning suite, whether it crosses a real cloud boundary, local environment support (mock covers it or not). **Done when:** covering tests listed, or `none` + nearest suite.
3. **Build 3 options** from **Choose the kind — ladder**: the lowest rung that can show the behavior plus the next two viable rungs, each a different kind or environment, with a strategy (reproduce / regression) when the request implies it. Note why lower rungs were skipped. Behavior is an open question → one option may be an experiment (state its option: logic / runtime / integration / ui). Cover a gap with "write a new test in <suite>" as an option when no test exists. **Done when:** 3 distinct options.
4. **Print**, per option:
   - **Option N — <name>** (kind [+ strategy], environment)
   - **What it proves / misses:** behavior covered vs blind spots (mocked boundaries, real IAM, timing)
   - **Command:** exact command + filter from `suites.run` (cite source doc)
   - **Needs:** preflight items (docker, creds, image ID, accounts file)
   - **Cost / time:** local free vs cloud cost, rough duration
   - **Reasoning:** why this option fits the request
5. **Recommend** one option in one line with the deciding reason, then stop. Run nothing until the user picks. **Done when:** options + recommendation printed.

## Key Rule

Help is read-only. Print usage or options; execution waits for an explicit pick.
