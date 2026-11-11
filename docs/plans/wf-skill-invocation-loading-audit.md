# WF skill invocation loading audit

Initiative: `wf-skill-invocation-loading-plan` (the approved plan filename). Migration base: `c484152be9ca452c3f9bbaf3755b036e6ca74e9a`; original checklist base: `717dfe084bd6691e908fcedb3444ce6d54787286`.

Scope: WF caller wording, shared authoring/runtime instructions, invocation checker, affected tests. Other plugins and standalone skill callers retain their existing policy. Exclude `_backup/`, `_in-progress/`, `docs/kbs/`.

## Coverage

- [x] Reconciled all **272** original checklist occurrences against current main and the final files.
- [x] Fresh scan found **277** canonical literal/template call occurrences across **90** WF files; all checked by the invocation consistency suite.
- [x] Every applicable call uses the full-load prefix. The shared loading contract covers body, selected procedure, required/triggered resources, truncation, same-revision reuse, unavailable dependencies and skill-capable workers.
- [x] Updated dynamic workers and generated routing calls; retained read-only enforcement and the review-specific coordinator-loaded Explore fallback.
- [x] Preserved human slash examples, incoming command routing, prohibitions, tool ownership metadata, and upstream principles consolidation.
- [x] Optional host skills have explicit scoped dependency declarations; runtime instructions require resolving their current installed descriptions or reporting unavailable dependencies. External descriptions are not invented or statically certified.
- [x] Source checks establish syntax and dependency coverage. They do not establish that a model actually loaded a file.

| Original checklist disposition | Occurrences |
| --- | ---: |
| availability check; actual calls use owning actions | 2 |
| canonical | 252 |
| coordinator loads via resolved calls; Explore receives instructions | 1 |
| migration refers to canonical Step 7 call | 1 |
| resolved dynamic call | 6 |
| tool ownership metadata; selected call rendered by dispatcher | 3 |
| upstream consolidated into Design Principles rule; named triggers preserved | 7 |

## Load-path walkthrough

Static walkthrough, not an observed agent execution:

| Case | Expected loading and preserved behavior |
| --- | --- |
| Principles | Full body, then only named/index-matching local files through EOF; preserve unmatched-file exclusion and phase reselection. |
| Review code | GitHub owner and selected Pull requests/Diff guidance before acquisition; Review code playbook before review actions; only required/triggered resources. |
| Design architect | Full Design body and Architect playbook; shared Principles rule remains the owner of phase-specific principle selection; preserve requested checkpoint and artifact paths. |
| Dynamic investigation | Resolve exact installed name/description, render canonical task call, load full body/route/resources in the skill-capable worker. |
| Explore fallback | Coordinator loads via resolved investigation calls and supplies applicable read-only instructions; Explore is never instructed to invoke a skill. |
| Truncated or missing content | Continue to EOF; unavailable content blocks dependent steps, not independent work. |
| Reuse and conditional loading | Reuse only complete unchanged content still available; reload after context loss; skip unrelated routes and untriggered resources. |

## Original caller checklist

Each checkbox accounts for one occurrence in the approved plan. `canonical` means the mapped final source contains the rewritten target call. Other dispositions explicitly distinguish dynamic rendering, metadata and upstream consolidation from an executable call. Source locations below are original-baseline anchors; final canonical calls are inventoried by file below.

- [x] 001. [plugins/wf/agents/codey.agent.md:17](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/agents/codey.agent.md#L17) → `git`: canonical.
- [x] 002. [plugins/wf/agents/codey.agent.md:19](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/agents/codey.agent.md#L19) → `git`: canonical.
- [x] 003. [plugins/wf/agents/codey.agent.md:67](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/agents/codey.agent.md#L67) → `testing-integrations`: canonical.
- [x] 004. [plugins/wf/agents/hunter.agent.md:29](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/agents/hunter.agent.md#L29) → `@work resolved skill`: resolved dynamic call.
- [x] 005. [plugins/wf/agents/hunter.agent.md:109](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/agents/hunter.agent.md#L109) → `graphify`: canonical.
- [x] 006. [plugins/wf/install/assets/factory-mode/SKILL.md:20](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/SKILL.md#L20) → `sharpen`: canonical.
- [x] 007. [plugins/wf/install/assets/factory-mode/SKILL.md:21](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/SKILL.md#L21) → `prove`: canonical.
- [x] 008. [plugins/wf/install/assets/factory-mode/SKILL.md:23](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/SKILL.md#L23) → `design`: canonical.
- [x] 009. [plugins/wf/install/assets/factory-mode/SKILL.md:24](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/SKILL.md#L24) → `design`: canonical.
- [x] 010. [plugins/wf/install/assets/factory-mode/SKILL.md:26](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/SKILL.md#L26) → `research`: canonical.
- [x] 011. [plugins/wf/install/assets/factory-mode/SKILL.md:28](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/SKILL.md#L28) → `crew-commit`: canonical.
- [x] 012. [plugins/wf/install/assets/factory-mode/SKILL.md:85](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/SKILL.md#L85) → `subagents`: canonical.
- [x] 013. [plugins/wf/install/assets/factory-mode/SKILL.md:118](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/SKILL.md#L118) → `github`: canonical.
- [x] 014. [plugins/wf/install/assets/factory-mode/SKILL.md:120](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/SKILL.md#L120) → `git`: canonical.
- [x] 015. [plugins/wf/install/assets/factory-mode/SKILL.md:126](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/SKILL.md#L126) → `git`: canonical.
- [x] 016. [plugins/wf/install/assets/factory-mode/SKILL.md:127](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/SKILL.md#L127) → `github`: canonical.
- [x] 017. [plugins/wf/install/assets/factory-mode/SKILL.md:128](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/SKILL.md#L128) → `review`: canonical.
- [x] 018. [plugins/wf/install/assets/factory-mode/agents/verifier.md:13](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/agents/verifier.md#L13) → `each supplied repository verification skill`: resolved dynamic call.
- [x] 019. [plugins/wf/install/assets/factory-mode/playbooks/bug-fix.md:7](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/bug-fix.md#L7) → `testing-integrations`: canonical.
- [x] 020. [plugins/wf/install/assets/factory-mode/playbooks/bug-fix.md:7](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/bug-fix.md#L7) → `prototype-cloud-scenario`: canonical.
- [x] 021. [plugins/wf/install/assets/factory-mode/playbooks/bug-fix.md:11](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/bug-fix.md#L11) → `git`: canonical.
- [x] 022. [plugins/wf/install/assets/factory-mode/playbooks/bug-fix.md:12](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/bug-fix.md#L12) → `draft-artifact`: canonical.
- [x] 023. [plugins/wf/install/assets/factory-mode/playbooks/design.md:7](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/design.md#L7) → `design`: canonical.
- [x] 024. [plugins/wf/install/assets/factory-mode/playbooks/design.md:11](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/design.md#L11) → `design`: canonical.
- [x] 025. [plugins/wf/install/assets/factory-mode/playbooks/design.md:16](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/design.md#L16) → `design`: canonical.
- [x] 026. [plugins/wf/install/assets/factory-mode/playbooks/feature.md:11](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/feature.md#L11) → `research`: canonical.
- [x] 027. [plugins/wf/install/assets/factory-mode/playbooks/feature.md:12](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/feature.md#L12) → `prove`: canonical.
- [x] 028. [plugins/wf/install/assets/factory-mode/playbooks/feature.md:15](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/feature.md#L15) → `challenge-this`: canonical.
- [x] 029. [plugins/wf/install/assets/factory-mode/playbooks/feature.md:23](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/feature.md#L23) → `show-me-your-work`: canonical.
- [x] 030. [plugins/wf/install/assets/factory-mode/playbooks/feature.md:27](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/feature.md#L27) → `design`: canonical.
- [x] 031. [plugins/wf/install/assets/factory-mode/playbooks/feature.md:28](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/feature.md#L28) → `design`: canonical.
- [x] 032. [plugins/wf/install/assets/factory-mode/playbooks/feature.md:29](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/feature.md#L29) → `implement`: canonical.
- [x] 033. [plugins/wf/install/assets/factory-mode/playbooks/feature.md:30](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/feature.md#L30) → `testing-integrations`: canonical.
- [x] 034. [plugins/wf/install/assets/factory-mode/playbooks/feature.md:33](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/feature.md#L33) → `review`: canonical.
- [x] 035. [plugins/wf/install/assets/factory-mode/playbooks/feature.md:36](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/feature.md#L36) → `show-me-your-work`: canonical.
- [x] 036. [plugins/wf/install/assets/factory-mode/playbooks/feature.md:37](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/feature.md#L37) → `github`: canonical.
- [x] 037. [plugins/wf/install/assets/factory-mode/playbooks/investigation.md:7](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/investigation.md#L7) → `prove`: canonical.
- [x] 038. [plugins/wf/install/assets/factory-mode/playbooks/investigation.md:9](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/investigation.md#L9) → `writing-style`: canonical.
- [x] 039. [plugins/wf/install/assets/factory-mode/playbooks/prototype.md:9](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/prototype.md#L9) → `prove`: canonical.
- [x] 040. [plugins/wf/install/assets/factory-mode/playbooks/refactoring.md:9](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/refactoring.md#L9) → `design`: canonical.
- [x] 041. [plugins/wf/install/assets/factory-mode/playbooks/refactoring.md:11](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/refactoring.md#L11) → `csharp-refactoring`: canonical.
- [x] 042. [plugins/wf/install/assets/factory-mode/playbooks/refactoring.md:14](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/refactoring.md#L14) → `git`: canonical.
- [x] 043. [plugins/wf/install/assets/factory-mode/playbooks/stories.md:5](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/stories.md#L5) → `draft-artifact`: canonical.
- [x] 044. [plugins/wf/install/assets/factory-mode/playbooks/stories.md:37](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/stories.md#L37) → `draft-artifact`: canonical.
- [x] 045. [plugins/wf/install/assets/factory-mode/playbooks/stories.md:53](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/playbooks/stories.md#L53) → `draft-artifact`: canonical.
- [x] 046. [plugins/wf/install/assets/factory-mode/references/post-implementation.md:15](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/references/post-implementation.md#L15) → `github`: canonical.
- [x] 047. [plugins/wf/install/assets/factory-mode/references/post-implementation.md:19](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/references/post-implementation.md#L19) → `git`: canonical.
- [x] 048. [plugins/wf/install/assets/factory-mode/references/post-implementation.md:62](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/references/post-implementation.md#L62) → `github`: canonical.
- [x] 049. [plugins/wf/install/assets/factory-mode/references/post-implementation.md:68](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/references/post-implementation.md#L68) → `review`: canonical.
- [x] 050. [plugins/wf/install/assets/factory-mode/references/post-implementation.md:80](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/references/post-implementation.md#L80) → `github`: canonical.
- [x] 051. [plugins/wf/install/assets/factory-mode/references/post-implementation.md:80](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/references/post-implementation.md#L80) → `git`: canonical.
- [x] 052. [plugins/wf/install/assets/factory-mode/references/post-implementation.md:86](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/factory-mode/references/post-implementation.md#L86) → `git`: canonical.
- [x] 053. [plugins/wf/install/assets/testing-integrations/kinds/local-runtime.md:9](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/testing-integrations/kinds/local-runtime.md#L9) → `resolved localInstance skill when selected`: resolved dynamic call.
- [x] 054. [plugins/wf/install/assets/testing-integrations/strategies/reproduce.md:13](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/assets/testing-integrations/strategies/reproduce.md#L13) → `challenge-this`: canonical.
- [x] 055. [plugins/wf/install/copilot-instructions.template.md:69](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/copilot-instructions.template.md#L69) → `search-{{proj}}`: canonical.
- [x] 056. [plugins/wf/install/copilot-instructions.template.md:70](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/copilot-instructions.template.md#L70) → `search-infra-nuget`: canonical.
- [x] 057. [plugins/wf/install/copilot-instructions.template.md:71](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/copilot-instructions.template.md#L71) → `search-aws-sdk-nuget`: canonical.
- [x] 058. [plugins/wf/install/copilot-instructions.template.md:72](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/copilot-instructions.template.md#L72) → `search-aws-docs`: canonical.
- [x] 059. [plugins/wf/install/copilot-instructions.template.md:73](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/copilot-instructions.template.md#L73) → `query-aws`: canonical.
- [x] 060. [plugins/wf/install/copilot-instructions.template.md:74](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/copilot-instructions.template.md#L74) → `preflight-atlassian`: canonical.
- [x] 061. [plugins/wf/install/copilot-instructions.template.md:86](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/copilot-instructions.template.md#L86) → `lsp-recover`: canonical.
- [x] 062. [plugins/wf/install/copilot-instructions.template.md:92](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/copilot-instructions.template.md#L92) → `graphify`: canonical.
- [x] 063. [plugins/wf/install/copilot-instructions.template.md:118](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/copilot-instructions.template.md#L118) → `query-aws`: tool ownership metadata; selected call rendered by dispatcher.
- [x] 064. [plugins/wf/install/copilot-instructions.template.md:119](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/copilot-instructions.template.md#L119) → `preflight-atlassian`: tool ownership metadata; selected call rendered by dispatcher.
- [x] 065. [plugins/wf/install/copilot-instructions.template.md:120](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/copilot-instructions.template.md#L120) → `search-aws-docs`: tool ownership metadata; selected call rendered by dispatcher.
- [x] 066. [plugins/wf/install/copilot-instructions.template.md:123](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/copilot-instructions.template.md#L123) → `git`: canonical.
- [x] 067. [plugins/wf/install/copilot-instructions.template.md:123](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/copilot-instructions.template.md#L123) → `github`: canonical.
- [x] 068. [plugins/wf/install/github.md:7](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/github.md#L7) → `git`: canonical.
- [x] 069. [plugins/wf/install/install.md:21](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/install.md#L21) → `doc-architecture`: availability check; actual calls use owning actions.
- [x] 070. [plugins/wf/install/install.md:21](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/install.md#L21) → `github`: availability check; actual calls use owning actions.
- [x] 071. [plugins/wf/install/install.md:44](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/install/install.md#L44) → `doc-architecture`: canonical.
- [x] 072. [plugins/wf/skills/atlassian/SKILL.md:28](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/atlassian/SKILL.md#L28) → `daily-briefing`: canonical.
- [x] 073. [plugins/wf/skills/atlassian/SKILL.md:32](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/atlassian/SKILL.md#L32) → `preflight-atlassian`: canonical.
- [x] 074. [plugins/wf/skills/atlassian/assets/preflight-atlassian/preflight-atlassian.SKILL.template.md:18](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/atlassian/assets/preflight-atlassian/preflight-atlassian.SKILL.template.md#L18) → `atlassian`: canonical.
- [x] 075. [plugins/wf/skills/atlassian/assets/preflight-atlassian/preflight-atlassian.SKILL.template.md:19](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/atlassian/assets/preflight-atlassian/preflight-atlassian.SKILL.template.md#L19) → `daily-briefing`: canonical.
- [x] 076. [plugins/wf/skills/atlassian/assets/preflight-atlassian/preflight-atlassian.SKILL.template.md:53](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/atlassian/assets/preflight-atlassian/preflight-atlassian.SKILL.template.md#L53) → `atlassian`: canonical.
- [x] 077. [plugins/wf/skills/atlassian/assets/preflight-atlassian/preflight-atlassian.SKILL.template.md:54](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/atlassian/assets/preflight-atlassian/preflight-atlassian.SKILL.template.md#L54) → `atlassian`: canonical.
- [x] 078. [plugins/wf/skills/atlassian/references/install.md:44](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/atlassian/references/install.md#L44) → `atlassian`: canonical.
- [x] 079. [plugins/wf/skills/atlassian/references/install.md:47](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/atlassian/references/install.md#L47) → `atlassian`: migration refers to canonical Step 7 call.
- [x] 080. [plugins/wf/skills/atlassian/references/install.md:54](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/atlassian/references/install.md#L54) → `atlassian`: canonical.
- [x] 081. [plugins/wf/skills/challenge-this/SKILL.md:23](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/challenge-this/SKILL.md#L23) → `principles`: canonical.
- [x] 082. [plugins/wf/skills/challenge-this/SKILL.md:29](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/challenge-this/SKILL.md#L29) → `subagents`: canonical.
- [x] 083. [plugins/wf/skills/challenge-this/SKILL.md:43](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/challenge-this/SKILL.md#L43) → `git`: canonical.
- [x] 084. [plugins/wf/skills/challenge-this/references/adversary-prompt.md:14](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/challenge-this/references/adversary-prompt.md#L14) → `prove`: canonical.
- [x] 085. [plugins/wf/skills/define/SKILL.md:19](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/define/SKILL.md#L19) → `doc-architecture`: canonical.
- [x] 086. [plugins/wf/skills/define/references/concept.md:3](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/define/references/concept.md#L3) → `doc-architecture`: canonical.
- [x] 087. [plugins/wf/skills/define/references/concept.md:7](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/define/references/concept.md#L7) → `doc-architecture`: canonical.
- [x] 088. [plugins/wf/skills/define/references/concept.md:11](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/define/references/concept.md#L11) → `research`: canonical.
- [x] 089. [plugins/wf/skills/define/references/concept.md:50](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/define/references/concept.md#L50) → `doc-architecture`: canonical.
- [x] 090. [plugins/wf/skills/define/references/concept.md:50](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/define/references/concept.md#L50) → `doc-architecture`: canonical.
- [x] 091. [plugins/wf/skills/define/references/concept.md:82](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/define/references/concept.md#L82) → `doc-architecture`: canonical.
- [x] 092. [plugins/wf/skills/define/references/concept.md:82](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/define/references/concept.md#L82) → `doc-architecture`: canonical.
- [x] 093. [plugins/wf/skills/define/references/research.md:65](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/define/references/research.md#L65) → `research`: canonical.
- [x] 094. [plugins/wf/skills/define/references/research.md:65](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/define/references/research.md#L65) → `prove`: canonical.
- [x] 095. [plugins/wf/skills/define/references/research.md:123](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/define/references/research.md#L123) → `research`: canonical.
- [x] 096. [plugins/wf/skills/define/references/research.md:124](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/define/references/research.md#L124) → `prove`: canonical.
- [x] 097. [plugins/wf/skills/design/playbooks/architect.md:29](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/architect.md#L29) → `research`: canonical.
- [x] 098. [plugins/wf/skills/design/playbooks/architect.md:35](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/architect.md#L35) → `subagents`: canonical.
- [x] 099. [plugins/wf/skills/design/playbooks/architect.md:37](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/architect.md#L37) → `principles`: upstream consolidated into Design Principles rule; named triggers preserved.
- [x] 100. [plugins/wf/skills/design/playbooks/architect.md:47](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/architect.md#L47) → `challenge-this`: canonical.
- [x] 101. [plugins/wf/skills/design/playbooks/architect.md:66](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/architect.md#L66) → `subagents`: canonical.
- [x] 102. [plugins/wf/skills/design/playbooks/architect.md:67](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/architect.md#L67) → `challenge-this`: canonical.
- [x] 103. [plugins/wf/skills/design/playbooks/architect.md:68](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/architect.md#L68) → `prove`: canonical.
- [x] 104. [plugins/wf/skills/design/playbooks/architect.md:83](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/architect.md#L83) → `principles`: upstream consolidated into Design Principles rule; named triggers preserved.
- [x] 105. [plugins/wf/skills/design/playbooks/architect.md:84](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/architect.md#L84) → `principles`: upstream consolidated into Design Principles rule; named triggers preserved.
- [x] 106. [plugins/wf/skills/design/playbooks/architect.md:90](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/architect.md#L90) → `principles`: upstream consolidated into Design Principles rule; named triggers preserved.
- [x] 107. [plugins/wf/skills/design/playbooks/architect.md:107](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/architect.md#L107) → `principles`: upstream consolidated into Design Principles rule; named triggers preserved.
- [x] 108. [plugins/wf/skills/design/playbooks/architect.md:108](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/architect.md#L108) → `principles`: upstream consolidated into Design Principles rule; named triggers preserved.
- [x] 109. [plugins/wf/skills/design/playbooks/grill.md:20](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/grill.md#L20) → `doc-architecture`: canonical.
- [x] 110. [plugins/wf/skills/design/playbooks/grill.md:21](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/grill.md#L21) → `doc-architecture`: canonical.
- [x] 111. [plugins/wf/skills/design/playbooks/grill.md:29](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/grill.md#L29) → `research`: canonical.
- [x] 112. [plugins/wf/skills/design/playbooks/grill.md:30](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/grill.md#L30) → `doc-architecture`: canonical.
- [x] 113. [plugins/wf/skills/design/playbooks/grill.md:31](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/grill.md#L31) → `doc-architecture`: canonical.
- [x] 114. [plugins/wf/skills/design/playbooks/grill.md:158](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/grill.md#L158) → `draft-artifact`: canonical.
- [x] 115. [plugins/wf/skills/design/playbooks/review.md:9](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/review.md#L9) → `research`: canonical.
- [x] 116. [plugins/wf/skills/design/playbooks/review.md:9](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/review.md#L9) → `research`: canonical.
- [x] 117. [plugins/wf/skills/design/playbooks/spec.md:15](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/spec.md#L15) → `doc-contracts`: canonical.
- [x] 118. [plugins/wf/skills/design/playbooks/tickets.md:29](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/tickets.md#L29) → `git`: canonical.
- [x] 119. [plugins/wf/skills/design/playbooks/wayfinder.md:88](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/wayfinder.md#L88) → `research`: canonical.
- [x] 120. [plugins/wf/skills/design/playbooks/wayfinder.md:89](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/wayfinder.md#L89) → `prove`: canonical.
- [x] 121. [plugins/wf/skills/design/playbooks/wayfinder.md:93](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/wayfinder.md#L93) → `design`: canonical.
- [x] 122. [plugins/wf/skills/design/playbooks/wayfinder.md:93](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/wayfinder.md#L93) → `doc-diagram`: canonical.
- [x] 123. [plugins/wf/skills/design/playbooks/wayfinder.md:170](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/playbooks/wayfinder.md#L170) → `ticket-selected research/prove/design skill`: resolved dynamic call.
- [x] 124. [plugins/wf/skills/design/references/closing-sweep.md:19](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/closing-sweep.md#L19) → `doc-architecture`: canonical.
- [x] 125. [plugins/wf/skills/design/references/closing-sweep.md:25](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/closing-sweep.md#L25) → `doc-architecture`: canonical.
- [x] 126. [plugins/wf/skills/design/references/design-it-twice.md:21](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/design-it-twice.md#L21) → `subagents`: canonical.
- [x] 127. [plugins/wf/skills/design/references/evidence-routing.md:21](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/evidence-routing.md#L21) → `research`: canonical.
- [x] 128. [plugins/wf/skills/design/references/evidence-routing.md:34](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/evidence-routing.md#L34) → `prove`: canonical.
- [x] 129. [plugins/wf/skills/design/references/evidence-routing.md:40](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/evidence-routing.md#L40) → `challenge-this`: canonical.
- [x] 130. [plugins/wf/skills/design/references/github.md:11](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L11) → `git`: canonical.
- [x] 131. [plugins/wf/skills/design/references/github.md:17](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L17) → `github`: canonical.
- [x] 132. [plugins/wf/skills/design/references/github.md:21](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L21) → `github`: canonical.
- [x] 133. [plugins/wf/skills/design/references/github.md:43](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L43) → `github`: canonical.
- [x] 134. [plugins/wf/skills/design/references/github.md:47](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L47) → `github`: canonical.
- [x] 135. [plugins/wf/skills/design/references/github.md:51](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L51) → `github`: canonical.
- [x] 136. [plugins/wf/skills/design/references/github.md:55](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L55) → `github`: canonical.
- [x] 137. [plugins/wf/skills/design/references/github.md:59](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L59) → `github`: canonical.
- [x] 138. [plugins/wf/skills/design/references/github.md:63](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L63) → `github`: canonical.
- [x] 139. [plugins/wf/skills/design/references/github.md:81](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L81) → `git`: canonical.
- [x] 140. [plugins/wf/skills/design/references/github.md:89](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L89) → `github`: canonical.
- [x] 141. [plugins/wf/skills/design/references/github.md:93](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L93) → `github`: canonical.
- [x] 142. [plugins/wf/skills/design/references/github.md:97](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L97) → `github`: canonical.
- [x] 143. [plugins/wf/skills/design/references/github.md:101](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L101) → `github`: canonical.
- [x] 144. [plugins/wf/skills/design/references/github.md:105](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L105) → `github`: canonical.
- [x] 145. [plugins/wf/skills/design/references/github.md:109](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L109) → `github`: canonical.
- [x] 146. [plugins/wf/skills/design/references/github.md:113](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L113) → `github`: canonical.
- [x] 147. [plugins/wf/skills/design/references/github.md:117](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L117) → `github`: canonical.
- [x] 148. [plugins/wf/skills/design/references/github.md:121](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L121) → `github`: canonical.
- [x] 149. [plugins/wf/skills/design/references/github.md:125](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L125) → `git`: canonical.
- [x] 150. [plugins/wf/skills/design/references/github.md:135](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/github.md#L135) → `git`: canonical.
- [x] 151. [plugins/wf/skills/design/references/issue-template.md:84](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/issue-template.md#L84) → `doc-contracts`: canonical.
- [x] 152. [plugins/wf/skills/design/references/sketch-contract.md:16](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/sketch-contract.md#L16) → `principles`: upstream consolidated into Design Principles rule; named triggers preserved.
- [x] 153. [plugins/wf/skills/design/references/tactics-external-source.md:13](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/design/references/tactics-external-source.md#L13) → `github`: canonical.
- [x] 154. [plugins/wf/skills/doc-architecture/SKILL.md:35](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/doc-architecture/SKILL.md#L35) → `doc-diagram`: canonical.
- [x] 155. [plugins/wf/skills/doc-architecture/SKILL.md:35](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/doc-architecture/SKILL.md#L35) → `research`: canonical.
- [x] 156. [plugins/wf/skills/doc-architecture/playbooks/building-block.md:19](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/doc-architecture/playbooks/building-block.md#L19) → `doc-diagram`: canonical.
- [x] 157. [plugins/wf/skills/doc-architecture/playbooks/building-block.md:23](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/doc-architecture/playbooks/building-block.md#L23) → `doc-diagram`: canonical.
- [x] 158. [plugins/wf/skills/doc-architecture/playbooks/concept.md:87](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/doc-architecture/playbooks/concept.md#L87) → `research`: canonical.
- [x] 159. [plugins/wf/skills/doc-architecture/templates/BUILDING-BLOCK-FORMAT.md:39](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/doc-architecture/templates/BUILDING-BLOCK-FORMAT.md#L39) → `doc-diagram`: canonical.
- [x] 160. [plugins/wf/skills/doc-architecture/templates/domain-business-process.md:36](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/doc-architecture/templates/domain-business-process.md#L36) → `doc-diagram`: canonical.
- [x] 161. [plugins/wf/skills/doc-architecture/templates/domain-business-process.md:62](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/doc-architecture/templates/domain-business-process.md#L62) → `doc-diagram`: canonical.
- [x] 162. [plugins/wf/skills/doc-architecture/templates/ops-policy.md:29](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/doc-architecture/templates/ops-policy.md#L29) → `doc-diagram`: canonical.
- [x] 163. [plugins/wf/skills/doc-architecture/templates/structure-implementation.md:28](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/doc-architecture/templates/structure-implementation.md#L28) → `doc-diagram`: canonical.
- [x] 164. [plugins/wf/skills/doc-architecture/templates/structure-implementation.md:28](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/doc-architecture/templates/structure-implementation.md#L28) → `doc-diagram`: canonical.
- [x] 165. [plugins/wf/skills/doc-diagram/examples/architecture.md:105](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/doc-diagram/examples/architecture.md#L105) → `doc-diagram`: canonical.
- [x] 166. [plugins/wf/skills/draft-artifact/tactics/bug.md:10](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/draft-artifact/tactics/bug.md#L10) → `research`: canonical.
- [x] 167. [plugins/wf/skills/draft-artifact/tactics/feature-design.md:52](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/draft-artifact/tactics/feature-design.md#L52) → `doc-diagram`: canonical.
- [x] 168. [plugins/wf/skills/draft-artifact/tactics/feature-design.md:56](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/draft-artifact/tactics/feature-design.md#L56) → `doc-diagram`: canonical.
- [x] 169. [plugins/wf/skills/draft-artifact/tactics/feature-design.md:58](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/draft-artifact/tactics/feature-design.md#L58) → `doc-diagram`: canonical.
- [x] 170. [plugins/wf/skills/draft-artifact/tactics/feature-design.md:69](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/draft-artifact/tactics/feature-design.md#L69) → `doc-contracts`: canonical.
- [x] 171. [plugins/wf/skills/draft-artifact/tactics/feature-design.md:69](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/draft-artifact/tactics/feature-design.md#L69) → `doc-contracts`: canonical.
- [x] 172. [plugins/wf/skills/draft-artifact/tactics/feature-design.md:70](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/draft-artifact/tactics/feature-design.md#L70) → `doc-diagram`: canonical.
- [x] 173. [plugins/wf/skills/draft-artifact/tactics/story.md:16](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/draft-artifact/tactics/story.md#L16) → `writing-style`: canonical.
- [x] 174. [plugins/wf/skills/draft-artifact/tactics/story.md:21](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/draft-artifact/tactics/story.md#L21) → `writing-style`: canonical.
- [x] 175. [plugins/wf/skills/draft-artifact/tactics/story.md:22](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/draft-artifact/tactics/story.md#L22) → `doc-contracts`: canonical.
- [x] 176. [plugins/wf/skills/draft-artifact/tactics/story.md:22](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/draft-artifact/tactics/story.md#L22) → `doc-contracts`: canonical.
- [x] 177. [plugins/wf/skills/draft-artifact/tactics/story.md:29](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/draft-artifact/tactics/story.md#L29) → `writing-style`: canonical.
- [x] 178. [plugins/wf/skills/draft-artifact/tactics/toi.md:53](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/draft-artifact/tactics/toi.md#L53) → `research`: canonical.
- [x] 179. [plugins/wf/skills/draft-artifact/tactics/toi.md:94](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/draft-artifact/tactics/toi.md#L94) → `doc-diagram`: canonical.
- [x] 180. [plugins/wf/skills/draft-artifact/templates/design-template.md:80](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/draft-artifact/templates/design-template.md#L80) → `doc-diagram`: canonical.
- [x] 181. [plugins/wf/skills/draft-artifact/templates/design-template.md:89](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/draft-artifact/templates/design-template.md#L89) → `doc-diagram`: canonical.
- [x] 182. [plugins/wf/skills/draft-artifact/templates/design-template.md:102](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/draft-artifact/templates/design-template.md#L102) → `doc-diagram`: canonical.
- [x] 183. [plugins/wf/skills/draft-artifact/templates/toi-template.md:50](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/draft-artifact/templates/toi-template.md#L50) → `doc-diagram`: canonical.
- [x] 184. [plugins/wf/skills/git/references/commit-messages.md:7](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/git/references/commit-messages.md#L7) → `writing-style`: canonical.
- [x] 185. [plugins/wf/skills/git/tactics/repository.md:5](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/git/tactics/repository.md#L5) → `github`: canonical.
- [x] 186. [plugins/wf/skills/github/SKILL.md:20](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/github/SKILL.md#L20) → `review`: canonical.
- [x] 187. [plugins/wf/skills/github/references/fetch-diff.md:15](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/github/references/fetch-diff.md#L15) → `git`: canonical.
- [x] 188. [plugins/wf/skills/github/references/fetch-diff.md:35](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/github/references/fetch-diff.md#L35) → `git`: canonical.
- [x] 189. [plugins/wf/skills/github/references/transports.md:3](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/github/references/transports.md#L3) → `git`: canonical.
- [x] 190. [plugins/wf/skills/github/tactics/pull-requests.md:5](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/github/tactics/pull-requests.md#L5) → `writing-style`: canonical.
- [x] 191. [plugins/wf/skills/github/tactics/repository.md:3](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/github/tactics/repository.md#L3) → `git`: canonical.
- [x] 192. [plugins/wf/skills/github/tactics/reviews.md:3](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/github/tactics/reviews.md#L3) → `writing-style`: canonical.
- [x] 193. [plugins/wf/skills/implement/SKILL.md:22](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/implement/SKILL.md#L22) → `github`: canonical.
- [x] 194. [plugins/wf/skills/implement/SKILL.md:22](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/implement/SKILL.md#L22) → `git`: canonical.
- [x] 195. [plugins/wf/skills/implement/SKILL.md:59](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/implement/SKILL.md#L59) → `git`: canonical.
- [x] 196. [plugins/wf/skills/implement/SKILL.md:114](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/implement/SKILL.md#L114) → `git`: canonical.
- [x] 197. [plugins/wf/skills/implement/SKILL.md:127](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/implement/SKILL.md#L127) → `git`: canonical.
- [x] 198. [plugins/wf/skills/implement/SKILL.md:171](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/implement/SKILL.md#L171) → `git`: canonical.
- [x] 199. [plugins/wf/skills/implement/SKILL.md:173](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/implement/SKILL.md#L173) → `testing-integrations`: canonical.
- [x] 200. [plugins/wf/skills/implement/agents/chore.md:17](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/implement/agents/chore.md#L17) → `git`: canonical.
- [x] 201. [plugins/wf/skills/implement/references/breakdown.md:18](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/implement/references/breakdown.md#L18) → `git`: canonical.
- [x] 202. [plugins/wf/skills/implement/references/breakdown.md:181](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/implement/references/breakdown.md#L181) → `doc-contracts`: canonical.
- [x] 203. [plugins/wf/skills/implement/references/fetch-diff.md:3](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/implement/references/fetch-diff.md#L3) → `github`: canonical.
- [x] 204. [plugins/wf/skills/implement/references/publication.md:25](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/implement/references/publication.md#L25) → `github`: canonical.
- [x] 205. [plugins/wf/skills/implement/references/publication.md:35](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/implement/references/publication.md#L35) → `git`: canonical.
- [x] 206. [plugins/wf/skills/implement/references/worktrees.md:11](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/implement/references/worktrees.md#L11) → `git`: canonical.
- [x] 207. [plugins/wf/skills/implement/references/worktrees.md:18](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/implement/references/worktrees.md#L18) → `git`: canonical.
- [x] 208. [plugins/wf/skills/implement/references/worktrees.md:32](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/implement/references/worktrees.md#L32) → `git`: canonical.
- [x] 209. [plugins/wf/skills/implement/references/worktrees.md:33](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/implement/references/worktrees.md#L33) → `git`: canonical.
- [x] 210. [plugins/wf/skills/principles/principles/explain-the-number.md:8](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/principles/principles/explain-the-number.md#L8) → `benchmark-checklist`: canonical.
- [x] 211. [plugins/wf/skills/prove/SKILL.md:36](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/prove/SKILL.md#L36) → `principles`: canonical.
- [x] 212. [plugins/wf/skills/prove/SKILL.md:37](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/prove/SKILL.md#L37) → `research`: canonical.
- [x] 213. [plugins/wf/skills/prove/SKILL.md:38](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/prove/SKILL.md#L38) → `subagents`: canonical.
- [x] 214. [plugins/wf/skills/prove/SKILL.md:45](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/prove/SKILL.md#L45) → `research`: canonical.
- [x] 215. [plugins/wf/skills/prove/SKILL.md:73](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/prove/SKILL.md#L73) → `git`: canonical.
- [x] 216. [plugins/wf/skills/prove/tactics/integration.md:7](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/prove/tactics/integration.md#L7) → `testing-integrations`: canonical.
- [x] 217. [plugins/wf/skills/prove/tactics/integration.md:8](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/prove/tactics/integration.md#L8) → `testing-integrations`: canonical.
- [x] 218. [plugins/wf/skills/research/SKILL.md:36](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/research/SKILL.md#L36) → `@work resolved skill`: resolved dynamic call.
- [x] 219. [plugins/wf/skills/research/SKILL.md:53](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/research/SKILL.md#L53) → `graphify`: canonical.
- [x] 220. [plugins/wf/skills/research/SKILL.md:93](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/research/SKILL.md#L93) → `subagents`: canonical.
- [x] 221. [plugins/wf/skills/research/how/README.md:3](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/research/how/README.md#L3) → `research`: canonical.
- [x] 222. [plugins/wf/skills/research/how/explainer-prompt.md:33](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/research/how/explainer-prompt.md#L33) → `doc-diagram`: canonical.
- [x] 223. [plugins/wf/skills/research/how/how.md:13](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/research/how/how.md#L13) → `subagents`: canonical.
- [x] 224. [plugins/wf/skills/research/why/sources/atlassian.md:9](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/research/why/sources/atlassian.md#L9) → `atlassian`: canonical.
- [x] 225. [plugins/wf/skills/research/why/sources/atlassian.md:14](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/research/why/sources/atlassian.md#L14) → `atlassian`: canonical.
- [x] 226. [plugins/wf/skills/research/why/sources/atlassian.md:22](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/research/why/sources/atlassian.md#L22) → `atlassian`: canonical.
- [x] 227. [plugins/wf/skills/research/why/why.md:7](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/research/why/why.md#L7) → `subagents`: canonical.
- [x] 228. [plugins/wf/skills/research/why/why.md:21](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/research/why/why.md#L21) → `github`: canonical.
- [x] 229. [plugins/wf/skills/research/why/why.md:41](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/research/why/why.md#L41) → `github`: canonical.
- [x] 230. [plugins/wf/skills/research/why/why.md:43](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/research/why/why.md#L43) → `preflight-atlassian`: canonical.
- [x] 231. [plugins/wf/skills/review/SKILL.md:23](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/SKILL.md#L23) → `github`: canonical.
- [x] 232. [plugins/wf/skills/review/SKILL.md:23](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/SKILL.md#L23) → `design`: canonical.
- [x] 233. [plugins/wf/skills/review/playbooks/blast-radius.md:19](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/blast-radius.md#L19) → `git`: canonical.
- [x] 234. [plugins/wf/skills/review/playbooks/blast-radius.md:42](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/blast-radius.md#L42) → `research`: canonical.
- [x] 235. [plugins/wf/skills/review/playbooks/blast-radius.md:44](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/blast-radius.md#L44) → `research`: canonical.
- [x] 236. [plugins/wf/skills/review/playbooks/blast-radius.md:46](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/blast-radius.md#L46) → `testing-integrations`: canonical.
- [x] 237. [plugins/wf/skills/review/playbooks/blast-radius.md:47](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/blast-radius.md#L47) → `subagents`: canonical.
- [x] 238. [plugins/wf/skills/review/playbooks/blast-radius.md:48](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/blast-radius.md#L48) → `subagents`: canonical.
- [x] 239. [plugins/wf/skills/review/playbooks/blast-radius.md:57](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/blast-radius.md#L57) → `git`: canonical.
- [x] 240. [plugins/wf/skills/review/playbooks/blast-radius.md:74](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/blast-radius.md#L74) → `writing-style`: canonical.
- [x] 241. [plugins/wf/skills/review/playbooks/code.md:10](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/code.md#L10) → `github`: canonical.
- [x] 242. [plugins/wf/skills/review/playbooks/code.md:12](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/code.md#L12) → `github`: canonical.
- [x] 243. [plugins/wf/skills/review/playbooks/code.md:27](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/code.md#L27) → `github`: canonical.
- [x] 244. [plugins/wf/skills/review/playbooks/code.md:28](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/code.md#L28) → `github`: canonical.
- [x] 245. [plugins/wf/skills/review/playbooks/code.md:38](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/code.md#L38) → `github`: canonical.
- [x] 246. [plugins/wf/skills/review/playbooks/comments.md:3](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/comments.md#L3) → `github`: canonical.
- [x] 247. [plugins/wf/skills/review/playbooks/comments.md:17](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/comments.md#L17) → `github`: canonical.
- [x] 248. [plugins/wf/skills/review/playbooks/comments.md:31](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/comments.md#L31) → `git`: canonical.
- [x] 249. [plugins/wf/skills/review/playbooks/comments.md:31](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/comments.md#L31) → `github`: canonical.
- [x] 250. [plugins/wf/skills/review/playbooks/comments.md:34](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/comments.md#L34) → `git`: canonical.
- [x] 251. [plugins/wf/skills/review/playbooks/comments.md:87](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/comments.md#L87) → `git`: canonical.
- [x] 252. [plugins/wf/skills/review/playbooks/comments.md:97](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/comments.md#L97) → `github`: canonical.
- [x] 253. [plugins/wf/skills/review/playbooks/comments.md:101](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/comments.md#L101) → `github`: canonical.
- [x] 254. [plugins/wf/skills/review/playbooks/comments.md:121](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/comments.md#L121) → `github`: canonical.
- [x] 255. [plugins/wf/skills/review/playbooks/comments.md:127](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/comments.md#L127) → `git`: canonical.
- [x] 256. [plugins/wf/skills/review/playbooks/comments.md:127](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/comments.md#L127) → `git`: canonical.
- [x] 257. [plugins/wf/skills/review/playbooks/comments.md:143](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/comments.md#L143) → `git`: canonical.
- [x] 258. [plugins/wf/skills/review/playbooks/hitl.md:23](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/hitl.md#L23) → `github`: canonical.
- [x] 259. [plugins/wf/skills/review/playbooks/hitl.md:96](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/hitl.md#L96) → `github`: canonical.
- [x] 260. [plugins/wf/skills/review/playbooks/hitl.md:131](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/playbooks/hitl.md#L131) → `research`: canonical.
- [x] 261. [plugins/wf/skills/review/references/blast-radius-worker-prompt.md:21](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/references/blast-radius-worker-prompt.md#L21) → `testing-integrations`: canonical.
- [x] 262. [plugins/wf/skills/review/references/blast-radius-worker-prompt.md:21](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/references/blast-radius-worker-prompt.md#L21) → `prove`: canonical.
- [x] 263. [plugins/wf/skills/review/references/conversation-flows.md:3](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/references/conversation-flows.md#L3) → `github`: canonical.
- [x] 264. [plugins/wf/skills/review/references/conversation-flows.md:77](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/references/conversation-flows.md#L77) → `github`: canonical.
- [x] 265. [plugins/wf/skills/review/references/investigation.md:7](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/references/investigation.md#L7) → `skill-name`: canonical.
- [x] 266. [plugins/wf/skills/review/references/investigation.md:15](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/references/investigation.md#L15) → `selected investigation skill; coordinator-only fallback loading`: coordinator loads via resolved calls; Explore receives instructions.
- [x] 267. [plugins/wf/skills/review/references/investigation.md:34](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/references/investigation.md#L34) → `each resolved investigation skill in worker brief`: resolved dynamic call.
- [x] 268. [plugins/wf/skills/review/references/posting.md:15](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/review/references/posting.md#L15) → `github`: canonical.
- [x] 269. [plugins/wf/skills/subagents/SKILL.md:24](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/subagents/SKILL.md#L24) → `git`: canonical.
- [x] 270. [plugins/wf/skills/subagents/arena.md:39](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/subagents/arena.md#L39) → `principles`: canonical.
- [x] 271. [plugins/wf/skills/subagents/arena.md:43](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/subagents/arena.md#L43) → `principles`: canonical.
- [x] 272. [plugins/wf/skills/subagents/arena.md:49](https://github.com/antshc/brain/blob/717dfe084bd6691e908fcedb3444ce6d54787286/plugins/wf/skills/subagents/arena.md#L49) → `principles`: canonical.

## Final WF caller inventory

Every final canonical occurrence is listed; repeated same-target calls on a line remain separate. Dynamic placeholders require runtime resolution, not a fictional installed skill.

| File | Final lines and targets |
| --- | --- |
| `plugins/wf/agents/codey.agent.md` | 17: `git`; 19: `git`; 19: `git`; 25: `principles`; 69: `testing-integrations` |
| `plugins/wf/agents/hunter.agent.md` | 32: `skill-name`; 112: `graphify` |
| `plugins/wf/install/assets/factory-mode/SKILL.md` | 14: `sync-skill`; 20: `sharpen`; 21: `prove`; 23: `design`; 24: `design`; 26: `research`; 28: `crew-commit`; 34: `principles`; 55: `subagents`; 88: `github`; 90: `git`; 96: `git`; 97: `github`; 98: `github`; 98: `review` |
| `plugins/wf/install/assets/factory-mode/agents/verifier.md` | 13: `skill-name` |
| `plugins/wf/install/assets/factory-mode/playbooks/bug-fix.md` | 7: `testing-integrations`; 7: `prototype-cloud-scenario`; 9: `design`; 11: `git`; 12: `draft-artifact` |
| `plugins/wf/install/assets/factory-mode/playbooks/design.md` | 7: `design`; 11: `design`; 16: `design` |
| `plugins/wf/install/assets/factory-mode/playbooks/feature.md` | 11: `research`; 12: `prove`; 15: `challenge-this`; 23: `show-me-your-work`; 27: `design`; 28: `design`; 29: `implement`; 30: `testing-integrations`; 33: `review`; 36: `show-me-your-work`; 37: `github` |
| `plugins/wf/install/assets/factory-mode/playbooks/investigation.md` | 7: `prove`; 9: `writing-style` |
| `plugins/wf/install/assets/factory-mode/playbooks/prototype.md` | 9: `prove` |
| `plugins/wf/install/assets/factory-mode/playbooks/refactoring.md` | 11: `design`; 11: `design`; 13: `csharp-refactoring`; 16: `git` |
| `plugins/wf/install/assets/factory-mode/playbooks/stories.md` | 5: `draft-artifact`; 37: `draft-artifact`; 53: `draft-artifact` |
| `plugins/wf/install/assets/factory-mode/references/post-implementation.md` | 15: `github`; 19: `git`; 62: `github`; 68: `review`; 80: `github`; 80: `git`; 86: `git` |
| `plugins/wf/install/assets/testing-integrations/SKILL.md` | 15: `principles` |
| `plugins/wf/install/assets/testing-integrations/kinds/local-runtime.md` | 9: `skill-name` |
| `plugins/wf/install/assets/testing-integrations/strategies/reproduce.md` | 13: `challenge-this` |
| `plugins/wf/install/copilot-instructions.template.md` | 80: `search-{{proj}}`; 81: `search-infra-nuget`; 82: `search-aws-sdk-nuget`; 83: `search-aws-docs`; 84: `query-aws`; 85: `preflight-atlassian`; 97: `lsp-recover`; 103: `skill-name`; 105: `graphify`; 136: `git`; 136: `github` |
| `plugins/wf/install/github.md` | 7: `git` |
| `plugins/wf/install/install.md` | 44: `doc-architecture` |
| `plugins/wf/skills/atlassian/SKILL.md` | 28: `daily-briefing`; 32: `preflight-atlassian` |
| `plugins/wf/skills/atlassian/assets/preflight-atlassian/preflight-atlassian.SKILL.template.md` | 18: `atlassian`; 19: `daily-briefing`; 53: `atlassian`; 54: `atlassian` |
| `plugins/wf/skills/atlassian/references/install.md` | 44: `atlassian`; 54: `atlassian` |
| `plugins/wf/skills/challenge-this/SKILL.md` | 23: `principles`; 29: `subagents`; 43: `git` |
| `plugins/wf/skills/challenge-this/references/adversary-prompt.md` | 14: `prove` |
| `plugins/wf/skills/define/SKILL.md` | 19: `doc-architecture` |
| `plugins/wf/skills/define/references/concept.md` | 3: `doc-architecture`; 7: `doc-architecture`; 11: `research`; 50: `doc-architecture`; 50: `doc-architecture`; 82: `doc-architecture`; 82: `doc-architecture` |
| `plugins/wf/skills/define/references/research.md` | 65: `research`; 65: `prove`; 123: `research`; 124: `prove` |
| `plugins/wf/skills/design/SKILL.md` | 29: `principles` |
| `plugins/wf/skills/design/playbooks/architect.md` | 29: `research`; 35: `subagents`; 47: `challenge-this`; 66: `subagents`; 67: `challenge-this`; 68: `prove` |
| `plugins/wf/skills/design/playbooks/grill.md` | 20: `doc-architecture`; 21: `doc-architecture`; 29: `research`; 30: `doc-architecture`; 31: `doc-architecture`; 158: `draft-artifact` |
| `plugins/wf/skills/design/playbooks/review.md` | 9: `research`; 9: `research` |
| `plugins/wf/skills/design/playbooks/spec.md` | 15: `doc-contracts` |
| `plugins/wf/skills/design/playbooks/tickets.md` | 29: `git` |
| `plugins/wf/skills/design/playbooks/wayfinder.md` | 88: `research`; 89: `prove`; 93: `design`; 93: `doc-diagram`; 170: `skill-name` |
| `plugins/wf/skills/design/references/closing-sweep.md` | 19: `doc-architecture`; 25: `doc-architecture` |
| `plugins/wf/skills/design/references/design-it-twice.md` | 21: `subagents` |
| `plugins/wf/skills/design/references/evidence-routing.md` | 21: `research`; 34: `prove`; 40: `challenge-this` |
| `plugins/wf/skills/design/references/github.md` | 11: `git`; 17: `github`; 21: `github`; 43: `github`; 47: `github`; 51: `github`; 55: `github`; 59: `github`; 63: `github`; 81: `git`; 89: `github`; 93: `github`; 97: `github`; 101: `github`; 105: `github`; 109: `github`; 113: `github`; 117: `github`; 121: `github`; 125: `git`; 135: `git` |
| `plugins/wf/skills/design/references/issue-template.md` | 84: `doc-contracts` |
| `plugins/wf/skills/design/references/tactics-external-source.md` | 13: `github` |
| `plugins/wf/skills/diagnosing-bugs/SKILL.md` | 23: `principles` |
| `plugins/wf/skills/doc-architecture/SKILL.md` | 35: `doc-diagram`; 35: `research` |
| `plugins/wf/skills/doc-architecture/playbooks/building-block.md` | 19: `doc-diagram`; 23: `doc-diagram` |
| `plugins/wf/skills/doc-architecture/playbooks/concept.md` | 87: `research` |
| `plugins/wf/skills/doc-architecture/templates/BUILDING-BLOCK-FORMAT.md` | 39: `doc-diagram` |
| `plugins/wf/skills/doc-architecture/templates/domain-business-process.md` | 36: `doc-diagram`; 62: `doc-diagram` |
| `plugins/wf/skills/doc-architecture/templates/ops-policy.md` | 29: `doc-diagram` |
| `plugins/wf/skills/doc-architecture/templates/structure-implementation.md` | 28: `doc-diagram`; 28: `doc-diagram` |
| `plugins/wf/skills/doc-diagram/examples/architecture.md` | 105: `doc-diagram` |
| `plugins/wf/skills/draft-artifact/tactics/bug.md` | 10: `research` |
| `plugins/wf/skills/draft-artifact/tactics/feature-design.md` | 52: `doc-diagram`; 56: `doc-diagram`; 58: `doc-diagram`; 69: `doc-contracts`; 69: `doc-contracts`; 70: `doc-diagram` |
| `plugins/wf/skills/draft-artifact/tactics/story.md` | 16: `writing-style`; 21: `writing-style`; 22: `doc-contracts`; 29: `writing-style` |
| `plugins/wf/skills/draft-artifact/tactics/toi.md` | 53: `research`; 94: `doc-diagram` |
| `plugins/wf/skills/draft-artifact/templates/design-template.md` | 80: `doc-diagram`; 89: `doc-diagram`; 102: `doc-diagram` |
| `plugins/wf/skills/draft-artifact/templates/toi-template.md` | 50: `doc-diagram` |
| `plugins/wf/skills/git/references/commit-messages.md` | 7: `writing-style` |
| `plugins/wf/skills/git/tactics/repository.md` | 5: `github` |
| `plugins/wf/skills/github/SKILL.md` | 20: `review` |
| `plugins/wf/skills/github/references/fetch-diff.md` | 15: `git`; 35: `git` |
| `plugins/wf/skills/github/references/transports.md` | 3: `git` |
| `plugins/wf/skills/github/tactics/pull-requests.md` | 5: `writing-style` |
| `plugins/wf/skills/github/tactics/repository.md` | 3: `git` |
| `plugins/wf/skills/github/tactics/reviews.md` | 3: `writing-style` |
| `plugins/wf/skills/implement/SKILL.md` | 22: `github`; 22: `git`; 57: `principles`; 61: `git`; 116: `git`; 129: `git`; 172: `principles`; 174: `git`; 176: `testing-integrations` |
| `plugins/wf/skills/implement/agents/chore.md` | 17: `git` |
| `plugins/wf/skills/implement/references/breakdown.md` | 18: `git`; 181: `doc-contracts` |
| `plugins/wf/skills/implement/references/fetch-diff.md` | 3: `github` |
| `plugins/wf/skills/implement/references/publication.md` | 25: `github`; 35: `git` |
| `plugins/wf/skills/implement/references/worktrees.md` | 11: `git`; 18: `git`; 32: `git`; 33: `git` |
| `plugins/wf/skills/principles/principles/explain-the-number.md` | 10: `benchmark-checklist` |
| `plugins/wf/skills/prove/SKILL.md` | 36: `principles`; 37: `research`; 38: `subagents`; 45: `principles`; 47: `research`; 75: `git` |
| `plugins/wf/skills/prove/tactics/integration.md` | 7: `testing-integrations`; 8: `testing-integrations` |
| `plugins/wf/skills/research/SKILL.md` | 39: `skill-name`; 56: `graphify`; 96: `principles`; 98: `subagents` |
| `plugins/wf/skills/research/how/README.md` | 3: `research` |
| `plugins/wf/skills/research/how/explainer-prompt.md` | 33: `doc-diagram` |
| `plugins/wf/skills/research/how/how.md` | 13: `subagents` |
| `plugins/wf/skills/research/why/sources/atlassian.md` | 9: `atlassian`; 14: `atlassian`; 22: `atlassian` |
| `plugins/wf/skills/research/why/why.md` | 7: `subagents`; 21: `github`; 41: `github`; 43: `preflight-atlassian` |
| `plugins/wf/skills/review/SKILL.md` | 23: `github`; 23: `design` |
| `plugins/wf/skills/review/playbooks/blast-radius.md` | 19: `git`; 42: `principles`; 44: `research`; 46: `research`; 48: `testing-integrations`; 49: `subagents`; 50: `subagents`; 59: `git`; 76: `writing-style` |
| `plugins/wf/skills/review/playbooks/code.md` | 10: `github`; 11: `principles`; 12: `github`; 27: `github`; 28: `github`; 38: `github` |
| `plugins/wf/skills/review/playbooks/comments.md` | 3: `github`; 17: `github`; 31: `git`; 31: `github`; 34: `git`; 87: `git`; 97: `github`; 101: `github`; 121: `github`; 127: `git`; 127: `git`; 143: `git` |
| `plugins/wf/skills/review/playbooks/hitl.md` | 23: `github`; 96: `github`; 131: `research` |
| `plugins/wf/skills/review/playbooks/tests-gap.md` | 25: `principles` |
| `plugins/wf/skills/review/references/blast-radius-worker-prompt.md` | 21: `testing-integrations`; 21: `prove` |
| `plugins/wf/skills/review/references/conversation-flows.md` | 3: `github`; 77: `github` |
| `plugins/wf/skills/review/references/investigation.md` | 7: `skill-name`; 34: `skill-name` |
| `plugins/wf/skills/review/references/posting.md` | 15: `github` |
| `plugins/wf/skills/review/references/smells-review-guidance.md` | 33: `principles` |
| `plugins/wf/skills/subagents/SKILL.md` | 24: `principles`; 26: `git` |
| `plugins/wf/skills/subagents/arena.md` | 39: `principles`; 43: `principles`; 49: `principles` |

## Verification

- Invocation tests: 29 passed (35 across the repo-consistency suite), including WF route/reference/template coverage, declared external and generated targets, dynamic rendering, missing terminators, multiple calls, human examples, guards, exclusions and retained non-WF legacy resolution.
- Affected WF design, implementation and subagents contract suites: passed.
- Full repository unit suite (`python3 .github/scripts/run-python-tests.py --unit-only`) and description lint: passed.
- No load traces were collected; runtime compliance remains an instruction contract, not a claimed static guarantee.
