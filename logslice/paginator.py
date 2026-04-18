from dataclasses import dataclass, field
from typing import List, Optional
from logslice.parser import LogLine


@dataclass
class Page:
    number: int
    lines: List[LogLine]
    total_pages: int

    def __len__(self) -> int:
        return len(self.lines)

    @property
    def is_last(self) -> bool:
        return self.number >= self.total_pages

    @property
    def is_first(self) -> bool:
        return self.number == 1


def paginate(lines: List[LogLine], page_size: int, page_number: int = 1) -> Page:
    if page_size < 1:
        raise ValueError(f"page_size must be >= 1, got {page_size}")
    if page_number < 1:
        raise ValueError(f"page_number must be >= 1, got {page_number}")

    total_pages = max(1, (len(lines) + page_size - 1) // page_size)
    page_number = min(page_number, total_pages)

    start = (page_number - 1) * page_size
    end = start + page_size
    return Page(number=page_number, lines=lines[start:end], total_pages=total_pages)


def iter_pages(lines: List[LogLine], page_size: int):
    """Yield all pages for a list of lines."""
    if page_size < 1:
        raise ValueError(f"page_size must be >= 1, got {page_size}")
    total_pages = max(1, (len(lines) + page_size - 1) // page_size)
    for i in range(1, total_pages + 1):
        yield paginate(lines, page_size, i)


def format_page(page: Page) -> str:
    header = f"--- Page {page.number}/{page.total_pages} ---"
    body = "\n".join(line.raw for line in page.lines)
    return f"{header}\n{body}" if body else header
