# Migration, nâng cấp và bảo trì của <db>

> Template của design-architecture. Mục có `<!-- required -->` là bắt buộc (Q3: nâng cấp, bảo trì). Phiên bản và ngày hết hỗ trợ lấy từ [versions-features.md](../../../02-tech-stack/versions-features.md). Không đặt ID ở ô đầu dòng bảng.

## Migration schema
<!-- required -->

| Mục | Giá trị |
| --- | --- |
| Công cụ | <tên, phiên bản chốt> |
| Quy tắc thay đổi an toàn | <thêm cột có mặc định, tạo index đồng thời, không khóa bảng quá giây> |
| Thời gian khóa tối đa cho phép (giây) | <số> |
| Cách rollback | <migration ngược, khôi phục từ backup> |
| Quy trình backfill | <batch kích thước (dòng), giờ chạy, cách kiểm> |

## Nâng cấp
<!-- required -->

| Mục | Giá trị |
| --- | --- |
| Phiên bản hiện tại và ngày hết hỗ trợ | <major.minor, YYYY-MM-DD, link versions-features.md> |
| Đường nâng cấp | <bản kế tiếp, cách nâng (tại chỗ, dump, logical replication), thay đổi phá vỡ> |
| Gián đoạn tối đa (giây) | <số> |
| Diễn tập trước khi nâng | <môi trường, tần suất> |

## Bảo trì
<!-- required -->

| Việc định kỳ | Tần suất | Giờ mỗi tháng | Cơ sở ước tính |
| --- | --- | --- | --- |
| <dọn bloat, phân tích thống kê, kiểm tra backup> | <ngày, tuần, tháng> | <giờ> | <vì sao ước tính như vậy> |
