# Sổ rủi ro

## Sổ rủi ro
<!-- required -->

| ID | Mô tả | Nhóm | Khả năng × Tác động | Thành phần liên quan | Dấu hiệu sớm | Cơ sở dấu hiệu sớm | Giảm thiểu | Phương án dự phòng | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R-001 | Trang tải chậm trên máy yếu và mạng 4G chậm, khách bỏ đặt đơn | capacity | 3 × 3 = 9 | [frontend](../02-tech-stack/layers/frontend.md) | LCP trên 2,5 s trong 7 ngày liên tiếp | NFR-001 | Lighthouse CI chặn merge khi vượt ngân sách ở [performance-budget.md](../05-frontend/performance-budget.md) | tách gói mã theo route sâu hơn, bỏ thư viện nặng nhất khỏi gói tải ban đầu | đang theo dõi |
| R-002 | Chưa từng khôi phục thử bản sao lưu, đến lúc cần thì khôi phục lâu hơn RTO và mất đơn trong khoảng RPO | dữ liệu | 2 × 4 = 8 | [data](../02-tech-stack/layers/data.md) | thời gian khôi phục thử vượt 240 phút | NFR-002 | diễn tập khôi phục mỗi quý, bắt đầu trước ngày ra mắt (xem [backup-recovery.md](../07-data/backup-recovery.md)) | dựng lại từ bản sao standby, nhận mất tối đa 15 phút dữ liệu | đang theo dõi |

## Ngưỡng xử lý
<!-- required -->

- 15–25 điểm: bắt buộc có giảm thiểu; nếu vẫn giữ, người dùng chấp nhận rõ ràng và trạng thái ghi "đã chấp nhận".
- 8–14 điểm: bắt buộc có giảm thiểu và dấu hiệu sớm.
- 1–7 điểm: theo dõi, có dấu hiệu sớm.

## Cảnh báo tương ứng
<!-- required -->

- R-001: kết quả Lighthouse CI mỗi lần build, xem [performance-budget.md](../05-frontend/performance-budget.md)
- R-002: báo cáo diễn tập khôi phục mỗi quý, xem [backup-recovery.md](../07-data/backup-recovery.md)

## Rà soát
<!-- required -->

- Lần rà gần nhất: G5, 2026-10-13
