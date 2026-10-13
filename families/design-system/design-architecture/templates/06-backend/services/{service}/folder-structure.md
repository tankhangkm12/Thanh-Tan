# Cấu trúc thư mục của service

> Template của design-architecture. Mục có `<!-- required -->` là bắt buộc. Cây mã nguồn của service; quy ước chung cho cả repo ở [repo-structure.md](../../repo-structure.md).

## Cây thư mục
<!-- required -->

```text
<service>/
├── <thư mục>/    # <vai trò>
└── <thư mục>/    # <vai trò>
```

## Quy ước
<!-- required -->

- Ranh giới module: <thư mục nào được phụ thuộc thư mục nào>
- Đặt tên: <quy ước tên file, tên package>
- Chỗ đặt: <nơi viết API, nơi viết truy cập dữ liệu, nơi viết test>
