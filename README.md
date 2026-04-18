# logslice

CLI tool to extract and filter log segments by time range and pattern.

## Features

- **Parse** log lines with timestamps and messages
- **Filter** by time range (start/end) and pattern matching
- **Highlight** patterns with color in terminal output
- **Stats** — count lines, levels, and timestamp ranges
- **Export** to text, JSON, or CSV
- **Deduplicate** consecutive repeated lines
- **Chunk** logs by size or time interval
- **Sample** logs every nth line or randomly
- **Merge** multiple log streams in chronological order
- **Annotate** lines with tags based on rules
- **Paginate** output for large log files
- **Diff** two log streams to find added/removed lines
- **Truncate** long log messages
- **Group** lines by level, hour, or custom field

## Usage

```bash
logslice --start "2024-01-01T10:00" --end "2024-01-01T11:00" --pattern ERROR app.log
```

## Modules

| Module | Description |
|---|---|
| `parser` | Parse raw log lines into structured `LogLine` objects |
| `filter` | Filter and format log lines by time and pattern |
| `highlighter` | Colorize pattern matches in output |
| `stats` | Compute summary statistics over log lines |
| `reporter` | Build structured reports from stats |
| `exporter` | Export lines to text, JSON, CSV |
| `deduplicator` | Collapse consecutive duplicate lines |
| `chunker` | Split logs into chunks by size or time |
| `sampler` | Sample lines by interval or randomly |
| `merger` | Merge multiple streams chronologically |
| `annotator` | Tag lines with labels based on regex rules |
| `paginator` | Paginate lines into pages |
| `differ` | Diff two log streams |
| `truncator` | Truncate long messages |
| `grouper` | Group lines by level, hour, or custom key |
