# logslice

> CLI tool to extract and filter log segments by time range and pattern

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/yourname/logslice.git && cd logslice && pip install .
```

---

## Usage

```bash
logslice [OPTIONS] <logfile>
```

### Examples

Extract log entries between two timestamps:

```bash
logslice --start "2024-01-15 08:00:00" --end "2024-01-15 09:00:00" app.log
```

Filter by pattern within a time range:

```bash
logslice --start "2024-01-15 08:00:00" --end "2024-01-15 09:00:00" --pattern "ERROR" app.log
```

Write output to a file:

```bash
logslice --start "2024-01-15 08:00:00" --pattern "WARN" app.log -o output.log
```

### Options

| Flag | Description |
|------|-------------|
| `--start` | Start of time range (inclusive) |
| `--end` | End of time range (inclusive) |
| `--pattern` | Regex or string pattern to filter lines |
| `-o, --output` | Write results to a file instead of stdout |
| `--format` | Timestamp format (default: `%Y-%m-%d %H:%M:%S`) |

---

## Requirements

- Python 3.8+

---

## License

This project is licensed under the [MIT License](LICENSE).