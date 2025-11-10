"""Utilities for assembling structured case data JSON payloads."""

from __future__ import annotations

from typing import Dict


def build_case_json(
    *,
    law: str,
    analysis: str,
    order: str,
    facts_text: str,
    case_text: str,
) -> Dict[str, str]:
    """Produce a dictionary ready for JSON serialization from pre-parsed sections."""
    if not facts_text or not facts_text.strip():
        raise ValueError("facts_text must be a non-empty string")
    if not case_text or not case_text.strip():
        raise ValueError("case_text must be a non-empty string")

    return {
        "law": law.strip(),
        "analysis": analysis.strip(),
        "order": order.strip(),
        "facts_text": facts_text.strip(),
        "case_text": case_text,
    }


__all__ = ["build_case_json"]
