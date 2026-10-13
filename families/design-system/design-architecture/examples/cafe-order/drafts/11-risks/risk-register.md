# Sổ rủi ro

## Sổ rủi ro
<!-- required -->

| ID | Mô tả | Nhóm | Khả năng × Tác động | Thành phần liên quan | Dấu hiệu sớm | Cơ sở dấu hiệu sớm | Giảm thiểu | Phương án dự phòng | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R-001 | Trang tải chậm trên máy yếu và mạng 4G chậm, khách bỏ đặt đơn | capacity | 3 × 3 = 9 | [frontend](../02-tech-stack/layers/frontend.md) | LCP trên 2,5 s trong 7 ngày liên tiếp | NFR-001 | Lighthouse CI chặn merge khi vượt ngân sách ở [performance-budget.md](../05-frontend/performance-budget.md) | tách gói mã theo route sâu hơn, bỏ thư viện nặng nhất khỏi gói tải ban đầu | đang theo dõi |

## Ngưỡng xử lý
<!-- required -->

- 15–25 điểm: bắt buộc có giảm thiểu; nếu vẫn giữ, người dùng chấp nhận rõ ràng và trạng thái ghi "đã chấp nhận".
- 8–14 điểm: bắt buộc có giảm thiểu và dấu hiệu sớm.
- 1–7 điểm: theo dõi, có dấu hiệu sớm.

## Cảnh báo tương ứng
<!-- required -->

- R-001: kết quả Lighthouse CI mỗi lần build, xem [performance-budget.md](../05-frontend/performance-budget.md)

## Rà soát
<!-- required -->

- Lần rà gần nhất: G5, 2026-10-13
