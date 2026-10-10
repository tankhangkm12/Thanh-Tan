# Nhóm software-dev

> **Bản nháp.** Chuẩn của nhóm còn đang định hình; mọi mục dưới đây có thể đổi trước khi có skill/agent thật.

Nhóm plugin phục vụ phát triển phần mềm. `dev-core` giữ chuẩn chung của nhóm; các plugin con (`dev-design`, `dev-backend`, `dev-frontend`, `dev-infra`) phụ thuộc vào `dev-core` và chỉ thêm phần nghiệp vụ riêng.

| Plugin | Phạm vi |
|---|---|
| `dev-core` | Quy trình, gitflow, gate dùng chung |
| `dev-design` | Thiết kế giao diện (UI brief, design token, component spec) và thiết kế hệ thống (ADR, sơ đồ C4, contract API OpenAPI, data model) |
| `dev-backend` | Service, API, dữ liệu |
| `dev-frontend` | Giao diện, state phía client |
| `dev-infra` | CI/CD, container, triển khai |

## Quy trình 7 bước

1. **Yêu cầu**: làm rõ mục tiêu, phạm vi, tiêu chí chấp nhận.
2. **Thiết kế**: thiết kế giao diện (UI brief, design token, component spec) và thiết kế hệ thống (ADR, sơ đồ C4, contract OpenAPI, data model).
3. **Lập kế hoạch**: chia việc thành task nhỏ nhất, mỗi task có tiêu chí xong kiểm được bằng lệnh.
4. **Triển khai**: làm từng task trên nhánh feature.
5. **Kiểm thử**: chạy test và các gate tự động; chỉ đi tiếp khi xanh.
6. **Review**: người duyệt xem diff, kết quả gate và các việc còn mở.
7. **Bàn giao**: merge theo gitflow, gắn tag phiên bản, ghi lại thay đổi.

## Gitflow

- `main`: chỉ chứa bản đã phát hành.
- `develop`: nhánh tích hợp; mọi nhánh feature tách từ đây.
- `feature/<tên>`: một việc một nhánh, commit nhỏ, merge về `develop` sau review.
- `release/<phiên bản>` và `hotfix/<tên>`: theo gitflow chuẩn khi cần.
- Agent không tự `push`, không tự merge vào `main`/`develop`, không tạo PR khi chưa được phép.

## Gate bằng tool

Một bước chỉ được coi là xong khi tool xác nhận, không dựa vào nhận định của agent:

- Test: `uv run pytest` (hoặc test runner của dự án) phải xanh.
- Manifest plugin: `claude plugin validate` và `agy plugin validate` phải qua.
- Bí mật: quét Gitleaks phải sạch trước khi push.
- Các gate khác (lint, type check, build) sẽ được bổ sung theo từng plugin con.
