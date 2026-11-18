# Bug report template

Use this exact structure without wrapper prose:

```markdown
**Impact**
{{impact|prose, business language; PO impact: affected behavior/users, impact on users and the system, boundaries, definition of fixed. Exclude implementation/root cause unless impact-relevant}}

**Preconditions**
- {{Required state/setup}}

**User Actions**
1. ...
2. ...
3. ...

**Actual Results:**
{{What happens}}

**Expected Results:**
{{What should happen}}

---
<details>
<summary>Technical notes</summary>

**Technical notes**
{{Any useful technical context}}

**Root cause (if known):**
{{Verified root cause, or omit}}
</details>
```
