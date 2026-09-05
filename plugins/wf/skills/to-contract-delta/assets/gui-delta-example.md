# GUI delta — worked example

<!-- Referenced from gui-delta-template.md and SKILL.md. Full worked example: a page with tabs, a table, a popover, a modal, and its Shared component declaration. -->

#### Alerts
<details>
<summary>Alerts</summary>

```text
+ route: /alerts
+ @Header
+ data: GET /api/alerts | poll 10s

+ Tabs
  * Active -> /alerts/active
    Badge <- activeCount

    Toolbar
      Search: input
      Refresh: button -> reload

    Table: Alerts
      Severity <- severity
      Name <- name | link -> /alerts/{id}
      Updated <- updatedAt
      Actions <- derived
        Details: icon -> Popover: Alert details
        Delete: icon -> Modal: Delete alert

      sort: Updated desc
      row -> Popover: Alert details

  History -> /alerts/history
    data: GET /api/alerts/history | on open

    Table: History
      Date <- createdAt
      Event <- event
      User <- userName

+ Popover: Alert details
  Severity <- severity
  Message <- message
  Created <- createdAt

+ Modal: Delete alert
  title: Delete alert?
  text: This action cannot be undone.
  Cancel: button -> close
  Delete: button -> DELETE /api/alerts/{id}

Behaviour:
+ Refresh reloads the active tab.
+ Successful delete closes the modal and reloads Alerts.
+ Failed delete keeps the modal open and shows the error.
```

```gherkin
Scenario: Delete alert
  Given an alert is shown in Alerts
  When the user deletes and confirms it
  Then DELETE /api/alerts/{id} is called
  And Alerts reloads
```

</details>

## Shared

```text
Header
  Logo -> /
  Alerts -> /alerts
  Settings -> /settings
```
