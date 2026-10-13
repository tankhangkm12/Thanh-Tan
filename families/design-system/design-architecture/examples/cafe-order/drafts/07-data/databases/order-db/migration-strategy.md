# Migration, nâng cấp và bảo trì của order-db

## Migration schema
<!-- required -->

| Mục | Giá trị |
| --- | --- |
| Công cụ | công cụ migration của team |
| Quy tắc thay đổi an toàn | thêm cột có giá trị mặc định, tạo index đồng thời |
| Thời gian khóa tối đa cho phép (giây) | 2 giây |
| Cách rollback | migration ngược, hoặc khôi phục từ backup |
| Quy trình backfill | lô 1.000 dòng, chạy ngoài giờ cao điểm |

## Nâng cấp
<!-- required -->

| Mục | Giá trị |
| --- | --- |
| Phiên bản hiện tại và ngày hết hỗ trợ | 16.4, 2028-11-09, xem [versions-features.md](../../../02-tech-stack/versions-features.md) |
| Đường nâng cấp | bản 17 bằng sao chép logic |
| Gián đoạn tối đa (giây) | 60 giây |
| Diễn tập trước khi nâng | môi trường staging, mỗi lần nâng |

## Bảo trì
<!-- required -->

| Việc định kỳ | Tần suất | Giờ mỗi tháng | Cơ sở ước tính |
| --- | --- | --- | --- |
| phân tích thống kê, kiểm tra backup | mỗi tuần | 3 giờ | kinh nghiệm team |
