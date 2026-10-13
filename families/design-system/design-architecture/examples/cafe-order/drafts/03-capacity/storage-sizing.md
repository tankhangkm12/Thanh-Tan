# Dung lượng object storage

<!-- Sinh bởi calc_capacity.py từ capacity/*.yaml. Không sửa tay: sửa yaml rồi chạy lại. -->

Mức dự án: M. Mốc: Ra mắt (launch), 1 năm (1y), 3 năm (3y). 1 năm = 365 ngày, 1 tháng = 365/12 ngày, 1 ngày = 86,400 giây.

Công thức: `file đang giữ = min(file đã tải lên, file/ngày × số ngày giữ)`; `dung lượng = file đang giữ × kích thước trung bình`; `băng thông ra/tháng = lượt xem/ngày × kích thước × (365/12)`.
Giả định xem [assumptions.md](../00-context/assumptions.md).

## menu-images (BKT-menu-images)

File/ngày: A-menu-images-per-day; kích thước trung bình: A-image-bytes; giữ lại: mãi mãi; lượt xem/ngày: không có.

| Mốc | File/ngày (giai đoạn) | File đã tải lên | File đang giữ | Kích thước TB | Dung lượng lưu | Lượt xem/ngày | Băng thông ra/tháng |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Ra mắt | 0 | 0 | 0 | 292.97 KiB (300,000 byte) | 0.00 B (0 byte) | 0 | 0.00 B (0 byte) |
| 1 năm | 2 | 730 | 730 | 292.97 KiB (300,000 byte) | 208.85 MiB (219,000,000 byte) | 0 | 0.00 B (0 byte) |
| 3 năm | 5 | 4,380 | 4,380 | 292.97 KiB (300,000 byte) | 1.22 GiB (1,314,000,000 byte) | 0 | 0.00 B (0 byte) |
