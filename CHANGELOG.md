# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project uses Semantic Versioning.

## [Unreleased]

## [0.1.0] - 2026-03-17

### Added

- Initial ATS-friendly resume builder application built with Streamlit
- Guided resume workflow for personal info, experience, education, skills, extras, and preview
- PDF export using `fpdf2`
- Resume data import and export with JSON
- Sample resume loader for demos and testing
- Open source community files: `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and `SECURITY.md`
- Initial pytest-based test suite covering utilities, data shaping, validation, and PDF generation

### Changed

- Refactored the original monolithic `app.py` into the modular `resume_builder/` package
- Updated PDF generation to use the current `fpdf2` API and eliminate deprecation warnings
- Expanded the `README.md` for public open source use

