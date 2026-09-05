## GUI delta

<!-- One copy per surface (page or route family) touched; delete unused copies. -->

Legend: `+` added · `~` changed · `-` removed · `% old → new` rename (same meaning) · `->` interaction/navigation · `<-` data binding · `*` default item · `@` shared component · `match:` existing implementation anchor.

#### {{surfaceHeader| e.g. a new page name, or an existing route/component name/visible label when modifying one}}
<details>
<summary>{{surfaceHeader}}</summary>

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
      <Column label> <- <API field> | <optional behaviour>
      <Column> <- <field>
      <Column> <- <field> | link -> /items/{id}
      <Column> <- derived
        <Action>: icon -> <effect>
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

<!-- Modifying an existing component instead of adding one — anchor with `match:` on a route: -->

```text
match: /alerts

~ Table: Alerts
  + Owner <- ownerName
  ~ Name <- name -> displayName
  % Severity -> Level <- severity
  - Legacy ID
  ~ sort: Updated desc -> Level desc
```

<!-- `match:` may also identify the component directly when a route is not specific enough: -->

```text
match: AlertsTable
~ Table: Alerts
  + Owner <- ownerName
```

<!-- Tabs do not use special `nav` or `content` syntax. Indent each tab's rendered content under that tab. -->

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

<!-- Modal -->

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

**Behaviour changes:**

- `{{changeType| One of (+|-|~)}}` {{change| one line}}.

**Scenarios:**

```gherkin
Scenario: {{intent}}
  Given {{context}}
  When {{action}}
  Then {{result}}
```

</details>

#### Components referenced
<!-- Declare reusable components once. Reference them from surfaces: @Header -->

<details>
<summary>Components referenced</summary>
```text
Header
  Logo -> /
  Alerts -> /alerts
  Settings -> /settings
```
</details>
