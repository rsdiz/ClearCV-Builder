"""Shared configuration and seed data for ClearCV Builder."""

SECTIONS = [
    ("👤", "Personal Info"),
    ("💼", "Experience"),
    ("🎓", "Education"),
    ("🛠️", "Skills"),
    ("🌐", "Extras"),
    ("📄", "Preview & Download"),
]

SECTION_KEYS = [section[1] for section in SECTIONS]

ACTION_VERBS = (
    "Led, Managed, Developed, Designed, Implemented, Increased, Reduced, "
    "Optimised, Delivered, Launched, Collaborated, Mentored, Automated, "
    "Negotiated, Achieved"
)

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

PDF_DASH = " - "
DATE_FORMAT = "%Y%m%d"

SAMPLE_RESUMES = {
    "en": {
        "full_name": "Jordan Lee",
        "email": "jordan.lee@example.com",
        "phone": "+1 555 123 4567",
        "linkedin": "linkedin.com/in/jordanlee",
        "location": "Austin, TX",
        "professional_title": "Senior Software Engineer",
        "summary": (
            "Senior software engineer with 8 years of experience building scalable SaaS products. "
            "Strengths include Python, distributed systems, and mentoring high-performing teams. "
            "Focused on delivering measurable business outcomes through reliable, user-centered software."
        ),
        "experiences": [
            {
                "title": "Senior Software Engineer",
                "company": "Northstar Labs",
                "dates": "Jan 2022 - Present",
                "description": (
                    "Led API modernization initiative that reduced average response time by 42%.\n"
                    "Introduced CI quality gates and cut production incidents by 35%.\n"
                    "Mentored 5 engineers across backend architecture and release practices."
                ),
            }
        ],
        "educations": [
            {
                "degree": "B.S. Computer Science",
                "institution": "University of Texas",
                "grad_year": "2018",
            }
        ],
        "skill_categories": {
            "Programming Languages": "Python, TypeScript, SQL, Go",
            "Frameworks & Libraries": "FastAPI, React, Django, pandas",
            "Tools & Platforms": "AWS, Docker, PostgreSQL, GitHub Actions",
            "Soft Skills": "Leadership, Stakeholder Management, Mentoring",
        },
        "extra_links": [
            {"label": "GitHub", "url": "github.com/jordanlee"},
            {"label": "Portfolio", "url": "jordanlee.dev"},
        ],
        "languages": [
            {"language": "English", "level": "Native"},
            {"language": "Spanish", "level": "Intermediate (B1)"},
        ],
        "certifications": [
            {"name": "AWS Certified Developer", "issuer": "Amazon Web Services", "year": "2024"}
        ],
    },
    "id": {
        "full_name": "Jordan Lee",
        "email": "jordan.lee@example.com",
        "phone": "+62 812 3456 7890",
        "linkedin": "linkedin.com/in/jordanlee",
        "location": "Jakarta, Indonesia",
        "professional_title": "Senior Software Engineer",
        "summary": (
            "Senior software engineer dengan pengalaman 8 tahun membangun produk SaaS yang skalabel. "
            "Memiliki kekuatan di Python, sistem terdistribusi, dan pengembangan tim berkinerja tinggi. "
            "Berfokus pada hasil bisnis yang terukur melalui perangkat lunak yang andal dan berpusat pada pengguna."
        ),
        "experiences": [
            {
                "title": "Senior Software Engineer",
                "company": "Northstar Labs",
                "dates": "Jan 2022 - Sekarang",
                "description": (
                    "Memimpin modernisasi API yang menurunkan rata-rata waktu respons sebesar 42%.\n"
                    "Menerapkan quality gate di CI dan mengurangi insiden produksi sebesar 35%.\n"
                    "Membimbing 5 engineer dalam arsitektur backend dan praktik rilis."
                ),
            }
        ],
        "educations": [
            {
                "degree": "S1 Ilmu Komputer",
                "institution": "Universitas Indonesia",
                "grad_year": "2018",
            }
        ],
        "skill_categories": {
            "Bahasa Pemrograman": "Python, TypeScript, SQL, Go",
            "Framework & Library": "FastAPI, React, Django, pandas",
            "Tools & Platform": "AWS, Docker, PostgreSQL, GitHub Actions",
            "Soft Skills": "Kepemimpinan, Manajemen Stakeholder, Mentoring",
        },
        "extra_links": [
            {"label": "GitHub", "url": "github.com/jordanlee"},
            {"label": "Portofolio", "url": "jordanlee.dev"},
        ],
        "languages": [
            {"language": "Indonesia", "level": "Native"},
            {"language": "English", "level": "Intermediate (B1)"},
        ],
        "certifications": [
            {"name": "AWS Certified Developer", "issuer": "Amazon Web Services", "year": "2024"}
        ],
    },
}
