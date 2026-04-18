import pytest
from logslice.parser import LogLine
from logslice.contexter import ContextBlock, extract_context, format_context_blocks


def make_line(n: int, msg: str) -> LogLine:
    return LogLine(line_number=n, raw=msg, message=msg, timestamp=None)


LINES = [make_line(i, f"msg {i}") for i in range(1, 9)]


def is_match(line: LogLine) -> bool:
    return line.line_number in (3, 7)


def test_extract_context_returns_blocks():
    blocks = extract_context(LINES, is_match, before=1, after=1)
    assert len(blocks) == 2


def test_extract_context_before_lines():
    blocks = extract_context(LINES, is_match, before=2, after=0)
    block = blocks[0]  # match at line 3
    assert len(block.before) == 2
    assert block.before[0].line_number == 1
    assert block.before[1].line_number == 2


def test_extract_context_after_lines():
    blocks = extract_context(LINES, is_match, before=0, after=2)
    block = blocks[0]
    assert len(block.after) == 2
    assert block.after[0].line_number == 4


def test_extract_context_clamps_at_boundaries():
    blocks = extract_context(LINES, is_match, before=10, after=10)
    first = blocks[0]
    assert first.before[0].line_number == 1
    last = blocks[1]
    assert last.after[-1].line_number == 8


def test_all_lines_no_duplicates():
    blocks = extract_context(LINES, is_match, before=2, after=2)
    for block in blocks:
        nums = [l.line_number for l in block.all_lines()]
        assert len(nums) == len(set(nums))


def test_all_lines_sorted():
    blocks = extract_context(LINES, is_match, before=2, after=2)
    for block in blocks:
        nums = [l.line_number for l in block.all_lines()]
        assert nums == sorted(nums)


def test_extract_context_no_match():
    blocks = extract_context(LINES, lambda l: False, before=2, after=2)
    assert blocks == []


def test_extract_context_invalid_before():
    with pytest.raises(ValueError):
        extract_context(LINES, is_match, before=-1, after=0)


def test_extract_context_invalid_after():
    with pytest.raises(ValueError):
        extract_context(LINES, is_match, before=0, after=-1)


def test_format_context_blocks_marker():
    blocks = extract_context(LINES, lambda l: l.line_number == 4, before=1, after=1)
    lines = format_context_blocks(blocks)
    match_line = [l for l in lines if ">> " in l]
    assert len(match_line) == 1
    assert "[4]" in match_line[0]


def test_format_context_blocks_separator():
    blocks = extract_context(LINES, is_match, before=1, after=1)
    lines = format_context_blocks(blocks, separator="===")
    assert "===" in lines


def test_format_context_blocks_empty():
    assert format_context_blocks([]) == []
