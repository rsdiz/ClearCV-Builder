"""Unit tests for PDF generation."""

from resume_builder.pdf import generate_pdf


def test_generate_pdf_returns_pdf_bytes():
    payload = {
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "123456",
        "linkedin": "https://linkedin.com/in/janedoe",
        "location": "Remote",
        "professional_title": "Senior Engineer",
        "summary": "Built systems. Led delivery. Improved operations.",
        "experiences": [
            {
                "title": "Senior Engineer",
                "company": "Acme",
                "dates": "2022 - Present",
                "description": "Improved deployment speed by 30%\nReduced incidents by 20%",
            }
        ],
        "educations": [{"degree": "BSc Computer Science", "institution": "State University", "grad_year": "2020"}],
        "skill_categories": {"Languages": ["Python", "SQL"], "Tools": ["Docker", "AWS"]},
        "extra_links": [{"label": "GitHub", "url": "https://github.com/janedoe"}],
        "languages": [{"language": "English", "level": "Native"}],
        "certifications": [{"name": "AWS Certified Developer", "issuer": "AWS", "year": "2024"}],
    }

    result = generate_pdf(payload)

    assert isinstance(result, bytes)
    assert result.startswith(b"%PDF")
    assert len(result) > 500


def test_generate_pdf_handles_unicode_text_via_sanitisation():
    payload = {
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "",
        "linkedin": "",
        "location": "",
        "professional_title": "Engineer — Platform",
        "summary": "Built APIs • improved reliability…",
        "experiences": [],
        "educations": [],
        "skill_categories": {},
        "extra_links": [],
        "languages": [],
        "certifications": [],
    }

    result = generate_pdf(payload)

    assert result.startswith(b"%PDF")
