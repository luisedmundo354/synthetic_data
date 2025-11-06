"""Utilities for assembling structured case data JSON payloads."""

from __future__ import annotations

import re
from typing import Dict

_HEADING_PATTERN = re.compile(
    r"(?<!\w)(?:(?P<roman>[IVXLCDM]+)\.\s*)?(?P<heading>LAW|ANALYSIS|ORDER)(?=\s*[:\n])",
    flags=re.IGNORECASE,
)


def build_case_json(facts_text: str, case_text: str) -> Dict[str, str]:
    """Produce a dictionary ready for JSON serialization from case content."""
    if not facts_text or not facts_text.strip():
        raise ValueError("facts_text must be a non-empty string")
    if not case_text or not case_text.strip():
        raise ValueError("case_text must be a non-empty string")

    sections = _extract_sections(case_text)

    return {
        "law": sections.get("LAW", ""),
        "analysis": sections.get("ANALYSIS", ""),
        "order": sections.get("ORDER", ""),
        "facts_text": facts_text.strip(),
        "case_text": case_text,
    }


def _extract_sections(case_text: str) -> Dict[str, str]:
    matches = list(_HEADING_PATTERN.finditer(case_text))
    sections: Dict[str, str] = {}
    if not matches:
        return sections

    for idx, match in enumerate(matches):
        heading = match.group("heading").upper()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(case_text)
        sections[heading] = case_text[start:end].lstrip(" \t\r\n:\u2028\u2029").rstrip()

    return sections


__all__ = ["build_case_json"]
