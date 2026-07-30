# Agent Registration and Exposure in Plugin System

## Plugin Structure

### Plugin Registration (marketplace.json)
- **Location**: [.github/plugin/marketplace.json](.github/plugin/marketplace.json)
- Plugins are registered in a central `marketplace.json` with name, source path, and description
- This is the **source of truth** for which plugins are available
- **Rule**: When adding/renaming/deleting a plugin, must update marketplace.json

### Current Plugins
All plugins follow identical structure in their `plugin.json`:
```json
{
  "name": "<plugin-name>",
  "version": "<version>",
  "description": "<description>",
  "skills": ["./skills"]
}
```

Five plugins registered:
1. **review** - PR code review skills
2. **wf** - Workflow automation skills
3. **ralph** - PR review automation
4. **atl** - Atlassian workflow
5. **az** - Azure CLI workflow

## Skills vs Agents Distinction

### Skills (SKILL.md)
- Standard entry point for Copilot agent capabilities
- Named in YAML frontmatter: `name: <skill-name>`
- Discovered by scanning all `SKILL.md` files in plugin skill directories
- All current plugins use only SKILL.md files

### Agents (.agent.md)
- **ONLY FOUND**: One agent file in the entire workspace
  - [/brain/plugins/ralph/skills/dev/ralphy-coder.agent.md]
  - Also: [/brain/plugins/ralph/skills/dev/ralph-impl.agent.md]
- Companion files to skills, providing autonomous agent specifications
- Named in YAML frontmatter: `name: <agent-name>`
- **Key difference**: Agents are invoked via `runSubagent` tool, NOT direct skill invocation

## Agent Discovery and Invocation

### How Agents Become Visible
**Pattern**: Agents appear to be discovered automatically based on `.agent.md` file presence
- File naming: `<name>.agent.md` where name matches the `name:` field in YAML frontmatter
- Location: Any skill directory within a plugin's `./skills/` path
- Auto-discovery: VS Code agent system appears to scan for these files when indexing plugin skills

### Agent vs Skill Registration
- **Skills**: Directly exposed in agent mode selection (immediate invocation)
- **Agents**: Referenced by other skills via `runSubagent` tool; not directly selectable by user

### Example: dev Skill's Nested Agent
The `dev` skill ([/brain/plugins/ralph/skills/dev/SKILL.md]) invokes the nested agent:
```
Invoke the `ralphy-coder` agent via `runSubagent` with the following prompt
```
The `ralphy-coder` agent is defined in [/brain/plugins/ralph/skills/dev/ralphy-coder.agent.md]

## Key Rules

1. **Marketplace is authoritative**: All plugin references start in marketplace.json
2. **No "agents" key in plugin.json**: Plugins only declare `skills` key; agents are auto-discovered within skill directories
3. **File-based discovery**: Presence of `*.agent.md` file determines agent visibility
4. **.agent.md naming convention**: Filename and frontmatter `name:` must match (both are `ralphy-coder`, `ralph-impl`)
5. **No central agent registry file**: Unlike marketplace.json for plugins, there's no centralized agent list

## To Make Agents Visible for Direct Invocation

Based on patterns observed:
1. Create `<agent-name>.agent.md` file in a skill directory
2. Use YAML frontmatter with matching `name:` and `description:`
3. Agent will be auto-discovered by VS Code plugin system
4. Agent becomes available for selection in agent mode

**Note**: Current workspace only shows `ralphy-coder` and `ralph-impl` as agents available for `runSubagent` invocation within dev skill context. Other agents may not be directly selectable—they are accessible only through skills that invoke them.
