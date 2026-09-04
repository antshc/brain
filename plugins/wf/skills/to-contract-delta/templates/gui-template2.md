## GUI delta

<!-- Simplified diff-first GUI contract. Describe only changed UI. Use indentation for ownership instead of component-specific row grammars. -->

## Convention

```text
+ added
~ changed
- removed

-> interaction / navigation
<- data binding
*  default item
@  shared component
```

Rules:

- A surface is a full page or route family.
- Describe only changed UI. Do not repeat untouched components.
- Indentation defines ownership and scope.
- Use `Component: Name` for named components; omit `: Name` when the label is enough.
- Use `key: value` for simple properties.
- Use `->` for navigation, actions, and opening another component.
- Use `<-` for API/data binding.
- Use `*` for the default tab/item.
- Use `@Name` to reference a shared component declared once under `## Shared`.
- Put `data:` beside the component that consumes it; do not hoist all data calls to page level.
- Avoid qualified names such as `Table.Column`, `tabs.nav`, `tabs.content`, `table.hd`, `table.col`, or `table.sort`.
- Add visible text explicitly only when it differs from the component/item name or when the text itself is important to the contract.
- Use `Behaviour:` only for rules that cannot be expressed naturally on the owning component.
- Use `Scenario:` only for non-trivial multi-step flows.

## Skeleton

```text
## <Page>

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

Behaviour:
+ <rule>

Scenario: <intent>
<action> -> <effect> -> <effect>
```

## Changes to an existing component

```text
~ Table: Alerts
  + Owner <- ownerName
  ~ Name <- name -> displayName
  - Legacy ID
  ~ sort: Updated desc -> Severity desc
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

## Shared

Declare reusable components once:

```text
## Shared

Header
  Logo -> /
  Alerts -> /alerts
  Settings -> /settings
```

Reference them from surfaces:

```text
+ @Header
```

## Behaviour

Use only when the rule spans components or cannot be expressed inline:

```text
Behaviour:
+ Selecting rows enables Delete.
+ Successful delete closes the modal and reloads the table.
+ Failed delete keeps the modal open and shows the error.
```

## Scenarios

Use only for important multi-step flows:

```text
Scenario: Delete alerts
select rows -> Delete -> confirmation -> DELETE requests -> reload table
```

## Example

```text
## Alerts

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

Scenario: Delete alert
row.Actions.Delete -> Modal: Delete alert -> Delete -> DELETE /api/alerts/{id} -> reload
```

## Shared

```text
Header
  Logo -> /
  Alerts -> /alerts
  Settings -> /settings
```

**Done when:** every touched surface contains only changed UI; nesting makes ownership clear; shared components are declared once; no component-specific grammar is introduced when indentation plus `key: value`, `->`, or `<-` is sufficient.