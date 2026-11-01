# eBay Listing Drafter

A friendly, local-first command-line tool that helps you write eBay listing
titles and descriptions from your item details — and adds a plain-language
profit estimate so you know what you might make before you list.

Built by **Asdale Dynamics, LLC** (Indiana, formed October 2026). We create
beginner-friendly AI education, books, and practical tools you can actually use.
Find more at [dylanasdale.github.io](https://dylanasdale.github.io) and in
*The Massive AI Manual* by Dylan Asdale.

## Who this is for

You don't need to be a developer or an AI expert to use this. If you sell on
eBay — clothes, books, electronics, collectibles, whatever — and you want a
quick, decent listing draft without staring at a blank screen, this tool is for
you.

It runs on your own computer. No API keys. No accounts. No personal data
leaves your machine unless you choose to send it somewhere.

## What it does

Give it a little bit of information about an item (brand, model, condition,
size, what you paid, etc.) and it writes:

- **A listing title** — under 80 characters, with the key details buyers search
  for
- **A friendly description** — short paragraphs, bullet points, honest about
  condition, with an "about the seller" section at the end
- **A profit-estimate note** — suggested sale price, estimated eBay fees,
  shipping, break-even price, and your estimated profit

It can then save the whole draft to a local JSON file you can open, edit, or
paste into eBay.

## How it works

The tool talks to any OpenAI-compatible chat endpoint over plain HTTP. Out of
the box it points at **Ollama** running on your own computer
(`http://localhost:11434/v1`, model `llama3.2`), so everything happens locally
and no API key is ever needed.

Prefer a different compatible server? You can change the endpoint with a
command-line flag, an environment variable, or a small config file.

## Install

You need Python 3.9 or newer.

```bash
pip install -e .
```

This gives you the `ebay-draft` command. At runtime the tool uses only the
Python standard library — nothing else to install.

## Try it right away

We've included an example item file (`example-item.json`) so you can see how it
works without typing anything:

```bash
ebay-draft draft example-item.json -o my-listing.json
```

That drafts a title and description for a pair of Nike Air Max 90s and saves
the result to `my-listing.json`.

### Without a model running (offline template mode)

If you don't have Ollama (or any model endpoint) running yet, use `--no-llm` to
build a simple template draft without calling any AI:

```bash
ebay-draft draft example-item.json --no-llm
```

You can also pipe item details from a file or stdin:

```bash
cat example-item.json | ebay-draft draft -
```

### Interactive mode

Run `ebay-draft draft` with no file and it will ask you for each item detail
one at a time. Just press Enter to skip any field you don't know.

## Configuration

Settings come from (in order of priority):

1. Command-line flags
2. Environment variables
3. `~/.config/ebay-listing-drafter/config.json`
4. Built-in defaults

See what's currently active:

```bash
ebay-draft config
```

Write an example config file:

```bash
ebay-draft config --write-example
```

Environment variables you can set:

| Variable | Default | What it does |
|---|---|---|
| `EBAY_DRAFTER_BASE_URL` | `http://localhost:11434/v1` | Your OpenAI-compatible endpoint |
| `EBAY_DRAFTER_MODEL` | `llama3.2` | Model name to use |
| `EBAY_DRAFTER_TEMPERATURE` | `0.7` | Creativity (0.0 = more predictable) |
| `EBAY_DRAFTER_TIMEOUT_SECONDS` | `60` | How long to wait for a response |
| `EBAY_DRAFTER_MAX_TOKENS` | `800` | Maximum length of the model's reply |

## Item details format

The tool reads item details from a JSON file. Here's an example:

```json
{
  "title": "Nike Air Max 90",
  "brand": "Nike",
  "model": "Air Max 90",
  "condition": "Pre-owned",
  "category": "Shoes",
  "size": "10",
  "color": "Black",
  "weight": "1.2 lbs",
  "purchase_price": 40,
  "shipping_cost": 5,
  "notes": "Light wear on soles, smoke-free home"
}
```

You can include as many or as few fields as you like. Leave out anything you
don't know — the tool will be honest about it in the description.

## Profit estimates

If you provide a `purchase_price`, the tool adds a profit-estimate note to your
draft. It estimates eBay fees (about 13% of the sale price plus $0.30 by
default), suggests a sale price that targets a 30% profit margin, and never
suggests below your break-even point.

The numbers are estimates to help you decide — they're not a guarantee of what
you'll actually make.

## Tests

The test suite uses Python's built-in `unittest` (no extra packages needed):

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

If you have `pytest` installed, you can also run:

```bash
pytest
```

## Local-first, no secrets

This tool is local-first by design:

- **No API keys** are required or stored anywhere
- **Ollama runs on your computer**, so your item details don't leave your
  machine unless you point the tool at a remote endpoint yourself
- Drafts are saved only to local JSON files that you choose
- No personal data, secrets, or keys are ever written into the source code

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.
