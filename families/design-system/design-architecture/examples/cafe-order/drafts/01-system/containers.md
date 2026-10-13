# Containers (C4 mức 2)

## Danh sách container
<!-- required -->

| Container | Loại | Vai trò | Công nghệ | Đơn vị triển khai | Scale, nâng cấp, bảo trì |
| --- | --- | --- | --- | --- | --- |
| order-service | service | API đặt đơn | [Node.js](../02-tech-stack/layers/backend.md) | service riêng | [scaling.md](../06-backend/services/order-service/scaling.md) |
| order-db | database | Lưu đơn | [PostgreSQL](../02-tech-stack/layers/data.md) | service riêng | [layers/data.md](../02-tech-stack/layers/data.md) |

## Sơ đồ
<!-- required -->

```mermaid
flowchart LR
  service[order-service] --> db[(order-db)]
```

## Liên lạc giữa container
<!-- required -->

| Từ | Đến | Kiểu | Lý do | Luồng |
| --- | --- | --- | --- | --- |
| order-service | order-db | đồng bộ | đọc và ghi đơn | FL-001, FL-002, FL-003 |

## Rủi ro
<!-- required -->

Không có rủi ro mới từ cách chia container.
