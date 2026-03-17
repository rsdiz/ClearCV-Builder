"""Session state and data shaping helpers."""

import json

import streamlit as st

from .constants import DEFAULT_SKILL_CATEGORIES
from .utils import clean_text, normalise_url, parse_skill_category


def init_session_state():
    """Initialise all session state keys with safe defaults."""
    defaults = {
        "current_section": "Personal Info",
        "full_name": "",
        "email": "",
        "phone": "",
        "linkedin": "",
        "location": "",
        "professional_title": "",
        "summary": "",
        "experiences": [],
        "educations": [],
        "skill_categories": {cat: "" for cat in DEFAULT_SKILL_CATEGORIES},
        "extra_links": [],
        "languages": [],
        "certifications": [],
        "generated_pdf": None,
        "generated_pdf_name": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def calculate_progress() -> float:
    """Return a 0.0-1.0 float representing form completion."""
    score = 0
    total = 5

    if st.session_state.full_name and st.session_state.email:
        score += 1
    if st.session_state.summary.strip():
        score += 1
    if st.session_state.experiences:
        score += 1
    if st.session_state.educations:
        score += 1
    if any(value.strip() for value in st.session_state.skill_categories.values()):
        score += 1

    return score / total


def all_skills_flat() -> list[str]:
    """Return a flat list of all skills across all categories."""
    skills = []
    for raw in st.session_state.skill_categories.values():
        skills.extend(parse_skill_category(raw))
    return skills


def clean_list_entries(items: list[dict], fields: list[str], required_field: str | None = None) -> list[dict]:
    """Trim records and discard empty rows before preview/export."""
    cleaned_items = []
    for item in items:
        cleaned = {field: clean_text(str(item.get(field, ""))) for field in fields}
        if required_field and not cleaned.get(required_field, ""):
            continue
        if any(cleaned.values()):
            cleaned_items.append(cleaned)
    return cleaned_items


def apply_resume_data(data: dict):
    """Load a resume payload into session state."""
    st.session_state.full_name = clean_text(data.get("full_name", ""))
    st.session_state.email = clean_text(data.get("email", ""))
    st.session_state.phone = clean_text(data.get("phone", ""))
    st.session_state.linkedin = clean_text(data.get("linkedin", ""))
    st.session_state.location = clean_text(data.get("location", ""))
    st.session_state.professional_title = clean_text(data.get("professional_title", ""))
    st.session_state.summary = clean_text(data.get("summary", ""))
    st.session_state.experiences = clean_list_entries(
        data.get("experiences", []),
        ["title", "company", "dates", "description"],
        required_field="title",
    )
    st.session_state.educations = clean_list_entries(
        data.get("educations", []),
        ["degree", "institution", "grad_year"],
        required_field="degree",
    )
    st.session_state.skill_categories = {
        clean_text(category): clean_text(raw)
        for category, raw in data.get("skill_categories", {}).items()
        if clean_text(category)
    } or {cat: "" for cat in DEFAULT_SKILL_CATEGORIES}
    st.session_state.extra_links = clean_list_entries(
        data.get("extra_links", []),
        ["label", "url"],
        required_field="url",
    )
    st.session_state.languages = clean_list_entries(
        data.get("languages", []),
        ["language", "level"],
        required_field="language",
    )
    st.session_state.certifications = clean_list_entries(
        data.get("certifications", []),
        ["name", "issuer", "year"],
        required_field="name",
    )
    st.session_state.generated_pdf = None
    st.session_state.generated_pdf_name = ""


def reset_resume_data():
    """Reset session state to an empty resume."""
    apply_resume_data({"skill_categories": {cat: "" for cat in DEFAULT_SKILL_CATEGORIES}})
    st.session_state.current_section = "Personal Info"


def collect_data() -> dict:
    """Flatten session state into a single data dict for preview and PDF generation."""
    skill_categories = {}
    for category, raw in st.session_state.skill_categories.items():
        cleaned_category = clean_text(category)
        parsed = parse_skill_category(raw)
        if parsed:
            skill_categories[cleaned_category] = parsed

    return {
        "full_name": clean_text(st.session_state.full_name),
        "email": clean_text(st.session_state.email),
        "phone": clean_text(st.session_state.phone),
        "linkedin": normalise_url(st.session_state.linkedin),
        "location": clean_text(st.session_state.location),
        "professional_title": clean_text(st.session_state.professional_title),
        "summary": clean_text(st.session_state.summary),
        "experiences": clean_list_entries(
            st.session_state.experiences,
            ["title", "company", "dates", "description"],
            required_field="title",
        ),
        "educations": clean_list_entries(
            st.session_state.educations,
            ["degree", "institution", "grad_year"],
            required_field="degree",
        ),
        "skill_categories": skill_categories,
        "extra_links": [
            {"label": clean_text(link["label"]), "url": normalise_url(link["url"])}
            for link in clean_list_entries(
                st.session_state.extra_links,
                ["label", "url"],
                required_field="url",
            )
        ],
        "languages": clean_list_entries(
            st.session_state.languages,
            ["language", "level"],
            required_field="language",
        ),
        "certifications": clean_list_entries(
            st.session_state.certifications,
            ["name", "issuer", "year"],
            required_field="name",
        ),
    }


def export_resume_json(data: dict) -> str:
    """Serialize current resume to formatted JSON."""
    return json.dumps(data, indent=2)
