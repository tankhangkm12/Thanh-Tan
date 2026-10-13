# Tech stack

## Stack đã chốt
<!-- required -->

| Lớp | Công nghệ | Phiên bản | TC đáp ứng | Chi tiết |
| --- | --- | --- | --- | --- |
| backend | Node.js — runtime cho order-service | 24.0 | TC-001, TC-002, TC-004 | [backend](layers/backend.md) |
| frontend | React — thư viện dựng ứng dụng order-web | 19.2 | TC-001, TC-002, TC-003 | [frontend](layers/frontend.md) |
| frontend | Vite — công cụ build order-web | 7.3 | TC-001, TC-002, TC-003 | [frontend](layers/frontend.md) |
| data | PostgreSQL — database quan hệ cho order-db | 16.4 | TC-001, TC-003, TC-004 | [data](layers/data.md) |

## Quyết định
<!-- required -->

| Lớp | Quyết định | Duyệt ngày | Rủi ro |
| --- | --- | --- | --- |
| backend | D-002 | 2026-10-12 | không có rủi ro mới |
| data | D-002 | 2026-10-12 | không có rủi ro mới |
| frontend | D-003 | 2026-10-12 | R-001 |

## Kiểm tra chéo toàn stack
<!-- required -->

Xem [compatibility.md](compatibility.md), [cost-licensing.md](cost-licensing.md), [team-readiness.md](team-readiness.md). Kết quả: không còn xung đột.
