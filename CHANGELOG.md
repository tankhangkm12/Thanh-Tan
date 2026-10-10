# Changelog

Mọi thay đổi đáng chú ý của repo này được ghi ở đây. Định dạng theo [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

Repo chứa nhiều thành phần có số phiên bản riêng: `agentflow` (foundation), `dev-core`, `dev-backend`. Số phiên bản hiện tại: agentflow 0.5.0, dev-core 0.4.0, dev-backend 0.2.0. Chưa có bản phát hành (tag) nào; bản đầu tiên dự kiến là `v1.0.0` (xem [docs/release.md](docs/release.md)).

## [Unreleased]

### Added

- Tài liệu release gitflow cho người làm tay: [docs/release.md](docs/release.md).
- `CHANGELOG.md`.

- Tier theo mục kế hoạch: `tier: fast|deep` (thiếu là deep), `plan check` kiểm giá trị, `agentflow plan assign` cho biết agent nào nhận mục nào, `tiered_roles` trong `workflow.yaml`.
- `dev-core`: hai agent `implementer-fast` (Claude Code `sonnet`/`low`, Antigravity `flash`) và `implementer-deep` (`opus`/`medium`, `pro`) sinh từ `variants` trong nguồn role; `db-engineer` là một agent ở mức mạnh nhất. `tools/build.py` kiểm model/effort theo tài liệu từng CLI. Skill `continue` giao từng mục cho đúng agent.
- Luật plan `layer-order`: quy ước `layers:` (thứ tự các lớp) và `scope:` (tùy chọn) do dự án khai báo; mặc định kiểm trên toàn bộ kế hoạch. `agentflow decide --layers --scope`.
- `summary.md` ghi tier và layer của từng mục.
- Chế độ nhẹ: `agentflow task new --size small|normal` (mặc định `normal`). Mục `sizes` trong `workflow.yaml` mô tả cỡ (bước bỏ duyệt, số mục kế hoạch tối đa, tool scan theo bước); `small` của dev-core bỏ duyệt `plan` (vẫn kiểm `plan check`), tối đa 3 mục, bước `security` chỉ chạy Gitleaks và Semgrep. Size nằm trong `state.json`, `STATE.md`, `status` và `summary.md`. Skill `start` và prompt planner biết cỡ nhỏ.

### Changed

- Agent `dev-core:implementer` được thay bằng `dev-core:implementer-fast` và `dev-core:implementer-deep` (role trong kế hoạch vẫn là `implementer`).
- README liệt kê đủ 7 role của `dev-core` (thêm `scout`).
- `families/software-dev/README.md`: mục gate bằng tool mô tả Semgrep, Trivy, Gitleaks, Squawk, Schemathesis và các gate của plan/review.
- `docs/architecture.md`: thêm lệnh `agentflow hook`, danh sách lệnh chỉ người được chạy trong guard đầy đủ.

## Các mốc trước khi có bản phát hành

Các mục dưới đây tóm tắt lịch sử `git log`, theo thứ tự mốc.

### M13 - smoke và chuẩn bị phát hành (agentflow 0.5.0, dev-core 0.4.0, dev-backend 0.2.0)

- Smoke test của dev-core và dev-backend bao quát setup, thứ tự kế hoạch, câu hỏi, quy ước, gate review.
- Kiểm tra cài đặt xác nhận scout, skill setup và server MCP trong cả hai CLI.
- File khóa phụ thuộc `uv.lock` cho agentflow 0.5.0.

### M12 - quy ước và kho kiến thức

- Quy ước từ ba nguồn (`decisions/` > `project/conventions.md` > kho cá nhân), lệnh `agentflow conventions` và tool MCP `conventions`.
- Ba cách kiểm quy ước: `plan` (luật `item-order`, trường `kind`), `semgrep` (rule do người viết, chạy trong container chỉ đọc) và `review` (gate `conventions-reviewed`).
- Câu hỏi "Chưa có quy ước" trong kế hoạch chặn cho tới khi người trả lời bằng `agentflow decide --answer`.
- Kho kiến thức cá nhân ngoài mọi repo (`knowledge init|pull|push`), tool MCP `knowledge_search`/`knowledge_read` chỉ đọc.
- Bài học đề xuất ở cuối báo cáo review được tách thành file khi seal.

### M11 - scout và hồ sơ dự án

- Role `scout` và skill `setup` hồ sơ hóa dự án vào `.agentflow/project/`.
- Tool MCP `project_write`; quy ước agent ghi luôn là `unconfirmed`, chỉ người `agentflow project confirm`.
- `agentflow task new` cảnh báo khi còn quy ước chưa xác nhận.

### M10 - server MCP

- `agentflow mcp serve` (SDK `mcp`, stdio) với các tool `status`, `next_step`, `plan_check`, `report_write`, `scan_summary`; `WorkspaceService` dùng chung cho CLI và MCP.
- Báo cáo chỉ ghi được cho bước hiện tại đang chạy; báo cáo của bước đã qua là cuối cùng.
- Server tìm dự án qua `cwd`, `AGENTFLOW_PROJECT_DIR`, `PWD` rồi con trỏ `~/.agentflow/active-project.txt` (cho Antigravity).
- Agent của Claude Code nhận tên tool MCP đầy đủ theo role; ghi chú thử thật trong [docs/mcp-notes.md](docs/mcp-notes.md).

### M9 - bảo vệ workspace

- Hook chặn tool ghi file của cả hai CLI và lệnh shell ghi vào `.agentflow/` (mức cố gắng tốt nhất).
- `AGENTFLOW_HOOK_LOG` để chẩn đoán hook.

### M8 - smoke dev-backend

- Smoke end-to-end trên dự án mẫu (PostgreSQL trong Docker, migration lên/xuống, OpenAPI) và kiểm tra cài đặt trong cả hai CLI.

### M7 - extension và dev-backend 0.1.0

- Hợp đồng extension: role, luật đường dẫn, luật plan, tool scan, gate; lệnh `ext` và `config`.
- `dev-backend`: role `db-engineer`, 6 skill, Squawk và Schemathesis.

### M6 - scan (agentflow 0.3.0)

- `agentflow scan` chạy Semgrep, Trivy, Gitleaks trong container (image ghim phiên bản, repo mount chỉ đọc); gate `scans-clean`; `agentflow decide --suppress` cho báo nhầm.

### M5 - dev-core 0.3.0 (agentflow 0.2.0)

- Skill và role chạy từng bước theo vòng lặp, không nối lệnh agentflow, không push/merge/PR.
- Planner kiểm kế hoạch bằng `plan check`; gate `plan-valid`.
- Task xong được seal: `summary.md` và tag duyệt `agentflow/<task>/approved`; commit gắn với mục kế hoạch (`Plan-Item`).
- Guard chặn `git commit` trực tiếp, tag duyệt giả và các lệnh chỉ người được chạy.

### M4 - cài đặt và smoke

- Hướng dẫn cài từng bước cho Claude Code và Antigravity; smoke test end-to-end trên repo tạm.

### M3 - nội dung dev-core (dev-core 0.2.0)

- Skill `start`, `continue`, `status`, `approve`; sáu role sinh từ một nguồn bằng `tools/build.py` cho cả hai CLI.

### M2 - hook

- `agentflow hook` với adapter cho Claude Code và Antigravity; hook của `dev-core`.

### M1 - vòng đời task

- Chuyển trạng thái task thuần (không I/O), vòng làm lại `max_rounds`, `task new|advance|approve|cancel`, `report`, `commit` có quét secret Gitleaks, `guard` chặn lệnh git nguy hiểm.

### M0 - bộ khung và workspace

- Bộ khung repo: marketplace, các plugin `dev-*`, README.
- `agentflow`: `doctor`, `init`, `status`, `next`, `workflow sync`; `.agentflow/` (state, `STATE.md`, bản chép workflow) loại khỏi git qua `.git/info/exclude`.
