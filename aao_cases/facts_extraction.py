"""Helper to derive narrative fact descriptions from case text."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI


def _default_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    return OpenAI(api_key=api_key)


@dataclass(frozen=True)
class FactsExtractionConfig:
    model: str = "gpt-5-mini"
    temperature: float = 0.2
    max_output_tokens: int = 800


_SYSTEM_PROMPT = (
    "use the information under analysis, and under analyse only, to extract only the facts "
    "and avoid including any application of the law. Make it a description of the facts "
    "that I will use as an excecise to later analyze the case; this is why it should not "
    "contain any application of the described rules or other rules or precedents that are "
    "not extrictly facts of the case. This description of facts should be written in "
    "natural language that is something that is coherent when reading. Not a list of facts "
    "but a description of the facts as if it where a human description of them."
)

_USER_TEMPLATE = "Case text under analysis:\n{case_text}"  # newline keeps prompt readable


def extract_facts_description(
    case_text: str,
    *,
    client: Optional[OpenAI] = None,
    config: Optional[FactsExtractionConfig] = None,
) -> str:
    """Return a narrative description of facts using the provided case text."""
    if not case_text or not case_text.strip():
        raise ValueError("case_text must be a non-empty string")

    cfg = config or FactsExtractionConfig()
    gpt_client = client or _default_client()

    response = gpt_client.responses.create(
        model=cfg.model,
        instructions=_SYSTEM_PROMPT,
        input=_USER_TEMPLATE.format(case_text=case_text.strip()),  # plain string OK
        reasoning={"effort": "low"},
        max_output_tokens=cfg.max_output_tokens,
    )


    facts = _extract_text(response)
    if not facts:
        raise RuntimeError("Language model returned no text output")
    return facts


def _extract_text(response: object) -> str:
    """Collect concatenated text content from an OpenAI response payload."""
    chunks: list[str] = []

    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            if getattr(content, "type", None) == "output_text":
                text = getattr(content, "text", "")
                if text:
                    chunks.append(text)

    return "".join(chunks).strip()


__all__ = ["FactsExtractionConfig", "extract_facts_description"]
