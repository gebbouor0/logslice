"""Tests for logslice.exporter."""

import json
import csv
import io
from datetime import datetime

import pytest

from logslice.parser import LogLine
from logslice.exporter import export_text, export_json, export_csv, export_lines


TS = datetime(2024, 1, 15, 10, 0, 0)


def make_line(n=1, ts=TS, level="INFO", message="hello", raw=None):
    raw = raw or f"{ts.isoformat()} {level} {message}"
    return LogLine(line_number=n, timestamp=ts, level=level, message=message, raw=raw)


def test_export_text_basic():
    lines = [make_line(1, raw="line one"), make_line(2, raw="line two")]
    result = export_text(lines)
    assert result == "line one\nline two"


def test_export_text_empty():
    assert export_text([]) == ""


def test_export_json_structure():
    ll = make_line(3)
    result = json.loads(export_json([ll]))
    assert len(result) == 1
    rec = result[0]
    assert rec["line_number"] == 3
    assert rec["level"] == "INFO"
    assert rec["message"] == "hello"
    assert rec["timestamp"] == TS.isoformat()


def test_export_json_null_timestamp():
    ll = make_line(ts=None)
    result = json.loads(export_json([ll]))
    assert result[0]["timestamp"] is None


def test_export_csv_has_header():
    ll = make_line(1)
    result = export_csv([ll])
    first_line = result.splitlines()[0]
    assert "line_number" in first_line
    assert "timestamp" in first_line
    assert "level" in first_line


def test_export_csv_row_values():
    ll = make_line(7, level="ERROR", message="boom")
    result = export_csv([ll])
    reader = csv.DictReader(io.StringIO(result))
    rows = list(reader)
    assert len(rows) == 1
    assert rows[0]["line_number"] == "7"
    assert rows[0]["level"] == "ERROR"
    assert rows[0]["message"] == "boom"


def test_export_csv_no_timestamp():
    ll = make_line(ts=None)
    result = export_csv([ll])
    reader = csv.DictReader(io.StringIO(result))
    rows = list(reader)
    assert rows[0]["timestamp"] == ""


def test_export_lines_dispatches_json():
    ll = make_line(1)
    result = export_lines([ll], fmt="json")
    assert result.startswith("[")


def test_export_lines_dispatches_csv():
    ll = make_line(1)
    result = export_lines([ll], fmt="csv")
    assert "line_number" in result


def test_export_lines_default_text():
    ll = make_line(1, raw="raw text")
    assert export_lines([ll]) == "raw text"
