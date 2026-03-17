# ClearCV Builder

ClearCV Builder is a Streamlit application for drafting a clean, single-column resume, reviewing common screening issues, and exporting the final document to PDF.

## Why This Project Exists

Many resume tools optimize for visual styling first and machine readability second. This project takes the opposite approach:

- Keep the layout simple and easy to parse
- Help users catch weak or incomplete resume data early
- Make resume data portable with JSON import and export
- Generate a straightforward PDF without unnecessary formatting noise

## Features

- Guided resume builder for core resume sections
- Inline validation for common formatting issues
- Resume screening-oriented coaching and content checks
- Sample resume loader for demos and quick testing
- JSON import and export for saving progress
- PDF export powered by `fpdf2`
- Modular codebase organized under `resume_builder/`

## Tech Stack

- Python
- Streamlit
- `fpdf2`

## Getting Started

### Prerequisites

- Python 3.10+ recommended

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run Locally

```bash
streamlit run app.py
```

Open the local Streamlit URL shown in the terminal, usually `http://localhost:8501`.

## How To Use

1. Start the app with `streamlit run app.py`.
2. Fill out the resume sections from the sidebar.
3. Use `Load Sample` if you want example data immediately.
4. Export your resume data to JSON to save work in progress.
5. Review the preview and generate the PDF from `Preview & Download`.

## Project Structure

```text
.
├── app.py
├── requirements.txt
└── resume_builder/
    ├── app.py
    ├── constants.py
    ├── data.py
    ├── pdf.py
    ├── ui.py
    ├── utils.py
    └── validation.py
```

## Development

Install dependencies and run the app locally:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Basic syntax verification:

```bash
python -m py_compile app.py resume_builder/*.py
```

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](./CONTRIBUTING.md) before opening a pull request.

For community expectations, see [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md).

To report a security issue, use [SECURITY.md](./SECURITY.md).

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE).
