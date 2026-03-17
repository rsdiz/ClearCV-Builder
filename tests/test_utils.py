"""Unit tests for low-level helpers."""

from resume_builder.pdf import sanitise
from resume_builder.utils import clean_text, is_valid_email, is_valid_year, normalise_url, parse_skill_category


def test_parse_skill_category_strips_values_and_skips_empty_items():
    assert parse_skill_category(" Python, SQL , ,Docker ") == ["Python", "SQL", "Docker"]


def test_is_valid_email_accepts_basic_email_and_rejects_invalid_value():
    assert is_valid_email("user@example.com") is True
    assert is_valid_email("invalid-email") is False


def test_normalise_url_preserves_scheme_and_adds_https_when_missing():
    assert normalise_url("https://example.com/profile") == "https://example.com/profile"
    assert normalise_url("github.com/example") == "https://github.com/example"


def test_is_valid_year_accepts_blank_or_four_digits_only():
    assert is_valid_year("") is True
    assert is_valid_year("2024") is True
    assert is_valid_year("24") is False


def test_clean_text_trims_whitespace_and_collapses_extra_blank_lines():
    raw = "  First line  \n\n\nSecond line  \n"

    assert clean_text(raw) == "First line\n\nSecond line"


def test_sanitise_replaces_common_unicode_outside_latin_one():
    assert sanitise("Senior Engineer — Python • APIs") == "Senior Engineer -- Python * APIs"
