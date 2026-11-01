"""Local JSON export for drafted listings."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def export_listing(
    path: str | Path,
    title: str,
    description: str,
    item_details: dict[str, Any],
    profit_notes: str | None = None,
    model: str | None = None,
) -> Path:
    """Write a drafted listing to a JSON file and return the path written."""
    record: dict[str, Any] = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "title": title,
        "description": description,
        "item_details": item_details,
    }
    if profit_notes:
        record["profit_notes"] = profit_notes
    if model:
        record["model"] = model

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return target
