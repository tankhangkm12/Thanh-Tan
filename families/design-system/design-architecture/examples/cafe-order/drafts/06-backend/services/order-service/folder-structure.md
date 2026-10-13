# Cấu trúc thư mục của service

## Cây thư mục
<!-- required -->

```text
order-service/
├── src/api/      # xử lý request
├── src/domain/   # quy tắc đơn hàng
└── src/data/     # truy cập order-db
```

## Quy ước
<!-- required -->

- Ranh giới module: api gọi domain, domain gọi data, không đi ngược
- Đặt tên: kebab-case cho file
- Chỗ đặt: test cạnh file được test
