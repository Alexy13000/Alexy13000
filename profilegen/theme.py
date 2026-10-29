"""GitHub's own colours (Primer), for the dark and light variants."""

from __future__ import annotations

THEMES = {
    "dark": dict(
        bg="#0d1117", card="#0d1117", border="#30363d", fg="#e6edf3", muted="#8b949e",
        accent="#4493f8", subtle="#161b22", track="#21262d",
        green=("#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"),
        attention="#d29922",
    ),
    "light": dict(
        bg="#ffffff", card="#ffffff", border="#d0d7de", fg="#1f2328", muted="#656d76",
        accent="#0969da", subtle="#f6f8fa", track="#eaeef2",
        green=("#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"),
        attention="#9a6700",
    ),
}


def palette(theme: str) -> dict:
    return THEMES[theme]
