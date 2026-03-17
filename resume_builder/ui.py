"""Streamlit UI rendering for ClearCV Builder."""

from html import escape
import json
import re
from datetime import datetime

import streamlit as st

from .constants import (
    ACTION_VERBS,
    DATE_FORMAT,
    LANGUAGE_PROFICIENCY_LEVELS,
    SAMPLE_RESUMES,
    SECTION_KEYS,
    SECTIONS,
)
from .data import (
    apply_resume_data,
    all_skills_flat,
    calculate_progress,
    collect_data,
    export_resume_json,
    reset_resume_data,
)
from .i18n import LANGUAGE_OPTIONS, get_language, language_name, proficiency_label, section_label, t
from .pdf import generate_pdf
from .validation import required_fields_filled, run_career_coach_checks
from .utils import is_valid_email, is_valid_year, normalise_url, parse_skill_category


def render_sidebar():
    """Render the app sidebar and workspace actions."""
    with st.sidebar:
        active_language = get_language()
        navigation_items = _section_navigation_items()
        suggested_section = _suggested_section(navigation_items)
        current_index = SECTION_KEYS.index(st.session_state.current_section) + 1

        st.markdown(
            "<div style='padding:1rem 1rem 0.25rem 1rem;background:var(--clearcv-surface);"
            "border:1px solid var(--clearcv-border);border-radius:18px'>"
            "<p style='margin:0;font-size:0.78rem;letter-spacing:0.08em;text-transform:uppercase;color:var(--clearcv-muted)'>ClearCV Builder</p>"
            f"<h2 style='margin:0.25rem 0 0 0;color:var(--clearcv-text)'>📋 {escape(t('app.hero_title'))}</h2>"
            f"<p style='color:var(--clearcv-muted);font-size:0.9rem;margin:0.35rem 0 0 0'>{escape(t('app.subtitle'))}</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.divider()

        selected_language = st.selectbox(
            t("app.language_label"),
            LANGUAGE_OPTIONS,
            index=LANGUAGE_OPTIONS.index(active_language),
            format_func=lambda code: language_name(code, language=active_language),
        )
        if selected_language != active_language:
            st.session_state.ui_language = selected_language
            st.rerun()

        progress = calculate_progress()
        st.markdown(
            f"<div style='padding:0.85rem 1rem;background:var(--clearcv-progress);color:white;border-radius:18px'>"
            f"<p style='margin:0;font-size:0.78rem;letter-spacing:0.08em;text-transform:uppercase;color:var(--clearcv-progress-muted)'>{escape(t('app.progress_title'))}</p>"
            f"<div style='display:flex;justify-content:space-between;align-items:end;gap:1rem'>"
            f"<div><p style='margin:0.2rem 0 0 0;font-size:1.6rem;font-weight:700'>{int(progress * 100)}%</p></div>"
            f"<p style='margin:0;font-size:0.86rem;color:var(--clearcv-progress-muted)'>{escape(t('app.step_of', current=current_index, total=len(SECTION_KEYS)))}</p>"
            f"</div></div>",
            unsafe_allow_html=True,
        )
        st.progress(progress)

        if suggested_section and suggested_section != st.session_state.current_section:
            suggested_icon = next(icon for icon, label in SECTIONS if label == suggested_section)
            if st.button(
                t("app.continue_with", icon=suggested_icon, section=section_label(suggested_section)),
                use_container_width=True,
                type="primary",
            ):
                st.session_state.current_section = suggested_section
                st.rerun()

        st.divider()

        st.caption(t("app.navigator"))
        for index, item in enumerate(navigation_items, start=1):
            active = item["label"] == st.session_state.current_section
            badge_bg = (
                "var(--clearcv-accent)"
                if item["state"] == "complete"
                else "#f59e0b"
                if item["state"] == "partial"
                else "var(--clearcv-badge-empty-bg)"
            )
            badge_color = "white" if item["state"] != "empty" else "var(--clearcv-badge-empty-text)"
            card_bg = "var(--clearcv-surface-active)" if active else "var(--clearcv-surface-strong)"
            card_border = "var(--clearcv-accent)" if active else "var(--clearcv-border)"

            st.markdown(
                "<div style='padding:0.85rem 0.9rem;border-radius:18px;margin-bottom:0.45rem;"
                f"background:{card_bg};border:1px solid {card_border}'>"
                "<div style='display:flex;justify-content:space-between;align-items:flex-start;gap:0.8rem'>"
                "<div>"
                f"<p style='margin:0;font-size:0.76rem;color:var(--clearcv-muted);text-transform:uppercase;letter-spacing:0.08em'>{escape(t('app.step_of', current=index, total=len(navigation_items)))}</p>"
                f"<p style='margin:0.15rem 0 0 0;font-size:1rem;font-weight:700;color:var(--clearcv-text)'>{item['icon']} {escape(section_label(item['label']))}</p>"
                f"<p style='margin:0.3rem 0 0 0;font-size:0.84rem;color:var(--clearcv-muted)'>{escape(item['summary'])}</p>"
                "</div>"
                f"<span style='display:inline-block;padding:0.25rem 0.55rem;border-radius:999px;background:{badge_bg};"
                f"color:{badge_color};font-size:0.72rem;font-weight:700;white-space:nowrap'>{escape(item['status'])}</span>"
                "</div></div>",
                unsafe_allow_html=True,
            )

            if active:
                st.button(t("app.current_section"), key=f"nav_current_{item['label']}", use_container_width=True, disabled=True)
            elif st.button(t("app.open_section", section=section_label(item["label"])), key=f"nav_{item['label']}", use_container_width=True):
                st.session_state.current_section = item["label"]
                st.rerun()

        st.divider()

        st.caption(t("app.workspace"))
        col_load, col_reset = st.columns(2)
        with col_load:
            if st.button(t("app.load_sample"), use_container_width=True):
                apply_resume_data(SAMPLE_RESUMES.get(get_language(), SAMPLE_RESUMES["en"]))
                st.session_state.current_section = "Personal Info"
                st.rerun()
        with col_reset:
            if st.button(t("app.reset"), use_container_width=True):
                reset_resume_data()
                st.rerun()

        export_data = collect_data()
        st.download_button(
            t("app.export_json"),
            data=export_resume_json(export_data),
            file_name="resume-data.json",
            mime="application/json",
            use_container_width=True,
        )
        uploaded = st.file_uploader(t("app.import_json"), type=["json"], accept_multiple_files=False)
        if uploaded is not None:
            try:
                payload = json.loads(uploaded.getvalue().decode("utf-8"))
                if st.button(t("app.apply_imported"), use_container_width=True):
                    apply_resume_data(payload)
                    st.session_state.current_section = "Personal Info"
                    st.rerun()
            except json.JSONDecodeError:
                st.error(t("app.invalid_json"))

        st.divider()
        st.caption(t("app.tip_complete_sections"))


def render_personal_info():
    """Render the personal information section."""
    st.header(t("personal.header"))
    st.caption(t("personal.caption"))

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.full_name = st.text_input(
            t("personal.full_name"),
            value=st.session_state.full_name,
            placeholder=t("placeholder.full_name"),
        )
        st.session_state.email = st.text_input(
            t("personal.email"),
            value=st.session_state.email,
            placeholder=t("placeholder.email"),
        )
        if st.session_state.email and not is_valid_email(st.session_state.email):
            st.caption(t("personal.email_hint"))
        st.session_state.phone = st.text_input(
            t("personal.phone"),
            value=st.session_state.phone,
            placeholder=t("placeholder.phone"),
        )
    with col2:
        st.session_state.professional_title = st.text_input(
            t("personal.title"),
            value=st.session_state.professional_title,
            placeholder=t("placeholder.professional_title"),
        )
        st.session_state.location = st.text_input(
            t("personal.location"),
            value=st.session_state.location,
            placeholder=t("placeholder.location"),
        )
        st.session_state.linkedin = st.text_input(
            t("personal.linkedin"),
            value=st.session_state.linkedin,
            placeholder=t("placeholder.linkedin"),
        )
        if st.session_state.linkedin:
            st.caption(t("personal.saved_as", url=normalise_url(st.session_state.linkedin)))

    st.subheader(t("personal.summary_title"))
    st.session_state.summary = st.text_area(
        t("personal.summary_label"),
        value=st.session_state.summary,
        height=130,
        placeholder=t("placeholder.summary"),
    )
    sentence_count = len([sentence for sentence in re.split(r"[.!?]+", st.session_state.summary) if sentence.strip()])
    if st.session_state.summary.strip():
        color = "green" if sentence_count >= 3 else "orange"
        st.caption(t("personal.summary_sentences", color=color, count=sentence_count))

    _nav_buttons("Personal Info")


def render_experience():
    """Render the experience section."""
    st.header(t("experience.header"))
    st.caption(t("experience.caption"))

    for idx, experience in enumerate(st.session_state.experiences):
        with st.expander(
            f"**{experience.get('title', t('experience.untitled'))}** @ {experience.get('company', '?')}  ·  {experience.get('dates', '')}",
            expanded=False,
        ):
            col1, col2, col3 = st.columns([3, 3, 2])
            with col1:
                new_title = st.text_input(t("experience.job_title"), experience["title"], key=f"exp_title_{idx}")
            with col2:
                new_company = st.text_input(t("experience.company"), experience["company"], key=f"exp_company_{idx}")
            with col3:
                new_dates = st.text_input(
                    t("experience.dates"),
                    experience["dates"],
                    key=f"exp_dates_{idx}",
                    placeholder=t("placeholder.experience_dates"),
                )
            new_desc = st.text_area(t("experience.description"), experience["description"], key=f"exp_desc_{idx}", height=120)
            st.caption(
                t("experience.action_tip", verbs=ACTION_VERBS)
            )
            col_save, col_del, _ = st.columns([1, 1, 4])
            with col_save:
                if st.button(t("common.save"), key=f"save_exp_{idx}"):
                    st.session_state.experiences[idx] = {
                        "title": new_title,
                        "company": new_company,
                        "dates": new_dates,
                        "description": new_desc,
                    }
                    st.success(t("common.saved"))
                    st.rerun()
            with col_del:
                if st.button(t("common.delete"), key=f"del_exp_{idx}"):
                    st.session_state.experiences.pop(idx)
                    st.rerun()

    st.divider()
    st.subheader(t("experience.add_role_title"))
    with st.form("new_exp_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            new_title = st.text_input(t("experience.job_title_required"), placeholder=t("placeholder.experience_title"))
        with col2:
            new_company = st.text_input(t("experience.company_required"), placeholder=t("placeholder.experience_company"))
        with col3:
            new_dates = st.text_input(t("experience.dates"), placeholder=t("placeholder.experience_dates"))
        new_desc = st.text_area(
            t("experience.achievements"),
            height=120,
            placeholder=t("placeholder.experience_description"),
        )
        st.caption(t("experience.add_role_tip", verbs=ACTION_VERBS))
        if st.form_submit_button(t("experience.add_role"), type="primary"):
            if not new_title.strip() or not new_company.strip():
                st.error(t("experience.required_error"))
            else:
                st.session_state.experiences.append(
                    {
                        "title": new_title.strip(),
                        "company": new_company.strip(),
                        "dates": new_dates.strip(),
                        "description": new_desc.strip(),
                    }
                )
                st.success(t("experience.added", title=new_title, company=new_company))
                st.rerun()

    _nav_buttons("Experience")


def render_education():
    """Render the education section."""
    st.header(t("education.header"))
    st.caption(t("education.caption"))

    for idx, education in enumerate(st.session_state.educations):
        with st.expander(
            f"**{education.get('degree', t('education.degree'))}** - {education.get('institution', '?')}  ·  {education.get('grad_year', '')}",
            expanded=False,
        ):
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                new_degree = st.text_input(t("education.degree"), education["degree"], key=f"edu_deg_{idx}")
            with col2:
                new_institution = st.text_input(t("education.institution"), education["institution"], key=f"edu_inst_{idx}")
            with col3:
                new_year = st.text_input(t("education.year"), str(education["grad_year"]), key=f"edu_year_{idx}")
                if new_year and not is_valid_year(new_year):
                    st.caption(t("education.year_hint"))
            col_save, col_delete, _ = st.columns([1, 1, 4])
            with col_save:
                if st.button(t("common.save"), key=f"save_edu_{idx}"):
                    st.session_state.educations[idx] = {
                        "degree": new_degree,
                        "institution": new_institution,
                        "grad_year": new_year,
                    }
                    st.success(t("common.saved"))
                    st.rerun()
            with col_delete:
                if st.button(t("common.delete"), key=f"del_edu_{idx}"):
                    st.session_state.educations.pop(idx)
                    st.rerun()

    st.divider()
    st.subheader(t("education.add_title"))
    with st.form("new_edu_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([3, 3, 1])
        with col1:
            new_degree = st.text_input(t("education.degree_required"), placeholder=t("placeholder.education_degree"))
        with col2:
            new_institution = st.text_input(f"{t('education.institution')} *", placeholder=t("placeholder.education_institution"))
        with col3:
            new_year = st.text_input(t("education.year"), placeholder=t("placeholder.education_year"))
            if new_year and not is_valid_year(new_year):
                st.caption(t("education.year_hint"))
        if st.form_submit_button(t("education.add_button"), type="primary"):
            if not new_degree.strip() or not new_institution.strip():
                st.error(t("education.required_error"))
            elif not is_valid_year(new_year):
                st.error(t("education.year_error"))
            else:
                st.session_state.educations.append(
                    {
                        "degree": new_degree.strip(),
                        "institution": new_institution.strip(),
                        "grad_year": new_year.strip(),
                    }
                )
                st.success(t("education.added"))
                st.rerun()

    _nav_buttons("Education")


def render_skills():
    """Render the skills section."""
    st.header(t("skills.header"))
    st.caption(t("skills.caption"))

    for category in list(st.session_state.skill_categories.keys()):
        with st.container(border=True):
            col_name, col_rename, col_actions = st.columns([3, 3, 1])
            with col_name:
                st.markdown(f"**{category}**")
            with col_rename:
                new_name = st.text_input(
                    t("skills.rename_to"),
                    value="",
                    key=f"rename_input_{category}",
                    placeholder=t("skills.new_category"),
                    label_visibility="collapsed",
                )
            with col_actions:
                rename_col, delete_col = st.columns(2)
                with rename_col:
                    if st.button("✏️", key=f"rename_btn_{category}", help=t("skills.apply_rename")):
                        trimmed = new_name.strip()
                        if trimmed and trimmed != category:
                            if trimmed in st.session_state.skill_categories:
                                st.warning(t("skills.category_exists", name=trimmed))
                            else:
                                updated = {}
                                for key, value in st.session_state.skill_categories.items():
                                    updated[trimmed if key == category else key] = value
                                st.session_state.skill_categories = updated
                                st.rerun()
                with delete_col:
                    if st.button("🗑️", key=f"del_cat_{category}", help=t("skills.delete_category")):
                        del st.session_state.skill_categories[category]
                        st.rerun()

            raw = st.text_area(
                t("skills.input_label"),
                value=st.session_state.skill_categories.get(category, ""),
                height=80,
                key=f"skill_cat_{category}",
                placeholder=_skill_category_placeholder(category),
                label_visibility="collapsed",
            )
            if category in st.session_state.skill_categories:
                st.session_state.skill_categories[category] = raw

            skills_list = parse_skill_category(raw)
            if skills_list:
                pills_html = " ".join(
                    f"<span style='background:var(--clearcv-pill-bg);color:var(--clearcv-pill-text);padding:2px 9px;border-radius:16px;font-size:0.82em;margin:2px;display:inline-block'>{skill}</span>"
                    for skill in skills_list
                )
                st.markdown(pills_html, unsafe_allow_html=True)

    st.divider()
    with st.form("add_cat_form", clear_on_submit=True):
        new_category = st.text_input(t("skills.new_category"), placeholder=t("placeholder.skill_new_category"))
        if st.form_submit_button(t("skills.add_category"), type="primary"):
            if new_category.strip() and new_category.strip() not in st.session_state.skill_categories:
                st.session_state.skill_categories[new_category.strip()] = ""
                st.success(t("skills.category_added", name=new_category.strip()))
                st.rerun()
            elif new_category.strip() in st.session_state.skill_categories:
                st.warning(t("skills.category_exists_plain"))
            else:
                st.error(t("skills.category_required"))

    total_skills = sum(len(parse_skill_category(raw)) for raw in st.session_state.skill_categories.values())
    if total_skills:
        color = "green" if total_skills >= 8 else "orange"
        st.caption(t("skills.total", color=color, count=total_skills))

    _nav_buttons("Skills")


def render_extras():
    """Render the optional extras section."""
    st.header(t("extras.header"))
    st.caption(t("extras.caption"))

    st.subheader(t("extras.links_title"))
    st.caption(t("extras.links_caption"))
    for idx, link in enumerate(st.session_state.extra_links):
        col1, col2, col3 = st.columns([2, 4, 1])
        with col1:
            link["label"] = st.text_input(t("extras.label"), link.get("label", ""), key=f"lnk_label_{idx}", placeholder=t("placeholder.link_label"))
        with col2:
            link["url"] = st.text_input(t("extras.url"), link.get("url", ""), key=f"lnk_url_{idx}", placeholder=t("placeholder.link_url"))
            if link.get("url"):
                st.caption(f"`{normalise_url(link['url'])}`")
        with col3:
            st.write("")
            st.write("")
            if st.button("✕", key=f"del_lnk_{idx}"):
                st.session_state.extra_links.pop(idx)
                st.rerun()
    if st.button(t("extras.add_link")):
        st.session_state.extra_links.append({"label": "", "url": ""})
        st.rerun()

    st.divider()
    st.subheader(t("extras.languages_title"))
    st.caption(t("extras.languages_caption"))
    for idx, language in enumerate(st.session_state.languages):
        col1, col2, col3 = st.columns([3, 3, 1])
        with col1:
            language["language"] = st.text_input(
                t("extras.language"),
                language.get("language", ""),
                key=f"lang_name_{idx}",
                placeholder=t("placeholder.language"),
            )
        with col2:
            current_level = language.get("level", LANGUAGE_PROFICIENCY_LEVELS[0])
            if current_level not in LANGUAGE_PROFICIENCY_LEVELS:
                current_level = LANGUAGE_PROFICIENCY_LEVELS[0]
            language["level"] = st.selectbox(
                t("extras.proficiency"),
                LANGUAGE_PROFICIENCY_LEVELS,
                index=LANGUAGE_PROFICIENCY_LEVELS.index(current_level),
                key=f"lang_level_{idx}",
                format_func=proficiency_label,
            )
        with col3:
            st.write("")
            st.write("")
            if st.button("✕", key=f"del_lang_{idx}"):
                st.session_state.languages.pop(idx)
                st.rerun()
    if st.button(t("extras.add_language")):
        st.session_state.languages.append({"language": "", "level": LANGUAGE_PROFICIENCY_LEVELS[0]})
        st.rerun()

    st.divider()
    st.subheader(t("extras.certifications_title"))
    st.caption(t("extras.certifications_caption"))
    for idx, certification in enumerate(st.session_state.certifications):
        col1, col2, col3, col4 = st.columns([4, 3, 1, 1])
        with col1:
            certification["name"] = st.text_input(
                t("extras.cert_name"),
                certification.get("name", ""),
                key=f"cert_name_{idx}",
                placeholder=t("placeholder.certification_name"),
            )
        with col2:
            certification["issuer"] = st.text_input(
                t("extras.issuer"),
                certification.get("issuer", ""),
                key=f"cert_issuer_{idx}",
                placeholder=t("placeholder.certification_issuer"),
            )
        with col3:
            certification["year"] = st.text_input(
                t("education.year"),
                certification.get("year", ""),
                key=f"cert_year_{idx}",
                placeholder=t("placeholder.certification_year"),
            )
            if certification.get("year") and not is_valid_year(certification["year"]):
                st.caption(t("education.year_hint"))
        with col4:
            st.write("")
            st.write("")
            if st.button("✕", key=f"del_cert_{idx}"):
                st.session_state.certifications.pop(idx)
                st.rerun()
    if st.button(t("extras.add_certification")):
        st.session_state.certifications.append({"name": "", "issuer": "", "year": ""})
        st.rerun()

    _nav_buttons("Extras")


def render_preview_download():
    """Render preview, coaching feedback, and exports."""
    st.header(t("preview.header"))

    st.subheader(t("preview.analysis_title"))
    for tip in run_career_coach_checks():
        if tip["level"] == "warning":
            st.warning(tip["msg"])
        elif tip["level"] == "info":
            st.info(tip["msg"])
        else:
            st.success(tip["msg"])

    st.divider()
    st.subheader(t("preview.resume_title"))
    data = collect_data()

    with st.container(border=True):
        if data["full_name"]:
            st.markdown(f"## {data['full_name']}")
        if data["professional_title"]:
            st.markdown(f"*{data['professional_title']}*")

        contact_items = [data["email"], data["phone"], data["location"], data["linkedin"]]
        for link in data.get("extra_links", []):
            if link.get("url"):
                label = link.get("label", "")
                contact_items.append(f"{label}: {link['url']}" if label else link["url"])

        contact_line = " · ".join(filter(None, contact_items))
        if contact_line:
            st.caption(contact_line)

        if data["summary"]:
            st.markdown("---")
            st.markdown(f"**{t('preview.summary_heading')}**")
            st.write(data["summary"])

        if data["experiences"]:
            st.markdown("---")
            st.markdown(f"**{t('preview.experience_heading')}**")
            for experience in data["experiences"]:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"**{experience['title']}** - {experience.get('company', '')}")
                with col_b:
                    st.caption(experience.get("dates", ""))
                for line in experience.get("description", "").splitlines():
                    line = line.strip().lstrip("*->- ").strip()
                    if line:
                        st.markdown(f"• {line}")

        if data["educations"]:
            st.markdown("---")
            st.markdown(f"**{t('preview.education_heading')}**")
            for education in data["educations"]:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"**{education['degree']}** - {education.get('institution', '')}")
                with col_b:
                    st.caption(str(education.get("grad_year", "")))

        if data["skill_categories"]:
            st.markdown("---")
            st.markdown(f"**{t('preview.skills_heading')}**")
            for category, skills_list in data["skill_categories"].items():
                st.markdown(f"**{category}:** {', '.join(skills_list)}")

        if any(certification.get("name") for certification in data.get("certifications", [])):
            st.markdown("---")
            st.markdown(f"**{t('preview.certifications_heading')}**")
            for certification in data["certifications"]:
                if certification.get("name"):
                    line = certification["name"]
                    if certification.get("issuer"):
                        line += f" - {certification['issuer']}"
                    if certification.get("year"):
                        line += f" ({certification['year']})"
                    st.markdown(f"• {line}")

        if any(language.get("language") for language in data.get("languages", [])):
            st.markdown("---")
            st.markdown(f"**{t('preview.languages_heading')}**")
            language_strings = []
            for language in data["languages"]:
                if language.get("language"):
                    entry = language["language"]
                    if language.get("level"):
                        entry += f" ({proficiency_label(language['level'])})"
                    language_strings.append(entry)
            st.write("  ·  ".join(language_strings))

    st.divider()
    st.subheader(t("preview.download_title"))
    st.download_button(
        t("preview.download_json"),
        data=export_resume_json(data),
        file_name="resume-data.json",
        mime="application/json",
    )

    if not required_fields_filled():
        st.error(t("preview.fill_required", section=section_label("Personal Info")))
    elif not is_valid_email(data["email"]):
        st.error(t("preview.invalid_email"))
    else:
        if st.button(t("preview.generate_pdf"), type="primary"):
            with st.spinner(t("preview.rendering")):
                try:
                    st.session_state.generated_pdf = generate_pdf(data, language=get_language())
                    st.session_state.generated_pdf_name = (
                        t(
                            "pdf.file_name",
                            name=data["full_name"].replace(" ", "_"),
                            date=datetime.now().strftime(DATE_FORMAT),
                        )
                    )
                    st.success(t("preview.ready"))
                except Exception as exc:
                    st.error(t("preview.failed", error=exc))
                    raise
        if st.session_state.generated_pdf:
            st.download_button(
                label=t("preview.download_pdf"),
                data=st.session_state.generated_pdf,
                file_name=st.session_state.generated_pdf_name,
                mime="application/pdf",
                type="primary",
            )

    _nav_buttons("Preview & Download")


def render_main_area():
    """Dispatch the active section renderer."""
    dispatch = {
        "Personal Info": render_personal_info,
        "Experience": render_experience,
        "Education": render_education,
        "Skills": render_skills,
        "Extras": render_extras,
        "Preview & Download": render_preview_download,
    }
    renderer = dispatch.get(st.session_state.current_section)
    if renderer:
        renderer()


def _skill_category_placeholder(category: str) -> str:
    placeholders = {
        "Programming Languages": t("placeholder.skill_programming_languages"),
        "Frameworks & Libraries": t("placeholder.skill_frameworks"),
        "Tools & Platforms": t("placeholder.skill_tools"),
        "Soft Skills": t("placeholder.skill_soft_skills"),
    }
    return placeholders.get(category, t("placeholder.skill_generic"))


def _nav_buttons(current: str):
    idx = SECTION_KEYS.index(current)
    col_prev, _, col_next = st.columns([1, 4, 1])
    with col_prev:
        if idx > 0 and st.button(t("nav.back"), key=f"back_{current}"):
            st.session_state.current_section = SECTION_KEYS[idx - 1]
            st.rerun()
    with col_next:
        if idx < len(SECTION_KEYS) - 1 and st.button(t("nav.next"), key=f"next_{current}", type="primary"):
            st.session_state.current_section = SECTION_KEYS[idx + 1]
            st.rerun()


def _section_navigation_items() -> list[dict[str, str]]:
    personal_complete = bool(st.session_state.full_name.strip() and st.session_state.email.strip())
    personal_has_content = bool(
        st.session_state.full_name.strip()
        or st.session_state.email.strip()
        or st.session_state.professional_title.strip()
        or st.session_state.summary.strip()
    )

    experience_count = sum(1 for item in st.session_state.experiences if item.get("title", "").strip())
    education_count = sum(1 for item in st.session_state.educations if item.get("degree", "").strip())
    skills_count = len(all_skills_flat())
    filled_skill_categories = sum(1 for raw in st.session_state.skill_categories.values() if raw.strip())
    extras_count = (
        sum(1 for item in st.session_state.extra_links if item.get("url", "").strip())
        + sum(1 for item in st.session_state.languages if item.get("language", "").strip())
        + sum(1 for item in st.session_state.certifications if item.get("name", "").strip())
    )
    preview_ready = required_fields_filled() and is_valid_email(st.session_state.email)

    return [
        {
            "icon": "👤",
            "label": "Personal Info",
            "summary": st.session_state.professional_title.strip() or t("nav.summary.personal_empty"),
            **_state_meta(personal_complete, personal_has_content),
        },
        {
            "icon": "💼",
            "label": "Experience",
            "summary": (
                t("nav.summary.experience_count", count=experience_count)
                if experience_count
                else t("nav.summary.experience_empty")
            ),
            **_state_meta(experience_count > 0, experience_count > 0),
        },
        {
            "icon": "🎓",
            "label": "Education",
            "summary": (
                t("nav.summary.education_count", count=education_count)
                if education_count
                else t("nav.summary.education_empty")
            ),
            **_state_meta(education_count > 0, education_count > 0),
        },
        {
            "icon": "🛠️",
            "label": "Skills",
            "summary": (
                t(
                    "nav.summary.skills_count",
                    count=skills_count,
                    categories=filled_skill_categories,
                    category_word="category" if get_language() == "en" and filled_skill_categories == 1 else "categories"
                    if get_language() == "en"
                    else "kategori",
                )
                if skills_count
                else t("nav.summary.skills_empty")
            ),
            **_state_meta(skills_count >= 8, skills_count > 0),
        },
        {
            "icon": "🌐",
            "label": "Extras",
            "summary": t("nav.summary.extras_count", count=extras_count) if extras_count else t("nav.summary.extras_empty"),
            **_state_meta(extras_count > 0, extras_count > 0),
        },
        {
            "icon": "📄",
            "label": "Preview & Download",
            "summary": t("nav.summary.preview_ready") if preview_ready else t("nav.summary.preview_empty"),
            **_state_meta(preview_ready, st.session_state.full_name.strip() or st.session_state.email.strip()),
        },
    ]


def _state_meta(complete: bool, started: bool) -> dict[str, str]:
    if complete:
        return {"state": "complete", "status": t("status.ready")}
    if started:
        return {"state": "partial", "status": t("status.in_progress")}
    return {"state": "empty", "status": t("status.start")}


def _suggested_section(items: list[dict[str, str]]) -> str:
    for item in items:
        if item["state"] != "complete":
            return item["label"]
    return "Preview & Download"
