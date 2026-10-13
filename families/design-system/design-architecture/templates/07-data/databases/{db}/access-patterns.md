# Mẫu truy cập của <db>

> Template của design-architecture. Mục có `<!-- required -->` là bắt buộc. Mỗi mẫu truy cập truy về luồng và API; tần suất lấy từ giả định `A-xx` hoặc [workload-model.md](../../../03-capacity/workload-model.md), không viết số mới. Không đặt ID ở ô đầu dòng bảng.

## Mẫu truy cập
<!-- required -->

| Mẫu | Đọc / ghi | Bảng | Luồng | Tần suất (số + đơn vị) | Độ trễ mục tiêu (ms) | Index phục vụ |
| --- | --- | --- | --- | --- | --- | --- |
| <mô tả truy vấn> | <đọc, ghi> | <TBL-xx> | <FL-xx> | <req/s, nguồn A-xx hoặc link> | <số> | <tên index trong indexing.md> |

## Truy vấn nặng

Truy vấn quét nhiều dòng, báo cáo, batch: cách chạy (replica, giờ thấp điểm) và giới hạn thời gian (giây). Không có thì ghi "không có truy vấn nặng".
