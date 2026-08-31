# User Stories — ZIC Monitoring: Alerts & Tasks

> Derived from [`monitoring-alerts-tasks.md`](monitoring-alerts-tasks.md) and the feature
> design [ZIC Monitoring GUI — Alerts & Tasks](https://zerto.atlassian.net/wiki/spaces/ZIC/pages/2547974145/ZIC+Monitoring+GUI+Alerts+Tasks).
> One story per capability, plus technical enablement stories (11, 12, 13). GUI/FE development is
> out of scope: acceptance criteria are scoped to backend (REST API, DynamoDB, retention,
> CLI) behavior only. Each story ends with **Implementation decisions:** and, where the
> contract changes, a **Contract changes:** section.

---

**Epic:** [ZIC-5488] ZIC Health and Quality - Bug reduction, Upgrade Stabilization, Quality improvements

All user stories below linked to this epic as child work items.

## Story 0 — [ZIC-5764] [MONITORING] [BE] Technical: Expose the new alert monitoring fields on the REST contract ahead of implementation

- Review and manage alerts

**Blocked by:** None.

The FE team needs the new alerts fields available on the REST API contract returning stable placeholder (hardcoded dummy) values, so they can start building the monitoring UI in parallel before the backend logic that computes the real values exists.

### Acceptance Criteria
- The alerts read endpoints expose the new fields — related VPG (id and name), and entity area — populated with placeholder values.
- The published API documentation (Swagger/OpenAPI) reflects the new fields, request parameters, and endpoints.
- The placeholder implementation is isolated so it can be replaced by real logic without a contract change, and is clearly identifiable as temporary.

### Implementation decisions:
- Add the new fields to the alerts array model (`affectedVpgs` id/name), returning hardcoded placeholder values.
- Field names/types/nullability match the final contract so no client change is needed when the real logic lands.
- Placeholder logic is isolated and clearly marked temporary; Swagger/OpenAPI is regenerated; endpoints enforce the existing Keycloak auth.

### Contract changes:
- GET /api/v2/alerts: + affectedVpgs[{id,name}].

---


## Story 1 — [ZIC-5754] [MONITORING] [BE] Present, review and manage alerts

- Present a count of active alerts
- Review and manage alerts
- Resolve the related VPG information of an alert

**Blocked by:** None.

Users need to see how many active alerts exist and review the most recent ones at a glance, and to review, filter, acknowledge, and reset the full set of alerts, so they notice failures early and can triage system health and clear alerts they have handled.

Users need each alert in the alert set to show its related VPG (id and name), so they can identify the affected protection group directly from the review without cross-referencing identifiers by hand.

### Acceptance Criteria
- The number of alerts shown in the short list is capped by configurable count (5).
- The full set of alerts is presented with severity, Alert ID, related VPGs (when any), entity area, start time, and description.
- Filter active (non-dismissed) alerts; dismissed (acknowledged) alerts on the User's request. All alerts shown by default
- Alerts are ordered most-recent-first by start time by default.
- The User can dismiss or undismiss one selected alert.
- Each dismiss or undismiss is applied independently per selected alert, and a per-alert failure is reported for that alert only without aborting the others.
- Each alert's related VPG (id and name) is resolved on the fly from the alert's stored VPG identifier against the current VPG list.
- A platform-level (ZIC) alert is presented with no related VPG.
- When an alert references a VPG that no longer exists, the alert is omitted from the set.

### Implementation decisions:
- `GET /api/v2/alerts` sorts by `startTime` descending server-side; no server-side pagination.
- `top` caps the returned rows; when `top` exceeds the max-result limit (default 1000), the max-result limit is returned.
- Max-result limit is 1000, read from configuration (tweakable), not hardcoded.
- `isDismissed=false` returns active (non-dismissed) alerts; omitting the parameter returns all.
- No bulk endpoints (see the no-bulk Concept): dismiss/undismiss act on a single alert per call keyed by `AlertKey`; the client issues one request per selected alert and surfaces per-alert failures independently.
- `affectedVpgs` is a single-item array (one alert per VPG); the legacy `vpgId` field is obsolete, kept one version for backward compatibility.
- `affectedVpgs` (id + name) is resolved on the fly by joining the alert's stored VPG identifier against the current VPGs list; it is not persisted on the alert.
- ZIC (platform-level) alerts resolve to an empty `affectedVpgs`.
- A referenced VPG that no longer exists resolves to id-only (or is omitted) and never fails the alert row.
- `affectedVpgs` supersedes the obsolete `vpgId`; one alert maps to one VPG (single-item array).

### Contract changes:
GET /api/v2/alerts — added query parameter:
| Parameter | Type   | Description                                              |
| --------- | ------ | -------------------------------------------------------- |
| top       | number | Cap returned rows; if top > max result, max is returned. |

GET /api/v2/alerts — each alert gains:
| Parameter       | Type              | Description                                                                       |
| --------------- | ----------------- | -------------------------------------------------------------------------------- |
| affectedVpgs    | array             | Related VPGs [{id,name}]; single item; resolved on the fly; empty for ZIC.        |

PUT /api/v2/alerts (Get alert by AlertKey) — the returned alert gains the same `affectedVpgs` field.

(`isDismissed` query param and `isDismissed`/`alertEntity`/`reasons` fields, and the `PUT /alerts/dismiss|undismiss` endpoints, already exist.)

---

## Story 2 — [ZIC-5755] [MONITORING] [BE] Export alerts to a spreadsheet

- Export alerts to a spreadsheet

**Blocked by:** Story 1 [ZIC-5754] (reuses the `GET /api/v2/alerts` read and its filters).

Users need to export the current set of alerts to a spreadsheet, so they can share and archive alert data outside the product.

### Acceptance Criteria
- A spreadsheet file containing the alerts the User is viewing is produced and delivered as a file `alerts.xlsx`.
- Only authenticated Users may export alerts, using the same authorization as viewing alerts.
- The exported spreadsheet reflects the alerts requested at export time.
- When there are no alerts to export, an empty (headers-only) spreadsheet is produced.
- If export generation fails, the failure is presented and no partial file is downloaded.

### Implementation decisions:
- Export reuses `GET /api/v2/alerts` with `Accept: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`; content negotiation switches the response to XLSX.
- XLSX serialization uses EPPlus 4.5.3.2 (same version as ZVM) to avoid new licensing/legal approval.
- Export honors the same query filters as the JSON read; the file is named `alerts.xlsx`.
- Same Keycloak auth/authorization as the alerts read endpoint.
- Empty result yields a headers-only workbook; generation failure returns an error with no partial file.

### Contract changes:
GET /api/v2/alerts
Accept: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

Response: 200 OK, Content-Disposition: attachment; filename="alerts.xlsx"
Body: XLSX binary (one row per alert, same fields as the JSON response).

---

## Story 3 — [ZIC-5756] [MONITORING] [BE] Review and manage tasks

- Present a count of running and waiting tasks
- Review and manage tasks

**Blocked by:** None.

Users need to see how many tasks are in progress or waiting for their input and review the most recent active ones, and also review the full set of tasks — filtering by status and time period and inspecting who ran each and any notes — so they can track long-running operations, respond when a Failover Test needs to be stopped, and audit operations end to end.

### Acceptance Criteria
- A count of tasks Waiting for User Input is presented when any exist and a count of running tasks is presented. The running count excludes tasks Waiting for User Input, and the waiting count excludes running tasks.
- One set of tasks is presented with operation type, status, progress, start time, and completion time (existing fields); related entities, initiator, and notes are added to this same set by [ZIC-5757], [ZIC-5758], and [ZIC-5759] respectively. 
- The list of tasks, ordered by start time descending with running and waiting tasks prioritized,
- The User can cap the list size by configurable parameter.
- The User can filter tasks by one or more statuses (combined with OR; with no status selected, all tasks are shown).
- The User can filter tasks by a time using startedAfterDate filter.
- Tasks Waiting for User Input are indicated, and the User can trigger Failover Test Stop directly for such a task.
- Tasks are ordered by start time descending by default; when sorted by status-and-date, order is Running → Waiting → Failed → Completed, then start time descending.
- The derived `waiting` and `failed` statuses are computed over the full task list so status sorting is correct.
- The returned task set is capped at a configurable limit (10000).
- Notes are returned verbatim (null when omitted); the initiator is shown when present and empty for tasks without one.

### Implementation decisions:
- `GET /api/v2/tasks` filters by `status` (CSV, OR semantics), `startedAfterDate` (UTC), and `sort` (0=None, 1=StatusAndDate); no server-side pagination, `top` supported. The active short list is served by `GET /api/v2/tasks?top=5&status=running,waiting&sort=1`.
- `running` and `waiting` counts are computed on the fly server-side: `running` excludes waiting, `waiting` excludes running.
- `waiting` and `failed` are derived on the fly over the full list: `waiting` = FailoverTest task `Completed` while its VPG state is still `FailoverTest`; `failed` = `status == Completed && taskResult.taskCompletionStatus == Failed`.
- `sort=1` orders Running → Waiting → Failed → Completed, then `startTime` desc.
- Counts and derived statuses are calculated over the entire task list so status sorting stays correct; retention keeps the list small (in-memory cache deferred).
- `relatedEntities`, `initiatedBy`, and `completeResult` are surfaced on each task (Stories 4, 5, 6).
- Remove the `topPerProperty` query parameter (previously used to return the last two tasks per VPG).
- Result cap read from configuration; retention keeps the list bounded.

### Contract changes:
GET /api/v2/tasks — added query parameters:
| Parameter        | Type     | Description                                                                                                                                    |
| ---------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| status           | string   | CSV, OR filter; values: completed, running, waiting, failed. waiting = FailoverTest Completed + VPG state FailoverTest; failed = Completed + taskCompletionStatus Failed. Omit for all. |
| startedAfterDate | datetime | UTC, e.g. 2024-01-15T10:30:00Z.                                                                                                               |
| sort             | number   | 0=None (default), 1=StatusAndDate.                                                                                                            |

GET /api/v2/tasks — response gains count fields:
| Parameter | Type   | Description                                |
| --------- | ------ | ------------------------------------------ |
| running   | number | Count of running tasks, excludes waiting.  |
| waiting   | number | Count of waiting tasks, excludes running.  |

Removed: `topPerProperty` query parameter. (`top` already exists.)

---

## Story 3A — [ZIC-5866] [MONITORING] [FE] Present running and waiting tasks in the header indicator

- Present running and waiting tasks

**Blocked by:** [ZIC-5756] (`GET /api/v2/tasks` `top`/`status`/`sort` query and the `running`/`waiting` counts the widget reads).

Users need to see, without any action, how many tasks are running or waiting for their input while on any ZIC page, and glance at the most recent ones, so they notice long-running or stuck operations early.

### Acceptance Criteria
- A tasks indicator is shown in the page header on every ZIC page.
- The indicator's badge shows the waiting count when it is greater than zero; otherwise it shows the running count.
- The indicator's data is kept current by polling on a configurable client-side interval (default 2 seconds).
- Clicking the indicator opens a dropdown listing up to a configurable number (default 5) of the most recent running or waiting tasks, each showing its operation type and status/progress.
- When there are no running or waiting tasks, the dropdown shows a "No running tasks" message instead of a list.
- Each waiting task is visually marked as waiting for user input; clicking that marker opens the Failover Test Stop confirmation for that task directly from the dropdown.
- The dropdown offers a "Show All" action that navigates to the full Tasks view.

### Implementation decisions:
- The widget polls `GET /api/v2/tasks?top=5&status=running,waiting&sort=1` ([ZIC-5756]'s contract) on the configurable interval;
- Badge value is derived client-side from the response's `running`/`waiting` counts: show `waiting` when `> 0`, else `running`.
- Dropdown rows render `operationType` and a progress bar from `progress`; a row is marked "waiting for user input" when `status == waiting && operationType == FailoverTest`, matching the derivation already returned by [ZIC-5756].
- Clicking the "waiting for user input" marker opens the existing Failover Test Stop confirmation modal for that task's VPG.
- "Show All" navigates to `/main/monitoring/tasks`.
- Polling interval and dropdown item count are read from client-side configuration, not hardcoded, mirroring the equivalent alerts header indicator.

### Contract changes:
use the `GET /api/v2/tasks` contract (including `running`/`waiting` counts and `top`/`status`/`sort` parameters) already delivered by [ZIC-5756].

---

## Story 3B — [ZIC-5694] [MONITORING] [FE]  Implement Tasks View in ZIC UI

- Review and manage tasks

**Blocked by:** [ZIC-5756] (`status`/`startedAfterDate`/`sort` query and `running`/`waiting` counts), [ZIC-5757] (`relatedEntities`), [ZIC-5758] (`initiatedBy`), [ZIC-5759] (`completeReason`/Failover Test Stop result), [ZIC-5762] (tasks export).

Users need a full-page Tasks view where they can review, filter, sort, and export the complete task set, and trigger Failover Test Stop for a waiting task, so they can audit and manage long-running operations beyond the header dropdown's short list.

### Acceptance Criteria
- A Tasks tab is available at `/main/monitoring/tasks`, reachable from the header tasks dropdown's "Show All" link.
- The full task set is presented with operation type, status, progress, start time, initiator, related entities, and notes.
- The task data is kept current by polling on a configurable client-side interval (default 2 seconds) while the tab is active; polling stops when the tab is inactive and resumes when it becomes active again.
- The User can filter the task set by one or more statuses (running, waiting, failed, completed); with none selected, all tasks are shown.
- The User can filter the task set by a start-date threshold.
- The User can apply a client-side free-text quick-filter across the visible task set.
- The task set defaults to status-priority ordering (Running → Waiting → Failed → Completed), then start time descending; sort matches the API's `sort` parameter.
- A task waiting for user input is visually marked, and the User can trigger the Failover Test Stop confirmation for it directly from the grid.
- The User can choose which columns are shown via a column chooser.
- The User can export the currently selected/visible tasks to a spreadsheet file.
- Large task sets render without degrading the page (client-side virtualised grid; no server-side pagination).

### Implementation decisions:
- The tab polls `GET /api/v2/tasks` with `status`, `startedAfterDate`, and `sort` query parameters ([ZIC-5756]'s contract) on the configurable interval; polling is paused via the existing tab-visibility pattern used by the Alerts tab.
- Status filter maps to the CSV `status` query parameter; date filter maps to `startedAfterDate` (UTC); sort toggle maps to `sort` (0=None, 1=StatusAndDate).
- Free-text quick-filter is applied client-side against the already-fetched grid rows.
- Grid renders `initiatedBy`, `relatedEntities` (comma-separated resolved names), and `completeReason` columns delivered by [ZIC-5757]/[ZIC-5758]/[ZIC-5759]; blank when null.
- A row is marked "waiting for user input" using the same derivation as the header widget (`status == waiting && operationType == FailoverTest`); clicking it opens the existing Failover Test Stop confirmation modal.
- Export button fires the tasks export request from [ZIC-5762] scoped to the selected rows and triggers a `tasks.xlsx` download.
- Column visibility (chooser) and grid virtualisation follow the same ag-Grid pattern already used by the Alerts tab; no server-side pagination.

### Contract changes:
No new contract; consumes the `GET /api/v2/tasks` (`status`/`startedAfterDate`/`sort`, `initiatedBy`, `relatedEntities`, `completeReason`) and tasks export contracts already delivered by [ZIC-5756], [ZIC-5757], [ZIC-5758], [ZIC-5759], and [ZIC-5762].

---

## Story 4 — [ZIC-5757] [MONITORING] [BE] Resolve the related entities of a task

- Resolve the related entities of a task

**Blocked by:** None.

Users need to see which domain objects each task affected, so they can understand a task's scope without cross-referencing identifiers by hand.

### Acceptance Criteria
- For each task, the named domain objects it touches are resolved on the fly by joining the task's Vpg identifiers against the current VPG and member-account lists.
- VPG-related tasks present the VPG name and its protected and recovery account/region information.
- Member-account tasks present the account identifier and its description when available.
- Tasks with no related domain object (e.g., log collection) present no related entities.

### Implementation decisions:
- `relatedEntities` is computed on the fly by joining the task's identifiers against the current VPGs and member-accounts lists; not persisted.
- Each entry is an abstract object keyed by `type` (`Vpg` | `MemberAccount`); `Vpg` carries id, name, state, protected account/region and recovery account/region; `MemberAccount` carries id and optional description.
- VPG task types: CreateVpg, UpdateVpg, DeleteVpg, ReverseProtectVpg, FailoverLive, FailoverTest, FailoverTestStop, FailoverLiveCommit, FailoverLiveRollback, InsertVpgCheckpoint.
- MemberAccount task types: CreateMemberAccount, UpdateMemberAccount, DeleteMemberAccount. LogCollection tasks resolve to empty `relatedEntities`.
- A referenced entity that no longer exists resolves to id-only (or is omitted) and never fails the task row.

### Contract changes:
GET /api/v2/tasks , GET /api/v2/tasks/{taskId} — each task gains:
| Parameter              | Type   | Description                                                              |
| ---------------------- | ------ | ----------------------------------------------------------------------- |
| relatedEntities        | array  | Domain objects the task touches; computed on the fly.                   |
| relatedEntities[].type | string | Vpg or MemberAccount; drives the entity shape.                          |
| relatedEntities[].id   | string | Entity identifier.                                                      |
| relatedEntities[].name | string | VPG name / member-account description.                                  |

Vpg entries also carry `state`, `protectedAccountId`, `protectedRegionId`, `recoveryAccountId`, `recoveryRegionId`.

---

## Story 5 — [ZIC-5758] [MONITORING] [BE] Record the Initiator of a task

- Record the Initiator of a task

**Blocked by:** None.

The business needs each task to record who started it, so Users and auditors can attribute every operation to a user or to the system.

### Acceptance Criteria
- The initiating User's identity is captured once at task creation from the authenticated request's Keycloak `preferred_username` claim and is not re-derived on later reads.
- The captured initiator is persisted with the task and exposed on reads for a single task and for the task set.
- Tasks created before this capability existed return null or omitted the initiator.

### Implementation decisions:
- `initiatedBy` is captured once at task creation from `ICurrentUser.Username` (Keycloak `preferred_username`) and passed explicitly into the task factory/constructor; never read inside the lazily-evaluated `ZicTaskMetadata` getter.
- `ICurrentUser` abstraction lives in the Core/Framework abstractions bar (pure BCL-only interface); implementation `CurrentUserHttpContext` lives in ApiGateway, injects `IHttpContextAccessor`, and reads `HttpContext?.User.FindFirstValue("preferred_username")`.
- Register `IHttpContextAccessor` (not currently registered); bind `ICurrentUser` as scoped. Use the explicit `"preferred_username"` claim lookup (scheme sets no `NameClaimType`).
- Persisted via a nullable `ZicTaskMetadata.initiatedBy` into the existing `TaskMetadataSerialized` DynamoDB column; rehydrated on read. No change to the external `Zerto.Infrastructure.Tasks` package, no new DB column.
- Applied across the 4 task-creating managers (11 task types): `VpgManagementManager` (Create/Update/ReverseProtect/Delete), `RecoveryOperationsManager` (Failover/Commit/Rollback), `ReplicationManager` (Insert checkpoint), `MemberAccountManager` (Create/Delete/Update). No system scheduled tasks.
- Automated/system-triggered tasks record the fixed value `"System"`; `null` for missing claim and for pre-existing tasks.
- Exposed as a nullable `initiatedBy` on `TaskInfoModel`.

### Contract changes:
GET /api/v2/tasks , GET /api/v2/tasks/{taskId} — each task gains:
| Parameter   | Type              | Description                                                                    |
| ----------- | ----------------- | ------------------------------------------------------------------------------ |
| initiatedBy | string (nullable) | preferred_username of the user who started the task; "System" for automated; null for none/old tasks. |

DynamoDB Tasks--<deploymentId>:
| TaskMetadataSerialized.initiatedBy | string (nullable) | Captured once at creation. |

---

## Story 6 — [ZIC-5759] [MONITORING] [BE] Capture User completeReason and result status when stopping a Failover Test

- Capture User notes and result when stopping a Failover Test

**Blocked by:** None.

Users need to record a free-text completeReason and a result status when stopping a Failover Test, so the outcome of the drill is captured with the task for later review.

### Acceptance Criteria
- The User can submit a completeReason and a result status when triggering Failover Test Stop.
- The completeReason and result status are persisted with the resulting task and exposed on task reads.
- A completeReason is accepted only for the Failover Test Stop action and has no effect on other recovery actions.
- The completeReason is limited to 4000 characters; a completeReason that exceeds 4000 characters is rejected with a validation error.
- An omitted completeReason is recorded as null; a blank/whitespace-only completeReason is recorded as an empty ("") completeReason; both are returned verbatim.
- An omitted result status is recorded as null; a blank/whitespace-only result status is recorded as an empty ("") result status; both are returned verbatim.

### Implementation decisions:
- the request model uses the 'completeResult' field the dynamodb stores 'completeResult' in the serialized blob, and the response model uses 'completeResult' to mirrors ZVM response contract.
- `PUT /api/v2/vpgs/{vpgId}/failover` with header `Zic-Action: FailoverTestStop` carries `failoverTest.summary` (completeReason) and `failoverTest.success` (testResult.status).
- `failoverTest.summary` is `[StringLength(4000)]` (ZVM DB column limit); only applied for FailoverTestStop and ignored by other recovery actions dispatched through the shared request model.
- `failoverTest.success` is mapped to `FailoverTestStatus` enum: `FailedByUser=4`, `Success=5`.
- The failoverTest.summary (note) is threaded through `IRecoveryOperationManager.FailoverTestStop`, captured once and stored in a task field (mirroring the VPG-id / initiatedBy pattern), exposed via `ZicTaskMetadata.failoverTest.Summary`/`.Status`; not read inside the lazy metadata getter.
- Serialized into the existing `TaskMetadataSerialized` column (`failoverTest.Summary`, `failoverTest.Status`); no new DB column, no infra package change.
- Response adds nullable `completeReason` on `TaskInfoModel`, null when absent; blank note stored as null, omitted as null.

### Contract changes:
PUT /api/v2/vpgs/{vpgId}/failover (Header: Zic-Action: FailoverTestStop) — request body gains:
| Parameter                 | Type   | Description                                    |
| ------------------------- | ------ | ---------------------------------------------- |
| failoverTest.summary | string | Note; FailoverTestStop only; max 4000 chars.   |
| failoverTest.success         | bool   | true/false mapped to FailoverTestStatus: FailedByUser=4, Success=5.         |

GET /api/v2/tasks , GET /api/v2/tasks/{taskId} — task gains:
| Parameter              | Type              | Description                          |
| ---------------------- | ----------------- | ------------------------------------ |
| completeReason | string (nullable) | failoverTest.summary entered on Failover Test Stop.  |

DynamoDB Tasks--<deploymentId> — added fields:
| TaskMetadataSerialized.failoverTest.Summary | string (nullable) | Max 4000 chars.               |
| TaskMetadataSerialized.failoverTest.Status         | number            | FailoverTestStatus enum id.   |

---

## Story 7 — [ZIC-5760] [MONITORING] [BE] Present the latest task for each VPG

- Present the latest task for each VPG

**Blocked by:** None.

Users need to see the latest task for each VPG alongside the VPG itself, so the product can show in-progress operation state and enable the Failover Test Stop action without a separate lookup.

### Acceptance Criteria
- Each VPG includes its latest-task information (operation type, status, progress, start and completion times, completion status), available with the VPG itself.
- The latest-task information reflects the most recent task for that VPG, mirroring the same latest-task selection previously produced by `GET /tasks?top=1&topPerProperty=VpgId`.

### Implementation decisions:
- `GET /api/v2/vpgs` response gains a `tasksInfo` array containing only the VPG's latest task (single item), replacing the previous `GET /tasks` aggregation.
- `tasksInfo[0]` carries taskId, operationType, status, progress, startTime, endTime, and taskResult.taskCompletionStatus.
- `tasksInfo` is empty list when the VPG has no task.
- Failover Test Stop availability is derived from `vpgState` including FailoverTest AND last task not being a currently-running FailoverTestStop.

### Contract changes:
GET /api/v2/vpgs — each vpg gains:
| Parameter | Type  | Description                                               |
| --------- | ----- | -------------------------------------------------------- |
| tasksInfo | array | Latest task for the VPG (single item); empty array when none. Item carries taskId, operationType, status, progress, startTime, endTime, taskResult. |

---

## Story 7A — [ZIC-5865] [MONITORING] [FE] Use VPG latest-task info to decide when to show the Failover Test Stop button

- Present the latest task for each VPG
- Failover Test Stop action availability

**Blocked by:** Story 7 [ZIC-5760] (VPG `tasksInfo` latest-task data is exposed on `GET /api/v2/vpgs`).

Users need the VPG summary to drive the Failover Test Stop action availability without a separate task lookup, so the action is only enabled when the VPG is actually in a stop-eligible state and no stop task is already running.

### Acceptance Criteria
- The action is available only while the protection group is in the failover-test state.
- The action is not available while a failover-test stop is already running for the same protection group.
- When the most recent task for a protection group is not a failover-test stop that is still running, the action can be shown as available.
- If the protection group has no recent task, the action is based on the protection-group state alone.
- If the system cannot determine the latest task, the action stays unavailable rather than being shown in an invalid state.

### Implementation decisions:
- `isStopTestDisabled()` in `helper.ts` already implements the correct condition (`vpgState` includes `FailoverTest` AND latest task is not a running `FailoverTestStop`); the condition itself is unchanged by this story.
- Only the source of the latest task changes: stop reading it from the separate `GET /tasks?top=1&topPerProperty=VpgId` call (joined client-side into a `tasksByVpgId` map) and read it from the VPG's own `tasksInfo` instead.
- `topPerProperty` is removed from the tasks contract ([ZIC-5756]), so this FE call must be retired regardless; `useVpgDataSource` and the `task` parameter threaded into `isStopTestDisabled`/`getButtonsState` are updated to source from `vpg.tasksInfo[0]` instead of the separate map.
- The unrelated `latestCheckpoint` existence check in the same function is out of scope and stays as-is.

### Contract changes:
No contract change. The FE consumes the existing `GET /api/v2/vpgs` payload:
| Parameter | Type | Description |
| --------- | ---- | ----------- |
| vpgState | string/enum | Current VPG state, including `FailoverTest`. |
| tasksInfo | array | Latest task for the VPG; item includes `operationType`, `status`, `progress`, `startTime`, `endTime`, and task result metadata. |

---

## Story 12 — [ZIC-5765] [MONITORING] [BE] Technical: Index and filter the tasks DynamoDB collection for bounded, recent-first retrieval

- Review and manage tasks

**Blocked by:** None.

The task query layer needs a server-side sort index and bounded, filtered retrieval over the tasks DynamoDB collection, so task reads return the most recent tasks efficiently and stay within the result limit as the table grows without bound.

### Acceptance Criteria
- Task queries return results ordered most-recent-first using a `startTime` descending index on the tasks collection.
- Only tasks whose `endTime` falls within the configured recent window (assumption: last 30 days) are returned; older completed records remain in the table but are excluded.
- Results are capped at a configurable limit (assumption: 10 000 items), and the cap discards the oldest tasks first by virtue of the `startTime` index.
- Running and waiting tasks (with no `endTime`) are not excluded by the `endTime` window.
- The status, time-period, and free-text filters requested by the task review are applied at query time against the indexed collection.
- The recent-window duration and result cap are read from configuration.

### Implementation decisions:
- Add a `startTime` descending index on the tasks DynamoDB collection for most-recent-first retrieval.
- Apply an `endTime` age filter (recent window, assumption 30 days) at query time; older completed records stay in the table but are excluded; running/waiting tasks (no `endTime`) are never excluded by the window.
- Cap results at a configurable limit (assumption 10 000); the index discards the oldest first.
- Read the window duration and result cap from `IZertoConfiguration.TryRead`, not hardcoded.
- Status and time filters are applied at query time on the indexed collection (free-text quick-filter remains client-side).

---

## Story 8 — [ZIC-5761] [MONITORING] [BE] Apply a retention policy to tasks

- Apply a retention policy to tasks

**Blocked by:** None.

The business needs old tasks to be cleaned up automatically, so stored task data stays bounded and the task API remains within its result limit.

### Acceptance Criteria
- Tasks are evaluated for eviction on a recurring interval (assumption: every 1 hour) and again on ZIC restart.
- A task that has completed and is older than 48 hours is evicted; a completed task younger than 48 hours is retained.
- Running or waiting tasks are retained, and Waiting-for-User-Input tasks are protected from the 48-hour rule until the input is resolved.
- Any task, regardless of status, is evicted once it exceeds the absolute age limit (assumption: 90 days).
- A still-running or waiting task has its per-operation-type compensation action run before eviction, including for stale tasks evaluated on restart.
- Boundary ages (exactly 48 hours or the absolute limit) apply the eviction rule consistently.

### Implementation decisions:
- A background service evaluates tasks on a recurring 1-hour timer and once on ZIC startup.
- Eviction rules: completed & age > 48h → evict; running/waiting → retain; Waiting-for-User-Input → protected from the 48h rule; any task with age ≥ 90 days → evict via the absolute limit regardless of status.
- Still-running/waiting tasks run their per-operation-type compensation action before eviction, including stale tasks scanned at restart.
- A DB-level query filter selects tasks completed within the recent window (assumption: last 30 days) to keep reads bounded; interval and windows are configurable.

---

## Story 9 — [ZIC-5762] [MONITORING] [BE] Export tasks to a spreadsheet

- Export tasks to a spreadsheet

**Blocked by:** Story 3 [ZIC-5756] (task read/selection the export is built on).

Users need to export a selected set of tasks to a spreadsheet, so they can share and archive task data outside the product.

### Acceptance Criteria
- A spreadsheet file containing the selected tasks is produced and delivered as a file named `tasks.xlsx`.
- Only authenticated Users may export tasks, using the same authorization as viewing tasks.
- The exported spreadsheet reflects the tasks requested at export time.
- When no tasks are selected, an empty (headers-only) spreadsheet is produced.
- If export generation fails, the failure is presented and no partial file is downloaded.

### Implementation decisions:
- Export via `POST /api/v2/tasks` with `Accept: application/xlsx` and a body containing the selected task ids; returns an XLSX download named `tasks.xlsx`.
- XLSX serialization uses EPPlus 4.5.3.2 (same version as ZVM).
- Same Keycloak auth/authorization as the tasks read endpoint; empty selection → headers-only workbook; failure → error with no partial file.

### Contract changes:
POST /api/v2/tasks
Accept: application/xlsx

Request body
[ "taskId1", "taskId2" ]   // selected task ids

Response: 200 OK, Content-Disposition: attachment; filename="tasks.xlsx"
Body: XLSX binary.

---

## Story 10 — [ZIC-5763] [MONITORING] [BE] Enable command-line access to alerts and tasks monitoring

- Enable command-line access to alerts and tasks monitoring

**Blocked by:** Stories 1–7 and 9 [ZIC-5754, ZIC-5755, ZIC-5756, ZIC-5757, ZIC-5758, ZIC-5759, ZIC-5760, ZIC-5762] (the REST endpoints, fields, and actions the CLI surfaces).

Users need the ZIC command-line client to support the new alerts and tasks monitoring behaviors, so they can consume monitoring data and actions outside the GUI.

### Acceptance Criteria
- A command-line User can retrieve alerts and tasks through the CLI.
- A command-line User can perform the new monitoring actions supported by the REST API (assumption: dismiss/undismiss alerts, stop a Failover Test with a note/result, filter tasks).
- The new task and alert fields (initiator, notes, related entities, latest task) are reflected in CLI output.
- The CLI uses the same authentication and authorization as the REST API and mirrors its contract for alerts and tasks.
- When a field is absent for a record (e.g., null initiator or notes), the CLI omits it or shows it as empty rather than failing.
- When an action is unavailable for a record's current state, the CLI reports the reason rather than performing it.

### Implementation decisions:
- The CLI consumes the updated REST contract: `GET /api/v2/alerts` (with `isDismissed`/`top`), `GET /api/v2/tasks` (with `status`/`startedAfterDate`/`sort`), `PUT /api/v2/alerts/dismiss|undismiss`, and `PUT /api/v2/vpgs/{vpgId}/failover` (FailoverTestStop with note/result).
- Output reflects the new fields: `initiatedBy`, `completeResult`, `relatedEntities`, and VPG `tasksInfo` latest task.
- Uses the same Keycloak auth/authorization as the REST API; per-operation calls (no bulk endpoints).
- Absent fields (null initiator/notes) are omitted or rendered empty; unavailable state-dependent actions report the reason instead of executing.

---

## Story 11 — [ZIC-5767] [MONITORING] [BE] Technical: Expose the new task monitoring fields on the REST contract ahead of implementation

- Review and manage tasks

**Blocked by:** None.

The FE team needs the new tasks fields available on the REST API contract returning stable placeholder (hardcoded dummy) values, so they can start building the monitoring UI in parallel before the backend logic that computes the real values exists.

### Acceptance Criteria
- The tasks read endpoints (`GET /tasks` and `GET /tasks/{taskId}`) expose the new fields — initiator (`initiatedBy`), note (`completeReason`), related entities.
- The vpgs set endpoint (`GET /vpgs`) exposes the latest-task information in the tasksInfo set for each VPG.
- The alerts read endpoints expose the new fields — related VPG (id and name).
- The new monitoring actions (Failover Test Stop with failoverTest.summary/failoverTest.success, task status/time/text filter parameters) are present in the contract, accept well-formed requests, and return stubbed success responses.
- Each field's name, type, and nullability matches the agreed final contract, so no client change is required when placeholder values are replaced with real ones.
- The published API documentation (Swagger/OpenAPI) reflects the new fields, request parameters, and endpoints.
- The endpoints enforce the same authentication and authorization as the rest of the tasks and alerts API.
- The placeholder implementation is isolated so it can be replaced by real logic without a contract change, and is clearly identifiable as temporary.

### Implementation decisions:
- Add the new fields to `TaskInfoModel` (`initiatedBy`, `completeReason`, `relatedEntities`, latest-task info), returning hardcoded placeholder values.
- Stub the new actions (FailoverTestStop failoverTest.summary/failoverTest.success, task `status`/`startedAfterDate`/`sort` params) to accept well-formed requests and return success.
- Field names/types/nullability match the final contract so no client change is needed when the real logic lands.
- Placeholder logic is isolated and clearly marked temporary; Swagger/OpenAPI is regenerated; endpoints enforce the existing Keycloak auth.

### Contract changes:
- GET /api/v2/tasks , /api/v2/tasks/{taskId}: + initiatedBy, completeResult, relatedEntities; response + running/waiting counts.
- New query params: tasks status/startedAfterDate/sort
- Stubbed actions: PUT /api/v2/vpgs/{vpgId}/failover (FailoverTestStop action, failover request model add new field failoverTest)

---

## Story 13 — [ZIC-5768] [MONITORING] [BE] Technical: Remove obsolete legacy fields from the tasks and alerts contract

- Remove the obsolete legacy fields on the tasks and alerts REST contract now superseded by the new monitoring fields

**Blocked by:** [ZIC-5754] (`affectedVpgs` supersedes alert `vpgId`) and [ZIC-5757] (`relatedEntities` supersedes task `vpgId`/`memberAccountId`); clients must have migrated to the new fields before the legacy ones are removed.

The legacy `vpgId` field on alerts and the legacy `vpgId`/`memberAccountId` fields on tasks were kept one version for backward compatibility while clients migrated to `affectedVpgs` and `relatedEntities`. Once that migration window has passed, the obsolete fields need to be dropped from the contract so the API doesn't carry duplicate, unresolved identifiers indefinitely.

### Acceptance Criteria
- The legacy `vpgId` field is no longer present on alerts returned by `alerts` or by alert-by-key lookups, now that `affectedVpgs` provides the same information.
- The legacy `vpgId` and `memberAccountId` fields are no longer present on tasks returned by `tasks` and by task-by-key lookups, now that `relatedEntities` provides the same information.
- Schema components left over solely to support already-removed parameters (e.g. `TopPerPropertyModel`, unused after `topPerProperty` was removed) are removed from the contract.
- No other alert or task field, behavior, filter, or endpoint changes as a result of this cleanup.
- The published API documentation (Swagger/OpenAPI) no longer references the removed fields or schemas.

### Implementation decisions:
- Remove `vpgId` from the alert model (`AlertModel`); superseded by `affectedVpgs` (Story 1).
- Remove `vpgId` and `memberAccountId` from `TaskInfoModel`; superseded by `relatedEntities` (Story 4).
- Remove the now-unused `TopPerPropertyModel` schema left over after `topPerProperty` was removed (Story 3).
- Regenerate Swagger/OpenAPI after the removal.
- This is a breaking contract change; it ships only after the FE/CLI clients have migrated to the superseding fields, so it is sequenced behind Stories 1 and 4 rather than alongside them.

### Contract changes:
Breaking, removes fields superseded by earlier stories:
- GET /api/v2/alerts, alert-by-key lookup — removed: `vpgId` (superseded by `affectedVpgs`).
- GET /api/v2/tasks, GET /api/v2/tasks/{taskId} — removed: `vpgId`, `memberAccountId` (superseded by `relatedEntities`).
- Removed schema: `TopPerPropertyModel`.
