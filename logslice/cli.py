"""CLI entry point for logslice."""

import sys
from datetime import datetime
from typing import Optional

import click

from logslice.filter import filter_lines, format_output
from logslice.parser import parse_lines

DATETIME_FORMATS = ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]


def parse_dt(value: Optional[str]) -> Optional[datetime]:
    if value is None:
        return None
    for fmt in DATETIME_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise click.BadParameter(f"Unrecognized datetime format: {value!r}")


@click.command()
@click.argument("logfile", type=click.Path(exists=True, readable=True))
@click.option("--start", default=None, help="Start datetime (inclusive), e.g. 2024-01-01T00:00:00")
@click.option("--end", default=None, help="End datetime (inclusive), e.g. 2024-01-01T23:59:59")
@click.option("--pattern", "-p", default=None, help="Regex pattern to match against log lines")
@click.option("--line-numbers", "-n", is_flag=True, help="Show original line numbers")
def main(logfile, start, end, pattern, line_numbers):
    """Extract and filter log segments by time range and pattern."""
    start_dt = parse_dt(start)
    end_dt = parse_dt(end)

    with open(logfile, "r", errors="replace") as f:
        lines = parse_lines(f)

    filtered = filter_lines(lines, start=start_dt, end=end_dt, pattern=pattern)

    if not filtered:
        click.echo("No matching log lines found.", err=True)
        sys.exit(1)

    click.echo(format_output(filtered, show_line_numbers=line_numbers))


if __name__ == "__main__":
    main()
