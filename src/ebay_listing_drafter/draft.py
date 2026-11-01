"""Prompt builders for drafting eBay listing titles and descriptions."""

from __future__ import annotations

SYSTEM_PROMPT = """You are a helpful eBay listing writer. Write clear, honest, beginner-friendly
eBay listing titles and descriptions from the item details provided. Never invent
condition, authenticity, or brand details that were not supplied. If something is
unknown, say so plainly. Keep tone warm and simple, like a friend explaining it."""


def item_summary(details: dict) -> str:
    """Render item details as a compact block for prompts."""
    lines = [f"- {key}: {value}" for key, value in details.items() if value not in (None, "", [])]
    return "\n".join(lines) if lines else "(no details provided)"


def title_prompt(details: dict) -> str:
    return f"""Write one eBay listing title (max 80 characters) for the item below.
Include brand, model, size, condition, and key specifics if known.
Return only the title, nothing else.

Item details:
{item_summary(details)}"""


def description_prompt(details: dict, profit_notes: str | None = None) -> str:
    extra = ""
    if profit_notes:
        extra = f"\n\nAdd this profit-estimate section at the end, exactly as given:\n{profit_notes}"
    return f"""Write an eBay listing description for the item below. Use short paragraphs,
simple language, and bullet points for item specifics and shipping. Be honest
about condition and note any unknowns. End with a short "About the seller"
section that is friendly and beginner-friendly.{extra}

Item details:
{item_summary(details)}"""


def draft_messages(details: dict, profit_notes: str | None = None) -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": title_prompt(details)},
        {"role": "user", "content": description_prompt(details, profit_notes)},
    ]
