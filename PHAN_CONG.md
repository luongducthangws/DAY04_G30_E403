# Phân công nhóm — Day 04 Lab v2 (Research Agent Tool Eval)

## Tình trạng hiện tại

- `.env` đã cấu hình xong tại `starter_v0/.env` (OpenRouter + Tavily + Firecrawl + RapidAPI Twitter).
- Baseline `v0` đã chạy: `runs/v0_B_base_openrouter_20260729T145327968976.json`
  - `case_accuracy = 0.70`, `tool_routing_accuracy = 0.75`, `argument_accuracy = 0.70`, `multiturn_accuracy = 1.00`
  - `provider_error_cases = 0`, `measured_cases = 20/20` → metric hợp lệ để so sánh.
  - Failure chính: `out_of_scope` (2), `missing_info` (2), `wrong_boundary` (1), `wrong_tool` (1); mismatch chủ yếu là `missing_tool_call` (3) và `unexpected_tool_call` (2).
- Việc tiếp theo: dựa vào các failure trên để đặt giả thuyết cho `v1`.

## Bảng phân công

| # | Người phụ trách | Vai trò | Việc chính | File sở hữu | Deadline gợi ý |
|---|---|---|---|---|---|
| 1 | _(điền tên)_ | Eval Runner / Lead | Preflight provider, chạy `v1`/`v2`/`v3`, chạy `parse_runs.py`, tổng hợp metric cho cả nhóm | `runs/`, `analysis/`, `.env` | Xuyên suốt buổi |
| 2 | _(điền tên)_ | Prompt/Tool Engineer | Đọc `observed_mismatch`/`failures` mỗi run, đặt giả thuyết, sửa prompt & tool schema, ghi version log — làm cặp sát với #1 | `artifacts/system_prompt.md`, `artifacts/tools.yaml`, `artifacts/version_log.csv` | Song song #1 |
| 3 | _(điền tên)_ | Tool Dev A | Viết tool mới #1 (bắt buộc): `TOOL.md` + `tool.py`, đăng ký `tools/__init__.py` + `tools.yaml`, smoke-test | `tools/<tool_moi_1>/` | Trước 15:50 |
| 4 | _(điền tên)_ | Tool Dev B | Viết tool mới #2, #3 (để đạt bonus >3 tool) nếu kịp; nếu không, hỗ trợ #3 test bằng `chat.py` | `tools/<tool_moi_2>/`, `tools/<tool_moi_3>/` | Trước 16:30 |
| 5 | _(điền tên)_ | Eval Case Writer | Thiết kế đúng 10 case trong `eval_group.json` (5 single-turn + 5 multi-turn), phủ đủ 6 `failure_type`, đối chiếu schema mẫu | `data/eval_group.json` | Trước 16:30 |
| 6 | _(điền tên)_ | UI + Deploy + Report | Xây `app.py` (Streamlit, tái dùng `run_model_tool_loop`), test local, mở Cloudflare Tunnel, viết `REPORT.md` Phần A trước 16:30 rồi Phần B cuối buổi bằng evidence cả nhóm | `app.py`, `requirements.txt`, `artifacts/REPORT.md` | Phần A: 16:30 / Phần B: 17:35 |

## Phụ thuộc cần lưu ý

- #3 phải hoàn thành tool + đăng ký vào `tools.yaml` **trước khi** #1/#2 chạy `v1`, nếu tool mới cần xuất hiện trong routing.
- #5 nên chờ `system_prompt.md`/`tools.yaml` tương đối ổn định (~sau v1) rồi mới chốt case, tránh phải sửa lại theo checklist rename tool.
- #6 cần số liệu (`case_accuracy`, `tool_routing_accuracy`...) từ #1 liên tục để cập nhật Report — nên có kênh riêng để #1 post metric sau mỗi run.
- Không ai được sửa `data/eval_base.json`, trừ field tên tool khi rename theo checklist trong README.
- Nếu đổi tên tool bất kỳ lúc nào, phải đồng bộ cả 8 file theo checklist trong README (`system_prompt.md`, `tools.yaml`, `TOOL.md`, `tools/__init__.py`, `eval_base.json`, `eval_research_extension.json`, `eval_group.json`, `REPORT.md`).

## Map theo checkpoint buổi chiều (14:00–18:00)

| Giờ | Checkpoint | Ai chủ trì |
|---|---|---|
| 14:00–14:15 | Kickoff, chia vai, mở `starter_v0/` | Cả nhóm |
| 14:15–14:40 | Setup môi trường, API keys, preflight | #1 |
| 14:40–15:15 | Baseline v0 (**đã xong**), đọc 1 failed trace, dựng UI local, ghi 4 metric | #1, #2, #6 |
| 15:15–15:50 | Sửa giả thuyết, hoàn thiện tool mới, chạy v1, cập nhật version log | #2, #3 |
| 15:50–16:05 | Nghỉ | — |
| 16:05–16:30 | Hoàn thành 10 eval case, evidence v2, 3 kịch bản demo, Report A, rehearsal | #5, #1, #2, #6 |
| 16:30–17:15 | Showdown: giới thiệu, live test, challenge | Cả nhóm |
| 17:15–17:35 | Áp dụng feedback, chạy v3, hoàn thiện Report B | #2, #6 |
| 17:35–17:40 | Final gate, chuẩn bị nộp `starter_v0/` | #1 |
| 17:40–18:00 | Kahoot Recap | Cả nhóm |
