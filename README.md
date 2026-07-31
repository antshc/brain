```sh
copilot plugin marketplace add antshc/brain
```
## Install worflow plugins
```sh
(copilot plugin uninstall wf@brain >/dev/null 2>&1 || true) && \
copilot plugin install wf@brain && \
(copilot plugin uninstall droid@brain >/dev/null 2>&1 || true) && \
copilot plugin install droid@brain && \
(copilot plugin uninstall ralph@brain >/dev/null 2>&1 || true) && \
copilot plugin install ralph@brain && \
(copilot plugin uninstall review@brain >/dev/null 2>&1 || true) && \
copilot plugin install review@brain

(copilot plugin uninstall wf@brain >/dev/null 2>&1 || true) &&  \
(copilot plugin uninstall pet@brain >/dev/null 2>&1 || true) && \
(copilot plugin uninstall droid@brain >/dev/null 2>&1 || true) && \
(copilot plugin uninstall ralph@brain >/dev/null 2>&1 || true) && \
(copilot plugin uninstall review@brain >/dev/null 2>&1 || true)
```
## Install dotnet skill 
```sh
copilot plugin list
copilot plugin marketplace add dotnet/skills
copilot plugin install dotnet@dotnet-agent-skills
```

## Install mattpocock skills
### Productivity
```
gh skill install mattpocock/skills skills/productivity/writing-great-skills --agent github-copilot --scope user -f && \
gh skill install mattpocock/skills skills/productivity/handoff --agent github-copilot --scope user -f && \
gh skill install mattpocock/skills skills/productivity/teach --agent github-copilot --scope user -f

gh skill install github/awesome-copilot skills/mini-context-graph --agent universal --scope user -f

```
### Engineering
```
gh skill install mattpocock/skills skills/engineering/codebase-design --agent github-copilot --scope user -f && \
gh skill install mattpocock/skills skills/engineering/research --agent github-copilot --scope user -f
```


## AI Engineering
```sh
gh skill search writing-great-skills --owner mattpocock
```

## Install atlassian 
```sh
(copilot plugin uninstall atlm@brain >/dev/null 2>&1 || true) && \
copilot plugin install atlm@brain

(copilot plugin uninstall atl@brain >/dev/null 2>&1 || true) && \
copilot plugin install atl@brain
```

## Install az cli plugins
```sh
(copilot plugin uninstall az@brain >/dev/null 2>&1 || true) && \
copilot plugin install az@brain
```

## Install brain skills
```sh
gh skill install antshc/brain skills/be-terse --agent github-copilot --scope user -f
gh skill install antshc/brain skills/suggest --agent github-copilot --scope user -f
```
