"""Terminal color highlighting for matched patterns in log output."""

import re
from typing import Optional

ANSI_COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "": "\033[1mEFAULT_HIGHLIGHT_COLOR = "yellow"


defize(text: str, color:Wrap text in ANSI color codes."""
    code = ANSI_COLORS.get(color, ANSI_COLORS[DEFAULT_HIGHLIGHT_COLOR])
    return f"{code}{text}{ANSI_COLORS['reset']}"


def highlight_pattern(line: str, pattern: str, color: str = DEFAULT_HIGHLIGHT_COLOR) -> str:
    """Highlight all occurrences of pattern in line using the given color."""
    if not pattern:
        return line

    def replacer(match: re.Match) -> str:
        return colorize(match.group(0), color)

    try:
        return re.sub(pattern, replacer, line)
    except re.error:
        # Fall back to literal string highlight if pattern is invalid regex
        escaped = re.escape(pattern)
        return re.sub(escaped, replacer, line)


def highlight_lines(
    lines: list,
    pattern: Optional[str] = None,
    color: str = DEFAULT_HIGHLIGHT_COLOR,
    use_color: bool = True,
) -> list:
    """Apply pattern highlighting to a list of LogLine objects' raw text.

    Returns a list of strings ready for output.
    """
    results = []
    for log_line in lines:
        text = log_line.raw
        if use_color and pattern:
            text = highlight_pattern(text, pattern, color)
        results.append(text)
    return results
