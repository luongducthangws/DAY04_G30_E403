from __future__ import annotations

import re
from collections import Counter
from typing import Any

# Extended list of common English & Vietnamese stop words to filter out top keywords
STOP_WORDS = {
    # English
    "a", "an", "the", "and", "or", "but", "if", "because", "as", "what", "which",
    "this", "that", "these", "those", "then", "just", "so", "than", "such",
    "when", "who", "how", "where", "why", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "for", "with", "about",
    "against", "between", "into", "through", "during", "before", "after", "above",
    "below", "to", "from", "up", "upon", "down", "in", "out", "on", "off", "over",
    "under", "again", "further", "then", "once", "here", "there", "all", "any",
    "both", "each", "few", "more", "most", "other", "some", "no", "nor", "not",
    "only", "own", "same", "than", "too", "very", "can", "will", "should", "now",
    # Vietnamese
    "và", "hoặc", "nhưng", "nếu", "vì", "như", "là", "của", "cho", "trong", "trên",
    "dưới", "với", "về", "được", "bị", "bởi", "ra", "vào", "đã", "đang", "sẽ",
    "các", "những", "một", "này", "khi", "đó", "người", "theo", "tại", "có", "không",
    "để", "đến", "nhiều", "hơn", "cũng", "từ"
}

URL_PATTERN = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
WORD_PATTERN = re.compile(r'\b[a-zA-Z0-9_\u00C0-\u024F\u1E00-\u1EFF]{2,}\b')


def text_stats(text: str = "", top_keywords_limit: int = 5) -> dict[str, Any]:
    """Analyzes a block of text and returns statistics, keywords, URLs, and emails.

    Args:
        text: The text to analyze.
        top_keywords_limit: Number of top keywords to extract (default: 5).

    Returns:
        Dictionary containing counts, reading time, extracted URLs, emails, and top keywords.
    """
    if not isinstance(text, str) or not text.strip():
        return {
            "word_count": 0,
            "char_count": 0,
            "line_count": 0,
            "sentence_count": 0,
            "reading_time_minutes": 0,
            "extracted_urls": [],
            "extracted_emails": [],
            "top_keywords": [],
            "error": "Input text is empty or invalid.",
        }

    try:
        char_count = len(text)
        lines = text.splitlines()
        line_count = len(lines)

        # Sentences approximation split by . ! ?
        sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
        sentence_count = len(sentences)

        # Words extraction
        all_words = WORD_PATTERN.findall(text)
        word_count = len(all_words)

        # Estimated reading time (average 200 words per minute)
        reading_time_minutes = max(1, round(word_count / 200)) if word_count > 0 else 0

        # URLs and Emails extraction
        extracted_urls = list(set(URL_PATTERN.findall(text)))
        extracted_emails = list(set(EMAIL_PATTERN.findall(text)))

        # Top keywords (case-insensitive, excluding stop words and numbers)
        filtered_words = [
            w.lower() for w in all_words
            if w.lower() not in STOP_WORDS and not w.isdigit() and len(w) > 2
        ]
        keyword_counts = Counter(filtered_words).most_common(top_keywords_limit)
        top_keywords = [{"word": word, "count": count} for word, count in keyword_counts]

        return {
            "word_count": word_count,
            "char_count": char_count,
            "line_count": line_count,
            "sentence_count": sentence_count,
            "reading_time_minutes": reading_time_minutes,
            "extracted_urls": extracted_urls,
            "extracted_emails": extracted_emails,
            "top_keywords": top_keywords,
            "error": None,
        }
    except Exception as exc:
        return {
            "word_count": 0,
            "char_count": 0,
            "line_count": 0,
            "sentence_count": 0,
            "reading_time_minutes": 0,
            "extracted_urls": [],
            "extracted_emails": [],
            "top_keywords": [],
            "error": f"Failed to analyze text stats: {exc}",
        }
