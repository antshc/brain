## GUI delta

<!-- One copy per surface (page or route family) touched; delete unused copies. -->

Legend: `+` added · `~` changed · `-` removed · `% old → new` rename (same meaning) · `->` interaction/navigation · `<-` data binding · `*` default item · `@` shared component · `match:` existing implementation anchor.

<!-- Skeleton -->

#### <Page>
<details>
<summary><Page></summary>

```text
+ route: /path
+ @Header

+ data: GET /api/resource | poll 10s

+ Tabs
  * <Tab> -> /path/tab
    data: GET /api/resource | on open

    Toolbar
      Search: input
      Refresh: button -> reload

    Table: <Name>
      <Column> <- <field>
      <Column> <- <field> | link -> /items/{id}
      <Column> <- derived
        <Action>: icon -> <effect>

      sort: <Column> desc
      row -> <effect>

  <Other tab> -> /path/other

+ Modal: <Name>
  title: <visible title>
  text: <visible body>
  Cancel: button -> close
  Confirm: button -> POST /api/resource
```

**Behaviour changes:**

- + <rule>

**Scenarios:**

```gherkin
Scenario: <intent>
  Given <context>
  When <action>
  Then <result>
```

</details>

## Changes to an existing component

Use `match:` when the implementation needs an explicit discovery anchor:

#### Alerts
<details>
<summary>Alerts</summary>

```text
match: /alerts

~ Table: Alerts
  + Owner <- ownerName
  ~ Name <- name -> displayName
  % Severity -> Level <- severity
  - Legacy ID
  ~ sort: Updated desc -> Level desc
```

</details>

`match:` may also identify an existing component when a route is not specific enough:

```text
match: AlertsTable
~ Table: Alerts
  + Owner <- ownerName
```

## Tables

Use one line per column:

```text
<Column label> <- <API field> | <optional behaviour>
```

Examples:

```text
+ Table: Users
  Name <- displayName | link -> /users/{id}
  Status <- status
  Created <- createdAt
  Actions <- derived
    Edit: icon -> Modal: Edit user
    Delete: icon -> Modal: Delete user

  sort: Created desc
  row -> /users/{id}
```

Use `derived` when there is no direct API field.

## Tabs

Tabs do not use special `nav` or `content` syntax. Indent each tab's rendered content under that tab.

```text
+ Tabs
  * Active -> /alerts/active
    Badge <- activeCount

    Table: Alerts
      Name <- name
      Status <- status

  History -> /alerts/history
    Table: History
      Date <- createdAt
      Event <- event
```

## Dialogs and popovers

```text
+ Modal: Delete alert
  title: Delete alert?
  text: This action cannot be undone.
  Cancel: button -> close
  Delete: button -> DELETE /api/alerts/{id}

+ Popover: Alert details
  Severity <- severity
  Message <- message
  Created <- createdAt
```

## Components referenced

Declare reusable components once:

#### Components referenced
<details>
<summary>Components referenced</summary>

```text
Header
  Logo -> /
  Alerts -> /alerts
  Settings -> /settings
```
</details>

Reference them from surfaces:

```text
+ @Header
```

## Behaviour

Use only when the rule spans components or cannot be expressed inline:

```text
**Behaviour changes:**

- + Selecting rows enables Delete.
- + Successful delete closes the modal and reloads the table.
- + Failed delete keeps the modal open and shows the error.
```

## Scenarios

Use Gherkin only for important multi-step flows, in their own fence outside the surface's diff block. Keep scenarios focused on observable behaviour; do not repeat UI structure already described above.

```gherkin
Scenario: Delete alerts
  Given alerts are selected
  When the user deletes and confirms them
  Then the delete requests are sent
  And the Alerts table reloads
```
