# PartsBox API Usage

## Access Method

PartsBox is accessed via **Python scripts** (not an MCP server). All scripts are
in `.claude/skills/partsbox-api/scripts/` and require `PARTSBOX_API_KEY` set in
environment or `.env` file.

See the skill at `.claude/skills/partsbox-api/SKILL.md` for the complete script
reference and usage guide.

## General Rules

- Do not search the PartsBox website unless explicitly asked to.
- When calling scripts that support `--limit`, stick to small batches of no
  greater than 200 at a time to limit memory usage and increase performance.
- When using `--query` (JMESPath):
  - Always supply a query that matches just the information required.
  - Be specific about child elements to avoid fetching large nested data.
- If you know the data set is large, use `--limit` and `--offset` for pagination.
- Always ask for permission before performing any action that is not read-only.

## Querying

- When searching for parts, always search at least these fields unless you know
  the data exists in a specific field:
  - part/name
  - part/tags
  - part/description
