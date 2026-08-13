"""Small numeric version primitive for Rhamaa apps."""

from typing import Tuple


def parse_version(value: str) -> Tuple[int, int, int]:
    """Parse MAJOR.MINOR[.PATCH]; normalize two-part versions to patch zero."""
    parts = str(value or "").strip().split(".")
    if len(parts) not in (2, 3) or any(not part.isdigit() for part in parts):
        raise ValueError(f"Invalid app version '{value}'; use MAJOR.MINOR[.PATCH].")
    numbers = tuple(int(part) for part in parts)
    if len(numbers) == 2:
        numbers += (0,)
    return numbers

