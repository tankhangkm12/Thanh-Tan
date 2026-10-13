# Scale, nâng cấp, bảo trì của service

> Template của design-architecture. Mục có `<!-- required -->` là bắt buộc (Q2, Q3). Số instance theo mốc do `calc_capacity.py` tính ở [compute-sizing.md](../../../03-capacity/compute-sizing.md): **dẫn link, không chép lại**. Phiên bản và ngày hết hỗ trợ lấy từ [versions-features.md](../../../02-tech-stack/versions-features.md).

## Scale
<!-- required -->

| Mục | Giá trị |
| --- | --- |
| Đơn vị scale | <instance, shard…> |
| Có trạng thái trong bộ nhớ không | <có / không; nếu có, cách chia sẻ> |
| Giới hạn một instance (số + đơn vị) | <req/s mỗi instance, nguồn benchmark> |
| Số instance theo mốc | <link tới mục SVC-xx trong compute-sizing.md> |
| Điểm nghẽn tiếp theo | <thành phần, ngưỡng số khi chạm> |
| Ngưỡng lên giai đoạn sau | <số kích hoạt, link scaling-stages.md nếu có> |

## Nâng cấp
<!-- required -->

| Mục | Giá trị |
| --- | --- |
| Runtime và framework | <tên, phiên bản chốt, link versions-features.md> |
| Ngày hết hỗ trợ gần nhất | <YYYY-MM-DD, link> |
| Đường nâng cấp | <bản kế tiếp, việc phải làm, thay đổi phá vỡ> |
| Cách nâng cấp không gián đoạn | <rolling, blue-green; thời gian gián đoạn tối đa (giây)> |

## Bảo trì
<!-- required -->

| Việc định kỳ | Tần suất | Giờ mỗi tháng | Cơ sở ước tính |
| --- | --- | --- | --- |
| <vá bảo mật, xoay khóa, dọn dữ liệu> | <ngày, tuần, tháng> | <giờ> | <vì sao ước tính như vậy> |

## Tối ưu
<!-- required -->

| Chỉ số | Mục tiêu (số + đơn vị) | NFR | Cách đo |
| --- | --- | --- | --- |
| <mức dùng CPU ở tải đỉnh> | <phần trăm> | <NFR-xx> | <công cụ, vị trí đo> |
| <thời gian khởi động một instance> | <giây> | <NFR-xx> | <công cụ, vị trí đo> |
