# Endpoints delta — template

Fill this template to document the REST API **delta** a feature introduces. Copy only the parts you need, replace every `<placeholder>`, and delete the rest.

- **More than one endpoint** → keep the three top-level sections: `# Endpoints`, `# Objects`, `# Conventions`.
- **Exactly one endpoint** → keep only the endpoint entry, inline its object schema into the Response block, and delete the `# Objects` and `# Conventions` sections.
- Every field / parameter / header / status table and every JSON schema block lists **only changed** entries — added, modified, or removed — never untouched ones. Each table carries a `Change` column valued `Added`, `Modified`, or `Removed`.
- Keep the `Example` block **only** when the user asked for examples.

---

## Endpoints

### <Resource>

#### <Verb> <operation title> — `<Added | Modified | Removed>`

<details>
<summary>Behaviour Changes</summary>

**Notes** _(optional — omit when there is nothing to record)_

- <Observation about how the system behaves today, a constraint, an open question, or a note the user provided.>

**Behaviour changes**

- <Added | Modified | Removed> <validation / side effect / ordering / default / error condition change>.
</details>

<details>
<summary>Request</summary>

**Request schema**

```http
<VERB> <path>?[<param>=<...>]
```

**<Path | Query> parameters** _(changed only: added/modified/removed)_

| Parameter | Type | Required | Change | Description |
|---|---|---:|---|---|
| `<param>` | `<type>` | `<Yes/No>` | `<Added\|Modified\|Removed>` | <description> |

**Request body** _(changed fields only: added/modified/removed)_

| Field | Type | Required | Change | Constraints | Description |
|---|---|---:|---|---|---|
| `<field>` | `<type>` | `<Yes/No>` | `<Added\|Modified\|Removed>` | `<constraint>` | <description> |

</details>

<details>
<summary>Response</summary>

**Response schema** _(changed properties only: added/modified/removed)_

```json
{
  "type": "object",
  "properties": {
    "<field>": { "type": "<type>" }
  }
}
```

**Response body** _(changed fields only: added/modified/removed)_

| Field | Type | Change | Description |
|---|---|---|---|
| `<field>` | `<type>` | `<Added\|Modified\|Removed>` | <description> |

**Response codes** _(changed only: added/modified/removed)_

| Status | Change | Description |
|---:|---|---|
| `<code>` | `<Added\|Modified\|Removed>` | <description> |

</details>

<!-- Keep the block below ONLY if the user asked for examples. -->
<details>
<summary>Example</summary>

**Request**

```http
<VERB> <full path> HTTP/1.1
Host: <host>
Authorization: ******
```

**Response**

```http
HTTP/1.1 <code>
Content-Type: application/json

{ }
```

</details>

---

## Objects

<!-- Multi-endpoint layout only. Delete this whole section for a single endpoint. -->

### <Resource>

#### <Object> object — `<Added | Modified | Removed>`

<details>
<summary>Fields</summary>

**Changed fields only (added/modified/removed)**

| Field | Type | Nullable | Change | Description |
|---|---|---:|---|---|
| `<field>` | `<type>` | `<Yes/No>` | `<Added\|Modified\|Removed>` | <description> |

</details>

---

## Conventions

<!-- Multi-endpoint layout only. Include ONLY conventions the feature adds, modifies, or removes; delete the section otherwise. -->

### <Convention name>

<details>
<summary><Convention name></summary>

<Describe the added, modified, or removed convention — e.g. a new error code, a changed idempotency rule, a removed common header.>

</details>

---
