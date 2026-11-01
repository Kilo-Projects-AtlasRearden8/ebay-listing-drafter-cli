"""Tests for the eBay listing drafter."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from ebay_listing_drafter.client import ChatClient, LLMError, ChatMessage
from ebay_listing_drafter.config import Config, CONFIG_FILE, DEFAULT_BASE_URL, DEFAULT_MODEL
from ebay_listing_drafter.draft import draft_messages, parse_draft_output, title_prompt, description_prompt
from ebay_listing_drafter.exporter import export_listing
from ebay_listing_drafter.profit import calculate, estimate_fees, break_even_price, suggested_sale_price


class TestProfit(unittest.TestCase):
    def test_fees(self):
        self.assertAlmostEqual(estimate_fees(100.0), 13.30)
        self.assertAlmostEqual(estimate_fees(0.0), 0.30)

    def test_break_even(self):
        self.assertAlmostEqual(break_even_price(50.0, 5.0), (55.0 + 0.30) / 0.87)

    def test_suggested_price_never_below_break_even(self):
        price = suggested_sale_price(1.0, 0.0, target_margin=0.90)
        self.assertGreaterEqual(price, break_even_price(1.0, 0.0))

    def test_calculate_shape(self):
        est = calculate(purchase_price=50.0, sale_price=100.0, shipping_cost=5.0)
        self.assertAlmostEqual(est.ebay_fees, 13.30)
        self.assertAlmostEqual(est.profit, 100.0 - 50.0 - 5.0 - 13.30)
        self.assertIn("Estimated profit:", est.as_notes())
        self.assertIn("$31.70", est.as_notes())

    def test_calculate_derives_sale_price(self):
        est = calculate(purchase_price=50.0, shipping_cost=5.0)
        self.assertGreater(est.sale_price, est.break_even_price)
        self.assertGreaterEqual(est.profit_margin, 25.0)

    def test_loss_warning(self):
        est = calculate(purchase_price=100.0, sale_price=50.0, shipping_cost=10.0)
        self.assertLess(est.profit, 0)
        self.assertIn("Warning", est.as_notes())


class TestDraftPrompts(unittest.TestCase):
    def test_title_prompt_contains_details(self):
        prompt = title_prompt({"brand": "Nike", "condition": "New"})
        self.assertIn("Nike", prompt)
        self.assertIn("New", prompt)
        self.assertIn("80 characters", prompt)

    def test_description_prompt_includes_profit_notes(self):
        prompt = description_prompt({"title": "Widget"}, profit_notes="Profit estimate:\n  Estimated profit: $10.00")
        self.assertIn("Profit estimate:", prompt)
        self.assertIn("$10.00", prompt)

    def test_draft_messages_structure(self):
        messages = draft_messages({"title": "Thing"})
        self.assertEqual(messages[0]["role"], "system")
        self.assertTrue(all(m["role"] in ("system", "user") for m in messages))


class TestClient(unittest.TestCase):
    def _mock_response(self, content="Drafted title\n\nDrafted description", model="llama3.2"):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(
            {"model": model, "choices": [{"message": {"content": content}}]}
        ).encode("utf-8")
        return mock_resp

    def test_chat_posts_to_endpoint(self):
        with patch("ebay_listing_drafter.client.urllib.request.urlopen") as mock_open:
            mock_open.return_value.__enter__.return_value = self._mock_response()
            client = ChatClient(base_url="http://localhost:11434/v1", model="llama3.2")
            response = client.chat([ChatMessage(role="user", content="hello")])
            self.assertIn("Drafted title", response.content)
            self.assertIn("Drafted description", response.content)
            self.assertEqual(response.model, "llama3.2")
            call_args = mock_open.call_args
            self.assertEqual(call_args.kwargs["timeout"], 60)
            req = call_args[0][0]
            self.assertEqual(req.full_url, "http://localhost:11434/v1/chat/completions")
            body = json.loads(req.data.decode("utf-8"))
            self.assertEqual(body["model"], "llama3.2")
            self.assertFalse(body["stream"])

    def test_chat_raises_on_connection_error(self):
        import urllib.error

        with patch(
            "ebay_listing_drafter.client.urllib.request.urlopen",
            side_effect=urllib.error.URLError("refused"),
        ):
            client = ChatClient(base_url="http://localhost:11434/v1", model="llama3.2")
            with self.assertRaises(LLMError):
                client.chat([ChatMessage(role="user", content="hello")])

    def test_chat_raises_on_empty_choices(self):
        with patch("ebay_listing_drafter.client.urllib.request.urlopen") as mock_open:
            mock_resp = MagicMock()
            mock_resp.read.return_value = b'{"model":"x","choices":[]}'
            mock_open.return_value.__enter__.return_value = mock_resp
            client = ChatClient(base_url="http://localhost:11434/v1", model="llama3.2")
            with self.assertRaises(LLMError):
                client.chat([ChatMessage(role="user", content="hello")])


class TestConfig(unittest.TestCase):
    def test_defaults(self):
        config = Config()
        self.assertEqual(config.base_url, DEFAULT_BASE_URL)
        self.assertEqual(config.model, DEFAULT_MODEL)

    def test_env_overrides(self):
        with patch.dict(os.environ, {"EBAY_DRAFTER_MODEL": "mistral", "EBAY_DRAFTER_BASE_URL": "http://x:1/v1"}):
            config = Config.load()
            self.assertEqual(config.model, "mistral")
            self.assertEqual(config.base_url, "http://x:1/v1")
            self.assertEqual(config.source, "environment variables")


class TestExporter(unittest.TestCase):
    def test_export_creates_json_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "listing.json")
            written = export_listing(
                path,
                title="Test Title",
                description="Test description",
                item_details={"brand": "Nike"},
                profit_notes="Profit estimate:\n  Estimated profit: $5.00",
                model="llama3.2",
            )
            self.assertEqual(Path(path), Path(written))
            with open(path, encoding="utf-8") as handle:
                record = json.load(handle)
            self.assertEqual(record["title"], "Test Title")
            self.assertEqual(record["profit_notes"], "Profit estimate:\n  Estimated profit: $5.00")
            self.assertEqual(record["model"], "llama3.2")
            self.assertIn("created_at", record)


if __name__ == "__main__":
    unittest.main()
