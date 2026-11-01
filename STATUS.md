# STATUS

## What was built

A local-first Python CLI, `ebay-draft`, that drafts eBay listing titles and
descriptions from item details using a configurable OpenAI-compatible endpoint
(Ollama by default, no API keys required), with profit-estimate notes and local
JSON export.

### Contents

- `src/ebay_listing_drafter/` — package
  - `config.py` — config from CLI flags → env vars → `~/.config/ebay-listing-drafter/config.json` → defaults
  - `client.py` — minimal OpenAI-compatible chat client over stdlib urllib (default `http://localhost:11434/v1`, model `llama3.2`)
  - `draft.py` — prompt builder (title ≤80 chars, honest description, profit notes appended)
  - `profit.py` — profit/fee/break-even calculations with suggested sale price targeting a margin
  - `exporter.py` — local JSON export with timestamp, item details, profit notes, model used
  - `cli.py` — argparse CLI: `draft` (file/stdin/interactive, `--no-llm`, `-o`), `config`
- `tests/test_drafter.py` — 15 unittest tests (stdlib only), all passing
- `pyproject.toml` — packaging with `ebay-draft` console script
- `LICENSE` — MIT, Copyright (c) 2026 Asdale Dynamics, LLC
- `README.md` — usage, configuration, credits to Asdale Dynamics, LLC
- `STATUS.md` — this file

## How to run

```bash
# Install
pip install -e .

# See configuration (defaults: Ollama at localhost:11434/v1, model llama3.2)
ebay-draft config

# Draft from a JSON file (requires a running model endpoint)
ebay-draft draft item.json -o listing.json

# Draft without calling any model (template mode, works offline)
echo '{"title":"Nike Air Max 90","brand":"Nike","condition":"Pre-owned","purchase_price":"40"}' \
  | ebay-draft draft - --no-llm -o listing.json

# Interactive mode (prompts for each field)
ebay-draft draft --no-llm

# Run tests
PYTHONPATH=src python3 -m unittest discover -s tests
```

Configuration can also be set via environment variables, e.g.
`EBAY_DRAFTER_MODEL=mistral`.

## Verification results

- `pip install -e .` — succeeds; `ebay-draft` entry point available
- `ebay-draft config` — prints defaults correctly
- `ebay-draft draft - --no-llm` with sample item JSON — prints title, description, profit estimate, exports JSON
- Exported JSON validated: title, description, item_details, profit_notes, model, created_at all present
- Profit math spot-check: cost $40, suggested price $70.70, fees $9.49, profit $21.21 (30% margin)
- Tests: **15 tests, 15 passed**, using Python stdlib unittest only
- No .github/workflows files present; no API keys, secrets, or personal data in any file

## Known gaps

- Requires a running OpenAI-compatible endpoint (Ollama) for real LLM drafting; `--no-llm` covers offline/template use
- Fee rate (13%) and fixed fee ($0.30) are US estimates; adjust for other regions
- No built-in eBay API integration (listing creation, category lookup, photos) — drafting only
- Interactive mode is read-only prompts; no validation of field values beyond JSON parsing
- Tested with CPython 3.13; declared `requires-python >= 3.9`
