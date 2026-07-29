# math_eval Tool

## Overview

Tool `math_eval` thực hiện các phép tính toán học an toàn (Safe AST mathematical evaluation) để hỗ trợ Research Agent tính toán số liệu thu thập được.

Các biểu thức hỗ trợ:
- Phép tính cơ bản: `+`, `-`, `*`, `/`, `**` (lũy thừa), `%` (chia lấy dư).
- Các hàm toán học: `abs`, `round`, `min`, `max`, `sum`, `pow`.
- Tính phần trăm (ví dụ: `(150 - 100) / 100 * 100`).

## Parameters

| Argument | Type | Required | Description |
|---|---|---|---|
| `expression` | `string` | Yes | Biểu thức toán học dạng chuỗi, ví dụ: `"(120 + 80) / 2"` hoặc `"round(150.55, 1)"`. |

## Contract Output Format

```json
{
  "expression": "(120 + 80) / 2",
  "result": 100.0,
  "formatted_result": "100",
  "error": null
}
```
