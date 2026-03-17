# ATS-Friendly Resume Builder

Streamlit app for building a clean, ATS-focused resume and exporting it as PDF.

## Features

- Guided multi-step resume builder
- ATS-oriented coaching tips
- Categorized skills, certifications, languages, and profile links
- JSON import/export for saving progress
- Sample resume loader for quick testing
- One-click PDF generation with `fpdf2`

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Workflow

1. Fill out each section in the sidebar flow.
2. Use `Load Sample` if you want example content immediately.
3. Export your data as JSON to save progress.
4. Generate the PDF from `Preview & Download`.

## Project Notes

- The PDF output is intentionally single-column and simple for ATS compatibility.
- Unicode content is sanitized before PDF generation to avoid font encoding issues.
