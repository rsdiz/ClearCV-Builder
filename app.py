"""
=============================================================
  ATS-Ready Resume Builder — Streamlit + fpdf2
  Senior Python Developer / Expert Career Coach Tool
=============================================================
  Customisation tips are marked with  # CUSTOMISE:  comments.
  To add a new section:
    1. Add an entry to SECTIONS list below.
    2. Add a render_<section>() function.
    3. Add the section to render_main_area() dispatch dict.
    4. Add PDF generation logic inside generate_pdf().
=============================================================

  CHANGES v2:
  - FIX: Unicode em-dash (--) used instead of special char "—"
    to avoid Helvetica font range errors in fpdf2.
  - NEW: Skills are now organised by categories (e.g. Languages,
    Frameworks, Tools, Soft Skills). Each category renders as a
    labelled row in both the preview and the PDF.
  - NEW: Optional profile links section (GitHub, Portfolio, etc.)
  - NEW: Languages section (spoken languages + proficiency)
  - NEW: Certifications section
=============================================================
"""

import re
import io
from datetime import datetime

import streamlit as st
from fpdf import FPDF

# ─────────────────────────────────────────────────────────────
#  CONSTANTS & CONFIGURATION
# ─────────────────────────────────────────────────────────────

# CUSTOMISE: Change section order or labels here
SECTIONS = [
    ("👤", "Personal Info"),
    ("💼", "Experience"),
    ("🎓", "Education"),
    ("🛠️", "Skills"),
    ("🌐", "Extras"),          # NEW: Languages, Certs, Links
    ("📄", "Preview & Download"),
]

SECTION_KEYS = [s[1] for s in SECTIONS]

# CUSTOMISE: Action verb suggestions shown as helper text
ACTION_VERBS = (
    "Led, Managed, Developed, Designed, Implemented, Increased, Reduced, "
    "Optimised, Delivered, Launched, Collaborated, Mentored, Automated, "
    "Negotiated, Achieved"
)

# CUSTOMISE: Default skill category labels — users can rename these
DEFAULT_SKILL_CATEGORIES = [
    "Programming Languages",
    "Frameworks & Libraries",
    "Tools & Platforms",
    "Soft Skills",
]

LANGUAGE_PROFICIENCY_LEVELS = [
    "Native",
    "Fluent",
    "Advanced (C1)",
    "Upper-Intermediate (B2)",
    "Intermediate (B1)",
    "Basic (A2)",
]

# Unicode-safe dash used in PDF (avoids Helvetica encoding errors)
PDF_DASH = " - "


# ─────────────────────────────────────────────────────────────
#  SESSION STATE INITIALISATION
# ─────────────────────────────────────────────────────────────

def init_session_state():
    """Initialise all session state keys with safe defaults."""
    defaults = {
        "current_section": "Personal Info",
        # Personal Info
        "full_name": "",
        "email": "",
        "phone": "",
        "linkedin": "",
        "location": "",
        "professional_title": "",
        "summary": "",
        # Experience list: each item is a dict
        "experiences": [],
        # Education list
        "educations": [],
        # Skills: dict of {category_label: comma-separated string}
        "skill_categories": {cat: "" for cat in DEFAULT_SKILL_CATEGORIES},
        # Extras
        "extra_links": [],        # list of {"label": str, "url": str}
        "languages": [],          # list of {"language": str, "level": str}
        "certifications": [],     # list of {"name": str, "issuer": str, "year": str}
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ─────────────────────────────────────────────────────────────
#  PROGRESS CALCULATION
# ─────────────────────────────────────────────────────────────

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
    if any(v.strip() for v in st.session_state.skill_categories.values()):
        score += 1

    return score / total


# ─────────────────────────────────────────────────────────────
#  SKILL HELPERS
# ─────────────────────────────────────────────────────────────

def parse_skill_category(raw: str) -> list[str]:
    """Parse a comma-separated skills string into a clean list."""
    return [s.strip() for s in raw.split(",") if s.strip()]


def all_skills_flat() -> list[str]:
    """Return a flat list of all skills across all categories."""
    out = []
    for raw in st.session_state.skill_categories.values():
        out.extend(parse_skill_category(raw))
    return out


# ─────────────────────────────────────────────────────────────
#  VALIDATION / CAREER-COACH LOGIC
# ─────────────────────────────────────────────────────────────

def run_career_coach_checks() -> list[dict]:
    """
    Run ATS / content-quality checks.
    Returns a list of dicts: {"level": "warning"|"info"|"success", "msg": str}
    """
    tips = []

    # 1. Required fields
    required = {
        "Full Name": st.session_state.full_name,
        "Email": st.session_state.email,
        "Phone": st.session_state.phone,
        "Location": st.session_state.location,
        "Professional Title": st.session_state.professional_title,
    }
    missing = [k for k, v in required.items() if not v.strip()]
    if missing:
        tips.append({
            "level": "warning",
            "msg": f"**Missing required fields:** {', '.join(missing)}. "
                   "ATS systems may reject incomplete profiles."
        })
    else:
        tips.append({"level": "success", "msg": "Contact information is complete."})

    # 2. Professional Summary length
    sentences = [s.strip() for s in re.split(r'[.!?]+', st.session_state.summary) if s.strip()]
    if len(sentences) < 3:
        tips.append({
            "level": "warning",
            "msg": "**Summary too short.** Aim for at least 3 sentences covering: "
                   "your role, key skills, and career goal."
        })
    else:
        tips.append({"level": "success", "msg": "Professional summary looks great."})

    # 3. Experience
    if not st.session_state.experiences:
        tips.append({
            "level": "warning",
            "msg": "**No work experience added.** Add at least one role to stand out."
        })
    else:
        unquantified = []
        for exp in st.session_state.experiences:
            desc = exp.get("description", "")
            if not re.search(r'\d', desc):
                unquantified.append(exp.get("title", "Unknown role"))
        if unquantified:
            tips.append({
                "level": "info",
                "msg": f"**Add metrics to these roles:** {', '.join(unquantified)}. "
                       "Quantified achievements (e.g., 'Grew revenue by 30%') dramatically "
                       "improve interview callback rates."
            })
        else:
            tips.append({
                "level": "success",
                "msg": "Experience descriptions contain quantified results - great work!"
            })

    # 4. Skills
    skills = all_skills_flat()
    if len(skills) < 5:
        tips.append({
            "level": "info",
            "msg": "**Add more skills.** ATS systems keyword-match against job descriptions. "
                   "Aim for 8-15 relevant skills across categories."
        })
    else:
        tips.append({"level": "success", "msg": f"{len(skills)} skills listed - solid keyword coverage."})

    # 5. LinkedIn
    if not st.session_state.linkedin.strip():
        tips.append({
            "level": "info",
            "msg": "Adding a LinkedIn URL increases recruiter trust and profile visibility."
        })

    return tips


def required_fields_filled() -> bool:
    return bool(st.session_state.full_name.strip() and st.session_state.email.strip())


# ─────────────────────────────────────────────────────────────
#  UNICODE SANITISER  (fixes the Helvetica font crash)
# ─────────────────────────────────────────────────────────────

# Map of common Unicode chars that Helvetica/Times can't render
_UNICODE_REPLACEMENTS = {
    "\u2014": "--",   # em dash       —
    "\u2013": "-",    # en dash       -
    "\u2018": "'",    # left single quote
    "\u2019": "'",    # right single quote
    "\u201c": '"',    # left double quote
    "\u201d": '"',    # right double quote
    "\u2022": "*",    # bullet        *
    "\u2026": "...",  # ellipsis      ...
    "\u00b7": "*",    # middle dot
    "\u2012": "-",    # figure dash
    "\u2015": "--",   # horizontal bar
    "\u00e2": "a",    # a with circumflex (encoding artefact)
    "\u20ac": "EUR",  # euro sign
    "\u00a0": " ",    # non-breaking space
}

def sanitise(text: str) -> str:
    """Replace characters outside Helvetica's Latin-1 range."""
    if not text:
        return ""
    for char, replacement in _UNICODE_REPLACEMENTS.items():
        text = text.replace(char, replacement)
    # Final sweep: drop any remaining non-latin-1 characters
    return text.encode("latin-1", errors="replace").decode("latin-1")


# ─────────────────────────────────────────────────────────────
#  PDF GENERATION
# ─────────────────────────────────────────────────────────────

class ResumePDF(FPDF):
    """
    Custom FPDF subclass for resume layout.
    CUSTOMISE: Adjust MARGIN, FONT_FAMILY, accent colour etc.
    """
    MARGIN = 18
    FONT_FAMILY = "Helvetica"
    RULE_THICKNESS = 0.4

    def __init__(self):
        super().__init__()
        self.set_margins(self.MARGIN, self.MARGIN, self.MARGIN)
        self.set_auto_page_break(auto=True, margin=self.MARGIN)

    def section_header(self, title: str):
        self.ln(3)
        self.set_font(self.FONT_FAMILY, "B", 11)
        self.set_text_color(30, 30, 30)
        self.cell(0, 7, sanitise(title.upper()), ln=True)
        self.set_draw_color(60, 60, 60)
        self.set_line_width(self.RULE_THICKNESS)
        self.line(self.MARGIN, self.get_y(), self.w - self.MARGIN, self.get_y())
        self.ln(3)

    def bullet(self, text: str):
        self.set_font(self.FONT_FAMILY, "", 9.5)
        self.set_text_color(50, 50, 50)
        x = self.get_x() + 4
        self.set_x(x)
        self.cell(5, 5, chr(149), ln=False)
        self.multi_cell(0, 5, sanitise(text))
        self.set_x(self.MARGIN)


def generate_pdf(data: dict) -> bytes:
    """
    Render a clean, ATS-friendly single-column PDF resume.
    Returns raw bytes suitable for st.download_button.
    """
    pdf = ResumePDF()
    pdf.add_page()
    M = ResumePDF.MARGIN
    F = ResumePDF.FONT_FAMILY

    # ── NAME & TITLE ────────────────────────────────────────
    usable_w = pdf.w - 2 * M

    pdf.set_font(F, "B", 22)
    pdf.set_text_color(15, 15, 15)
    pdf.cell(0, 10, sanitise(data["full_name"]), ln=True, align="C")

    if data["professional_title"]:
        pdf.set_font(F, "I", 12)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 6, sanitise(data["professional_title"]), ln=True, align="C")

    # ── CONTACT LINE ────────────────────────────────────────
    contact_parts = [
        data["email"],
        data["phone"],
        data["location"],
        data["linkedin"],
    ]
    contact_parts = [sanitise(p) for p in contact_parts if p]

    # Append extra profile links on contact line
    for lnk in data.get("extra_links", []):
        if lnk.get("url"):
            label = sanitise(lnk.get("label", ""))
            url = sanitise(lnk["url"])
            contact_parts.append(f"{label}: {url}" if label else url)

    if contact_parts:
        pdf.ln(2)
        pdf.set_font(F, "", 9)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(usable_w, 5, "  |  ".join(contact_parts), align="C")

    pdf.ln(4)
    pdf.set_draw_color(30, 30, 30)
    pdf.set_line_width(0.6)
    pdf.line(M, pdf.get_y(), pdf.w - M, pdf.get_y())
    pdf.ln(4)

    # ── PROFESSIONAL SUMMARY ────────────────────────────────
    if data["summary"].strip():
        pdf.section_header("Professional Summary")
        pdf.set_font(F, "", 9.5)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 5.5, sanitise(data["summary"].strip()))
        pdf.ln(2)

    # ── EXPERIENCE ──────────────────────────────────────────
    if data["experiences"]:
        pdf.section_header("Work Experience")
        for exp in data["experiences"]:
            pdf.set_font(F, "B", 10)
            pdf.set_text_color(20, 20, 20)
            title_company = sanitise(exp["title"])
            if exp.get("company"):
                title_company += PDF_DASH + sanitise(exp["company"])
            pdf.cell(0, 6, title_company, ln=False)

            if exp.get("dates"):
                pdf.set_font(F, "I", 9)
                pdf.set_text_color(90, 90, 90)
                pdf.cell(0, 6, sanitise(exp["dates"]), ln=True, align="R")
            else:
                pdf.ln(6)

            desc = exp.get("description", "").strip()
            if desc:
                for line in desc.splitlines():
                    line = line.strip().lstrip("*-> ").strip()
                    if line:
                        pdf.bullet(line)
            pdf.ln(3)

    # ── EDUCATION ───────────────────────────────────────────
    if data["educations"]:
        pdf.section_header("Education")
        for edu in data["educations"]:
            pdf.set_font(F, "B", 10)
            pdf.set_text_color(20, 20, 20)
            degree_inst = sanitise(edu.get("degree", ""))
            if edu.get("institution"):
                degree_inst += PDF_DASH + sanitise(edu["institution"])
            pdf.cell(0, 6, degree_inst, ln=False)
            if edu.get("grad_year"):
                pdf.set_font(F, "I", 9)
                pdf.set_text_color(90, 90, 90)
                pdf.cell(0, 6, sanitise(str(edu["grad_year"])), ln=True, align="R")
            else:
                pdf.ln(6)
            pdf.ln(2)

    # ── SKILLS (categorised) ─────────────────────────────────
    skill_cats = data.get("skill_categories", {})
    has_skills = any(v for v in skill_cats.values())
    if has_skills:
        pdf.section_header("Skills")
        # Page usable width = paper width minus both margins
        usable_w = pdf.w - 2 * M
        LABEL_W = 44  # fixed label column width (mm)
        SKILLS_W = usable_w - LABEL_W  # remaining width for the skills text
        for cat_label, skills_list in skill_cats.items():
            if not skills_list:
                continue
            # Remember Y before this row so we can align label vertically
            row_y = pdf.get_y()
            # --- Skills text first (in the right column) ---
            pdf.set_xy(M + LABEL_W, row_y)
            pdf.set_font(F, "", 9.5)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(SKILLS_W, 5.5, sanitise(", ".join(skills_list)))
            row_bottom = pdf.get_y()
            # --- Bold label on the left, vertically centred on first line ---
            pdf.set_xy(M, row_y)
            pdf.set_font(F, "B", 9.5)
            pdf.set_text_color(40, 40, 40)
            pdf.cell(LABEL_W, 5.5, sanitise(cat_label) + ":", ln=False)
            # Move cursor below the tallest column
            pdf.set_xy(M, row_bottom)
        pdf.ln(2)

    # ── CERTIFICATIONS ───────────────────────────────────────
    certs = data.get("certifications", [])
    if certs:
        pdf.section_header("Certifications")
        for cert in certs:
            pdf.set_font(F, "B", 9.5)
            pdf.set_text_color(20, 20, 20)
            cert_line = sanitise(cert.get("name", ""))
            if cert.get("issuer"):
                cert_line += PDF_DASH + sanitise(cert["issuer"])
            pdf.cell(0, 6, cert_line, ln=False)
            if cert.get("year"):
                pdf.set_font(F, "I", 9)
                pdf.set_text_color(90, 90, 90)
                pdf.cell(0, 6, sanitise(str(cert["year"])), ln=True, align="R")
            else:
                pdf.ln(6)
        pdf.ln(2)

    # ── LANGUAGES ────────────────────────────────────────────
    langs = data.get("languages", [])
    if langs:
        pdf.section_header("Languages")
        pdf.set_font(F, "", 9.5)
        pdf.set_text_color(50, 50, 50)
        lang_strs = []
        for lg in langs:
            entry = sanitise(lg.get("language", ""))
            if lg.get("level"):
                entry += f" ({sanitise(lg['level'])})"
            lang_strs.append(entry)
        pdf.multi_cell(0, 5.5, "  *  ".join(lang_strs))
        pdf.ln(2)

    return bytes(pdf.output())


# ─────────────────────────────────────────────────────────────
#  DATA COLLECTION HELPER
# ─────────────────────────────────────────────────────────────

def collect_data() -> dict:
    """Flatten session state into a single data dict for PDF generation."""
    # Build categorised skills dict: {label: [skill, ...]}
    skill_cats = {}
    for cat, raw in st.session_state.skill_categories.items():
        parsed = parse_skill_category(raw)
        if parsed:
            skill_cats[cat] = parsed

    return {
        "full_name": st.session_state.full_name,
        "email": st.session_state.email,
        "phone": st.session_state.phone,
        "linkedin": st.session_state.linkedin,
        "location": st.session_state.location,
        "professional_title": st.session_state.professional_title,
        "summary": st.session_state.summary,
        "experiences": st.session_state.experiences,
        "educations": st.session_state.educations,
        "skill_categories": skill_cats,
        "extra_links": st.session_state.extra_links,
        "languages": st.session_state.languages,
        "certifications": st.session_state.certifications,
    }


# ─────────────────────────────────────────────────────────────
#  UI — SIDEBAR
# ─────────────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown(
            "<h2 style='margin-bottom:0'>📋 Resume Builder</h2>"
            "<p style='color:grey;font-size:0.85em;margin-top:2px'>"
            "ATS-Friendly · Career Coach Tips</p>",
            unsafe_allow_html=True,
        )
        st.divider()

        progress = calculate_progress()
        st.caption(f"Profile completion: {int(progress * 100)}%")
        st.progress(progress)
        st.divider()

        for icon, label in SECTIONS:
            active = st.session_state.current_section == label
            btn_label = f"{icon}  {label}"
            if active:
                st.markdown(
                    f"<div style='background:#1a6cf0;color:white;padding:8px 12px;"
                    f"border-radius:6px;margin-bottom:4px;font-weight:600'>"
                    f"{btn_label}</div>",
                    unsafe_allow_html=True,
                )
            else:
                if st.button(btn_label, key=f"nav_{label}", use_container_width=True):
                    st.session_state.current_section = label
                    st.rerun()

        st.divider()
        st.caption("💡 Tip: Fill every section for the best ATS score.")


# ─────────────────────────────────────────────────────────────
#  UI — SECTION RENDERERS
# ─────────────────────────────────────────────────────────────

def render_personal_info():
    st.header("👤 Personal Information")
    st.caption("This information appears at the top of your resume. Keep it professional.")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.full_name = st.text_input(
            "Full Name *", value=st.session_state.full_name,
            placeholder="e.g. Jane Smith"
        )
        st.session_state.email = st.text_input(
            "Email Address *", value=st.session_state.email,
            placeholder="jane.smith@email.com"
        )
        st.session_state.phone = st.text_input(
            "Phone Number", value=st.session_state.phone,
            placeholder="+1 555 123 4567"
        )
    with col2:
        st.session_state.professional_title = st.text_input(
            "Professional Title", value=st.session_state.professional_title,
            placeholder="e.g. Senior Software Engineer"
        )
        st.session_state.location = st.text_input(
            "Location", value=st.session_state.location,
            placeholder="City, Country"
        )
        st.session_state.linkedin = st.text_input(
            "LinkedIn URL", value=st.session_state.linkedin,
            placeholder="linkedin.com/in/janesmith"
        )

    st.subheader("Professional Summary")
    st.session_state.summary = st.text_area(
        "Write 3-5 sentences summarising your career, expertise, and goals.",
        value=st.session_state.summary,
        height=130,
        placeholder=(
            "Results-driven software engineer with 7+ years of experience building "
            "scalable web applications. Specialist in Python and cloud-native architectures. "
            "Passionate about leading cross-functional teams to deliver customer-centric solutions."
        ),
    )
    sentence_count = len([s for s in re.split(r'[.!?]+', st.session_state.summary) if s.strip()])
    if st.session_state.summary.strip():
        color = "green" if sentence_count >= 3 else "orange"
        st.caption(f":{color}[{sentence_count} sentence(s) detected -- aim for >= 3]")

    _nav_buttons("Personal Info")


# ── EXPERIENCE ──────────────────────────────────────────────

def render_experience():
    st.header("💼 Work Experience")
    st.caption("List your roles in **reverse chronological order** (most recent first).")

    for idx, exp in enumerate(st.session_state.experiences):
        with st.expander(
            f"**{exp.get('title', 'Untitled')}** @ {exp.get('company', '?')}  ·  {exp.get('dates', '')}",
            expanded=False,
        ):
            col1, col2, col3 = st.columns([3, 3, 2])
            with col1:
                new_title = st.text_input("Job Title", exp["title"], key=f"exp_title_{idx}")
            with col2:
                new_company = st.text_input("Company", exp["company"], key=f"exp_company_{idx}")
            with col3:
                new_dates = st.text_input("Dates", exp["dates"], key=f"exp_dates_{idx}",
                                          placeholder="Jan 2021 - Present")
            new_desc = st.text_area(
                "Description", exp["description"], key=f"exp_desc_{idx}", height=120
            )
            st.caption(
                f"💡 Use action verbs & metrics: *{ACTION_VERBS}*. "
                "e.g. 'Increased deployment frequency by 40% via CI/CD automation.'"
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
        c1, c2, c3 = st.columns([3, 3, 2])
        with c1:
            new_title = st.text_input("Job Title *", placeholder="Software Engineer")
        with c2:
            new_company = st.text_input("Company *", placeholder="Acme Corp")
        with c3:
            new_dates = st.text_input("Dates", placeholder="Jan 2021 - Present")
        new_desc = st.text_area(
            "Key Achievements & Responsibilities", height=120,
            placeholder=(
                "Led migration of monolith to microservices, reducing latency by 35%.\n"
                "Mentored 4 junior engineers; 2 promoted within 12 months.\n"
                "Shipped 3 major product features serving 500K+ users."
            ),
        )
        st.caption(
            f"💡 Action verbs: *{ACTION_VERBS}*. Always quantify: "
            "'Reduced costs by 20%' beats 'Reduced costs'."
        )
        submitted = st.form_submit_button("Add Role", type="primary")
        if submitted:
            if not new_title.strip() or not new_company.strip():
                st.error("Job Title and Company are required.")
            else:
                st.session_state.experiences.append({
                    "title": new_title.strip(),
                    "company": new_company.strip(),
                    "dates": new_dates.strip(),
                    "description": new_desc.strip(),
                })
                st.success(f"Added: {new_title} @ {new_company}")
                st.rerun()

    _nav_buttons("Experience")


# ── EDUCATION ───────────────────────────────────────────────

def render_education():
    st.header("🎓 Education")
    st.caption("List your highest qualification first.")

    for idx, edu in enumerate(st.session_state.educations):
        with st.expander(
            f"**{edu.get('degree', 'Degree')}** - {edu.get('institution', '?')}  ·  {edu.get('grad_year', '')}",
            expanded=False,
        ):
            c1, c2, c3 = st.columns([3, 3, 1])
            with c1:
                nd = st.text_input("Degree / Qualification", edu["degree"], key=f"edu_deg_{idx}")
            with c2:
                ni = st.text_input("Institution", edu["institution"], key=f"edu_inst_{idx}")
            with c3:
                ny = st.text_input("Year", str(edu["grad_year"]), key=f"edu_year_{idx}")
            cs, cd, _ = st.columns([1, 1, 4])
            with cs:
                if st.button("💾 Save", key=f"save_edu_{idx}"):
                    st.session_state.educations[idx] = {
                        "degree": nd, "institution": ni, "grad_year": ny
                    }
                    st.success("Saved!")
                    st.rerun()
            with cd:
                if st.button("🗑️ Delete", key=f"del_edu_{idx}"):
                    st.session_state.educations.pop(idx)
                    st.rerun()

    st.divider()
    st.subheader("➕ Add Qualification")
    with st.form("new_edu_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([3, 3, 1])
        with c1:
            new_deg = st.text_input("Degree *", placeholder="B.Sc. Computer Science")
        with c2:
            new_inst = st.text_input("Institution *", placeholder="University of Technology")
        with c3:
            new_year = st.text_input("Year", placeholder="2019")
        if st.form_submit_button("Add Education", type="primary"):
            if not new_deg.strip() or not new_inst.strip():
                st.error("Degree and Institution are required.")
            else:
                st.session_state.educations.append({
                    "degree": new_deg.strip(),
                    "institution": new_inst.strip(),
                    "grad_year": new_year.strip(),
                })
                st.success("Education added!")
                st.rerun()

    _nav_buttons("Education")


# ── SKILLS (categorised) ────────────────────────────────────

def render_skills():
    st.header("🛠️ Skills")
    st.caption(
        "Organise your skills by category. Mirror keywords from job descriptions to pass ATS filters."
    )

    # ── Per-category: skills input + inline rename + delete ──
    cats = list(st.session_state.skill_categories.keys())
    for cat in cats:
        with st.container(border=True):
            # Header row: current name | rename input | delete button
            h_col1, h_col2, h_col3 = st.columns([3, 3, 1])
            with h_col1:
                st.markdown(f"**{cat}**")
            with h_col2:
                new_name = st.text_input(
                    "Rename to",
                    value="",
                    key=f"rename_input_{cat}",
                    placeholder="New category name",
                    label_visibility="collapsed",
                )
            with h_col3:
                # Two sub-columns: rename confirm + delete
                r_col, d_col = st.columns(2)
                with r_col:
                    if st.button("✏️", key=f"rename_btn_{cat}", help="Apply rename"):
                        trimmed = new_name.strip()
                        if trimmed and trimmed != cat:
                            if trimmed in st.session_state.skill_categories:
                                st.warning(f"'{trimmed}' already exists.")
                            else:
                                # Preserve insertion order
                                updated = {}
                                for k, v in st.session_state.skill_categories.items():
                                    updated[trimmed if k == cat else k] = v
                                st.session_state.skill_categories = updated
                                st.rerun()
                with d_col:
                    if st.button("🗑️", key=f"del_cat_{cat}", help="Delete category"):
                        del st.session_state.skill_categories[cat]
                        st.rerun()

            # Skills textarea
            raw = st.text_area(
                "Skills (comma-separated)",
                value=st.session_state.skill_categories.get(cat, ""),
                height=80,
                key=f"skill_cat_{cat}",
                placeholder=_skill_category_placeholder(cat),
                label_visibility="collapsed",
            )
            if cat in st.session_state.skill_categories:
                st.session_state.skill_categories[cat] = raw

            skills_list = parse_skill_category(raw)
            if skills_list:
                pills_html = " ".join(
                    f"<span style='background:#e8f0fe;color:#1a6cf0;padding:2px 9px;"
                    f"border-radius:16px;font-size:0.82em;margin:2px;display:inline-block'>"
                    f"{s}</span>"
                    for s in skills_list
                )
                st.markdown(pills_html, unsafe_allow_html=True)

    st.divider()

    # ── Add new category ─────────────────────────────────────
    with st.form("add_cat_form", clear_on_submit=True):
        new_cat_name = st.text_input("New category name", placeholder="e.g. DevOps & Cloud")
        if st.form_submit_button("➕ Add Category", type="primary"):
            if new_cat_name.strip() and new_cat_name.strip() not in st.session_state.skill_categories:
                st.session_state.skill_categories[new_cat_name.strip()] = ""
                st.success(f"Category '{new_cat_name.strip()}' added!")
                st.rerun()
            elif new_cat_name.strip() in st.session_state.skill_categories:
                st.warning("Category already exists.")
            else:
                st.error("Please enter a category name.")

    total = all_skills_flat()
    if total:
        color = "green" if len(total) >= 8 else "orange"
        st.caption(f":{color}[{len(total)} total skill(s) across all categories]")

    _nav_buttons("Skills")


def _skill_category_placeholder(cat: str) -> str:
    placeholders = {
        "Programming Languages": "Python, JavaScript, TypeScript, Go",
        "Frameworks & Libraries": "FastAPI, React, Django, pandas",
        "Tools & Platforms": "Docker, Kubernetes, AWS, GitHub Actions",
        "Soft Skills": "Leadership, Communication, Problem Solving",
    }
    return placeholders.get(cat, "Skill A, Skill B, Skill C")


# ── EXTRAS (Links, Languages, Certifications) ────────────────

def render_extras():
    st.header("🌐 Extras")
    st.caption("Optional sections. Leave blank to omit from the PDF.")

    # ── Profile Links ─────────────────────────────────────
    st.subheader("🔗 Profile Links")
    st.caption("Add GitHub, Portfolio, Behance, or any other relevant links.")

    for idx, lnk in enumerate(st.session_state.extra_links):
        col1, col2, col3 = st.columns([2, 4, 1])
        with col1:
            lnk["label"] = st.text_input(
                "Label", lnk.get("label", ""), key=f"lnk_label_{idx}",
                placeholder="GitHub"
            )
        with col2:
            lnk["url"] = st.text_input(
                "URL", lnk.get("url", ""), key=f"lnk_url_{idx}",
                placeholder="github.com/username"
            )
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

    # ── Languages ─────────────────────────────────────────
    st.subheader("💬 Languages")
    st.caption("Spoken / written languages and your proficiency level.")

    for idx, lg in enumerate(st.session_state.languages):
        col1, col2, col3 = st.columns([3, 3, 1])
        with col1:
            lg["language"] = st.text_input(
                "Language", lg.get("language", ""), key=f"lang_name_{idx}",
                placeholder="English"
            )
        with col2:
            current_level = lg.get("level", LANGUAGE_PROFICIENCY_LEVELS[0])
            if current_level not in LANGUAGE_PROFICIENCY_LEVELS:
                current_level = LANGUAGE_PROFICIENCY_LEVELS[0]
            lg["level"] = st.selectbox(
                "Proficiency", LANGUAGE_PROFICIENCY_LEVELS,
                index=LANGUAGE_PROFICIENCY_LEVELS.index(current_level),
                key=f"lang_level_{idx}"
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

    # ── Certifications ────────────────────────────────────
    st.subheader("🏅 Certifications")
    st.caption("Professional certifications, licences, or online course credentials.")

    for idx, cert in enumerate(st.session_state.certifications):
        col1, col2, col3, col4 = st.columns([4, 3, 1, 1])
        with col1:
            cert["name"] = st.text_input(
                "Certification Name", cert.get("name", ""), key=f"cert_name_{idx}",
                placeholder="AWS Certified Solutions Architect"
            )
        with col2:
            cert["issuer"] = st.text_input(
                "Issuing Body", cert.get("issuer", ""), key=f"cert_issuer_{idx}",
                placeholder="Amazon Web Services"
            )
        with col3:
            cert["year"] = st.text_input(
                "Year", cert.get("year", ""), key=f"cert_year_{idx}",
                placeholder="2023"
            )
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


# ── PREVIEW & DOWNLOAD ──────────────────────────────────────

def render_preview_download():
    st.header("📄 Preview & Download")

    st.subheader("🤖 Career Coach Analysis")
    tips = run_career_coach_checks()
    for tip in tips:
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
        for lnk in data.get("extra_links", []):
            if lnk.get("url"):
                label = lnk.get("label", "")
                contact_items.append(f"{label}: {lnk['url']}" if label else lnk["url"])

        contact = " · ".join(filter(None, contact_items))
        if contact:
            st.caption(contact)

        if data["summary"]:
            st.markdown("---")
            st.markdown("**PROFESSIONAL SUMMARY**")
            st.write(data["summary"])

        if data["experiences"]:
            st.markdown("---")
            st.markdown("**WORK EXPERIENCE**")
            for exp in data["experiences"]:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"**{exp['title']}** - {exp.get('company','')}")
                with col_b:
                    st.caption(exp.get("dates", ""))
                for line in exp.get("description", "").splitlines():
                    line = line.strip().lstrip("*->- ").strip()
                    if line:
                        st.markdown(f"• {line}")

        if data["educations"]:
            st.markdown("---")
            st.markdown("**EDUCATION**")
            for edu in data["educations"]:
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{edu['degree']}** - {edu.get('institution','')}")
                with c2:
                    st.caption(str(edu.get("grad_year", "")))

        if data["skill_categories"]:
            st.markdown("---")
            st.markdown("**SKILLS**")
            for cat_label, skills_list in data["skill_categories"].items():
                st.markdown(f"**{cat_label}:** {', '.join(skills_list)}")

        certs = data.get("certifications", [])
        if any(c.get("name") for c in certs):
            st.markdown("---")
            st.markdown("**CERTIFICATIONS**")
            for cert in certs:
                if cert.get("name"):
                    line = cert["name"]
                    if cert.get("issuer"):
                        line += f" - {cert['issuer']}"
                    if cert.get("year"):
                        line += f" ({cert['year']})"
                    st.markdown(f"• {line}")

        langs = data.get("languages", [])
        if any(lg.get("language") for lg in langs):
            st.markdown("---")
            st.markdown("**LANGUAGES**")
            lang_strs = []
            for lg in langs:
                if lg.get("language"):
                    entry = lg["language"]
                    if lg.get("level"):
                        entry += f" ({lg['level']})"
                    lang_strs.append(entry)
            st.write("  ·  ".join(lang_strs))

    st.divider()

    st.subheader("⬇️ Download PDF")

    if not required_fields_filled():
        st.error(
            "Please fill in at least your **Full Name** and **Email** "
            "(Personal Info section) before generating the PDF."
        )
    else:
        if st.button("🔄 Generate PDF", type="primary"):
            with st.spinner("Rendering your resume..."):
                try:
                    pdf_bytes = generate_pdf(data)
                    filename = (
                        f"{data['full_name'].replace(' ', '_')}_Resume_"
                        f"{datetime.now().strftime('%Y%m%d')}.pdf"
                    )
                    st.download_button(
                        label="📥 Download Resume PDF",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        type="primary",
                    )
                    st.success("PDF ready! Click the button above to download.")
                except Exception as exc:
                    st.error(f"PDF generation failed: {exc}")
                    raise

    _nav_buttons("Preview & Download")


# ─────────────────────────────────────────────────────────────
#  NAVIGATION HELPERS
# ─────────────────────────────────────────────────────────────

def _nav_buttons(current: str):
    idx = SECTION_KEYS.index(current)
    col_prev, _, col_next = st.columns([1, 4, 1])
    with col_prev:
        if idx > 0:
            if st.button("← Back", key=f"back_{current}"):
                st.session_state.current_section = SECTION_KEYS[idx - 1]
                st.rerun()
    with col_next:
        if idx < len(SECTION_KEYS) - 1:
            if st.button("Next →", key=f"next_{current}", type="primary"):
                st.session_state.current_section = SECTION_KEYS[idx + 1]
                st.rerun()


# ─────────────────────────────────────────────────────────────
#  MAIN DISPATCH
# ─────────────────────────────────────────────────────────────

def render_main_area():
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


# ─────────────────────────────────────────────────────────────
#  APP ENTRY POINT
# ─────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="ATS Resume Builder",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.5rem; }
        div[data-testid="stSidebar"] button {
            background: transparent;
            border: none;
            text-align: left;
            color: inherit;
            padding: 8px 12px;
            border-radius: 6px;
        }
        div[data-testid="stSidebar"] button:hover {
            background: rgba(26,108,240,0.08);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    init_session_state()
    render_sidebar()
    render_main_area()


if __name__ == "__main__":
    main()
