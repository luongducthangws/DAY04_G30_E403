---
name: hacker_news_search
track: core
kind: live_api
provider: Hacker News Search by Algolia
requires_env: []
inputs: [query, sort_by, timeframe, max_results]
outputs: [items, total_results]
side_effect: false
---
# hacker_news_search

Searches Hacker News stories through the public Algolia HN Search API. The
tool is read-only and does not require an API key.

## Routing boundary

- Use this tool only when the user explicitly requests Hacker News or HN as a
  source.
- Use `lookup` for general web/news research when Hacker News is not requested.
- Use `timeline` or `social_search` for Twitter/X content.
- This tool searches stories; it does not publish, vote, comment, or fetch the
  full content of an external article.

## Arguments

- `query`: non-empty topic or keywords to search for.
- `sort_by`: `relevance` for the best matching stories, or `recent` for newest
  matching stories first.
- `timeframe`: `all`, `day`, `week`, `month`, or `year`.
- `max_results`: number of stories to return, clamped to 1–10.

## Output contract

`items` follows the shared research-item shape used by `format`: every item has
`title`, `url`, `source`, and `summary`. It also includes `discussion_url`,
`author`, `date`, `points`, `comments`, and `object_id`.

If a story links to an external article, `url` is that article and
`discussion_url` is the Hacker News discussion. For text-only HN posts, both
links point to the Hacker News discussion.

## Safe smoke test

From `starter_v0/`:

```bash
python -c "from tools import TOOL_FUNCTIONS as T; r=T['hacker_news_search']('AI agents', max_results=1); items=r.get('items') or []; print({'error':r.get('error'), 'item_count':len(items), 'first_title':items[0].get('title') if items else None})"
```

PASS when `error` is `None` and at least one item is returned.
