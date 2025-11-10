"""Utility helpers for parsing PDF documents into normalized text."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence, Union

PdfPath = Union[str, Path]
HeadingDetector = Callable[[str], bool]

_SOFT_JOIN_NO_SPACE_PREFIX = {".", ",", ":", ";", "!", "?", ")", "]", "}", "%", "'", '"'}
_WHITESPACE_RE = re.compile(r"\s+")
_CASE_HEADING_PATTERN = re.compile(
    r"(?<!\w)(?:(?P<roman>[IVXLCDM]+)\.\s*)?(?P<heading>LAW|ANALYSIS|ORDER)(?=\s*[:\n])",
    flags=re.IGNORECASE,
)


def parse_pdf_to_text(pdf_path: PdfPath, heading_detector: Optional[HeadingDetector] = None) -> str:
    """Extract text from a PDF file and smooth soft line breaks.

    Args:
        pdf_path: Path to the PDF file to parse.
        heading_detector: Optional callable that receives a single line of text
            and returns True when it should be treated as a heading. Headings
            remain on their own line while paragraph content is merged into a
            fluid block.

    Returns:
        A string containing the normalized text content of the PDF.

    Raises:
        FileNotFoundError: If the supplied path does not exist or is not a file.
        ImportError: If the required PDF parsing backend is not available.
    """
    path = Path(pdf_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"PDF file not found: {path}")

    detector = heading_detector or _default_heading_detector
    raw_lines: List[str] = []

    for page_text in _iter_pdf_text(path):
        if not page_text:
            continue
        raw_lines.extend(page_text.splitlines())
        raw_lines.append("")

    while raw_lines and raw_lines[-1] == "":
        raw_lines.pop()

    normalized_lines = _consolidate_lines(raw_lines, detector)
    return "\n".join(normalized_lines)


def _iter_pdf_text(pdf_path: Path) -> Iterable[str]:
    """Yield extracted text for each page in the given PDF."""
    try:
        from pypdf import PdfReader  # type: ignore import-not-found
    except ImportError:
        try:
            from PyPDF2 import PdfReader  # type: ignore import-not-found
        except ImportError as exc:  # pragma: no cover - defensive guard
            raise ImportError(
                "parse_pdf_to_text requires either 'pypdf' or 'PyPDF2' to be installed."
            ) from exc

    reader = PdfReader(str(pdf_path))
    for page in reader.pages:
        text = getattr(page, "extract_text", None)
        if callable(text):
            yield text() or ""
        else:  # pragma: no cover - fallback for unexpected reader APIs
            yield ""


def _consolidate_lines(lines: Sequence[str], heading_detector: HeadingDetector) -> List[str]:
    """Merge soft-wrapped lines while keeping headings on their own line."""
    result: List[str] = []
    buffer: List[str] = []

    def flush_buffer() -> None:
        if not buffer:
            return
        paragraph = _join_soft_lines(buffer)
        if paragraph:
            result.append(paragraph)
        buffer.clear()

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            flush_buffer()
            if result and result[-1] != "":
                result.append("")
            continue

        if heading_detector(line):
            flush_buffer()
            if result and result[-1] != "":
                result.append("")
            result.append(line)
            continue

        buffer.append(line)

    flush_buffer()

    while result and result[-1] == "":
        result.pop()

    return result


def _join_soft_lines(lines: Sequence[str]) -> str:
    """Join soft-wrapped lines into a single paragraph string."""
    if not lines:
        return ""

    text = lines[0]
    for line in lines[1:]:
        if text.endswith("-") and not text.endswith("--"):
            text = text[:-1] + line
            continue
        if line and line[0] in _SOFT_JOIN_NO_SPACE_PREFIX:
            text = text + line
            continue
        text = f"{text} {line}"

    return _collapse_whitespace(text)


def _collapse_whitespace(value: str) -> str:
    """Condense consecutive whitespace into a single space."""
    return _WHITESPACE_RE.sub(" ", value).strip()


def _default_heading_detector(line: str) -> bool:
    """Best-effort heuristic to decide whether a line is a heading."""
    if not line:
        return False
    if len(line) > 80:
        return False
    if line.endswith("."):
        return False

    words = [token for token in _WHITESPACE_RE.split(line) if token]
    if not words:
        return False

    alpha_words = [word for word in words if any(ch.isalpha() for ch in word)]
    if not alpha_words:
        return False

    uppercase_ratio = sum(1 for word in alpha_words if word.isupper()) / len(alpha_words)
    if uppercase_ratio >= 0.6:
        return True

    capitalized_words = sum(1 for word in alpha_words if word[0].isupper())
    if capitalized_words == len(alpha_words) and len(alpha_words) <= 8:
        return True

    return False


def extract_case_sections(case_text: str) -> dict[str, str]:
    """Return introduction, law, analysis, and order text segments."""
    if not case_text or not case_text.strip():
        raise ValueError("case_text must be a non-empty string")

    sections: dict[str, str] = {
        "introduction": "",
        "law": "",
        "analysis": "",
        "order": "",
    }

    matches = [m for m in _CASE_HEADING_PATTERN.finditer(case_text)]
    relevant = [m for m in matches if m.group("heading").upper() in {"LAW", "ANALYSIS", "ORDER"}]

    if not relevant:
        sections["introduction"] = case_text.strip()
        return sections

    law_match = next((m for m in relevant if m.group("heading").upper() == "LAW"), None)
    first_span_start = (law_match or relevant[0]).start()
    sections["introduction"] = case_text[:first_span_start].strip()

    for idx, match in enumerate(relevant):
        heading = match.group("heading").upper()
        start = match.end()
        end = relevant[idx + 1].start() if idx + 1 < len(relevant) else len(case_text)
        chunk = case_text[start:end].lstrip(" \t\r\n:\u2028\u2029").rstrip()
        key = heading.lower()
        if sections[key]:
            sections[key] = f"{sections[key]}\n\n{chunk}" if chunk else sections[key]
        else:
            sections[key] = chunk

    return sections


__all__ = ["parse_pdf_to_text", "HeadingDetector", "PdfPath", "extract_case_sections"]
