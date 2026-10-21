"""Maskowanie sekretów, zanim prompt opuści laptopa."""

import re

# Grupa `v` (jeśli jest) wskazuje, co maskujemy; bez niej maskujemy całe dopasowanie.
PATTERNS = {
    "private_key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]+?-----END [A-Z ]*PRIVATE KEY-----",
    "openrouter_key": r"sk-or-v1-[A-Za-z0-9]{20,}",
    "openai_key": r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}",
    "aws_access_key": r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
    "github_token": r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,})\b",
    "gitlab_token": r"\bglpat-[A-Za-z0-9_-]{20,}",
    "jwt": r"\beyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
    "bearer": r"(?i)\bbearer\s+(?P<v>[A-Za-z0-9._~+/=-]{20,})",
    "password": r"(?i)(?:password|passwd|pwd|secret|token|api_?key)[\"']?\s*[:=]\s*[\"']?(?P<v>[^\s\"',;]{6,})",
}
COMPILED = {kind: re.compile(p) for kind, p in PATTERNS.items()}


def mask(text: str) -> tuple[str, list[str]]:
    """Zwraca tekst z sekretami podmienionymi na [MASKED:<rodzaj>] i listę znalezionych rodzajów."""
    found = []
    for kind, regex in COMPILED.items():

        def replace(m: re.Match) -> str:
            found.append(kind)
            if "v" in regex.groupindex:
                start, end = m.span("v")
                return m.group(0)[: start - m.start()] + f"[MASKED:{kind}]" + m.group(0)[end - m.start() :]
            return f"[MASKED:{kind}]"

        text = regex.sub(replace, text)
    return text, found


def mask_messages(messages: list[dict]) -> tuple[list[dict], list[str]]:
    """Maskuje treść wszystkich wiadomości: tekst albo listę części {"type": "text"}."""
    found = []
    out = []
    for msg in messages:
        msg = dict(msg)
        content = msg.get("content")
        if isinstance(content, str):
            msg["content"], kinds = mask(content)
            found += kinds
        elif isinstance(content, list):
            parts = []
            for part in content:
                if part.get("type") == "text":
                    text, kinds = mask(part["text"])
                    part = {**part, "text": text}
                    found += kinds
                parts.append(part)
            msg["content"] = parts
        out.append(msg)
    return out, found
