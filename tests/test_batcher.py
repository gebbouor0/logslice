import pytest
from logslice.parser import LogLine
from logslice.batcher import Batch, batch_lines, iter_batches, format_batch


def make_line(n: int, msg: str = "log") -> LogLine:
    return LogLine(raw=f"{msg} {n}", timestamp=None, message=f"{msg} {n}", line_number=n)


def make_lines(count: int) -> list:
    return [make_line(i) for i in range(count)]


def test_batch_lines_basic():
    lines = make_lines(10)
    batches = batch_lines(lines, 3)
    assert len(batches) == 4
    assert len(batches[0]) == 3
    assert len(batches[-1]) == 1


def test_batch_lines_exact_division():
    lines = make_lines(9)
    batches = batch_lines(lines, 3)
    assert len(batches) == 3
    assert all(len(b) == 3 for b in batches)


def test_batch_lines_indices():
    lines = make_lines(6)
    batches = batch_lines(lines, 2)
    assert [b.index for b in batches] == [0, 1, 2]


def test_batch_lines_empty():
    assert batch_lines([], 5) == []


def test_batch_lines_invalid_size():
    with pytest.raises(ValueError):
        batch_lines(make_lines(5), 0)


def test_batch_first_last():
    lines = make_lines(5)
    batches = batch_lines(lines, 3)
    assert batches[0].first == lines[0]
    assert batches[0].last == lines[2]


def test_batch_first_last_empty():
    b = Batch(index=0, lines=[])
    assert b.first is None
    assert b.last is None


def test_iter_batches():
    lines = make_lines(7)
    result = list(iter_batches(lines, 3))
    assert len(result) == 3


def test_format_batch_header():
    lines = make_lines(2)
    batch = Batch(index=0, lines=lines)
    output = format_batch(batch)
    assert "Batch 0" in output
    assert "2 lines" in output


def test_format_batch_contains_raw():
    lines = [make_line(1, "hello"), make_line(2, "world")]
    batch = Batch(index=1, lines=lines)
    output = format_batch(batch)
    assert "hello 1" in output
    assert "world 2" in output
