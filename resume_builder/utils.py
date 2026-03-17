"""Low-level formatting and validation helpers."""

import re


def parse_skill_category(raw: str) -> list[str]:
    """Parse a comma-separated skills string into a clean list."""
    return [skill.strip() for skill in raw.split(",") if skill.strip()]


def is_valid_email(email: str) -> bool:
    """Basic email validation suitable for UI feedback."""
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()))


def normalise_url(url: str) -> str:
    """Normalise URLs so preview/export data is consistent."""
    cleaned = url.strip()
    if not cleaned:
        return ""
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", cleaned):
        return cleaned
    return f"https://{cleaned}"


def is_valid_year(year: str) -> bool:
    """Accept empty year or a four-digit year."""
    return not year.strip() or bool(re.fullmatch(r"\d{4}", year.strip()))


def clean_text(value: str) -> str:
    """Trim surrounding whitespace and collapse excess blank lines."""
    lines = [line.rstrip() for line in value.strip().splitlines()]
    compact = []
    previous_blank = False
    for line in lines:
        is_blank = not line.strip()
        if is_blank and previous_blank:
            continue
        compact.append(line)
        previous_blank = is_blank
    return "\n".join(compact).strip()
