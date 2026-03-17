"""Streamlit UI rendering for the resume builder."""

import json
import re
from datetime import datetime

import streamlit as st

from .constants import (
    ACTION_VERBS,
    DATE_FORMAT,
    LANGUAGE_PROFICIENCY_LEVELS,
    SAMPLE_RESUME,
    SECTION_KEYS,
    SECTIONS,
)
from .data import (
    apply_resume_data,
    calculate_progress,
    collect_data,
    export_resume_json,
    reset_resume_data,
)
from .pdf import generate_pdf
from .validation import required_fields_filled, run_career_coach_checks
from .utils import is_valid_email, is_valid_year, normalise_url, parse_skill_category


def render_sidebar():
    """Render the app sidebar and workspace actions."""
    with st.sidebar:
        st.markdown(
            "<h2 style='margin-bottom:0'>📋 Resume Builder</h2>"
            "<p style='color:grey;font-size:0.85em;margin-top:2px'>ATS-Friendly · Career Coach Tips</p>",
            unsafe_allow_html=True,
        )
        st.divider()

        progress = calculate_progress()
        st.caption(f"Profile completion: {int(progress * 100)}%")
        st.progress(progress)
        st.divider()

        st.caption("Workspace")
        col_load, col_reset = st.columns(2)
        with col_load:
            if st.button("Load Sample", use_container_width=True):
                apply_resume_data(SAMPLE_RESUME)
                st.session_state.current_section = "Personal Info"
                st.rerun()
        with col_reset:
            if st.button("Reset", use_container_width=True):
                reset_resume_data()
                st.rerun()

        export_data = collect_data()
        st.download_button(
            "Export JSON",
            data=export_resume_json(export_data),
            file_name="resume-data.json",
            mime="application/json",
            use_container_width=True,
        )
        uploaded = st.file_uploader("Import JSON", type=["json"], accept_multiple_files=False)
        if uploaded is not None:
            try:
                payload = json.loads(uploaded.getvalue().decode("utf-8"))
                if st.button("Apply Imported Data", use_container_width=True):
                    apply_resume_data(payload)
                    st.session_state.current_section = "Personal Info"
                    st.rerun()
            except json.JSONDecodeError:
                st.error("The uploaded file is not valid JSON.")

        st.divider()
        for icon, label in SECTIONS:
            active = st.session_state.current_section == label
            button_label = f"{icon}  {label}"
            if active:
                st.markdown(
                    f"<div style='background:#1a6cf0;color:white;padding:8px 12px;border-radius:6px;margin-bottom:4px;font-weight:600'>{button_label}</div>",
                    unsafe_allow_html=True,
                )
            elif st.button(button_label, key=f"nav_{label}", use_container_width=True):
                st.session_state.current_section = label
                st.rerun()

        st.divider()
        st.caption("💡 Tip: Fill every section for the best ATS score.")


def render_personal_info():
    """Render the personal information section."""
    st.header("👤 Personal Information")
    st.caption("This information appears at the top of your resume. Keep it professional.")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.full_name = st.text_input(
            "Full Name *",
            value=st.session_state.full_name,
            placeholder="e.g. Jane Smith",
        )
        st.session_state.email = st.text_input(
            "Email Address *",
            value=st.session_state.email,
            placeholder="jane.smith@email.com",
        )
        if st.session_state.email and not is_valid_email(st.session_state.email):
            st.caption(":orange[Use a valid email format, for example name@example.com]")
        st.session_state.phone = st.text_input(
            "Phone Number",
            value=st.session_state.phone,
            placeholder="+1 555 123 4567",
        )
    with col2:
        st.session_state.professional_title = st.text_input(
            "Professional Title",
            value=st.session_state.professional_title,
            placeholder="e.g. Senior Software Engineer",
        )
        st.session_state.location = st.text_input(
            "Location",
            value=st.session_state.location,
            placeholder="City, Country",
        )
        st.session_state.linkedin = st.text_input(
            "LinkedIn URL",
            value=st.session_state.linkedin,
            placeholder="linkedin.com/in/janesmith",
        )
        if st.session_state.linkedin:
            st.caption(f"Saved as: `{normalise_url(st.session_state.linkedin)}`")

    st.subheader("Professional Summary")
    st.session_state.summary = st.text_area(
        "Write 3-5 sentences summarising your career, expertise, and goals.",
        value=st.session_state.summary,
        height=130,
        placeholder=(
            "Results-driven software engineer with 7+ years of experience building scalable web applications. "
            "Specialist in Python and cloud-native architectures. "
            "Passionate about leading cross-functional teams to deliver customer-centric solutions."
        ),
    )
    sentence_count = len([sentence for sentence in re.split(r"[.!?]+", st.session_state.summary) if sentence.strip()])
    if st.session_state.summary.strip():
        color = "green" if sentence_count >= 3 else "orange"
        st.caption(f":{color}[{sentence_count} sentence(s) detected -- aim for >= 3]")

    _nav_buttons("Personal Info")


def render_experience():
    """Render the experience section."""
    st.header("💼 Work Experience")
    st.caption("List your roles in **reverse chronological order** (most recent first).")

    for idx, experience in enumerate(st.session_state.experiences):
        with st.expander(
            f"**{experience.get('title', 'Untitled')}** @ {experience.get('company', '?')}  ·  {experience.get('dates', '')}",
            expanded=False,
        ):
            col1, col2, col3 = st.columns([3, 3, 2])
            with col1:
                new_title = st.text_input("Job Title", experience["title"], key=f"exp_title_{idx}")
            with col2:
                new_company = st.text_input("Company", experience["company"], key=f"exp_company_{idx}")
            with col3:
                new_dates = st.text_input("Dates", experience["dates"], key=f"exp_dates_{idx}", placeholder="Jan 2021 - Present")
            new_desc = st.text_area("Description", experience["description"], key=f"exp_desc_{idx}", height=120)
            st.caption(
                f"💡 Use action verbs & metrics: *{ACTION_VERBS}*. e.g. 'Increased deployment frequency by 40% via CI/CD automation.'"
            )
            col_save, col_del, _ = st.columns([1, 1, 4])
            with col_save:
                if st.button("💾 Save", key=f"save_exp_{idx}"):
                    st.session_state.experiences[idx] = {
                        "title": new_title,
                        "company": new_company,
                        "dates": new_dates,
                        "description": new_desc,
                    }
                    st.success("Saved!")
                    st.rerun()
            with col_del:
                if st.button("🗑️ Delete", key=f"del_exp_{idx}"):
                    st.session_state.experiences.pop(idx)
                    st.rerun()

    st.divider()
    st.subheader("➕ Add New Role")
    with st.form("new_exp_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([3, 3, 2])
        with col1:
            new_title = st.text_input("Job Title *", placeholder="Software Engineer")
        with col2:
            new_company = st.text_input("Company *", placeholder="Acme Corp")
        with col3:
            new_dates = st.text_input("Dates", placeholder="Jan 2021 - Present")
        new_desc = st.text_area(
            "Key Achievements & Responsibilities",
            height=120,
            placeholder=(
                "Led migration of monolith to microservices, reducing latency by 35%.\n"
                "Mentored 4 junior engineers; 2 promoted within 12 months.\n"
                "Shipped 3 major product features serving 500K+ users."
            ),
        )
        st.caption(f"💡 Action verbs: *{ACTION_VERBS}*. Always quantify: 'Reduced costs by 20%' beats 'Reduced costs'.")
        if st.form_submit_button("Add Role", type="primary"):
            if not new_title.strip() or not new_company.strip():
                st.error("Job Title and Company are required.")
            else:
                st.session_state.experiences.append(
                    {
                        "title": new_title.strip(),
                        "company": new_company.strip(),
                        "dates": new_dates.strip(),
                        "description": new_desc.strip(),
                    }
                )
                st.success(f"Added: {new_title} @ {new_company}")
                st.rerun()

    _nav_buttons("Experience")


def render_education():
    """Render the education section."""
    st.header("🎓 Education")
    st.caption("List your highest qualification first.")

    for idx, education in enumerate(st.session_state.educations):
        with st.expander(
            f"**{education.get('degree', 'Degree')}** - {education.get('institution', '?')}  ·  {education.get('grad_year', '')}",
            expanded=False,
        ):
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                new_degree = st.text_input("Degree / Qualification", education["degree"], key=f"edu_deg_{idx}")
            with col2:
                new_institution = st.text_input("Institution", education["institution"], key=f"edu_inst_{idx}")
            with col3:
                new_year = st.text_input("Year", str(education["grad_year"]), key=f"edu_year_{idx}")
                if new_year and not is_valid_year(new_year):
                    st.caption(":orange[Use a 4-digit year]")
            col_save, col_delete, _ = st.columns([1, 1, 4])
            with col_save:
                if st.button("💾 Save", key=f"save_edu_{idx}"):
                    st.session_state.educations[idx] = {
                        "degree": new_degree,
                        "institution": new_institution,
                        "grad_year": new_year,
                    }
                    st.success("Saved!")
                    st.rerun()
            with col_delete:
                if st.button("🗑️ Delete", key=f"del_edu_{idx}"):
                    st.session_state.educations.pop(idx)
                    st.rerun()

    st.divider()
    st.subheader("➕ Add Qualification")
    with st.form("new_edu_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([3, 3, 1])
        with col1:
            new_degree = st.text_input("Degree *", placeholder="B.Sc. Computer Science")
        with col2:
            new_institution = st.text_input("Institution *", placeholder="University of Technology")
        with col3:
            new_year = st.text_input("Year", placeholder="2019")
            if new_year and not is_valid_year(new_year):
                st.caption(":orange[Use a 4-digit year]")
        if st.form_submit_button("Add Education", type="primary"):
            if not new_degree.strip() or not new_institution.strip():
                st.error("Degree and Institution are required.")
            elif not is_valid_year(new_year):
                st.error("Year must be empty or a 4-digit value.")
            else:
                st.session_state.educations.append(
                    {
                        "degree": new_degree.strip(),
                        "institution": new_institution.strip(),
                        "grad_year": new_year.strip(),
                    }
                )
                st.success("Education added!")
                st.rerun()

    _nav_buttons("Education")


def render_skills():
    """Render the skills section."""
    st.header("🛠️ Skills")
    st.caption("Organise your skills by category. Mirror keywords from job descriptions to pass ATS filters.")

    for category in list(st.session_state.skill_categories.keys()):
        with st.container(border=True):
            col_name, col_rename, col_actions = st.columns([3, 3, 1])
            with col_name:
                st.markdown(f"**{category}**")
            with col_rename:
                new_name = st.text_input(
                    "Rename to",
                    value="",
                    key=f"rename_input_{category}",
                    placeholder="New category name",
                    label_visibility="collapsed",
                )
            with col_actions:
                rename_col, delete_col = st.columns(2)
                with rename_col:
                    if st.button("✏️", key=f"rename_btn_{category}", help="Apply rename"):
                        trimmed = new_name.strip()
                        if trimmed and trimmed != category:
                            if trimmed in st.session_state.skill_categories:
                                st.warning(f"'{trimmed}' already exists.")
                            else:
                                updated = {}
                                for key, value in st.session_state.skill_categories.items():
                                    updated[trimmed if key == category else key] = value
                                st.session_state.skill_categories = updated
                                st.rerun()
                with delete_col:
                    if st.button("🗑️", key=f"del_cat_{category}", help="Delete category"):
                        del st.session_state.skill_categories[category]
                        st.rerun()

            raw = st.text_area(
                "Skills (comma-separated)",
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
                    f"<span style='background:#e8f0fe;color:#1a6cf0;padding:2px 9px;border-radius:16px;font-size:0.82em;margin:2px;display:inline-block'>{skill}</span>"
                    for skill in skills_list
                )
                st.markdown(pills_html, unsafe_allow_html=True)

    st.divider()
    with st.form("add_cat_form", clear_on_submit=True):
        new_category = st.text_input("New category name", placeholder="e.g. DevOps & Cloud")
        if st.form_submit_button("➕ Add Category", type="primary"):
            if new_category.strip() and new_category.strip() not in st.session_state.skill_categories:
                st.session_state.skill_categories[new_category.strip()] = ""
                st.success(f"Category '{new_category.strip()}' added!")
                st.rerun()
            elif new_category.strip() in st.session_state.skill_categories:
                st.warning("Category already exists.")
            else:
                st.error("Please enter a category name.")

    total_skills = sum(len(parse_skill_category(raw)) for raw in st.session_state.skill_categories.values())
    if total_skills:
        color = "green" if total_skills >= 8 else "orange"
        st.caption(f":{color}[{total_skills} total skill(s) across all categories]")

    _nav_buttons("Skills")


def render_extras():
    """Render the optional extras section."""
    st.header("🌐 Extras")
    st.caption("Optional sections. Leave blank to omit from the PDF.")

    st.subheader("🔗 Profile Links")
    st.caption("Add GitHub, Portfolio, Behance, or any other relevant links.")
    for idx, link in enumerate(st.session_state.extra_links):
        col1, col2, col3 = st.columns([2, 4, 1])
        with col1:
            link["label"] = st.text_input("Label", link.get("label", ""), key=f"lnk_label_{idx}", placeholder="GitHub")
        with col2:
            link["url"] = st.text_input("URL", link.get("url", ""), key=f"lnk_url_{idx}", placeholder="github.com/username")
            if link.get("url"):
                st.caption(f"`{normalise_url(link['url'])}`")
        with col3:
            st.write("")
            st.write("")
            if st.button("✕", key=f"del_lnk_{idx}"):
                st.session_state.extra_links.pop(idx)
                st.rerun()
    if st.button("➕ Add Link"):
        st.session_state.extra_links.append({"label": "", "url": ""})
        st.rerun()

    st.divider()
    st.subheader("💬 Languages")
    st.caption("Spoken / written languages and your proficiency level.")
    for idx, language in enumerate(st.session_state.languages):
        col1, col2, col3 = st.columns([3, 3, 1])
        with col1:
            language["language"] = st.text_input("Language", language.get("language", ""), key=f"lang_name_{idx}", placeholder="English")
        with col2:
            current_level = language.get("level", LANGUAGE_PROFICIENCY_LEVELS[0])
            if current_level not in LANGUAGE_PROFICIENCY_LEVELS:
                current_level = LANGUAGE_PROFICIENCY_LEVELS[0]
            language["level"] = st.selectbox(
                "Proficiency",
                LANGUAGE_PROFICIENCY_LEVELS,
                index=LANGUAGE_PROFICIENCY_LEVELS.index(current_level),
                key=f"lang_level_{idx}",
            )
        with col3:
            st.write("")
            st.write("")
            if st.button("✕", key=f"del_lang_{idx}"):
                st.session_state.languages.pop(idx)
                st.rerun()
    if st.button("➕ Add Language"):
        st.session_state.languages.append({"language": "", "level": LANGUAGE_PROFICIENCY_LEVELS[0]})
        st.rerun()

    st.divider()
    st.subheader("🏅 Certifications")
    st.caption("Professional certifications, licences, or online course credentials.")
    for idx, certification in enumerate(st.session_state.certifications):
        col1, col2, col3, col4 = st.columns([4, 3, 1, 1])
        with col1:
            certification["name"] = st.text_input(
                "Certification Name",
                certification.get("name", ""),
                key=f"cert_name_{idx}",
                placeholder="AWS Certified Solutions Architect",
            )
        with col2:
            certification["issuer"] = st.text_input(
                "Issuing Body",
                certification.get("issuer", ""),
                key=f"cert_issuer_{idx}",
                placeholder="Amazon Web Services",
            )
        with col3:
            certification["year"] = st.text_input("Year", certification.get("year", ""), key=f"cert_year_{idx}", placeholder="2023")
            if certification.get("year") and not is_valid_year(certification["year"]):
                st.caption(":orange[Use a 4-digit year]")
        with col4:
            st.write("")
            st.write("")
            if st.button("✕", key=f"del_cert_{idx}"):
                st.session_state.certifications.pop(idx)
                st.rerun()
    if st.button("➕ Add Certification"):
        st.session_state.certifications.append({"name": "", "issuer": "", "year": ""})
        st.rerun()

    _nav_buttons("Extras")


def render_preview_download():
    """Render preview, coaching feedback, and exports."""
    st.header("📄 Preview & Download")

    st.subheader("🤖 Career Coach Analysis")
    for tip in run_career_coach_checks():
        if tip["level"] == "warning":
            st.warning(tip["msg"])
        elif tip["level"] == "info":
            st.info(tip["msg"])
        else:
            st.success(tip["msg"])

    st.divider()
    st.subheader("Resume Preview")
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
            st.markdown("**PROFESSIONAL SUMMARY**")
            st.write(data["summary"])

        if data["experiences"]:
            st.markdown("---")
            st.markdown("**WORK EXPERIENCE**")
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
            st.markdown("**EDUCATION**")
            for education in data["educations"]:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"**{education['degree']}** - {education.get('institution', '')}")
                with col_b:
                    st.caption(str(education.get("grad_year", "")))

        if data["skill_categories"]:
            st.markdown("---")
            st.markdown("**SKILLS**")
            for category, skills_list in data["skill_categories"].items():
                st.markdown(f"**{category}:** {', '.join(skills_list)}")

        if any(certification.get("name") for certification in data.get("certifications", [])):
            st.markdown("---")
            st.markdown("**CERTIFICATIONS**")
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
            st.markdown("**LANGUAGES**")
            language_strings = []
            for language in data["languages"]:
                if language.get("language"):
                    entry = language["language"]
                    if language.get("level"):
                        entry += f" ({language['level']})"
                    language_strings.append(entry)
            st.write("  ·  ".join(language_strings))

    st.divider()
    st.subheader("⬇️ Download PDF")
    st.download_button(
        "Download Resume JSON",
        data=export_resume_json(data),
        file_name="resume-data.json",
        mime="application/json",
    )

    if not required_fields_filled():
        st.error("Please fill in at least your **Full Name** and **Email** (Personal Info section) before generating the PDF.")
    elif not is_valid_email(data["email"]):
        st.error("Enter a valid email address before generating the PDF.")
    else:
        if st.button("🔄 Generate PDF", type="primary"):
            with st.spinner("Rendering your resume..."):
                try:
                    st.session_state.generated_pdf = generate_pdf(data)
                    st.session_state.generated_pdf_name = (
                        f"{data['full_name'].replace(' ', '_')}_Resume_{datetime.now().strftime(DATE_FORMAT)}.pdf"
                    )
                    st.success("PDF ready! Click the button above to download.")
                except Exception as exc:
                    st.error(f"PDF generation failed: {exc}")
                    raise
        if st.session_state.generated_pdf:
            st.download_button(
                label="📥 Download Resume PDF",
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
        "Programming Languages": "Python, JavaScript, TypeScript, Go",
        "Frameworks & Libraries": "FastAPI, React, Django, pandas",
        "Tools & Platforms": "Docker, Kubernetes, AWS, GitHub Actions",
        "Soft Skills": "Leadership, Communication, Problem Solving",
    }
    return placeholders.get(category, "Skill A, Skill B, Skill C")


def _nav_buttons(current: str):
    idx = SECTION_KEYS.index(current)
    col_prev, _, col_next = st.columns([1, 4, 1])
    with col_prev:
        if idx > 0 and st.button("← Back", key=f"back_{current}"):
            st.session_state.current_section = SECTION_KEYS[idx - 1]
            st.rerun()
    with col_next:
        if idx < len(SECTION_KEYS) - 1 and st.button("Next →", key=f"next_{current}", type="primary"):
            st.session_state.current_section = SECTION_KEYS[idx + 1]
            st.rerun()
