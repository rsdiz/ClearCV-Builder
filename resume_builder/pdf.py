"""PDF rendering for the resume builder."""

from fpdf import FPDF

from .constants import PDF_DASH

_UNICODE_REPLACEMENTS = {
    "\u2014": "--",
    "\u2013": "-",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2022": "*",
    "\u2026": "...",
    "\u00b7": "*",
    "\u2012": "-",
    "\u2015": "--",
    "\u00e2": "a",
    "\u20ac": "EUR",
    "\u00a0": " ",
}


def sanitise(text: str) -> str:
    """Replace characters outside Helvetica's Latin-1 range."""
    if not text:
        return ""
    for char, replacement in _UNICODE_REPLACEMENTS.items():
        text = text.replace(char, replacement)
    return text.encode("latin-1", errors="replace").decode("latin-1")


class ResumePDF(FPDF):
    """Custom FPDF subclass for resume layout."""

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
        x_pos = self.get_x() + 4
        self.set_x(x_pos)
        self.cell(5, 5, chr(149), ln=False)
        self.multi_cell(0, 5, sanitise(text))
        self.set_x(self.MARGIN)


def generate_pdf(data: dict) -> bytes:
    """Render a clean, ATS-friendly single-column PDF resume."""
    pdf = ResumePDF()
    pdf.add_page()
    margin = ResumePDF.MARGIN
    font_family = ResumePDF.FONT_FAMILY
    usable_width = pdf.w - 2 * margin

    pdf.set_font(font_family, "B", 22)
    pdf.set_text_color(15, 15, 15)
    pdf.cell(0, 10, sanitise(data["full_name"]), ln=True, align="C")

    if data["professional_title"]:
        pdf.set_font(font_family, "I", 12)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 6, sanitise(data["professional_title"]), ln=True, align="C")

    contact_parts = [data["email"], data["phone"], data["location"], data["linkedin"]]
    contact_parts = [sanitise(part) for part in contact_parts if part]
    for link in data.get("extra_links", []):
        if link.get("url"):
            label = sanitise(link.get("label", ""))
            url = sanitise(link["url"])
            contact_parts.append(f"{label}: {url}" if label else url)

    if contact_parts:
        pdf.ln(2)
        pdf.set_font(font_family, "", 9)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(usable_width, 5, "  |  ".join(contact_parts), align="C")

    pdf.ln(4)
    pdf.set_draw_color(30, 30, 30)
    pdf.set_line_width(0.6)
    pdf.line(margin, pdf.get_y(), pdf.w - margin, pdf.get_y())
    pdf.ln(4)

    if data["summary"].strip():
        pdf.section_header("Professional Summary")
        pdf.set_font(font_family, "", 9.5)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 5.5, sanitise(data["summary"].strip()))
        pdf.ln(2)

    if data["experiences"]:
        pdf.section_header("Work Experience")
        for experience in data["experiences"]:
            pdf.set_font(font_family, "B", 10)
            pdf.set_text_color(20, 20, 20)
            title_company = sanitise(experience["title"])
            if experience.get("company"):
                title_company += PDF_DASH + sanitise(experience["company"])
            pdf.cell(0, 6, title_company, ln=False)

            if experience.get("dates"):
                pdf.set_font(font_family, "I", 9)
                pdf.set_text_color(90, 90, 90)
                pdf.cell(0, 6, sanitise(experience["dates"]), ln=True, align="R")
            else:
                pdf.ln(6)

            description = experience.get("description", "").strip()
            if description:
                for line in description.splitlines():
                    line = line.strip().lstrip("*-> ").strip()
                    if line:
                        pdf.bullet(line)
            pdf.ln(3)

    if data["educations"]:
        pdf.section_header("Education")
        for education in data["educations"]:
            pdf.set_font(font_family, "B", 10)
            pdf.set_text_color(20, 20, 20)
            degree_institution = sanitise(education.get("degree", ""))
            if education.get("institution"):
                degree_institution += PDF_DASH + sanitise(education["institution"])
            pdf.cell(0, 6, degree_institution, ln=False)
            if education.get("grad_year"):
                pdf.set_font(font_family, "I", 9)
                pdf.set_text_color(90, 90, 90)
                pdf.cell(0, 6, sanitise(str(education["grad_year"])), ln=True, align="R")
            else:
                pdf.ln(6)
            pdf.ln(2)

    if any(values for values in data.get("skill_categories", {}).values()):
        pdf.section_header("Skills")
        label_width = 44
        skills_width = usable_width - label_width
        for category, skills_list in data["skill_categories"].items():
            if not skills_list:
                continue
            row_y = pdf.get_y()
            pdf.set_xy(margin + label_width, row_y)
            pdf.set_font(font_family, "", 9.5)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(skills_width, 5.5, sanitise(", ".join(skills_list)))
            row_bottom = pdf.get_y()
            pdf.set_xy(margin, row_y)
            pdf.set_font(font_family, "B", 9.5)
            pdf.set_text_color(40, 40, 40)
            pdf.cell(label_width, 5.5, sanitise(category) + ":", ln=False)
            pdf.set_xy(margin, row_bottom)
        pdf.ln(2)

    if data.get("certifications"):
        pdf.section_header("Certifications")
        for certification in data["certifications"]:
            pdf.set_font(font_family, "B", 9.5)
            pdf.set_text_color(20, 20, 20)
            cert_line = sanitise(certification.get("name", ""))
            if certification.get("issuer"):
                cert_line += PDF_DASH + sanitise(certification["issuer"])
            pdf.cell(0, 6, cert_line, ln=False)
            if certification.get("year"):
                pdf.set_font(font_family, "I", 9)
                pdf.set_text_color(90, 90, 90)
                pdf.cell(0, 6, sanitise(str(certification["year"])), ln=True, align="R")
            else:
                pdf.ln(6)
        pdf.ln(2)

    if data.get("languages"):
        pdf.section_header("Languages")
        pdf.set_font(font_family, "", 9.5)
        pdf.set_text_color(50, 50, 50)
        language_strings = []
        for language in data["languages"]:
            entry = sanitise(language.get("language", ""))
            if language.get("level"):
                entry += f" ({sanitise(language['level'])})"
            language_strings.append(entry)
        pdf.multi_cell(0, 5.5, "  *  ".join(language_strings))
        pdf.ln(2)

    return bytes(pdf.output())
