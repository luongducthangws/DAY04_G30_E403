# text_stats Tool

## Overview

Tool `text_stats` dùng để phân tích và thống kê các chỉ số văn bản thu thập từ web (`fetch`), bài báo khoa học (`paper_text`) hoặc thông tin tra cứu.

Các tính năng:
- Đếm số từ, số ký tự, số dòng, số câu.
- Ước tính thời gian đọc (reading time in minutes).
- Trích xuất danh sách các URL, Email tìm thấy trong văn bản.
- Trích xuất các từ khóa (keywords) xuất hiện nhiều nhất.

## Parameters

| Argument | Type | Required | Description |
|---|---|---|---|
| `text` | `string` | Yes | Nội dung văn bản cần phân tích thống kê. |
| `top_keywords_limit` | `integer` | No (default: 5) | Số lượng từ khóa phổ biến cần liệt kê. |

## Contract Output Format

```json
{
  "word_count": 120,
  "char_count": 750,
  "line_count": 10,
  "sentence_count": 8,
  "reading_time_minutes": 1,
  "extracted_urls": ["https://example.com"],
  "extracted_emails": ["contact@example.com"],
  "top_keywords": [
    {"word": "research", "count": 12},
    {"word": "agent", "count": 8}
  ],
  "error": null
}
```
