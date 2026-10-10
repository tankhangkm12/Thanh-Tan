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

### agentflow

`agentflow` sẽ được cài global bằng `uv tool install` từ thư mục `foundation/`. Hiện chạy qua uv:

```
cd foundation
uv run agentflow doctor
uv run pytest
```

Dùng trong một dự án (thư mục gốc là repo git):

```
agentflow init --workflow <đường-dẫn>/families/software-dev/core/workflow.yaml
agentflow status
agentflow next
agentflow workflow sync      # khi workflow gốc của nhóm thay đổi
```

Workspace `.agentflow/` chỉ nằm ở local (ghi vào `.git/info/exclude`). Chi tiết: [docs/architecture.md](docs/architecture.md#workspace-của-dự-án).
