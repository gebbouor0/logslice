import pytest
from logslice.parser import LogLine
from logslice.paginator import Page, paginate, iter_pages, format_page


def make_line(text: str, n: int = 1) -> LogLine:
    return LogLine(raw=text, timestamp=None, line_number=n)


def make_lines(count: int) -> list:
    return [make_line(f"line {i}", i) for i in range(1, count + 1)]


def test_paginate_basic():
    lines = make_lines(10)
    page = paginate(lines, page_size=3, page_number=1)
    assert page.number == 1
    assert len(page) == 3
    assert page.lines[0].raw == "line 1"


def test_paginate_last_page_partial():
    lines = make_lines(10)
    page = paginate(lines, page_size=3, page_number=4)
    assert len(page) == 1
    assert page.lines[0].raw == "line 10"


def test_paginate_total_pages():
    lines = make_lines(10)
    page = paginate(lines, page_size=3)
    assert page.total_pages == 4


def test_paginate_is_first_and_last():
    lines = make_lines(5)
    first = paginate(lines, page_size=5, page_number=1)
    assert first.is_first
    assert first.is_last


def test_paginate_clamps_page_number():
    lines = make_lines(5)
    page = paginate(lines, page_size=2, page_number=999)
    assert page.number == 3
    assert page.is_last


def test_paginate_invalid_page_size():
    with pytest.raises(ValueError):
        paginate(make_lines(5), page_size=0)


def test_paginate_invalid_page_number():
    with pytest.raises(ValueError):
        paginate(make_lines(5), page_size=2, page_number=0)


def test_iter_pages_count():
    lines = make_lines(10)
    pages = list(iter_pages(lines, page_size=3))
    assert len(pages) == 4


def test_iter_pages_all_lines_covered():
    lines = make_lines(7)
    all_lines = [l for page in iter_pages(lines, page_size=3) for l in page.lines]
    assert len(all_lines) == 7


def test_iter_pages_invalid_size():
    with pytest.raises(ValueError):
        list(iter_pages(make_lines(5), page_size=-1))


def test_format_page_contains_header():
    lines = make_lines(3)
    page = paginate(lines, page_size=3, page_number=1)
    output = format_page(page)
    assert "Page 1/1" in output
    assert "line 1" in output


def test_format_page_empty_lines():
    page = Page(number=1, lines=[], total_pages=1)
    output = format_page(page)
    assert "Page 1/1" in output
