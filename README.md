# Thanh-Tan-

> **MVP.** Dùng được: plugin `dev-core` (quy trình task, hook an toàn, 4 skill, 6 role) cho Claude Code và Antigravity CLI, chạy trên động cơ `agentflow`. Các plugin `dev-design`, `dev-backend`, `dev-frontend`, `dev-infra` vẫn là khung.

Trung tâm của nhiều **nhóm plugin** cho Claude Code và Antigravity CLI. Mỗi nhóm có core và chuẩn riêng; mọi nhóm dùng chung một động cơ là `foundation/` (package Python `agentflow`).

## Các nhóm

| Nhóm | Trạng thái | Plugin |
|---|---|---|
| [software-dev](families/software-dev/README.md) | MVP (`dev-core` dùng được) | `dev-core`, `dev-design`, `dev-backend`, `dev-frontend`, `dev-infra` |
| [marketing](families/marketing/README.md) | Dự kiến, chưa xây | — |

Kiến trúc và quy tắc phụ thuộc: [docs/architecture.md](docs/architecture.md).

## Cấu trúc

```
.claude-plugin/marketplace.json   marketplace Claude Code (thanh-tan-plugins)
foundation/                       package agentflow (uv)
families/<nhóm>/<plugin>/         từng plugin: .claude-plugin/plugin.json + plugin.json (Antigravity)
tools/                            build.py (sinh agent), smoke.py (thử end-to-end)
docs/                             tài liệu kiến trúc
```

## Cài đặt từng bước

### Bước 0: yêu cầu

`git`, [`uv`](https://docs.astral.sh/uv/getting-started/installation/), và **Docker Desktop (hoặc Podman) đang chạy** (dùng để quét secret khi `agentflow commit`). Kiểm tra sau khi cài `agentflow` ở bước 1 bằng `agentflow doctor`.

Clone repo (nhánh mặc định là `develop`):

```
git clone https://github.com/tankhangkm12/Thanh-Tan-.git
cd Thanh-Tan-
```

Dưới đây `<repo>` là đường dẫn tới thư mục vừa clone.

### Bước 1: cài `agentflow` (bắt buộc, cả hai CLI đều dùng)

Hook của `dev-core` gọi lệnh `agentflow`, nên nó phải nằm trong PATH.

```
uv tool install --force --reinstall "<repo>/foundation"
agentflow --version
agentflow doctor
```

Không cần clone cũng được: `uv tool install --force "git+https://github.com/tankhangkm12/Thanh-Tan-#subdirectory=foundation"`.

Nếu terminal không nhận `agentflow`: chạy `uv tool update-shell` rồi mở lại terminal. Sau mỗi lần `git pull` repo, chạy lại lệnh `uv tool install --force --reinstall ...` ở trên. Gỡ: `uv tool uninstall agentflow`.

### Bước 2a: cài vào Claude Code

Cách 1, từ GitHub (không phụ thuộc nhánh đang checkout):

```
claude plugin marketplace add tankhangkm12/Thanh-Tan-
claude plugin install dev-core@thanh-tan-plugins
```

Cách 2, từ bản clone local (Claude Code đọc thẳng thư mục repo, nên nội dung đổi theo nhánh đang checkout; nên để repo ở `develop`):

```
claude plugin marketplace add "<repo>"
claude plugin install dev-core@thanh-tan-plugins
```

Kiểm tra: `claude plugin list` phải thấy `dev-core@thanh-tan-plugins` ở trạng thái enabled. Mở lại Claude Code, gõ `/dev-core:` sẽ thấy `start`, `continue`, `status`, `approve`. 6 agent hiện dưới tên `dev-core:orchestrator`, `dev-core:planner`, `dev-core:implementer`, `dev-core:tester`, `dev-core:security`, `dev-core:reviewer`. (Lệnh `claude plugin details` hiện báo `Agents (0)` do cách đếm của nó; agent vẫn được nạp.) Cập nhật: `claude plugin update dev-core@thanh-tan-plugins`.

### Bước 2b: cài vào Antigravity CLI

```
agy plugin install "<repo>/families/software-dev/core"
agy plugin list
agy agents
```

`agy plugin list` phải có `dev-core` với `skills`, `agents`, `hooks`; `agy agents` liệt kê 6 role. `agy plugin install` chép một bản vào máy, nên sau mỗi lần `git pull` hãy chạy lại lệnh cài. Cách cài thẳng từ GitHub cho repo nhiều plugin chưa được xác nhận.

### Bước 3: dùng trong một dự án

Dự án phải là repo git có nhánh `main` và `develop`, cây làm việc sạch.

```
cd <dự-án-của-bạn>
agentflow init --workflow "<repo>/families/software-dev/core/workflow.yaml"
```

`.agentflow/` được tạo ở local và tự thêm vào `.git/info/exclude` (không bị commit). Sau đó, trong Claude Code gõ `/dev-core:start` (Antigravity: nhờ agent dùng skill `start`) rồi làm theo hướng dẫn; hoặc tự chạy:

```
agentflow task new "Tiêu đề" --type feature    # tạo nhánh feature/T-001-...
agentflow status
agentflow task advance --result pass           # xong bước; bước cần duyệt thì tiếp theo là:
agentflow task approve
agentflow commit "nội dung"                    # quét secret rồi commit với tiền tố T-001:
agentflow workflow sync                        # khi workflow gốc của nhóm thay đổi
```

Hook chỉ hoạt động trong dự án đã có `.agentflow/`; ở dự án khác chúng không làm gì. Khi hook chạy, `git push`, `reset --hard`, `clean -fd`, `branch -D`, xóa tag, và commit/merge/rebase trên `main`/`develop` bị chặn với agent. Chi tiết: [docs/architecture.md](docs/architecture.md).

### Kiểm tra nhanh toàn bộ

```
uv run tools/smoke.py
```

Chạy `init → task → advance/approve → commit (Gitleaks thật) → guard → hook` trên một repo tạm, không đụng repo nào khác. Cần Docker đang chạy.

## Phát triển

```
cd foundation
uv run pytest
uv run --python 3.12 pytest
cd ..
uv run tools/build.py --check
uv run --with pyyaml --with pytest pytest tools
claude plugin validate --strict families/software-dev/core
agy plugin validate families/software-dev/core
```
