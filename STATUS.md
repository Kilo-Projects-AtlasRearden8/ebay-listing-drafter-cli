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
  - `draft.py` — prompt builder (single LLM call with TITLE:/DESCRIPTION: markers, robust `parse_draft_output`, title capped at 80 chars)
  - `profit.py` — profit/fee/break-even calculations with suggested sale price targeting a margin
  - `exporter.py` — local JSON export with timestamp, item details, profit notes, model used
  - `cli.py` — argparse CLI: `draft` (file/stdin/interactive, `--no-llm`, `-o`), `config`
- `tests/test_drafter.py` — module unit tests (profit, prompts, client, config, exporter)
- `tests/test_cli.py` — CLI-level tests (parse_draft_output, config command, no-llm draft, main entry point)
- `example-item.json` — sample item for users to try immediately
- `pyproject.toml` — packaging with `ebay-draft` console script
- `LICENSE` — MIT, Copyright (c) 2026 Asdale Dynamics, LLC
- `README.md` — warm, beginner-friendly usage guide, credits Asdale Dynamics, LLC
- `STATUS.md` — this file

## How to run

```bash
# Install (Python 3.9+)
pip install -e .

# See current configuration (defaults: Ollama at localhost:11434/v1, model llama3.2)
ebay-draft config

# Draft from the included example item file (requires a running model endpoint)
ebay-draft draft example-item.json -o listing.json

# Draft without calling any model (template mode, works offline)
ebay-draft draft example-item.json --no-llm

# Pipe item details from stdin
cat example-item.json | ebay-draft draft -

# Interactive mode (prompts for each field)
ebay-draft draft --no-llm

# Run tests (stdlib unittest only)
PYTHONPATH=src python3 -m unittest discover -s tests
```

Configuration can also be set via environment variables, e.g.
`EBAY_DRAFTER_MODEL=mistral`.

## Verification results

- `pip install -e .` — succeeds; `ebay-draft` entry point available
- `ebay-draft config` — prints defaults correctly
- `ebay-draft draft example-item.json --no-llm` — prints title, description, profit estimate, exports JSON
- `ebay-draft draft example-item.json -o listing.json` — exports valid JSON with title, description, item_details, profit_notes, model, created_at
- Exported JSON validated end-to-end
- Profit math spot-check: cost $40 → suggested price $70.70, fees $9.49, profit $21.21 (30% margin)
- Title length capped at 80 characters
- **Tests: 24 tests, 24 passed** (Python stdlib unittest only)
- `LICENSE` copyright line is exactly `Copyright (c) 2026 Asdale Dynamics, LLC`
- README credits Asdale Dynamics, LLC
- No `.github/workflows` files present
- No API keys, secrets, or personal data in any file
- Git initialized, one commit: `55ca814 Initial release of eBay listing drafter CLI` (then subsequent improvements committed)

## Known gaps

- Real LLM drafting requires a running OpenAI-compatible endpoint (Ollama); `--no-llm` covers offline/template use
- Fee rate (13%) and fixed fee ($0.30) are US estimates; adjust for other regions
- No built-in eBay API integration (listing creation, category lookup, photos) — drafting only
- Interactive mode prompts are read-only; no field validation beyond JSON parsing
- Profit estimates are estimates, not guarantees of actual earnings
- Tested with CPython 3.13; declared `requires-python >= 3.9`
