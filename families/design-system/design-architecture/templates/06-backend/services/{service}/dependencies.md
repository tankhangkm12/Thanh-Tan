# Phụ thuộc của service

> Template của design-architecture. Mục có `<!-- required -->` là bắt buộc. Nhắc service, hệ thống ngoài bằng ID hoặc link; thời gian chờ và số lần thử lại là số có đơn vị. Không đặt ID ở ô đầu dòng bảng.

## Phụ thuộc đồng bộ
<!-- required -->

Service mà service này gọi trực tiếp. Không có thì ghi "không có".

| Gọi tới | API | Thời gian chờ (ms) | Thử lại (lần) | Cách xử lý khi hỏng |
| --- | --- | --- | --- | --- |
| <SVC-xx> | <API-xx> | <số> | <số> | <ngắt mạch, giá trị mặc định, báo lỗi> |

## Phụ thuộc bất đồng bộ
<!-- required -->

Event hoặc hàng đợi qua [messaging](../../../07-data/messaging.md). Không có thì ghi "không có".

| Kênh | EVT | Hướng | Hậu quả khi kênh chậm hoặc mất |
| --- | --- | --- | --- |
| <tên> | <EVT-xx> | <phát, nhận> | <mô tả> |

## Hệ thống ngoài
<!-- required -->

Cách gọi, lỗi và phương án thay thế nằm ở [integrations.md](../../../01-system/integrations.md). Không có thì ghi "không có".

| Hệ thống | Giao thức | Thời gian chờ (ms) | Phương án dự phòng |
| --- | --- | --- | --- |
| <tên> | <REST, SDK…> | <số> | <phương án> |
