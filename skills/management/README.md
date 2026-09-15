| PM flow                           | Real skill/plugin           | Repository                           | Sources / inputs used                                                                                                          | Output                                                                                                                                                                                           |
| --------------------------------- | --------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Project initiation**            | `stakeholder-map`           | `phuryn/pm-skills`                   | Project brief, stakeholder names, org/team information, known responsibilities                                                 | Stakeholder map, influence/interest matrix, engagement/communication recommendations                                                                                                             |
|                                   | `doc-coauthoring`           | `anthropics/skills`                  | User context, existing project docs, notes, requirements, proposals, decision material                                         | Project charter, project brief, governance doc, kickoff document. The skill explicitly supports structured documentation and decision/spec documents. ([GitHub][1])                              |
|                                   | `googlecalendar-automation` | `ComposioHQ/awesome-claude-skills`   | Live **Google Calendar** through Rube MCP                                                                                      | Kickoff meeting, recurring status meetings, steering meetings, updated events. ([GitHub][2])                                                                                                     |
| **Project planning**              | `sprint-plan`               | `phuryn/pm-skills`                   | Prioritized backlog, previous sprint reports, velocity data, team roster, PTO/availability, capacity information               | Sprint capacity, selected work, dependency sequence, risks, sprint goal and plan. The skill explicitly asks for backlog, velocity, roster and previous sprint data when available. ([GitHub][3]) |
|                                   | `xlsx`                      | `anthropics/skills`                  | `.xlsx`, `.xlsm`, `.csv`, `.tsv`, or other tabular project data                                                                | Project schedule, milestone tracker, resource/capacity plan, dependency table, status workbook. ([GitHub][4])                                                                                    |
|                                   | `jira-automation`           | `Composio / AAS`                     | Live **Jira** projects, issues, boards, sprints, users and comments through Rube MCP                                           | Created/updated Jira issues, sprint configuration, project tasks, comments, board/project changes. ([GitHub][5])                                                                                 |
| **Risk management**               | `pre-mortem`                | `phuryn/pm-skills`                   | Project/launch plan, PRD or equivalent planning document, known assumptions and dependencies                                   | Risks grouped as Tigers / Paper Tigers / Elephants, severity, mitigation actions, suggested owners and due dates. ([GitHub][6])                                                                  |
|                                   | `project-artifact`          | `anthropics/claude-plugins-official` | Repositories/PRs, tracker such as Linear/Asana/issues, plans/specs/design docs, project channels, owners, milestones and dates | Living project-status page with overview, workstreams, next steps, risks, open questions and decisions. It remembers sources and can refresh from live state. ([GitHub][7])                      |
| **Meeting management**            | `summarize-meeting`         | `phuryn/pm-skills`                   | Meeting transcript, recording, notes; optionally related background material                                                   | Markdown meeting summary containing participants, topics, decisions, action items, owners, due dates and open questions. ([GitHub][8])                                                           |
|                                   | `googlecalendar-automation` | `ComposioHQ/awesome-claude-skills`   | Google Calendar events, attendees, schedules                                                                                   | Created/updated meeting events and schedules. ([GitHub][2])                                                                                                                                      |
|                                   | `googledocs-automation`     | `ComposioHQ/awesome-claude-skills`   | Existing Google Docs, templates, meeting notes, document IDs                                                                   | New/updated Google Doc, exported PDF, copied template, inserted/replaced text. ([GitHub][9])                                                                                                     |
| **Sprint management**             | `sprint-plan`               | `phuryn/pm-skills`                   | Jira/backlog export, velocity history, team availability, story estimates and dependencies                                     | Proposed sprint scope, capacity allocation, dependency ordering, identified risks and sprint goal. ([GitHub][3])                                                                                 |
|                                   | `retro`                     | `phuryn/pm-skills`                   | Sprint data, velocity charts, team feedback, previous retrospective notes                                                      | Structured retrospective plus prioritized improvement actions, owners and deadlines. ([GitHub][10])                                                                                              |
|                                   | `jira-automation`           | `Composio / AAS`                     | Live Jira sprint and issues                                                                                                    | Update sprint, issues, assignments, comments or board state. ([GitHub][5])                                                                                                                       |
| **Change control**                | `doc-coauthoring`           | `anthropics/skills`                  | Change request, current plan, scope, affected design/docs, stakeholder context                                                 | Change-request document, impact assessment, decision record or updated plan. ([GitHub][1])                                                                                                       |
|                                   | `jira-automation`           | `Composio / AAS`                     | Impacted Jira issues/projects/sprints                                                                                          | Updated scope/tasks, dates, assignments, new change-related issues and comments. ([GitHub][5])                                                                                                   |
|                                   | `project-artifact`          | `anthropics/claude-plugins-official` | Current tracker, PRs/repository, project docs and previously configured sources                                                | Refreshed project page showing changed workstreams, risks, decisions and next steps. ([GitHub][7])                                                                                               |
| **Release / milestone readiness** | `pre-release-review`        | `sickn33/agentic-awesome-skills`     | Git repo, branches/diffs, GitHub via `gh`, configs, migrations, deployment material, secrets references, rollout information   | Read-only release-readiness report: blockers, migration/config gaps, rollout risks, rollback risks, owner and recommended action. ([GitHub][11])                                                 |
|                                   | `pre-mortem`                | `phuryn/pm-skills`                   | Release/milestone plan and assumptions                                                                                         | Risk classification and mitigation/action plan before go-live. ([GitHub][6])                                                                                                                     |
| **Execution monitoring**          | `project-artifact`          | `anthropics/claude-plugins-official` | Jira/Linear/Asana or issues, repository/PRs, project docs, milestones, workstream owners, project channels                     | Persistent status page; on refresh it updates the same artifact and reports the delta since the previous version. ([GitHub][7])                                                                  |
|                                   | `jira-automation`           | `Composio / AAS`                     | Jira issues, projects, boards, sprints, comments and users                                                                     | Current status queries plus updates to issues, assignments, comments and sprint state. ([GitHub][5])                                                                                             |
| **Weekly reporting**              | `project-artifact`          | `anthropics/claude-plugins-official` | Tracker + repository + docs + milestones + previous artifact state                                                             | Living weekly project overview and delta report. ([GitHub][12])                                                                                                                                  |
|                                   | `xlsx`                      | `anthropics/skills`                  | Jira exports, milestone data, RAID data, budget/resource tables, previous workbook                                             | `.xlsx` status workbook containing KPIs, RAG status, milestone tracking, resource/budget tables and charts. ([GitHub][13])                                                                       |
|                                   | `pptx`                      | `anthropics/skills`                  | Existing deck/template, status data, project-artifact summary, spreadsheet or supplied content                                 | `.pptx` management/steering deck; it can also update an existing presentation/template. ([GitHub][14])                                                                                           |
|                                   | `gmail-automation`          | Composio ecosystem                   | Gmail account, recipients, existing threads/drafts, report attachments/content                                                 | Draft/send/reply email, attachments, labels and follow-up communication. ([GitHub][15])                                                                                                          |
| **Project closure**               | `retro`                     | `phuryn/pm-skills`                   | Final project/sprint data, feedback, previous retrospective notes, outcomes                                                    | Lessons learned, what worked/didn't, prioritized improvement actions and owners. ([GitHub][10])                                                                                                  |
|                                   | `doc-coauthoring`           | `anthropics/skills`                  | Final project plan, milestones, outcomes, RAID history, lessons, handover information                                          | Closure report, handover document, lessons-learned document, final decision record. ([GitHub][1])                                                                                                |
|                                   | `google-drive-automation`   | Composio ecosystem                   | Google Drive files/folders and locally generated artifacts                                                                     | Uploaded/organized final reports, folder structure, permissions/sharing and archived project files. The skill supports upload, download, search, folders and permissions. ([GitHub][16])         |

[1]: https://github.com/anthropics/skills/blob/main/skills/doc-coauthoring/SKILL.md?plain=1&utm_source=chatgpt.com "skills/skills/doc-coauthoring/SKILL.md at main · anthropics/skills · GitHub"
[2]: https://github.com/ComposioHQ/awesome-claude-skills/blob/master/composio-skills/googlecalendar-automation/SKILL.md?utm_source=chatgpt.com "awesome-claude-skills/composio-skills/googlecalendar-automation/SKILL.md at master · ComposioHQ/awesome-claude-skills · GitHub"
[3]: https://github.com/phuryn/pm-skills/blob/main/pm-execution/skills/sprint-plan/SKILL.md?utm_source=chatgpt.com "pm-skills/pm-execution/skills/sprint-plan/SKILL.md at main · phuryn/pm-skills · GitHub"
[4]: https://github.com/anthropics/skills/blob/main/skills/xlsx/SKILL.md?utm_source=chatgpt.com "skills/skills/xlsx/SKILL.md at main · anthropics/skills · GitHub"
[5]: https://github.com/sickn33/agentic-awesome-skills/blob/main/skills/jira-automation/SKILL.md?utm_source=chatgpt.com "agentic-awesome-skills/skills/jira-automation/SKILL.md at main · sickn33/agentic-awesome-skills · GitHub"
[6]: https://github.com/phuryn/pm-skills/blob/main/pm-execution/skills/pre-mortem/SKILL.md?utm_source=chatgpt.com "pm-skills/pm-execution/skills/pre-mortem/SKILL.md at main · phuryn/pm-skills · GitHub"
[7]: https://github.com/anthropics/claude-plugins-official/blob/main/plugins/project-artifact/skills/project-artifact/SKILL.md?utm_source=chatgpt.com "claude-plugins-official/plugins/project-artifact/skills/project-artifact/SKILL.md at main · anthropics/claude-plugins-official · GitHub"
[8]: https://github.com/phuryn/pm-skills/blob/main/pm-execution/skills/summarize-meeting/SKILL.md?utm_source=chatgpt.com "pm-skills/pm-execution/skills/summarize-meeting/SKILL.md at main · phuryn/pm-skills · GitHub"
[9]: https://github.com/ComposioHQ/awesome-claude-skills/blob/master/composio-skills/googledocs-automation/SKILL.md?utm_source=chatgpt.com "awesome-claude-skills/composio-skills/googledocs-automation/SKILL.md at master · ComposioHQ/awesome-claude-skills · GitHub"
[10]: https://github.com/phuryn/pm-skills/blob/main/pm-execution/skills/retro/SKILL.md?utm_source=chatgpt.com "pm-skills/pm-execution/skills/retro/SKILL.md at main · phuryn/pm-skills · GitHub"
[11]: https://github.com/sickn33/agentic-awesome-skills/blob/main/skills/pre-release-review/SKILL.md?utm_source=chatgpt.com "agentic-awesome-skills/skills/pre-release-review/SKILL.md at main · sickn33/agentic-awesome-skills · GitHub"
[12]: https://github.com/anthropics/claude-plugins-official/blob/main/plugins/project-artifact/README.md?utm_source=chatgpt.com "claude-plugins-official/plugins/project-artifact/README.md at main · anthropics/claude-plugins-official · GitHub"
[13]: https://github.com/anthropics/skills/blob/main/skills/xlsx/SKILL.md?plain=1&utm_source=chatgpt.com "skills/skills/xlsx/SKILL.md at main · anthropics/skills · GitHub"
[14]: https://github.com/anthropics/skills/blob/main/skills/pptx/SKILL.md?utm_source=chatgpt.com "skills/skills/pptx/SKILL.md at main · anthropics/skills · GitHub"
[15]: https://github.com/davepoon/buildwithclaude/blob/main/plugins/all-skills/skills/gmail-automation/SKILL.md?utm_source=chatgpt.com "buildwithclaude/plugins/all-skills/skills/gmail-automation/SKILL.md at main · davepoon/buildwithclaude · GitHub"
[16]: https://github.com/davepoon/buildwithclaude/blob/main/plugins/all-skills/skills/google-drive-automation/SKILL.md?utm_source=chatgpt.com "buildwithclaude/plugins/all-skills/skills/google-drive-automation/SKILL.md at main · davepoon/buildwithclaude · GitHub"

----

# Claude for Project Management

Yes — for project management, I would structure Claude around the **project delivery lifecycle**, not product discovery.

The strongest dedicated PM skill set I found includes:

* `senior-pm`
* `scrum-master`
* `jira-expert`
* `confluence-expert`
* `meeting-analyzer`
* `team-communications`
* `program-manager`
* `sprint-retrospective`

The Composio collection then supplies the **action layer** for Jira, Asana, ClickUp, Slack, Google Calendar, Google Drive, Google Sheets, Gmail, and similar tools.

---

## 1. Project Initiation

```text
New project / initiative
        ↓
Project brief / charter
        ↓
Identify stakeholders
        ↓
Define roles
        ↓
Kickoff
```

### Useful skills

```text
senior-pm
    ↓
Project objectives
Scope
Constraints
Success criteria
    ↓
Stakeholder Register
RACI Matrix
Communication Plan
```

Then:

```text
meeting-agenda
        ↓
Google Calendar plugin
        ↓
Project kickoff meeting
        ↓
meeting-recap
```

### Key artifacts

* Project Brief / Charter
* Stakeholder Register
* RACI Matrix
* Communication Plan
* Kickoff documentation

These are the traditional project-management artifacts needed to establish scope, responsibilities, stakeholders, and communication.

---

## 2. Project Planning

This is where Claude can become particularly useful.

```text
Project scope
      ↓
WBS
      ↓
Activities
      ↓
Dependencies
      ↓
Estimates
      ↓
Resources
      ↓
Milestones
      ↓
Schedule
```

### Skills

* `senior-pm`
* `program-manager`

### Outputs

```text
Work Breakdown Structure
        ↓
Dependency Map
        ↓
Resource / Capacity Plan
        ↓
Project Schedule
        ↓
Milestones
```

These are canonical PM artifacts:

```text
WBS
 ↓
Schedule
 ↓
Capacity / Resources
 ↓
Dependency Tracking
```

Then push the plan into the execution system:

```text
Claude planning skills
        ↓
Jira Automation
   OR
Asana Automation
   OR
ClickUp Automation
   OR
Monday / Wrike
```

Composio exposes these as project-management automation integrations.

---

## 3. Risk, Issue, and Dependency Management

This should be a continuous PM flow.

```text
Project information
      ↓
Identify
 ┌────┼─────┬──────────┐
 ↓    ↓     ↓          ↓
Risk Issue Assumption Dependency
 └────┼─────┴──────────┘
      ↓
    RAID
      ↓
Owner + Mitigation + Due Date
```

### Recommended skills

* `senior-pm`
* `program-manager`
* `jira-expert`

### Artifacts

```text
RAID Log
├── Risks
├── Assumptions
├── Issues
└── Dependencies
```

A mature PM flow could be:

```text
Claude detects new risk
        ↓
Update RAID
        ↓
Create / update Jira item
        ↓
Assign owner
        ↓
Notify Slack
```

Recurring governance artifacts include:

* Risk Register
* RAID Log
* Issue Log
* Assumption Log
* Dependency Log

---

## 4. Daily Project Execution

For a software project:

```text
Jira
 +
GitHub
 +
Slack
        ↓
Claude
        ↓
Execution Health
```

### Skills

* `jira-expert`
* `scrum-master`
* `senior-pm`

Claude can answer questions such as:

* What changed since yesterday?
* What was completed?
* What is in progress?
* What is blocked?
* What is overdue?
* What is waiting on another team?
* What has no owner?
* Which milestones are at risk?

Then act through:

* Jira Automation
* GitHub Automation
* Slack Automation

The Jira integration covers issues, boards, sprints, and JQL.

GitHub covers:

* Issues
* Pull requests
* Actions
* Development activity

Slack provides:

* Messages
* Threads
* Search
* Notifications

---

## 5. Meeting Management

This is one of the highest-value PM workflows.

### Before the meeting

```text
Google Calendar
       ↓
Find meeting
       ↓
Jira + Confluence + Drive
       ↓
Gather context
       ↓
meeting-agenda / meeting-brief
```

### During the meeting

```text
Discussion
   ↓
Transcript / Notes
```

### After the meeting

```text
meeting-analyzer
        ↓
Decisions
Actions
Open questions
Risks
Dependencies
        ↓
Create / update Jira tasks
        ↓
Publish recap
```

A dedicated PM meeting skill can identify:

* Decisions
* Actions
* Open questions
* Risks
* Dependencies
* Ownerless actions

### Useful integrations

* Google Calendar Automation
* Google Drive Automation
* Slack Automation
* Gmail Automation

---

## 6. Agile / Sprint Management

If the project uses Scrum:

```text
Backlog
   ↓
Capacity
   ↓
Sprint Planning
   ↓
Sprint Execution
   ↓
Daily Monitoring
   ↓
Sprint Review
   ↓
Retrospective
```

### Skills

* `scrum-master`
* `jira-expert`
* `sprint-retrospective`

The `scrum-master` skill can cover:

* Sprint health
* Velocity forecasting
* Capacity planning
* Blocker detection
* Retrospectives

### Sprint monitoring flow

```text
Jira Sprint
    ↓
scrum-master
    ↓
Velocity
Capacity
Burndown
Blockers
Scope Change
    ↓
Sprint Health
```

At the end of the sprint:

```text
Sprint Metrics
     +
Team Feedback
     ↓
sprint-retrospective
     ↓
What Worked
What Didn't
Actions
Owners
Due Dates
```

---

## 7. Change Management

This is something the previous product-oriented approach largely missed.

```text
Change Request
      ↓
Analyze Impact
 ┌────┼────┬──────┐
 ↓    ↓    ↓      ↓
Scope Cost Time Resources
 └────┼────┴──────┘
      ↓
Decision
      ↓
Update Project Baseline
```

Claude can combine:

```text
senior-pm
    +
jira-expert
    +
confluence-expert
```

to produce:

* Change Request
* Impact Assessment
* Recommendation
* Decision Record
* Updated Schedule
* Updated RAID
* Updated Scope

For larger programs, `program-manager` becomes especially useful because changes can introduce cross-project dependencies.

---

## 8. Weekly Project Status

This would be one of my primary Claude workflows for a PM.

```text
Jira
GitHub
Slack
Calendar
RAID
Schedule
   ↓
Claude
   ↓
Weekly Project Status
```

### Output

```text
Overall: 🟢 / 🟡 / 🔴

Progress
Milestones
Schedule Variance
Completed Work
Next Week's Work

Risks
Issues
Dependencies

Decisions Required
Escalations
```

Then:

```text
team-communications
        ↓
┌────────────┬──────────────┐
│ Team       │ Detailed     │
│ Management │ Concise      │
│ Customer   │ External     │
└────────────┴──────────────┘
```

A Status Report and executive or steering-committee briefing normally draw from:

* Project Schedule
* RAID Log
* Work completed
* Upcoming milestones
* Decisions
* Escalations

---

## 9. Steering Committee / Executive Reporting

```text
Weekly Status
     +
Schedule
     +
RAID
     +
Budget / Resources
       ↓
senior-pm
       ↓
Executive Summary
```

### Produce

* Overall RAG status
* Milestones
* Budget / Resource status
* Top 3 risks
* Top 3 issues
* Decisions needed
* Escalations

Then publish to:

* Google Slides
* Google Docs
* Google Drive
* Email

The Google Workspace skill bundle covers:

* Gmail
* Calendar
* Chat
* Docs
* Sheets
* Slides
* Drive

---

## 10. Project Closure

```text
Project Completed
       ↓
Validate Deliverables
       ↓
Close Open Items
       ↓
Retrospective
       ↓
Lessons Learned
       ↓
Archive
```

### Skills

* `senior-pm`
* `sprint-retrospective`
* `meeting-analyzer`
* `confluence-expert`

### Outputs

* Final Project Status
* Lessons Learned
* Open Follow-up Actions
* Handover
* Project Retrospective
* Archive Structure

Project and milestone retrospectives, together with lessons learned, are standard closure artifacts.

---

# The PM Flow I Would Actually Build

```text
              PROJECT REQUEST
                    │
                    ▼
               senior-pm
                    │
             Project Charter
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
   Stakeholder Register      RACI
          │                   │
          └─────────┬─────────┘
                    ▼
                 KICKOFF
                    │
                    ▼
             Project Planning
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
      WBS       Dependencies   Resources
       │            │            │
       └────────────┼────────────┘
                    ▼
                 Schedule
                    │
                    ▼
              Jira / Asana
                    │
                    ▼
                EXECUTION
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
        Tasks      RAID     Meetings
          │         │         │
          │         │   meeting-analyzer
          │         │         │
          └─────────┼─────────┘
                    ▼
              Progress Tracking
                    │
                senior-pm
                    │
           Weekly Status Report
                    │
           ┌────────┴────────┐
           ▼                 ▼
        Team Update      Steering Update
           │                 │
         Slack          Docs / Slides
           │                 │
           └────────┬────────┘
                    ▼
             Change / Issues
                    │
                    ▼
                Execution
                    │
                    ▼
             Project Closure
                    │
                    ▼
              Retrospective
                    │
                    ▼
             Lessons Learned
```

---

# Compact Skill and Plugin Set for a Project Manager

## Skills

| Skill                  | Primary Use                                         |
| ---------------------- | --------------------------------------------------- |
| `senior-pm`            | Project planning, governance, status, scope, risks  |
| `program-manager`      | Cross-project dependencies and program coordination |
| `scrum-master`         | Sprint planning, capacity, velocity, blockers       |
| `jira-expert`          | Jira queries, issue management, boards and sprints  |
| `confluence-expert`    | Project documentation and knowledge management      |
| `meeting-analyzer`     | Decisions, actions, risks and follow-ups            |
| `team-communications`  | Stakeholder-specific communication                  |
| `sprint-retrospective` | Retrospectives and improvement actions              |

## Action Plugins

| Plugin / Integration | Use                                      |
| -------------------- | ---------------------------------------- |
| Jira                 | Tasks, issues, sprints, workflows, JQL   |
| Google Calendar      | Meetings, scheduling, kickoff, reviews   |
| Google Drive         | Project files and shared artifacts       |
| Google Docs          | Charters, reports, meeting notes         |
| Google Sheets        | RAID, budgets, capacity and trackers     |
| Google Slides        | Steering and executive reporting         |
| Slack                | Team communication and alerts            |
| Gmail                | Customer and stakeholder communication   |
| GitHub               | Software delivery, PRs, issues and CI/CD |

---

# Overall Model

```text
Initiate
   ↓
Plan
   ↓
Execute
   ↓
Monitor & Control
   ↓
Report
   ↓
Close
```

This is much closer to a **Project Manager operating system**:

> **Initiate → Plan → Execute → Monitor & Control → Report → Close**

Claude acts across both:

1. **PM artifacts** — charter, WBS, RAID, schedule, reports, meeting notes, retrospectives.
2. **Execution systems** — Jira, GitHub, Slack, Google Workspace, Asana, ClickUp, and similar tools.

