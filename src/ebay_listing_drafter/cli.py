"""Command-line interface for the eBay listing drafter."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .client import ChatClient, ChatMessage, LLMError
from .config import Config, CONFIG_FILE
from .draft import draft_messages
from .exporter import export_listing
from .profit import calculate


def _load_item_details(source: str | None) -> dict[str, Any]:
    """Load item details from a JSON file, stdin, or an interactive prompt."""
    if source:
        path = Path(source)
        if path == Path("-"):
            raw = sys.stdin.read()
        else:
            raw = path.read_text(encoding="utf-8")
        try:
            details = json.loads(raw)
        except json.JSONDecodeError as exc:
            print(f"Error: could not parse JSON from {source}: {exc}", file=sys.stderr)
            sys.exit(2)
        if not isinstance(details, dict):
            print("Error: item details JSON must be an object.", file=sys.stderr)
            sys.exit(2)
        return details

    # Interactive mode: ask for details one field at a time (beginner-friendly).
    print("Enter item details. Press Enter with no value to skip a field.\n")
    fields = [
        "title",
        "brand",
        "model",
        "condition",
        "category",
        "size",
        "color",
        "weight",
        "purchase_price",
        "shipping_cost",
        "notes",
    ]
    details: dict[str, Any] = {}
    for field_name in fields:
        value = input(f"{field_name}: ").strip()
        if value:
            details[field_name] = value
    return details


def _ask_purchase_price(details: dict[str, Any]) -> float | None:
    raw = details.get("purchase_price")
    if raw in (None, ""):
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def cmd_draft(args: argparse.Namespace) -> int:
    config = Config.load()
    details = _load_item_details(args.item)

    client = ChatClient(
        base_url=args.base_url or config.base_url,
        model=args.model or config.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        timeout_seconds=args.timeout,
    )

    purchase_price = _ask_purchase_price(details)
    profit_notes: str | None = None
    if purchase_price is not None:
        shipping_raw = details.get("shipping_cost", 0)
        try:
            shipping_cost = float(shipping_raw)
        except (TypeError, ValueError):
            shipping_cost = 0.0
        estimate = calculate(purchase_price, shipping_cost=shipping_cost)
        profit_notes = estimate.as_notes()

    if args.no_llm:
        title = f"{details.get('brand','')} {details.get('model','')} {details.get('condition','')} - {details.get('title','item')}".strip(" -") or "eBay listing"
        description = f"Item: {details.get('title','Untitled item')}\n\nDetails:\n" + "\n".join(
            f"- {k}: {v}" for k, v in details.items()
        )
        if profit_notes:
            description += "\n\n" + profit_notes
    else:
        try:
            response = client.chat([ChatMessage(role=m["role"], content=m["content"]) for m in draft_messages(details, profit_notes)])
        except LLMError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            print("Tip: run with --no-llm to draft a template without calling the model.", file=sys.stderr)
            return 1
        parts = response.content.strip().split("\n\n", 1)
        title = parts[0].strip().strip('"') if parts else ""
        description = parts[1].strip() if len(parts) > 1 else response.content.strip()
        if profit_notes and profit_notes not in description:
            description += "\n\n" + profit_notes

    title = title or "eBay listing"
    description = description or "(no description generated)"

    print("\n=== DRAFTED TITLE ===")
    print(title)
    print("\n=== DRAFTED DESCRIPTION ===")
    print(description)
    if profit_notes and profit_notes not in description:
        print("\n=== PROFIT ESTIMATE ===")
        print(profit_notes)

    if args.output:
        export_listing(
            args.output,
            title=title,
            description=description,
            item_details=details,
            profit_notes=profit_notes,
            model=client.model,
        )
        print(f"\nExported to {args.output}")

    return 0


def cmd_config(args: argparse.Namespace) -> int:
    config = Config.load()
    print(f"Config source: {config.source}")
    print(f"Config file:   {CONFIG_FILE}")
    print(f"Base URL:      {config.base_url}")
    print(f"Model:         {config.model}")
    print(f"Temperature:   {config.temperature}")
    print(f"Timeout:       {config.timeout_seconds}s")
    print(f"Max tokens:    {config.max_tokens}")
    if args.write_example:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(
            json.dumps(
                {
                    "base_url": config.base_url,
                    "model": config.model,
                    "temperature": config.temperature,
                    "timeout_seconds": config.timeout_seconds,
                    "max_tokens": config.max_tokens,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"Wrote example config to {CONFIG_FILE}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ebay-draft",
        description="Draft eBay listing titles and descriptions using a local OpenAI-compatible endpoint (default Ollama).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    draft_parser = subparsers.add_parser("draft", help="Draft a listing title and description")
    draft_parser.add_argument("item", nargs="?", help="JSON file with item details, or '-' for stdin")
    draft_parser.add_argument("--base-url", help="OpenAI-compatible endpoint base URL")
    draft_parser.add_argument("--model", help="Model name")
    draft_parser.add_argument("--temperature", type=float, default=0.7)
    draft_parser.add_argument("--max-tokens", type=int, default=800)
    draft_parser.add_argument("--timeout", type=int, default=60, help="Request timeout in seconds")
    draft_parser.add_argument("--no-llm", action="store_true", help="Draft a template without calling the model")
    draft_parser.add_argument("-o", "--output", help="Export drafted listing to JSON file")
    draft_parser.set_defaults(func=cmd_draft)

    config_parser = subparsers.add_parser("config", help="Show (or write) configuration")
    config_parser.add_argument("--write-example", action="store_true", help="Write an example config file")
    config_parser.set_defaults(func=cmd_config)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
