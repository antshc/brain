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
