# Skills

Standalone Copilot agent skills. Each folder contains a `SKILL.md` and optional scripts.

## Install a skill

Preview before installing:

```bash
gh skill preview antshc/brain engineering/<skill-name>
```

Install a specific skill:

```bash
gh skill install antshc/brain engineering/<skill-name>
```

Install all skills interactively:

```bash
gh skill install antshc/brain
```

## Update

```bash
gh skill update --all
```

## Use a skill

Copilot picks the skill automatically based on your prompt and the skill's description.  
To invoke explicitly: `Use the /<skill-name> skill to ...`
