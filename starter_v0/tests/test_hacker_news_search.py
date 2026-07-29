from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from tools import TOOL_FUNCTIONS, load_tool_declarations
from tools._shared import TIMEOUT
from tools.hacker_news_search.tool import search_hacker_news


class HackerNewsSearchTests(unittest.TestCase):
    @patch("tools.hacker_news_search.tool.requests.get")
    def test_relevance_search_normalizes_story_for_format_tool(self, mock_get: Mock) -> None:
        response = Mock()
        response.json.return_value = {
            "nbHits": 1,
            "hits": [{
                "objectID": "123",
                "title": "An &amp; useful <em>AI</em> story",
                "url": "https://example.com/ai",
                "story_text": None,
                "author": "alice",
                "created_at": "2026-07-29T01:02:03Z",
                "points": 42,
                "num_comments": 7,
            }],
        }
        mock_get.return_value = response

        result = search_hacker_news("  AI   agents  ", max_results=1)

        self.assertNotIn("error", result)
        self.assertEqual(result["query"], "AI agents")
        self.assertEqual(result["total_results"], 1)
        self.assertEqual(len(result["items"]), 1)
        item = result["items"][0]
        self.assertEqual(item["title"], "An & useful AI story")
        self.assertEqual(item["url"], "https://example.com/ai")
        self.assertEqual(item["source"], "example.com")
        self.assertEqual(item["discussion_url"], "https://news.ycombinator.com/item?id=123")
        self.assertIn("42 points", item["summary"])

        mock_get.assert_called_once()
        call = mock_get.call_args
        self.assertEqual(call.args[0], "https://hn.algolia.com/api/v1/search")
        self.assertEqual(
            call.kwargs["params"],
            {"query": "AI agents", "tags": "story", "hitsPerPage": 1},
        )
        self.assertEqual(call.kwargs["timeout"], TIMEOUT)
        response.raise_for_status.assert_called_once_with()

    @patch("tools.hacker_news_search.tool.time.time", return_value=2_000_000_000)
    @patch("tools.hacker_news_search.tool.requests.get")
    def test_recent_search_applies_timeframe_and_clamps_limit(
        self,
        mock_get: Mock,
        _mock_time: Mock,
    ) -> None:
        response = Mock()
        response.json.return_value = {"nbHits": 0, "hits": []}
        mock_get.return_value = response

        result = search_hacker_news(
            "Python",
            sort_by="recent",
            timeframe="day",
            max_results=999,
        )

        self.assertEqual(result["items"], [])
        call = mock_get.call_args
        self.assertEqual(call.args[0], "https://hn.algolia.com/api/v1/search_by_date")
        self.assertEqual(call.kwargs["params"]["hitsPerPage"], 10)
        self.assertEqual(
            call.kwargs["params"]["numericFilters"],
            f"created_at_i>{2_000_000_000 - 86_400}",
        )

    @patch("tools.hacker_news_search.tool.requests.get")
    def test_text_post_uses_hn_discussion_as_primary_url(self, mock_get: Mock) -> None:
        response = Mock()
        response.json.return_value = {
            "nbHits": 1,
            "hits": [{
                "objectID": "456",
                "title": "Ask HN: Testing tools?",
                "url": None,
                "story_text": "<p>How do you test research agents?</p>",
                "points": 5,
                "num_comments": 2,
            }],
        }
        mock_get.return_value = response

        result = search_hacker_news("testing tools")

        item = result["items"][0]
        self.assertEqual(item["url"], "https://news.ycombinator.com/item?id=456")
        self.assertEqual(item["source"], "news.ycombinator.com")
        self.assertEqual(item["summary"], "How do you test research agents?")

    @patch("tools.hacker_news_search.tool.requests.get")
    def test_invalid_arguments_return_structured_error_without_network_call(
        self,
        mock_get: Mock,
    ) -> None:
        for kwargs in (
            {"query": ""},
            {"query": "AI", "sort_by": "popular"},
            {"query": "AI", "timeframe": "fortnight"},
        ):
            with self.subTest(kwargs=kwargs):
                result = search_hacker_news(**kwargs)
                self.assertEqual(result["tool"], "hacker_news_search")
                self.assertEqual(result["error"], "ValueError")

        mock_get.assert_not_called()

    @patch("tools.hacker_news_search.tool.requests.get")
    def test_unexpected_api_shape_returns_structured_error(self, mock_get: Mock) -> None:
        response = Mock()
        response.json.return_value = {"nbHits": 1}
        mock_get.return_value = response

        result = search_hacker_news("AI")

        self.assertEqual(result["error"], "ValueError")
        self.assertIn("'hits' must be a list", result["message"])

    def test_registry_and_yaml_declaration_are_synchronized(self) -> None:
        self.assertIs(TOOL_FUNCTIONS["hacker_news_search"], search_hacker_news)
        declarations = load_tool_declarations(
            Path(__file__).resolve().parents[1] / "artifacts" / "tools.yaml"
        )
        declaration = next(
            item for item in declarations if item["name"] == "hacker_news_search"
        )
        self.assertIn("Hacker News", declaration["description"])
        self.assertEqual(
            declaration["parameters"]["required"],
            ["query"],
        )


if __name__ == "__main__":
    unittest.main()
