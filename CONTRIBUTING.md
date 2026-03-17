# Contributing

Thanks for contributing. Keep changes focused, testable, and consistent with the project's ATS-first scope.

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Contribution Guidelines

- Open an issue first for large feature changes, architectural shifts, or breaking behavior.
- Keep pull requests small enough to review without reverse-engineering unrelated edits.
- Preserve the project's focus on resume readability, ATS compatibility, and simple export flows.
- Update documentation when user-facing behavior changes.
- Avoid introducing heavy dependencies without a clear reason.

## Before Opening a Pull Request

- Run the app locally and verify the affected flow.
- Run `python -m py_compile app.py resume_builder/*.py`.
- Make sure new copy, labels, and validation messages are clear and consistent.
- Include a concise explanation of the problem, approach, and testing in the pull request description.

## Pull Request Checklist

- The change has a clear user or maintenance benefit.
- The code remains modular and readable.
- Documentation is updated where needed.
- Basic verification was completed locally.

## Code Style

- Prefer small, composable functions over monolithic handlers.
- Keep Streamlit UI logic separate from data shaping and validation logic.
- Match the existing naming and file structure unless there is a strong reason to refactor further.

## Reporting Issues

When filing an issue, include:

- What you expected to happen
- What actually happened
- Steps to reproduce
- Screenshots or sample input if relevant
- Environment details if the issue appears platform-specific

## Community Standards

By participating in this project, you agree to follow [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md).
