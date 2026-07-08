---
name: to-requirements-table
description: Convert requirements from a requirements.md file (or selection) into a formatted HTML requirements table and save to an HTML file. Use whenever a user wants to export, format, or save requirements as HTML, generate a requirements report, or convert spec sections to an HTML table. Trigger on phrases like "format requirements to html", "export requirements", "save requirements as html", "create html table from spec".
---

Convert **ADDED requirements** from a requirements.md file into a styled HTML requirements table and save it to disk.

---

## Input

The skill accepts one of:
- The user's **active selection** from a requirements.md file
- A **full requirements.md file path** provided by the user
- The **currently open requirements.md file** in the editor

---

## Parsing Rules

Each requirement block in the requirements.md file follows this Markdown structure:

```
## <Capability title>

> **Priority**: <Priority> | **Risk**: <Risk>

### Stakeholder Requirement
<Stakeholder Requirement>

### Functional Requirements

- <criterion 1>
- <criterion 2>
...
```

Extract the following fields per requirement:

| Field | Source |
|---|---|
| **Name** | The `##` heading text — preserve exactly as written |
| **Priority** | Value after `**Priority**:` in the blockquote |
| **Risk** | Value after `**Risk**:` in the blockquote |
| **Stakeholder Requirement** | The paragraph under `### Stakeholder Requirement` — preserve exactly as written |
| **Functional Requirements** | The list items under `### Functional Requirements` |


> **Critical**: The requirement name and stakeholder requirement text must be copied **verbatim** — do not rephrase, summarize, or alter wording.
> **Critical**: The Functional Requirements must NOT be copied.

---

## Output Format

Generate a **single `<table>`** element. Each requirement produces **two `<tbody>` rows**:

1. **Header row** — ID (left empty), Requirement name, Priority, Risk
2. **Detail row** — `colspan="4"` cell containing the stakeholder requirement paragraph followed by the functional requirements as a `<ul>` list

```html
<table>
  <thead>
    <tr>
      <th><strong>ID</strong></th>
      <th><strong>Requirement</strong></th>
      <th><strong>Priority</strong></th>
      <th><strong>Risk assessment</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td></td>
      <td>Requirement name</td>
      <td>Priority</td>
      <td>Risk</td>
    </tr>
    <tr>
      <td colspan="4">
        <p>Stakeholder requirement paragraph.</p>
        <ul>
          <li>Functional requirement 1</li>
          <li>Functional requirement 2</li>
        </ul>
      </td>
    </tr>
    <!-- repeat for each requirement -->
  </tbody>
</table>
```

---

## HTML File Structure

Wrap the table in a complete HTML document:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Requirements</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; color: #333; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ccc; padding: 0.6rem 0.8rem; text-align: left; vertical-align: top; }
    th { background-color: #f0f1f2; font-weight: bold; }
    tr:nth-child(2n+1) { background-color: #f0f1f2; }
    td[colspan] p { margin: 0 0 0.5rem 0; }
    td[colspan] ul { margin: 0; padding-left: 1.5rem; }
    td[colspan] li { margin-bottom: 0.25rem; }
  </style>
</head>
<body>
  <h1>Requirements</h1>
  <!-- table goes here -->
</body>
</html>
```

---

## Output File Location

Save the HTML file alongside the source requirements.md file:
- If source is `path/to/requirements.md` → save as `path/to/requirements.html`
- If the user specifies a different output path, use that instead.

---

## Step-by-Step Workflow

1. **Locate the input**: Read the requirements.md file (or use active selection).
2. **Identify the ADDED section**: Find requirements under the `## ADDED Requirements` heading. Skip `## MODIFIED` and `## REMOVED` sections unless the user explicitly asks to include them.
3. **Parse each requirement**: Extract Name, Priority, Risk, Stakeholder Requirement, and Functional Requirements per the parsing rules above.
4. **Generate HTML**: Build the full HTML document using the output format above. Requirement text must be copied verbatim.
5. **Save file**: Write the HTML to `requirements.html` next to the requirements.md, or to the user-specified path. Use the `create_file` tool (if the file does not exist) or `replace_string_in_file`/`multi_replace_string_in_file` (if updating).
6. **Confirm**: Report the saved file path to the user.

---

## Edge Cases

- If a requirement has no Functional Requirements section, omit the `<ul>` and include only the `<p>` stakeholder requirement.
- If Priority or Risk is absent, leave the cell empty.
- Inline Markdown (`` `code` ``, `**bold**`) may be preserved as HTML (`<code>`, `<strong>`) or stripped — prefer preserving `<code>` spans.
- The ID column is always left empty (sequential numbering is not assigned by this skill).