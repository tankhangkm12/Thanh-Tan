# API của service

## Danh sách API
<!-- required -->

| API | Mô tả | Yêu cầu (FR) | Xác thực |
| --- | --- | --- | --- |
| API-create-order | Tạo đơn | FR-001 | khách đã đăng nhập |
| API-get-order | Lấy đơn | FR-002 | khách chủ đơn |
| API-update-status | Đổi trạng thái đơn | FR-003 | nhân viên |

## Chi tiết từng API
<!-- required -->

### API-create-order: POST /orders

| Mục | Giá trị | Cơ sở |
| --- | --- | --- |
| Yêu cầu vào | danh sách món (mã món, số lượng), ghi chú tối đa 200 byte | A-note-bytes |
| Phản hồi thành công | 201, mã đơn | |
| Lỗi | 400 khi danh sách rỗng, theo error model chung | |
| Idempotency | khóa do client gửi, giữ 86.400 giây | D-001 |
| Giới hạn tần suất | 5 request/giây/người dùng | NFR-003 |

### API-get-order: GET /orders/{id}

| Mục | Giá trị | Cơ sở |
| --- | --- | --- |
| Yêu cầu vào | mã đơn | |
| Phản hồi thành công | 200, trạng thái và các món | |
| Lỗi | 404 khi không có đơn | |
| Idempotency | không áp dụng (chỉ đọc) | |
| Giới hạn tần suất | 5 request/giây/người dùng | NFR-003 |

### API-update-status: PATCH /orders/{id}/status

| Mục | Giá trị | Cơ sở |
| --- | --- | --- |
| Yêu cầu vào | trạng thái mới | |
| Phản hồi thành công | 200 | |
| Lỗi | 409 khi chuyển trạng thái không hợp lệ | |
| Idempotency | đặt cùng trạng thái hai lần cho cùng kết quả | |
| Giới hạn tần suất | 10 request/giây/nhân viên | NFR-003 |

## Tối ưu
<!-- required -->

| API | Chỉ số | Mục tiêu (số + đơn vị) | NFR | Cách đo |
| --- | --- | --- | --- | --- |
| API-create-order | p95 độ trễ | dưới 300 ms | NFR-001 | log truy cập |
| API-get-order | p95 độ trễ | dưới 100 ms | NFR-001 | log truy cập |

## Được dùng bởi
<!-- required -->

- [FL-001](../../../04-flows/FL-001-dat-don.md)
- [FL-002](../../../04-flows/FL-002-xem-trang-thai.md)
- [FL-003](../../../04-flows/FL-003-cap-nhat-trang-thai.md)
- [requirements-trace.md](../../../00-context/requirements-trace.md)
- [data.md](data.md)
