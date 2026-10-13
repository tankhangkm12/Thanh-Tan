# Event của service

> Template của design-architecture. Mục có `<!-- required -->` là bắt buộc. `EVT-xx` được định nghĩa ở [`07-data/messaging.md`](../../../07-data/messaging.md), không ở đây: file này chỉ nhắc ID, nên cột đầu là tên sự kiện, không phải ID. Service không phát hay nhận event nào thì ghi "không có" ở mục tương ứng.

## Event phát ra
<!-- required -->

| Sự kiện | EVT | Khi nào phát | Đảm bảo giao | Kích thước payload (byte) |
| --- | --- | --- | --- | --- |
| <tên> | <EVT-xx> | <điều kiện, bước của FL-xx> | <at-least-once, exactly-once…> | <số> |

## Event nhận
<!-- required -->

| Sự kiện | EVT | Từ service | Xử lý | Thứ tự và trùng lặp |
| --- | --- | --- | --- | --- |
| <tên> | <EVT-xx> | <SVC-xx> | <hành động> | <cách xử lý trùng, thứ tự, thử lại tối đa bao nhiêu lần> |
