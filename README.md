# Thanh-Tan-

> **Bản nháp.** Repo đang ở giai đoạn dựng khung: chưa có skill, agent, hook hay MCP thật.

Trung tâm của nhiều **nhóm plugin** cho Claude Code và Antigravity CLI. Mỗi nhóm có core và chuẩn riêng; mọi nhóm dùng chung một động cơ là `foundation/` (package Python `agentflow`).

## Các nhóm

| Nhóm | Trạng thái | Plugin |
|---|---|---|
| [software-dev](families/software-dev/README.md) | Đang dựng khung | `dev-core`, `dev-design`, `dev-backend`, `dev-frontend`, `dev-infra` |
| [marketing](families/marketing/README.md) | Dự kiến, chưa xây | — |

Kiến trúc và quy tắc phụ thuộc: [docs/architecture.md](docs/architecture.md).

## Cấu trúc

```
.claude-plugin/marketplace.json   marketplace Claude Code (thanh-tan-plugins)
foundation/                       package agentflow (uv)
families/<nhóm>/<plugin>/         từng plugin: .claude-plugin/plugin.json + plugin.json (Antigravity)
tools/                            script build (chưa có)
docs/                             tài liệu kiến trúc
```

## Cài đặt

### Claude Code

```
/plugin marketplace add tankhangkm12/Thanh-Tan-
/plugin install dev-core@thanh-tan-plugins
```

Cài một plugin con (ví dụ `dev-backend@thanh-tan-plugins`) sẽ tự cài `dev-core` vì nó được khai báo là phụ thuộc.

### Antigravity CLI

Hiện cài từ đường dẫn local tới thư mục plugin sau khi clone repo:

```
agy plugin install <đường-dẫn-tới-repo>/families/software-dev/core
```

Cách cài thẳng từ GitHub cho repo nhiều plugin chưa được xác nhận.

### agentflow (bắt buộc cho hook và các lệnh của dev-core)

Hook của `dev-core` gọi lệnh `agentflow`, nên phải cài nó vào PATH. Cần `uv` và `git`; cần thêm Docker (hoặc Podman) đang chạy cho bước quét secret khi commit.

Từ bản clone local (chạy lại đúng lệnh này sau mỗi lần `git pull`):

```
uv tool install --force --reinstall "<đường-dẫn-repo>/foundation"
agentflow --version
agentflow doctor
```

Hoặc thẳng từ GitHub, không cần clone:

```
uv tool install --force "git+https://github.com/tankhangkm12/Thanh-Tan-#subdirectory=foundation"
```

Nếu terminal không nhận lệnh `agentflow`, chạy `uv tool update-shell` rồi mở lại terminal. Gỡ: `uv tool uninstall agentflow`.

Hook chỉ hoạt động trong dự án đã có `.agentflow/`; ở dự án khác chúng không làm gì.

Dùng trong một dự án (thư mục gốc là repo git, đã có nhánh `main` và `develop`):

```
agentflow init --workflow <đường-dẫn>/families/software-dev/core/workflow.yaml
agentflow task new "Tiêu đề" --type feature     # tạo nhánh feature/T-001-...
agentflow status
agentflow task advance --result pass            # xong bước; bước cần duyệt thì tiếp theo là:
agentflow task approve
agentflow commit "nội dung"                     # quét secret rồi commit với tiền tố T-001:
agentflow workflow sync                         # khi workflow gốc của nhóm thay đổi
```

Phát triển cục bộ: `cd foundation; uv run pytest; uv run --python 3.12 pytest`.

Workspace `.agentflow/` chỉ nằm ở local (ghi vào `.git/info/exclude`). Chi tiết: [docs/architecture.md](docs/architecture.md#workspace-của-dự-án).
