"""Test support helpers."""


class SessionState(dict):
    """Minimal dict-backed object matching Streamlit session-state access."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key, value):
        self[key] = value
