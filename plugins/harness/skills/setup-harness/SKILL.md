---
name: setup-harness
description: Create a Harness Configuration File in the current directory without overwriting an existing file.
---

# Setup Harness

Run from the intended harness directory. Resolve its physical absolute path:

```bash
harnessRoot=$(pwd -P)
```

If `$PWD/.harness.env` exists, print its contents and do not modify it:

```bash
cat .harness.env
```

Otherwise, create it with:

```bash
printf 'HARNESS_ROOT=%s\n' "$harnessRoot" > .harness.env
```

Emit the created path or the existing settings.