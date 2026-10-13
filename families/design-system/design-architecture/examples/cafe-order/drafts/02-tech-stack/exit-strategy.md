# Chiến lược thoát

## Đường thay thế
<!-- required -->

| Công nghệ | Mức khóa chặt | Phương án thay thế | Chi phí chuyển (người-ngày) | Dữ liệu cần chuyển |
| --- | --- | --- | --- | --- |
| Node.js | thấp: mã chuẩn, không dùng API riêng | Deno hoặc Bun | 10 | không có |
| PostgreSQL | vừa: dùng SQL chuẩn | MySQL | 20 | toàn bộ bảng, xem [data-sizing.md](../03-capacity/data-sizing.md) |

## Điều kiện kích hoạt
<!-- required -->

| Công nghệ | Điều kiện (số + đơn vị) | Cách phát hiện | Rủi ro | Cơ sở |
| --- | --- | --- | --- | --- |
| Node.js | hết hỗ trợ trong 6 tháng | lịch trong versions-features.md | không có | [versions-features.md](versions-features.md) |
| PostgreSQL | chi phí lưu trữ trên 100 USD mỗi tháng | cost-model.md | không có | C-001 |
