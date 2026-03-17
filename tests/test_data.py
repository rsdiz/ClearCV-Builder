"""Unit tests for session-state data helpers."""

import json

import resume_builder.data as data
from resume_builder.constants import DEFAULT_SKILL_CATEGORIES
from tests.helpers import SessionState


def test_init_session_state_populates_defaults(monkeypatch):
    session_state = SessionState()
    monkeypatch.setattr(data.st, "session_state", session_state)

    data.init_session_state()

    assert session_state.ui_language == "en"
    assert session_state.current_section == "Personal Info"
    assert session_state.experiences == []
    assert session_state.skill_categories == {cat: "" for cat in DEFAULT_SKILL_CATEGORIES}


def test_clean_list_entries_strips_fields_and_drops_empty_rows():
    items = [
        {"title": " Engineer ", "company": " Acme ", "dates": "", "description": " Built things \n"},
        {"title": " ", "company": "Ignored", "dates": "", "description": ""},
        {"title": "", "company": "", "dates": "", "description": ""},
    ]

    result = data.clean_list_entries(items, ["title", "company", "dates", "description"], required_field="title")

    assert result == [
        {
            "title": "Engineer",
            "company": "Acme",
            "dates": "",
            "description": "Built things",
        }
    ]


def test_apply_resume_data_cleans_and_resets_generated_pdf(monkeypatch):
    session_state = SessionState(generated_pdf=b"old", generated_pdf_name="old.pdf")
    monkeypatch.setattr(data.st, "session_state", session_state)

    payload = {
        "full_name": "  Jane Doe ",
        "email": " jane@example.com ",
        "experiences": [
            {"title": " Dev ", "company": " ACME ", "dates": "2020-2024", "description": " shipped \n\n things "}
        ],
        "educations": [
            {"degree": " BSc ", "institution": " Uni ", "grad_year": "2020 "}
        ],
        "skill_categories": {"  Languages ": " Python, SQL "},
        "extra_links": [
            {"label": " GitHub ", "url": " github.com/janedoe "}
        ],
        "languages": [{"language": " English ", "level": " Fluent "}],
        "certifications": [{"name": " AWS ", "issuer": " Amazon ", "year": " 2024 "}],
    }

    data.apply_resume_data(payload)

    assert session_state.full_name == "Jane Doe"
    assert session_state.experiences[0]["description"] == "shipped\n\n things"
    assert session_state.skill_categories == {"Languages": "Python, SQL"}
    assert session_state.extra_links == [{"label": "GitHub", "url": "github.com/janedoe"}]
    assert session_state.generated_pdf is None
    assert session_state.generated_pdf_name == ""


def test_collect_data_returns_cleaned_resume_payload(monkeypatch):
    session_state = SessionState(
        full_name=" Jane Doe ",
        email=" jane@example.com ",
        phone=" 123 ",
        linkedin=" linkedin.com/in/janedoe ",
        location=" Remote ",
        professional_title=" Engineer ",
        summary=" Builds systems. ",
        experiences=[
            {"title": " Engineer ", "company": " Acme ", "dates": "2021-Present", "description": " Did work "}
        ],
        educations=[{"degree": " BSc ", "institution": " Uni ", "grad_year": "2020 "}],
        skill_categories={"Languages": " Python, SQL ", "Empty": " , "},
        extra_links=[{"label": " GitHub ", "url": " github.com/janedoe "}],
        languages=[{"language": " English ", "level": " Fluent "}],
        certifications=[{"name": " AWS ", "issuer": " Amazon ", "year": " 2024 "}],
    )
    monkeypatch.setattr(data.st, "session_state", session_state)

    result = data.collect_data()

    assert result["linkedin"] == "https://linkedin.com/in/janedoe"
    assert result["skill_categories"] == {"Languages": ["Python", "SQL"]}
    assert result["extra_links"] == [{"label": "GitHub", "url": "https://github.com/janedoe"}]
    assert result["experiences"][0]["title"] == "Engineer"


def test_export_resume_json_outputs_indented_json():
    payload = {"full_name": "Jane Doe", "skills": ["Python"]}

    exported = data.export_resume_json(payload)

    assert json.loads(exported) == payload
    assert '\n  "full_name"' in exported
