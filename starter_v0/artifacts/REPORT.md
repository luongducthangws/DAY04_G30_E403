# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. Xong trước 16:30 để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. Có thể hoàn thiện sau buổi debate để nộp bài.

## Team

- Team: Day04 G30 E403
- Members: luongducthangDS (#1 Eval Runner), orms147 (#2 Prompt/Tool Engineer), Tri Tue (#3 Tool Dev — hacker_news_search), duong (#4 Tool Dev — datetime_utils/math_eval/text_stats), lichtchess666-ai20k (#5 Eval Case Writer), p-dat1301 (#6 UI + Deploy + Report)
- Provider/model: openrouter, openai/gpt-4o-mini

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent nội bộ: tra cứu tin tức/web, đọc nội dung một URL cụ thể, theo dõi Twitter/X (theo tài khoản hoặc theo từ khóa), tìm bài trên Hacker News, tra cứu chính sách công ty nội bộ, tìm & đọc paper arXiv, phân tích thống kê văn bản, tính toán số liệu nghiên cứu (%, tăng trưởng, trung bình), xử lý ngày tháng, tổng hợp kết quả thành digest markdown và gửi lên Telegram (luôn xác nhận yes/no trước khi gửi thật).

**Link dùng thử (truy cập được trong showdown):**

> UI chạy bằng `python server.py --port 8000` (stdlib HTTP server, không cần cài thêm). Hiện mới test local (`http://localhost:8000`); **chưa mở Cloudflare Tunnel** — cần chạy `cloudflared tunnel --url http://localhost:8000` trước showdown nếu người ngoài máy cần test.
>
> URL: (điền URL `trycloudflare.com` sau khi mở tunnel)

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin hoặc cần xác nhận yes/no | không |
| timeline | lấy bài đăng gần đây của một tài khoản Twitter/X cụ thể | không |
| social_search | tìm bài đăng trên Twitter/X theo từ khóa/chủ đề | không |
| lookup | tra cứu web/tin tức chung | không |
| fetch | đọc nội dung một URL cụ thể | không |
| format | trình bày các item đã có thành digest markdown | không |
| send | gửi văn bản lên kênh Telegram (cần xác nhận trước) | không (optional có sẵn) |
| policy | tra cứu chính sách công ty nội bộ | không (optional có sẵn) |
| papers | tìm paper trên arXiv | không (optional có sẵn) |
| paper_text | tải PDF arXiv và trích text | không (optional có sẵn) |
| hacker_news_search | tìm story trên Hacker News qua Algolia API | **có — #3** |
| datetime_utils | lấy ngày hiện tại, tính khoảng cách ngày, cộng/trừ ngày | **có — #4** |
| math_eval | tính biểu thức toán học đơn giản (%, tăng trưởng, trung bình) | **có — #4** |
| text_stats | thống kê văn bản (đếm từ/câu, thời gian đọc, URL/Email, từ khóa) | **có — #4** |

→ 4 tool mới do nhóm tự viết (> 3) — đủ điều kiện bonus.

## A3. Câu hỏi mẫu để thử

1. "Tweet mới nhất của Sam Altman là gì?"
2. "Tìm tin tức AI hôm nay trên web."
3. "Tìm trên Hacker News các bài viết về AI agents."
4. "Tính giúp mình tỷ lệ tăng trưởng từ 100 lên 150."
5. "Đăng bản tin này lên Telegram giúp mình." (kiểm tra agent có hỏi xác nhận trước khi gửi không)

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Yêu cầu gửi Telegram | `clarify(response_type=yes_no)` → (sau khi đồng ý) `send(confirmed=true)` | v0: gọi thẳng `send`, không xác nhận (FAIL) → v1+: hỏi xác nhận trước (PASS) | `runs/v0_B_base_openrouter_20260729T145327968976.json` case R12 vs `runs/v1_B_base_openrouter_20260729T152528755257.json` case R12 |
| Câu hỏi ngoài phạm vi (toán tích phân / code) | không gọi tool nào, trả lời từ chối bằng text | v0: tự trả lời rồi gọi `send` thừa (FAIL) → v1+: từ chối đúng, no_tool (PASS) | case R08/R14 trong cùng 2 run trên |
| Tìm trên Hacker News | `hacker_news_search(query=...)` | Chỉ có từ v2 trở đi (tool mới #3); trước đó không tồn tại | `runs/v2_B_base_openrouter_20260729T161715361893.json` + transcript live chat |
| Hỏi ngày một sự kiện thực tế (vd Tết Nguyên Đán) không cho ngày cụ thể | `datetime_utils` — hoặc không gọi tool nếu thiếu dữ liệu | v2: bịa ngày rồi tính `date_diff` ra kết quả vô lý (bug) → v3: hết bịa ngày để tính toán, nhưng vẫn còn trả lời bằng kiến thức riêng thay vì `lookup` (fix một phần, xem B4) | `transcripts/v2_openrouter_20260729T162444650900.transcript.json` vs `transcripts/v3_openrouter_20260729T162913999882.transcript.json` |

---

# PHẦN B — Chi tiết / Bằng chứng

> Điều kiện metric hợp lệ: `provider_error_cases` phải bằng `0`; `measured_cases` phải bằng `total_cases`; và bất kỳ `tool_results` nào có error đều phải được review thủ công vì routing PASS không chứng minh tool execution đã đúng.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | baseline (chưa sửa gì) | N/A | case_accuracy | N/A | 0.70 | `runs/v0_B_base_openrouter_20260729T145327968976.json` |
| v1 | `system_prompt.md` + `tools.yaml`: thêm scope/refuse rule, cấm đoán giá trị (bắt clarify), boundary xác nhận trước `send`, quy ước query/topic/timeframe cho `lookup`, phân biệt "gọi nhiều tool" vs "chuyển đổi nguồn" (fix regression M06 giữa 2 lần thử) | 4 nhóm lỗi gốc của v0 (out_of_scope gọi nhầm send, missing_info tự đoán, wrong_boundary không xác nhận, wrong_arg_value ở lookup) sẽ hết mà không hỏng case đang PASS | case_accuracy | 0.70 | 1.00 | `runs/v1_B_base_openrouter_20260729T152528755257.json` |
| v2 | Không đổi hypothesis chủ động — đây là bước **validate** sau khi #3 thêm `hacker_news_search`, #4 thêm `datetime_utils`/`math_eval`/`text_stats` và mở rộng scope prompt (bỏ "toán" khỏi danh sách từ chối) | 4 tool mới + scope mới không làm hỏng 20 case `eval_base` đang PASS, đặc biệt R08/R14 (out_of_scope) vẫn phải refuse dù đã có `math_eval` | case_accuracy | 1.00 | 1.00 (không regression) | `runs/v2_B_base_openrouter_20260729T161715361893.json` |
| v3 | `system_prompt.md`: thêm quy ước cho `datetime_utils` (start/end date chỉ lấy từ user hoặc tool khác, cấm bịa ngày sự kiện thực tế, phải `lookup`/`clarify` nếu thiếu) + rule "chỉ gọi tool thực sự cần thiết" | Sửa 2 lỗi phát hiện qua live-chat (không có trong eval_base): (1) bịa ngày Tết rồi tính `date_diff` ra kết quả vô lý; (2) gọi thừa `datetime_utils` cho câu hỏi `text_stats` | case_accuracy (base, không đổi) + quan sát định tính qua live chat | 1.00 / bug (1)+(2) còn nguyên | 1.00 / bug (1) fix một phần (hết bịa ngày để tính, nhưng vẫn trả lời từ kiến thức riêng thay vì `lookup`), bug (2) chưa fix | `runs/v3_B_base_openrouter_20260729T162857043923.json` |

## B2. Failure analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team eval cases

List the 10 cases added to `data/eval_group.json`:

- 5 single-turn
- 5 multi-turn

This section is for the mandatory team-authored eval set. Optional built-ins do
not belong here.

File template để trống có chủ đích; nhóm phải tự thiết kế đủ 10 case.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live chat evidence

Use `transcripts/*.transcript.json`.

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Tool capability evidence

Phân loại rõ tool mới bắt buộc, optional built-in và tool đủ điều kiện bonus. Chỉ ghi Telegram/PDF nếu nhóm thực sự dùng; base report không cần chúng.

UI is core deliverable, not bonus. Do not list it here.

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên |  |  |  |
| Optional built-in |  |  |  |
| Bonus: tool mới thứ 4 trở đi |  |  |  |

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?
