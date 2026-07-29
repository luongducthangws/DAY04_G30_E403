# datetime_utils Tool

## Overview

Tool `datetime_utils` giúp Agent tra cứu thời gian hiện tại, tính khoảng cách giữa 2 mốc ngày tháng, hoặc cộng/trừ số ngày để xác định khoảng thời gian nghiên cứu (timeframe).

Các action hỗ trợ:
- `current_time`: Lấy ngày giờ hiện tại (UTC hoặc múi giờ địa phương).
- `date_diff`: Tính số ngày chênh lệch giữa 2 mốc ngày (`YYYY-MM-DD`).
- `add_days`: Cộng hoặc trừ n ngày từ 1 mốc ngày (`YYYY-MM-DD`).

## Parameters

| Argument | Type | Required | Description |
|---|---|---|---|
| `action` | `string` | Yes | Một trong các hành động: `current_time`, `date_diff`, `add_days`. |
| `start_date` | `string` | No | Ngày bắt đầu (`YYYY-MM-DD`), bắt buộc khi dùng `date_diff` hoặc `add_days`. |
| `end_date` | `string` | No | Ngày kết thúc (`YYYY-MM-DD`), dùng khi `action="date_diff"`. |
| `days` | `integer` | No | Số ngày cần cộng (hoặc số âm để trừ), dùng khi `action="add_days"`. |

## Contract Output Format

```json
{
  "action": "current_time",
  "result": "2026-07-29",
  "details": {
    "iso_datetime": "2026-07-29T15:45:00Z",
    "year": 2026,
    "month": 7,
    "day": 29
  },
  "error": null
}
```
