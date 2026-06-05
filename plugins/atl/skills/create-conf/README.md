# conf-cpage Skill

Create a Confluence page from a local Markdown file using the Atlassian CLI (`acli`).

## Prerequisites

- [`acli`](https://developer.atlassian.com/cloud/acli/) installed and configured
- Environment variables set (via `setup-atl` or manually in `~/.profile`):
  ```bash
  export ACLI_EMAIL="you@example.com"
  export ACLI_API_TOKEN="ATATT3..."
  export ACLI_SITE="yourorg.atlassian.net"
  ```
- Python 3 installed

## Installation

**1. Install the Python dependency:**
```bash
pip install -r /path/to/conf-cpage/scripts/requirements.txt
```

Or directly:
```bash
pip install markdown
```

**2. Authenticate with Confluence** (if not already done):
```bash
echo "$ACLI_API_TOKEN" | acli confluence auth login --token --email "$ACLI_EMAIL" --site "$ACLI_SITE"
```

## Usage

Invoke the skill from GitHub Copilot CLI:
```
conf-cpage <md_file_path> <parent_page_url>
```

### Arguments

| Argument | Description |
|---|---|
| `<md_file_path>` | Path to the local Markdown file to publish |
| `<parent_page_url>` | Full URL of the Confluence page under which to create the new page |

### Example
```
conf-cpage ./docs/release-notes.md https://zerto.atlassian.net/wiki/spaces/~63f4d6193ec8aa51d3d20548/pages/1888616534/CR
```

## Markdown file requirements

- The page **title** is extracted from the first `# H1` heading in the file — this heading is required.
- Supported Markdown features: headings, bold/italic, bullet/numbered lists, tables, fenced code blocks, inline code, links.

### Example Markdown file
```markdown
# My Release Notes

## Summary

This release includes the following changes:

- Feature A
- Bug fix B

## Details

| Component | Version |
|-----------|---------|
| API       | 2.3.0   |
| UI        | 1.8.0   |

\```bash
echo "deployed!"
\```
```

## How it works

1. Reads the `.md` file and extracts the `# H1` as the page title.
2. Converts Markdown → HTML using Python's `markdown` library (`tables` + `fenced_code` extensions).
3. Parses the parent page URL to extract the space key and parent page ID.
4. POSTs to the Confluence REST API (`/wiki/rest/api/content`) using credentials from the environment.
5. Prints the URL of the newly created page on success.

## Troubleshooting

**Authentication error**  
Re-run the auth step or invoke the `conf-auth` skill:
```
conf-auth
```
Then retry.

**No H1 heading found**  
Add a `# Title` line at the top of your Markdown file.

**File not found**  
Check the path passed as `<md_file_path>`. Use an absolute path if in doubt.
