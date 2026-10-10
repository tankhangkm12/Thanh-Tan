# dev-backend

Plugin phát triển phía server của nhóm **software-dev** (phiên bản 0.2.0). Phụ thuộc `dev-core` (quy trình, gitflow, gate dùng chung) và chỉ thêm phần nghiệp vụ backend. Không giả định ngôn ngữ hay framework: mọi thông tin kỹ thuật lấy từ cấu hình dự án.

## Có gì bên trong

| Thành phần | Vị trí | Việc làm |
|---|---|---|
| Hợp đồng extension | `extension.yaml` | Role, quy tắc đường dẫn, quy tắc plan, tool scan, gate; `agentflow ext add` đọc file này |
| Role `db-engineer` | nguồn `src/roles/db-engineer.md` | **Role duy nhất** được viết migration. Sinh agent cho cả Claude Code và Antigravity bằng `tools/build.py` |
| 6 skill | `skills/*/SKILL.md` | `api-implementation`, `business-logic`, `db-migration`, `query-review`, `backend-testing`, `contract-test` |

## Gate và tool

| Gate / tool | Khi nào | Cách hoạt động |
|---|---|---|
| Quy tắc đường dẫn | `plan check` và `agentflow commit --item` | Mục kế hoạch hay commit đụng thư mục migration phải thuộc role `db-engineer` |
| Migration lên **và** xuống | `plan check` | `done-when` của mục có migration phải chứa nguyên văn lệnh lên và lệnh xuống của dự án (chạy trên DB trong container) |
| Squawk | bước `test` | Lint migration đã đổi khi `backend.db.engine` là `postgresql`; DB khác thì bỏ qua và `summary.md`/kết quả scan ghi rõ lý do |
| Schemathesis | bước `test` | Contract test (container) khi có `backend.openapi.spec` và `backend.openapi.url`; container gọi vào máy chủ qua `host.docker.internal` |

## Dùng với một dự án

1. Cài `agentflow` và hai plugin (`dev-core`, `dev-backend`); xem [README gốc](../../../README.md).
2. Trong dự án đã `agentflow init`, **bạn** chạy (không phải agent):

   ```
   agentflow ext add "<repo>/families/software-dev/backend/extension.yaml"
   agentflow config set backend.db.engine postgresql
   agentflow config set backend.migrations_dir db/migrations
   agentflow config set backend.migrations_lint_glob "db/migrations/*.up.sql"
   agentflow config set backend.migrate_up_command "<lệnh chạy migration lên trên DB trong container>"
   agentflow config set backend.migrate_down_command "<lệnh chạy migration xuống>"
   agentflow config set backend.test_command "<lệnh chạy test>"
   agentflow config set backend.openapi.spec openapi.yaml
   agentflow config set backend.openapi.url http://localhost:8000
   agentflow config check
   ```

3. Dùng như dev-core: `/dev-core:start`, rồi `/dev-core:continue`. Mục kế hoạch migration gán `role: db-engineer`, mục còn lại gán `implementer`.
