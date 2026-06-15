# Báo cáo Day 13 Observability Lab

> **Lưu ý**: Báo cáo này giữ nguyên các tag như `[GROUP_NAME]`, `[SLO_TABLE]`, `[TASKS_COMPLETED]` để phù hợp với mẫu chấm tự động.

## 1. Thông tin nhóm
- [GROUP_NAME]: Bài nộp cá nhân - Bui Hoang Linh
- [REPO_URL]: Repository local `/home/linh/Desktop/2A202600804-BuiHoangLinh-Day13` (chưa có remote URL)
- [MEMBERS]:
  - Member A: Bui Hoang Linh - 2A202600804 | Role: Logging & PII
  - Member B: Bui Hoang Linh - 2A202600804 | Role: Tracing & Enrichment
  - Member C: Bui Hoang Linh - 2A202600804 | Role: SLO & Alerts
  - Member D: Bui Hoang Linh - 2A202600804 | Role: Load Test & Dashboard
  - Member E: Bui Hoang Linh - 2A202600804 | Role: Demo & Report

---

## 2. Kết quả tổng quan
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 32
- [PII_LEAKS_FOUND]: 0

Kết quả kiểm tra local mới nhất:

| Hạng mục | Kết quả |
|---|---:|
| Tổng số log records đã phân tích | 70 |
| Records thiếu required fields | 0 |
| Records thiếu enrichment context | 0 |
| Số correlation IDs duy nhất | 39 |
| PII leaks phát hiện được | 0 |
| Pytest | 2 passed |

Metrics runtime từ lần chạy cuối:

| Metric | Giá trị |
|---|---:|
| total_requests | 30 |
| traffic | 20 |
| error_count | 10 |
| error_rate_pct | 33.33% |
| error_breakdown | `{"RuntimeError": 10}` |
| latency_p50 | 151ms |
| latency_p95_ms | 2651ms |
| latency_p99 | 2651ms |
| quality_avg | 0.88 |
| avg_cost_usd | $0.0051 |
| total_cost_usd | $0.1028 |
| hourly_cost_usd | $0.1028 |
| tokens_in_total | 680 |
| tokens_out_total | 6719 |

---

## 3. Bằng chứng kỹ thuật

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: Chưa attach ảnh trong repository; đã kiểm chứng bằng `scripts/validate_logs.py` và `data/logs.jsonl`.
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: Chưa attach ảnh trong repository; đã kiểm chứng bằng `scripts/validate_logs.py` với kết quả `PII_LEAKS_FOUND = 0`.
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: Chưa attach ảnh trong repository; Langfuse đã ghi nhận 32 traces.
- [TRACE_WATERFALL_EXPLANATION]: Trace chính `chat-request` có các observation con gồm `rag-retrieve` và `mock-llm-generate`. Nhờ vậy có thể tách riêng latency của bước retrieval và generation để xác định request chậm do RAG hay do LLM. Input/output preview trong trace đã được sanitize trước khi gửi lên Langfuse.

Các phần đã hoàn thành:

- Triển khai middleware correlation ID trong `app/middleware.py`.
- Tái sử dụng `x-request-id` từ request nếu client gửi lên.
- Tự tạo correlation ID dạng `req-<8-char-hex>` nếu request chưa có ID.
- Gắn response headers `x-request-id` và `x-response-time-ms`.
- Bind các context vào structlog gồm `correlation_id`, `user_id_hash`, `session_id`, `feature`, `model`, và `env`.
- Ghi structured JSON logs vào `data/logs.jsonl`.
- Thêm PII scrubbing trước bước render JSON trong `app/logging_config.py`.
- Redact các loại PII trong `app/pii.py`: email, số điện thoại Việt Nam, CCCD-like ID, số thẻ tín dụng, passport-like ID, IP address, và cụm địa chỉ tiếng Việt.
- Thêm Langfuse tracing trong `app/agent.py` với sanitized input/output, tags, user hash, session ID, và nested observations cho RAG/LLM.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: Chưa attach ảnh trong repository; dashboard đã được triển khai tại route `GET /dashboard` trong `app/dashboard.py`.
- [SLO_TABLE]:

| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 2651ms |
| Error Rate | < 2% | 28d | 33.33% |
| Cost Budget | < $2.5/day | 1d | $0.1028/giờ, xấp xỉ $2.4672/ngày nếu duy trì |

Dashboard đã có đủ 6 panel yêu cầu:

1. Latency P50/P95/P99.
2. Traffic.
3. Error rate và error breakdown.
4. Cost over time.
5. Tokens in/out.
6. Quality proxy.

Đánh giá SLO hiện tại:

- Latency P95 đang đạt target 3000ms.
- Error rate đang vượt target 2% vì lần chạy cuối có 10 lỗi `RuntimeError` trên tổng 30 requests.
- Cost vẫn dưới budget $2.5/ngày nếu ngoại suy theo hourly cost hiện tại, nhưng đã khá sát ngưỡng.

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: Chưa attach ảnh trong repository; alert rules đã được cấu hình trong `config/alert_rules.yaml`.
- [SAMPLE_RUNBOOK_LINK]: `docs/alerts.md#1-high-latency-p95`

Các alert đã cấu hình:

| Alert | Severity | Condition | Runbook |
|---|---|---|---|
| high_latency_p95 | P2 | `latency_p95_ms > 2000 for 1m` | `docs/alerts.md#1-high-latency-p95` |
| high_error_rate | P1 | `error_rate_pct > 5 for 1m` | `docs/alerts.md#2-high-error-rate` |
| cost_budget_spike | P2 | `hourly_cost_usd > 0.05 for 1m` | `docs/alerts.md#3-cost-budget-spike` |

---

## 4. Incident Response
- [SCENARIO_NAME]: tool_fail / RuntimeError failures
- [SYMPTOMS_OBSERVED]: Metrics cuối cho thấy có 10 lỗi `RuntimeError`, tổng 30 requests, error rate 33.33%. Đây là lỗi vượt SLO error rate và nên kích hoạt alert `high_error_rate`.
- [ROOT_CAUSE_PROVED_BY]: Endpoint `/metrics` trả về `error_breakdown = {"RuntimeError": 10}` và `error_rate_pct = 33.33`. Các log `request_failed` tương ứng có thể được truy vết bằng `correlation_id`, `session_id`, `feature`, và `error_type`.
- [FIX_ACTION]: Tắt incident/tool path đang lỗi, kiểm tra failed traces, group logs theo `error_type`, sau đó thêm fallback/retry cho tool call bị lỗi.
- [PREVENTIVE_MEASURE]: Duy trì alert `high_error_rate`, bắt buộc log mọi failed request kèm `error_type`, và dùng correlation giữa metrics, traces, logs để debug trước khi lỗi lan sang nhiều request hơn.

Flow debug đã dùng:

1. Bắt đầu từ `/metrics` để xác định symptom: error rate tăng và breakdown là `RuntimeError`.
2. Mở các traces cùng time window và feature tag liên quan.
3. Dùng `correlation_id` để tìm log của failed requests.
4. Xác định lỗi nằm ở tool execution, retrieval, LLM generation hay schema handling.
5. Tắt incident hoặc deploy fallback fix, sau đó kiểm tra error rate giảm về dưới 2%.

---

## 5. Đóng góp cá nhân & bằng chứng

### [MEMBER_A_NAME]
- [TASKS_COMPLETED]: Bui Hoang Linh đã triển khai correlation ID propagation, structured JSON logging, log enrichment, và PII redaction.
- [EVIDENCE_LINK]: Các file local `app/middleware.py`, `app/main.py`, `app/logging_config.py`, `app/pii.py`; command `.venv/bin/python scripts/validate_logs.py` trả về 100/100.

### [MEMBER_B_NAME]
- [TASKS_COMPLETED]: Bui Hoang Linh đã triển khai Langfuse tracing với sanitized trace data, trace tags, user hash, session ID, và nested observations `rag-retrieve` / `mock-llm-generate`.
- [EVIDENCE_LINK]: Các file local `app/agent.py` và `app/tracing.py`; tổng số traces ghi nhận: 32.

### [MEMBER_C_NAME]
- [TASKS_COMPLETED]: Bui Hoang Linh đã cấu hình SLO/alert cho latency, error rate, cost budget và viết runbook cho từng alert.
- [EVIDENCE_LINK]: Các file local `config/alert_rules.yaml`, `config/slo.yaml`, và `docs/alerts.md`.

### [MEMBER_D_NAME]
- [TASKS_COMPLETED]: Bui Hoang Linh đã triển khai metrics snapshot và dashboard live đủ 6 panel yêu cầu.
- [EVIDENCE_LINK]: Các file local `app/metrics.py`, `app/dashboard.py`, `scripts/load_test.py`; dashboard có thể mở tại `GET /dashboard` khi FastAPI app đang chạy.

### [MEMBER_E_NAME]
- [TASKS_COMPLETED]: Bui Hoang Linh đã hoàn thiện blueprint report, tổng hợp evidence, mô tả incident response, và ghi lại các nội dung đã làm được.
- [EVIDENCE_LINK]: File local `docs/blueprint-template.md`; latest upstream commit trước phần implementation local là `9ac5e22`.

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: Đã triển khai cost estimation trong `app/agent.py` qua hàm `_estimate_cost`. Metrics expose `avg_cost_usd`, `total_cost_usd`, và `hourly_cost_usd`; lần chạy cuối ghi nhận `avg_cost_usd = $0.0051` và `total_cost_usd = $0.1028`.
- [BONUS_AUDIT_LOGS]: Chưa triển khai audit log tách riêng trong repository hiện tại.
- [BONUS_CUSTOM_METRIC]: Đã triển khai quality score heuristic trong `app/agent.py` qua hàm `_heuristic_quality` và expose thành `quality_avg` trong `/metrics`; lần chạy cuối ghi nhận quality average là `0.88`.
