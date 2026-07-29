from __future__ import annotations

import html
import re
import time
from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err


HN_SEARCH_API = "https://hn.algolia.com/api/v1"
_ALLOWED_SORTS = {"relevance", "recent"}
_TIMEFRAME_SECONDS = {
    "all": None,
    "day": 24 * 60 * 60,
    "week": 7 * 24 * 60 * 60,
    "month": 30 * 24 * 60 * 60,
    "year": 365 * 24 * 60 * 60,
}
_MAX_RESULTS = 10


def _plain_text(value: Any) -> str:
    """Turn the small HTML fragments returned for text posts into plain text."""
    unescaped = html.unescape(str(value or ""))
    without_tags = re.sub(r"<[^>]+>", " ", unescaped)
    return " ".join(without_tags.split())


def _story_item(raw: dict[str, Any]) -> dict[str, Any]:
    object_id = str(raw.get("objectID") or "").strip()
    discussion_url = (
        f"https://news.ycombinator.com/item?id={object_id}"
        if object_id
        else "https://news.ycombinator.com/"
    )
    external_url = str(raw.get("url") or "").strip()
    story_url = external_url or discussion_url
    title = _plain_text(raw.get("title") or raw.get("story_title")) or "Untitled Hacker News story"
    story_text = _plain_text(raw.get("story_text"))
    points = raw.get("points")
    comments = raw.get("num_comments")
    summary = story_text[:600]
    if not summary:
        summary = (
            "Hacker News discussion"
            f" with {points if points is not None else 0} points"
            f" and {comments if comments is not None else 0} comments."
        )

    return {
        "title": title,
        "url": story_url,
        "source": domain(story_url) or "news.ycombinator.com",
        "summary": summary,
        "discussion_url": discussion_url,
        "author": raw.get("author"),
        "date": raw.get("created_at"),
        "points": points,
        "comments": comments,
        "object_id": object_id,
    }


def search_hacker_news(
    query: str = "",
    sort_by: str = "relevance",
    timeframe: str = "all",
    max_results: int = 5,
) -> dict[str, Any]:
    """Search HN stories through Algolia and return normalized research items."""
    try:
        cleaned_query = " ".join(str(query or "").split())
        if not cleaned_query:
            raise ValueError("query must not be empty")

        normalized_sort = str(sort_by or "relevance").lower()
        if normalized_sort not in _ALLOWED_SORTS:
            allowed = ", ".join(sorted(_ALLOWED_SORTS))
            raise ValueError(f"sort_by must be one of: {allowed}")

        normalized_timeframe = str(timeframe or "all").lower()
        if normalized_timeframe not in _TIMEFRAME_SECONDS:
            allowed = ", ".join(_TIMEFRAME_SECONDS)
            raise ValueError(f"timeframe must be one of: {allowed}")

        result_limit = max(1, min(int(max_results or 5), _MAX_RESULTS))
        endpoint = "search_by_date" if normalized_sort == "recent" else "search"
        params: dict[str, Any] = {
            "query": cleaned_query,
            "tags": "story",
            "hitsPerPage": result_limit,
        }
        timeframe_seconds = _TIMEFRAME_SECONDS[normalized_timeframe]
        if timeframe_seconds is not None:
            params["numericFilters"] = f"created_at_i>{int(time.time()) - timeframe_seconds}"

        response = requests.get(
            f"{HN_SEARCH_API}/{endpoint}",
            params=params,
            headers={"User-Agent": "AI20k-Day04-Research-Agent/1.0"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        hits = data.get("hits")
        if not isinstance(hits, list):
            raise ValueError("Unexpected HN API response: 'hits' must be a list")

        items = [_story_item(hit) for hit in hits if isinstance(hit, dict)]
        return {
            "tool": "hacker_news_search",
            "query": cleaned_query,
            "sort_by": normalized_sort,
            "timeframe": normalized_timeframe,
            "total_results": data.get("nbHits"),
            "items": items[:result_limit],
        }
    except Exception as exc:
        return err("hacker_news_search", exc)
