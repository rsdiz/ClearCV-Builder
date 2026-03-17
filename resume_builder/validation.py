"""Resume quality checks and simple validation rules."""

import re

import streamlit as st

from .data import all_skills_flat
from .utils import is_valid_email, is_valid_year, normalise_url


def run_career_coach_checks() -> list[dict]:
    """Run ATS and content-quality checks against the current form state."""
    tips = []

    required = {
        "Full Name": st.session_state.full_name,
        "Email": st.session_state.email,
        "Phone": st.session_state.phone,
        "Location": st.session_state.location,
        "Professional Title": st.session_state.professional_title,
    }
    missing = [field for field, value in required.items() if not value.strip()]
    if missing:
        tips.append(
            {
                "level": "warning",
                "msg": f"**Missing required fields:** {', '.join(missing)}. ATS systems may reject incomplete profiles.",
            }
        )
    else:
        tips.append({"level": "success", "msg": "Contact information is complete."})
        if not is_valid_email(st.session_state.email):
            tips.append(
                {
                    "level": "warning",
                    "msg": "**Email format looks invalid.** Use a standard address such as name@example.com.",
                }
            )

    sentences = [sentence.strip() for sentence in re.split(r"[.!?]+", st.session_state.summary) if sentence.strip()]
    if len(sentences) < 3:
        tips.append(
            {
                "level": "warning",
                "msg": "**Summary too short.** Aim for at least 3 sentences covering: your role, key skills, and career goal.",
            }
        )
    else:
        tips.append({"level": "success", "msg": "Professional summary looks great."})

    if not st.session_state.experiences:
        tips.append(
            {
                "level": "warning",
                "msg": "**No work experience added.** Add at least one role to stand out.",
            }
        )
    else:
        unquantified = []
        for experience in st.session_state.experiences:
            if not re.search(r"\d", experience.get("description", "")):
                unquantified.append(experience.get("title", "Unknown role"))
        if unquantified:
            tips.append(
                {
                    "level": "info",
                    "msg": f"**Add metrics to these roles:** {', '.join(unquantified)}. Quantified achievements (e.g., 'Grew revenue by 30%') dramatically improve interview callback rates.",
                }
            )
        else:
            tips.append({"level": "success", "msg": "Experience descriptions contain quantified results - great work!"})

    skills = all_skills_flat()
    if len(skills) < 5:
        tips.append(
            {
                "level": "info",
                "msg": "**Add more skills.** ATS systems keyword-match against job descriptions. Aim for 8-15 relevant skills across categories.",
            }
        )
    else:
        tips.append({"level": "success", "msg": f"{len(skills)} skills listed - solid keyword coverage."})

    if not st.session_state.linkedin.strip():
        tips.append({"level": "info", "msg": "Adding a LinkedIn URL increases recruiter trust and profile visibility."})
    elif "linkedin.com/" not in normalise_url(st.session_state.linkedin):
        tips.append(
            {
                "level": "info",
                "msg": "LinkedIn field does not look like a LinkedIn profile URL. Double-check the link.",
            }
        )

    invalid_years = [
        education.get("degree", "Education entry")
        for education in st.session_state.educations
        if not is_valid_year(str(education.get("grad_year", "")))
    ]
    if invalid_years:
        tips.append(
            {
                "level": "warning",
                "msg": f"**Check education year format:** {', '.join(invalid_years)} should use a 4-digit year.",
            }
        )

    return tips


def required_fields_filled() -> bool:
    """Return whether the minimal identity fields are present."""
    return bool(st.session_state.full_name.strip() and st.session_state.email.strip())
