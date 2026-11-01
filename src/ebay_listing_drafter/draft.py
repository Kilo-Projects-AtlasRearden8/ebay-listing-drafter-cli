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
    """Build a prompt asking for a title only (kept as a helper)."""
    return f"""Write one eBay listing title (max 80 characters) for the item below.
Include brand, model, size, condition, and key specifics if known.
Return only the title, nothing else.

Item details:
{item_summary(details)}"""


def description_prompt(details: dict, profit_notes: str | None = None) -> str:
    """Build a prompt asking for a description only (kept as a helper)."""
    extra = ""
    if profit_notes:
        extra = f"\n\nAdd this profit-estimate section at the end, exactly as given:\n{profit_notes}"
    return f"""Write an eBay listing description for the item below. Use short paragraphs,
simple language, and bullet points for item specifics and shipping. Be honest
about condition and note any unknowns. End with a short "About the seller"
section that is friendly and beginner-friendly.{extra}

Item details:
{item_summary(details)}"""


def draft_prompt(details: dict, profit_notes: str | None = None) -> str:
    """Build a single user prompt asking for both a title and a description."""
    extra = ""
    if profit_notes:
        extra = f"\n\nEnd the description with this profit-estimate section, exactly as given:\n{profit_notes}"
    return f"""Write an eBay listing for the item below. Reply with exactly two labeled sections:

TITLE: one title, 80 characters or fewer, including brand, model, size, condition, and key specifics if known.

DESCRIPTION: short paragraphs in simple language, bullet points for item specifics and shipping, honest about condition and any unknowns, then a short friendly "About the seller" section.{extra}

Item details:
{item_summary(details)}"""


def draft_messages(details: dict, profit_notes: str | None = None) -> list[dict]:
    """Build the chat messages for a single drafting call."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": draft_prompt(details, profit_notes)},
    ]


def parse_draft_output(text: str) -> tuple[str, str]:
    """Split an LLM response into (title, description) using TITLE:/DESCRIPTION: markers.

    Falls back gracefully if the markers are missing or malformed.
    """
    text = text.strip()
    title = ""
    description = text

    upper = text.upper()
    title_idx = upper.find("TITLE:")
    desc_idx = upper.find("DESCRIPTION:")

    if title_idx != -1:
        start = title_idx + len("TITLE:")
        end = desc_idx if desc_idx != -1 and desc_idx > title_idx else len(text)
        title = text[start:end].strip().strip('"').strip()

    if desc_idx != -1:
        description = text[desc_idx + len("DESCRIPTION:"):].strip().strip('"').strip()

    # Fallback: if no markers found, treat first line as title, rest as description.
    if not title and text:
        first_newline = text.find("\n")
        if first_newline != -1:
            title = text[:first_newline].strip().strip('"').strip()
            description = text[first_newline:].strip()
        else:
            title = text.strip().strip('"').strip()
            description = ""

    # Cap the title at 80 characters.
    if len(title) > 80:
        title = title[:77].rstrip() + "..."

    return title, description
