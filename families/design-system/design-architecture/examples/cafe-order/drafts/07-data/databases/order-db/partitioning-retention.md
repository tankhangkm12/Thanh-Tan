# Phân vùng, giữ dữ liệu và scale của order-db

## Phân vùng
<!-- required -->

Không phân vùng; xét lại khi bảng vượt 100 triệu dòng.

| Bảng | Khóa phân vùng | Kích thước mỗi phân vùng (số + đơn vị) | Ngưỡng bắt đầu phân vùng |
| --- | --- | --- | --- |
| TBL-orders | không | không có | 100 triệu dòng |

## Thời gian giữ dữ liệu
<!-- required -->

| Bảng | Giữ (ngày) | Cách xóa hoặc lưu trữ | Nguồn yêu cầu (C-xx / NFR-xx) |
| --- | --- | --- | --- |
| TBL-orders | 1095 ngày | xóa theo lô hằng đêm | C-001 |

## Scale
<!-- required -->

| Mục | Giá trị |
| --- | --- |
| Đơn vị scale | nâng cấu hình primary, thêm bản sao đọc |
| Giới hạn trước khi phải đổi (số + đơn vị) | CPU primary 70% |
| Ngưỡng lên giai đoạn sau | CPU primary trên 70% trong 15 phút |
| Số bản sao theo mốc | A-replicas |
