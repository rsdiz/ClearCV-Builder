"""Unit tests for resume validation and coaching checks."""

import resume_builder.validation as validation
from tests.helpers import SessionState


def test_required_fields_filled_depends_on_name_and_email(monkeypatch):
    session_state = SessionState(full_name="Jane Doe", email="jane@example.com")
    monkeypatch.setattr(validation.st, "session_state", session_state)

    assert validation.required_fields_filled() is True

    session_state.email = " "
    assert validation.required_fields_filled() is False


def test_run_career_coach_checks_flags_missing_fields_and_short_summary(monkeypatch):
    session_state = SessionState(
        full_name="",
        email="",
        phone="",
        location="",
        professional_title="",
        summary="Short summary",
        experiences=[],
        educations=[],
        linkedin="",
        skill_categories={},
    )
    monkeypatch.setattr(validation.st, "session_state", session_state)

    tips = validation.run_career_coach_checks()
    messages = [tip["msg"] for tip in tips]

    assert any("Missing required fields" in message for message in messages)
    assert any("Summary too short" in message for message in messages)
    assert any("No work experience added" in message for message in messages)
    assert any("Add more skills" in message for message in messages)


def test_run_career_coach_checks_flags_invalid_email_linkedin_and_year(monkeypatch):
    session_state = SessionState(
        full_name="Jane Doe",
        email="invalid-email",
        phone="123456",
        location="Remote",
        professional_title="Engineer",
        summary="Built systems. Led delivery. Improved performance.",
        experiences=[{"title": "Engineer", "description": "Improved developer workflow"}],
        educations=[{"degree": "BSc", "grad_year": "20"}],
        linkedin="portfolio.example.com/jane",
        skill_categories={"Languages": "Python, SQL, Go, Bash, JavaScript"},
    )
    monkeypatch.setattr(validation.st, "session_state", session_state)

    tips = validation.run_career_coach_checks()
    messages = [tip["msg"] for tip in tips]

    assert any("Email format looks invalid" in message for message in messages)
    assert any("does not look like a LinkedIn profile URL" in message for message in messages)
    assert any("Check education year format" in message for message in messages)
    assert any("Add metrics to these roles" in message for message in messages)


def test_run_career_coach_checks_reports_success_for_complete_data(monkeypatch):
    session_state = SessionState(
        full_name="Jane Doe",
        email="jane@example.com",
        phone="123456",
        location="Remote",
        professional_title="Engineer",
        summary="Built systems. Led delivery. Improved performance.",
        experiences=[{"title": "Engineer", "description": "Improved deployment speed by 30%"}],
        educations=[{"degree": "BSc", "grad_year": "2020"}],
        linkedin="linkedin.com/in/janedoe",
        skill_categories={"Languages": "Python, SQL, Go, Bash, JavaScript"},
    )
    monkeypatch.setattr(validation.st, "session_state", session_state)

    tips = validation.run_career_coach_checks()
    messages = [tip["msg"] for tip in tips]

    assert any("Contact information is complete." == message for message in messages)
    assert any("Professional summary looks great." == message for message in messages)
    assert any("Experience descriptions contain quantified results" in message for message in messages)
    assert any("skills listed - solid keyword coverage" in message for message in messages)


def test_run_career_coach_checks_can_translate_messages(monkeypatch):
    session_state = SessionState(
        ui_language="id",
        full_name="",
        email="",
        phone="",
        location="",
        professional_title="",
        summary="Pendek",
        experiences=[],
        educations=[],
        linkedin="",
        skill_categories={},
    )
    monkeypatch.setattr(validation.st, "session_state", session_state)

    tips = validation.run_career_coach_checks()
    messages = [tip["msg"] for tip in tips]

    assert any("Field wajib belum diisi" in message for message in messages)
    assert any("Ringkasan terlalu singkat" in message for message in messages)
