# Development

## Git Hooks

This repo ships hooks in `.githooks/`. After cloning, activate them once:

```bash
git config core.hooksPath .githooks
```

### pre-commit

Syncs `tools/src/modules/github/` → `plugins/review/skills/fix/github/` and stages the result before every commit.
