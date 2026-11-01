"""CLI-level tests for the eBay listing drafter."""

from __future__ import annotations

import argparse
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from ebay_listing_drafter.cli import build_parser, cmd_draft, cmd_config, main
from ebay_listing_drafter.draft import parse_draft_output


class TestParseDraftOutput(unittest.TestCase):
    def test_markers(self):
        text = 'TITLE: Nike Shoes Size 10\n\nDESCRIPTION: Great shoes.\n- Size: 10'
        title, desc = parse_draft_output(text)
        self.assertEqual(title, "Nike Shoes Size 10")
        self.assertIn("Great shoes", desc)
        self.assertIn("Size: 10", desc)

    def test_title_capped_at_80_chars(self):
        long_title = "A" * 100
        text = f"TITLE: {long_title}\n\nDESCRIPTION: some description"
        title, desc = parse_draft_output(text)
        self.assertLessEqual(len(title), 80)
        self.assertTrue(title.endswith("..."))

    def test_no_markers_fallback(self):
        text = "First line title\n\nSome description text here."
        title, desc = parse_draft_output(text)
        self.assertEqual(title, "First line title")
        self.assertIn("Some description text here", desc)

    def test_empty_input(self):
        title, desc = parse_draft_output("")
        self.assertEqual(title, "")
        self.assertEqual(desc, "")

    def test_quoted_title(self):
        text = 'TITLE: "Nike Shoes"\n\nDESCRIPTION: nice shoes'
        title, desc = parse_draft_output(text)
        self.assertEqual(title, "Nike Shoes")
        self.assertIn("nice shoes", desc)


class TestCmdConfig(unittest.TestCase):
    def test_config_prints(self):
        parser = build_parser()
        args = parser.parse_args(["config"])
        with patch("sys.stdout", new_callable=io.StringIO) as out:
            result = cmd_config(args)
        self.assertEqual(result, 0)
        output = out.getvalue()
        self.assertIn("Base URL:", output)
        self.assertIn("Model:", output)

    def test_config_write_example(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_file = os.path.join(tmp, "config.json")
            with patch("ebay_listing_drafter.cli.CONFIG_FILE", Path(config_file)):
                parser = build_parser()
                args = parser.parse_args(["config", "--write-example"])
                result = cmd_config(args)
            self.assertEqual(result, 0)
            self.assertTrue(os.path.exists(config_file))
            with open(config_file, encoding="utf-8") as handle:
                data = json.load(handle)
            self.assertIn("base_url", data)
            self.assertIn("model", data)


class TestCmdDraftNoLLM(unittest.TestCase):
    def test_no_llm_from_stdin(self):
        item_json = json.dumps(
            {"title": "Nike Air Max", "brand": "Nike", "model": "Air Max",
             "condition": "Pre-owned", "size": "10", "purchase_price": "40"}
        )
        parser = build_parser()
        args = parser.parse_args(["draft", "-", "--no-llm", "-o", "/tmp/kilo/cli_test.json"])
        with patch("sys.stdin", io.StringIO(item_json)):
            with patch("sys.stdout", new_callable=io.StringIO) as out:
                result = cmd_draft(args)
        self.assertEqual(result, 0)
        output = out.getvalue()
        self.assertIn("DRAFTED TITLE", output)
        self.assertIn("DRAFTED DESCRIPTION", output)
        self.assertIn("Profit estimate", output)
        self.assertTrue(os.path.exists("/tmp/kilo/cli_test.json"))
        with open("/tmp/kilo/cli_test.json", encoding="utf-8") as handle:
            record = json.load(handle)
        self.assertEqual(record["title"], "Nike Air Max Pre-owned - Nike Air Max")


class TestMain(unittest.TestCase):
    def test_main_no_llm(self):
        item_json = json.dumps({"title": "Test Item", "brand": "TestBrand"})
        test_args = ["draft", "-", "--no-llm"]
        with patch("sys.argv", ["ebay-draft"] + test_args):
            with patch("sys.stdin", io.StringIO(item_json)):
                with patch("sys.stdout", new_callable=io.StringIO):
                    result = main()
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
