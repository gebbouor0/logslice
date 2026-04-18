# logslice

CLI tool to extract and filter log segments by time range and pattern.

## Features

- Parse timestamps from common log formats
- Filter lines by time range and regex pattern
- Highlight matching patterns with color
- Compute stats (counts, levels, time range)
- Export to text, JSON, or CSV
- Deduplicate consecutive repeated lines
- Chunk logs by size or time interval
- Sample logs (every-nth or random)
- Merge multiple log streams in timestamp order
- Annotate lines with tags and notes via rules
- Paginate output
- Diff two log streams
- Truncate long messages
- Group lines by level or time bucket
- Sort by timestamp, message, or line number
- Count occurrences by pattern or field
- Tag lines by regex rules
- Split logs into named segments
- Score lines by keyword relevance
- Redact sensitive patterns
- Classify lines into categories
- Normalize messages (whitespace, case)
- Extract context lines around matches
- Pivot lines into a table by field
- **Window lines into tumbling or sliding time windows**

## Usage

```bash
logslice --start "2024-01-01T10:00:00" --end "2024-01-01T12:00:00" --pattern ERROR app.log
```

## Options

| Flag | Description |
|------|-------------|
| `--start` | Start datetime (ISO 8601) |
| `--end` | End datetime (ISO 8601) |
| `--pattern` | Regex pattern to filter/highlight |
| `--format` | Output format: text, json, csv |
| `--stats` | Print summary statistics |
| `--no-color` | Disable color output |

## Development

```bash
pip install -e .[dev]
pytest
```
