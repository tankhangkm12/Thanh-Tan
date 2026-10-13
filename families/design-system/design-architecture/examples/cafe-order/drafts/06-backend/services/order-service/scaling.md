# Scale, nâng cấp, bảo trì của service

## Scale
<!-- required -->

| Mục | Giá trị |
| --- | --- |
| Đơn vị scale | instance |
| Có trạng thái trong bộ nhớ không | không |
| Giới hạn một instance (số + đơn vị) | 150 req/s, nguồn https://example.com/benchmarks/order-service-2026-10 |
| Số instance theo mốc | [compute-sizing.md](../../../03-capacity/compute-sizing.md) |
| Điểm nghẽn tiếp theo | database order-db, CPU primary trên 70% |
| Ngưỡng lên giai đoạn sau | req/s đỉnh vượt công suất 2 instance |

## Nâng cấp
<!-- required -->

| Mục | Giá trị |
| --- | --- |
| Runtime và framework | Node.js 24.0, xem [versions-features.md](../../../02-tech-stack/versions-features.md) |
| Ngày hết hỗ trợ gần nhất | 2028-04-30 |
| Đường nâng cấp | bản LTS kế tiếp trước ngày hết hỗ trợ |
| Cách nâng cấp không gián đoạn | rolling update, gián đoạn 0 giây |

## Bảo trì
<!-- required -->

| Việc định kỳ | Tần suất | Giờ mỗi tháng | Cơ sở ước tính |
| --- | --- | --- | --- |
| vá bảo mật và cập nhật phụ thuộc | mỗi tháng | 2 giờ | kinh nghiệm team với một service |

## Tối ưu
<!-- required -->

| Chỉ số | Mục tiêu (số + đơn vị) | NFR | Cách đo |
| --- | --- | --- | --- |
| mức dùng CPU ở tải đỉnh | dưới 70% | NFR-003 | giám sát instance |
| thời gian khởi động một instance | dưới 10 giây | NFR-002 | log khởi động |
