# Draft artifact

Create or update one engineering artifact through its named route.

| Route | Result |
|---|---|
| `story` | Atomic user story |
| `task` | Implementation work item |
| `bug` | Defect report |
| `spec` | Specification |
| `hld` | High-level design |
| `toi` | Technical handover |

Use `draft` for new content, `update` for existing content, or `normalize` to revise only behavioral requirements. Untyped requirement fragments use `spec normalize`.

Examples: `draft-artifact story`, `draft-artifact task update`, `draft-artifact spec normalize`, `draft-artifact hld update`.

[SKILL.md](SKILL.md) selects the route and directly discloses its resources. Playbooks own procedures; templates own output structure; shared references own requirements and HLD update rules.

Design retains architecture decisions, interviews, evidence coordination, decomposition, approvals and publishing. Implement retains execution planning and integration. Writing style retains general prose, unslop, bottom lines and prompt sharpening. Draft artifact returns authored content and unresolved gaps to its caller.
