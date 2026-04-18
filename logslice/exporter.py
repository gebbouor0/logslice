"""Export filtered log lines to different output formats."""

import json
import csv
import io
from dataclasses import asdict
from typing import List, Literal

from logslice.parser import LogLine

OutputFormat = Literal["text", "json", "csv"]


def export_text(lines: List[LogLine]) -> str:
    """Return plain text, one raw line per entry."""
    return "\n".join(ll.raw for ll in lines)


def export_json(lines: List[LogLine]) -> str:
    """Serialize log lines to a JSON array."""
    records = []
    for ll in lines:
        rec = {
            "line_number": ll.line_number,
            "timestamp": ll.timestamp.isoformat() if ll.timestamp else None,
            "level": ll.level,
            "message": ll.message,
            "raw": ll.raw,
        }
        records.append(rec)
    return json.dumps(records, indent=2)


def export_csv(lines: List[LogLine]) -> str:
    """Serialize log lines to CSV with a header row."""
    buf = io.StringIO()
    fieldnames = ["line_number", "timestamp", "level", "message", "raw"]
    writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for ll in lines:
        writer.writerow({
            "line_number": ll.line_number,
            "timestamp": ll.timestamp.isoformat() if ll.timestamp else "",
            "level": ll.level or "",
            "message": ll.message or "",
            "raw": ll.raw,
        })
    return buf.getvalue().rstrip("\n")


def export_lines(lines: List[LogLine], fmt: OutputFormat = "text") -> str:
    """Dispatch to the correct exporter based on *fmt*."""
    if fmt == "json":
        return export_json(lines)
    if fmt == "csv":
        return export_csv(lines)
    return export_text(lines)
