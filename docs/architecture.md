# Kiến trúc

## Các tầng

```
foundation/ (agentflow)      động cơ dùng chung, không mang nghiệp vụ
      │
      ▼
families/<nhóm>/core/        core của nhóm: quy trình, chuẩn, gate của nhóm đó
      │
      ▼
families/<nhóm>/<plugin>/    plugin con: chỉ thêm nghiệp vụ riêng
```

- **foundation**: package Python `agentflow`, quản lý bằng uv, cài global bằng `uv tool install` để có lệnh `agentflow`. Không chứa khái niệm của bất kỳ nhóm nào.
- **core của nhóm**: ví dụ `dev-core`. Định nghĩa chuẩn chung của nhóm và dựa trên `foundation`.
- **plugin con**: ví dụ `dev-backend`. Khai báo phụ thuộc vào core của nhóm mình trong `.claude-plugin/plugin.json` (`"dependencies": ["dev-core"]`).

## Quy tắc phụ thuộc

- Chiều phụ thuộc chỉ đi xuống theo sơ đồ trên: plugin con → core nhóm → foundation.
- **Không dùng code chéo nhóm.** Plugin của nhóm này không được import, gọi hay phụ thuộc vào core hoặc plugin của nhóm khác. Thứ gì cần dùng chung giữa các nhóm thì đưa xuống `foundation`, và chỉ khi nó không mang nghiệp vụ.
- `foundation` không được biết đến bất kỳ nhóm nào.

## Mỗi plugin chạy trên hai CLI

| File | Dùng cho | Nội dung |
|---|---|---|
| `.claude-plugin/plugin.json` | Claude Code | `name`, `version`, `description`, `author`, `dependencies` |
| `plugin.json` (gốc plugin) | Antigravity CLI | Chỉ `$schema`, `name`, `description` (schema không cho thêm trường) |

Tên plugin có tiền tố nhóm (`dev-*` cho software-dev). Marketplace Claude Code nằm ở `.claude-plugin/marketplace.json` tại gốc repo.
