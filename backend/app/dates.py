"""Working-day and calendar helpers. Demo clock default: 2026-09-28."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Iterable

DEFAULT_CLOCK = date(2026, 9, 28)
HOLIDAYS = {
    date(2026, 10, 1),
    date(2026, 10, 19),
    date(2026, 12, 25),
    date(2026, 12, 26),
    date(2027, 1, 1),
}


def parse_date(value: str | date | None, default: date | None = None) -> date:
    if value is None:
        return default or DEFAULT_CLOCK
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    return date.fromisoformat(str(value)[:10])


def is_working_day(d: date, holidays: Iterable[date] | None = None) -> bool:
    hols = set(holidays) if holidays is not None else HOLIDAYS
    return d.weekday() < 5 and d not in hols


def next_working_day(d: date, holidays: Iterable[date] | None = None) -> date:
    cursor = d
    while not is_working_day(cursor, holidays):
        cursor += timedelta(days=1)
    return cursor


def add_working_days(start: date, n: int, holidays: Iterable[date] | None = None) -> date:
    """Return the date n working days after start (start itself is not counted)."""
    if n <= 0:
        return start
    cursor = start
    remaining = n
    while remaining:
        cursor += timedelta(days=1)
        if is_working_day(cursor, holidays):
            remaining -= 1
    return cursor


def working_days_between(start: date, end: date, holidays: Iterable[date] | None = None) -> int:
    """Count working days strictly after start, up to and including end."""
    if end <= start:
        return 0
    count = 0
    cursor = start
    while cursor < end:
        cursor += timedelta(days=1)
        if is_working_day(cursor, holidays):
            count += 1
    return count


def effective_created_working_day(created: date, holidays: Iterable[date] | None = None) -> date:
    return next_working_day(created, holidays)


def iso(d: date) -> str:
    return d.isoformat()


def days_between(start: date, end: date) -> int:
    return (end - start).days
