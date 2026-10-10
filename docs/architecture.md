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

## Foundation ↔ nhóm: hợp đồng workflow

Mỗi nhóm khai báo quy trình của mình trong một file `workflow.yaml` đặt trong plugin core của nhóm (ví dụ `families/software-dev/core/workflow.yaml`). Foundation chỉ đọc file này, không import hay gọi code của nhóm.

| Trường | Ý nghĩa |
|---|---|
| `schema_version` | Hiện là `1` |
| `family` | Tên nhóm, dạng `^[a-z][a-z0-9-]*$` |
| `steps[].id`, `name`, `role` | Mã bước, tên hiển thị, role phụ trách (foundation chỉ coi role là chuỗi) |
| `steps[].requires_approval` | Bước cần người duyệt (mặc định `false`) |
| `steps[].on_fail` | Bước `kind: loop` sẽ chuyển tới khi bước này lỗi |
| `steps[].kind: loop` + `loop.back_to`, `loop.max_rounds` | Bước sửa lỗi: quay về `back_to` (phải đứng trước nó), tối đa `max_rounds` vòng |

Các bước thường chạy theo thứ tự trong danh sách; bước `loop` chỉ được vào qua `on_fail`. Hết số vòng mà vẫn lỗi thì task chuyển `blocked`, cần người quyết định.

File được kiểm hai lớp: JSON Schema (`foundation/src/agentflow/schemas/workflow.schema.json`, editor có thể dùng qua dòng `# yaml-language-server: $schema=...`) và kiểm tham chiếu trong Python (id không trùng, `on_fail`/`back_to` trỏ đúng loại bước).

## Workspace của dự án

`agentflow init --workflow <file>` tạo `.agentflow/` ở gốc repo git của dự án. Thư mục này chỉ ở local: init ghi `.agentflow/` vào `.git/info/exclude` của dự án, không sửa `.gitignore`.

```
.agentflow/
  state.json      nguồn sự thật về trạng thái (kiểm theo state.schema.json)
  STATE.md        sinh lại từ state.json mỗi lần ghi, không sửa tay
  config.yaml     family, source_path và sha256 của workflow gốc lúc chép
  workflow.yaml   bản chép của workflow: status/next dùng bản này
  decisions/  tasks/  project/  knowledge/
```

- Chạy lại `init` không ghi đè `state.json` hay bản chép workflow; chỉ tạo phần còn thiếu và cập nhật `source_path`. Đổi sang workflow của nhóm khác thì bị từ chối.
- Khi bản gốc đổi (sha khác), `status`/`next`/`init` cảnh báo và gợi ý `agentflow workflow sync`. Khi bản gốc không còn, agentflow dùng bản chép và cảnh báo.
- `workflow sync` kiểm bản gốc theo schema trước, rồi mới thay bản chép. Có task đang `open`/`blocked` thì từ chối, trừ khi có `--force`; kể cả với `--force`, sync vẫn bị từ chối nếu workflow mới bỏ mất bước mà một task đang đứng.

Task trong `state.json` có `id` (`T-001`), `title`, `status` (`open`/`blocked`/`done`/`cancelled`), `current_step`, `step_status` (`in_progress`/`awaiting_approval`/`passed`/`failed`), `loop_round`, `branch` (chuỗi hoặc `null`) và `history`.

## Lệnh agentflow

| Lệnh | Việc làm | Exit code khác 0 khi |
|---|---|---|
| `agentflow doctor` | Kiểm uv, git (bắt buộc) và docker/podman (cần ít nhất một); in link cài chính thức cho công cụ thiếu | Thiếu công cụ bắt buộc. Engine container không chạy chỉ là cảnh báo |
| `agentflow init --workflow <file>` | Tạo hoặc bổ sung `.agentflow/` | Không phải repo git, workflow không hợp lệ, khác nhóm |
| `agentflow status` | Task đang mở, bước hiện tại, việc tiếp theo | Chưa có workspace, state hỏng |
| `agentflow next` | Bước tiếp theo, dạng `<loại>: <mô tả>` | Như `status` |
| `agentflow workflow sync [--force]` | Thay bản chép workflow bằng bản gốc đã kiểm | Bản gốc lỗi hoặc mất, khác nhóm, có task đang chạy |

Mã lỗi nằm trong `ExitCode` (`foundation/src/agentflow/constants.py`). Phần này chưa có lệnh tạo task hay chuyển bước.
