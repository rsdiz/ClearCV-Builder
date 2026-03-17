"""Resume quality checks and simple validation rules."""

import re

import streamlit as st

from .data import all_skills_flat
from .i18n import t
from .utils import is_valid_email, is_valid_year, normalise_url


def run_career_coach_checks() -> list[dict]:
    """Run resume screening and content-quality checks against the current form state."""
    tips = []

    required = {
        t("field.full_name"): st.session_state.full_name,
        t("field.email"): st.session_state.email,
        t("field.phone"): st.session_state.phone,
        t("field.location"): st.session_state.location,
        t("field.professional_title"): st.session_state.professional_title,
    }
    missing = [field for field, value in required.items() if not value.strip()]
    if missing:
        tips.append(
            {
                "level": "warning",
                "msg": t("validation.missing_required", fields=", ".join(missing)),
            }
        )
    else:
        tips.append({"level": "success", "msg": t("validation.contact_complete")})
        if not is_valid_email(st.session_state.email):
            tips.append(
                {
                    "level": "warning",
                    "msg": t("validation.invalid_email"),
                }
            )

    sentences = [sentence.strip() for sentence in re.split(r"[.!?]+", st.session_state.summary) if sentence.strip()]
    if len(sentences) < 3:
        tips.append(
            {
                "level": "warning",
                "msg": t("validation.summary_short"),
            }
        )
    else:
        tips.append({"level": "success", "msg": t("validation.summary_good")})

    if not st.session_state.experiences:
        tips.append(
            {
                "level": "warning",
                "msg": t("validation.no_experience"),
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
                    "msg": t("validation.add_metrics", roles=", ".join(unquantified)),
                }
            )
        else:
            tips.append({"level": "success", "msg": t("validation.experience_good")})

    skills = all_skills_flat()
    if len(skills) < 5:
        tips.append(
            {
                "level": "info",
                "msg": t("validation.add_skills"),
            }
        )
    else:
        tips.append({"level": "success", "msg": t("validation.skills_good", count=len(skills))})

    if not st.session_state.linkedin.strip():
        tips.append({"level": "info", "msg": t("validation.linkedin_missing")})
    elif "linkedin.com/" not in normalise_url(st.session_state.linkedin):
        tips.append(
            {
                "level": "info",
                "msg": t("validation.linkedin_invalid"),
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
                "msg": t("validation.invalid_years", entries=", ".join(invalid_years)),
            }
        )

    return tips


def required_fields_filled() -> bool:
    """Return whether the minimal identity fields are present."""
    return bool(st.session_state.full_name.strip() and st.session_state.email.strip())
