# eBay Listing Drafter

A local-first, beginner-friendly command-line tool that drafts eBay listing
titles and descriptions from item details, using a configurable
OpenAI-compatible endpoint (Ollama by default) and adding profit-estimate
notes. No API keys, no accounts, nothing leaves your machine unless you want
it to.

Built by **Asdale Dynamics, LLC** (Indiana, formed Oct 2026) — beginner-friendly
AI education, books, and practical tools. Find more at dylanasdale.github.io
and in *The Massive AI Manual* by Dylan Asdale.

## What it does

Give it a little bit of information about an item (brand, model, condition,
size, what you paid, etc.) and it writes:

- an eBay listing title (under 80 characters)
- a friendly, honest description with bullet points and an "about the seller"
  section
- a profit-estimate note (suggested price, fees, shipping, break-even, and
  estimated profit)

Then it can save the whole thing to a local JSON file.

## How it works

The tool talks to any OpenAI-compatible chat endpoint over plain HTTP. Out of
the box it points at **Ollama** on `http://localhost:11434/v1` using the
`llama3.2` model, so everything runs locally and no API key is ever needed.
Point it at another compatible server (or set environment variables) if you
prefer.

### Example

```bash
echo '{"title":"Nike Air Max 90","brand":"Nike","model":"Air Max 90",
"condition":"Pre-owned","size":"10","purchase_price":"40","notes":"Light wear on soles"}' \
  | ebay-draft draft - --no-llm
```

`--no-llm` builds a template without calling any model — useful offline or to
preview the format.

### With a local model (Ollama)

```bash
# start Ollama and pull a model, then
ebay-draft draft item.json -o listing.json
```

## Install

```bash
pip install -e .
```

This creates the `ebay-draft` command. Requires Python 3.9+. The tool uses
only Python standard library at runtime; `pytest` is needed to run the test
suite.

## Configuration

Settings come from (in priority order): command-line flags → environment
variables → `~/.config/ebay-listing-drafter/config.json` → built-in defaults.

```bash
ebay-draft config            # show current configuration
ebay-draft config --write-example  # write an example config file
```

Environment variables:

- `EBAY_DRAFTER_BASE_URL` (default `http://localhost:11434/v1`)
- `EBAY_DRAFTER_MODEL` (default `llama3.2`)
- `EBAY_DRAFTER_TEMPERATURE` (default `0.7`)
- `EBAY_DRAFTER_TIMEOUT_SECONDS` (default `60`)
- `EBAY_DRAFTER_MAX_TOKENS` (default `800`)

## Item details

Draft from a JSON file:

```json
{
  "title": "Nike Air Max 90",
  "brand": "Nike",
  "model": "Air Max 90",
  "condition": "Pre-owned",
  "size": "10",
  "color": "Black",
  "purchase_price": 40,
  "shipping_cost": 5,
  "notes": "Light wear on soles, smoke-free home"
}
```

```bash
ebay-draft draft item.json -o listing.json
```

Omit the file argument to be prompted for each field interactively.

## Profit estimates

The tool estimates eBay fees (13% of sale price + $0.30 by default), suggests
a sale price targeting a 30% profit margin (never below break-even), and prints
a plain-language profit note with the draft.

## Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

or, with pytest installed:

```bash
pytest
```

## Local-first, no secrets

No API keys are stored or required. Ollama runs on your machine. Nothing is
sent anywhere unless you configure a remote endpoint yourself. Drafts are saved
only as local JSON files you choose.

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.
