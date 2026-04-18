"""CLI entry point for logslice."""

import sys
import argparse
from datetime import datetime
from typing import Optional

from logslice.parser import parse_lines
from logslice.filter import filter_lines
from logslice.highlighter import highlight_lines
from logslice.exporter import export_lines, OutputFormat


def parse_dt(value: str) -> datetime:
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(f"Cannot parse datetime: {value!r}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="logslice",
        description="Extract and filter log segments by time range and pattern.",
    )
    parser.add_argument("file", nargs="?", help="Log file (default: stdin)")
    parser.add_argument("--start", type=parse_dt, metavar="DATETIME", help="Start datetime filter")
    parser.add_argument("--end", type=parse_dt, metavar="DATETIME", help="End datetime filter")
    parser.add_argument("--pattern", metavar="REGEX", help="Regex pattern to filter lines")
    parser.add_argument("--highlight", metavar="REGEX", help="Regex pattern to highlight in output")
    parser.add_argument(
        "--format",
        dest="fmt",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument("--color", default="red", help="Highlight color (default: red)")

    args = parser.parse_args(argv)

    if args.file:
        with open(args.file) as fh:
            raw_lines = fh.readlines()
    else:
        raw_lines = sys.stdin.readlines()

    log_lines = parse_lines(raw_lines)
    filtered = filter_lines(log_lines, start=args.start, end=args.end, pattern=args.pattern)

    if args.highlight and args.fmt == "text":
        filtered = highlight_lines(filtered, args.highlight, color=args.color)

    output = export_lines(filtered, fmt=args.fmt)
    if output:
        print(output)


if __name__ == "__main__":
    main()
