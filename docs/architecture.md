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
| `max_rounds` | Số lần một task được quay lại làm lại (cả workflow) |
| `steps[].on_fail` | Bước đứng trước mà task quay về khi bước này fail |
| `steps[].gates` | Gate bước phải qua trước khi `task advance --result pass` được nhận: `plan-valid` (kế hoạch qua `plan check`), `scans-clean` (kết quả scan không còn mục chặn) |

Các bước chạy theo thứ tự trong danh sách; không có bước "loop" riêng. Fail ở bước có `on_fail` thì task quay về bước đó và số vòng tăng 1. Hết `max_rounds`, hoặc bước không có `on_fail`, thì task chuyển `blocked`, cần người quyết định.

File được kiểm hai lớp: JSON Schema (`foundation/src/agentflow/schemas/workflow.schema.json`, editor có thể dùng qua dòng `# yaml-language-server: $schema=...`) và kiểm tham chiếu trong Python (id không trùng, `on_fail` trỏ tới bước đứng trước).

## Workspace của dự án

`agentflow init --workflow <file>` tạo `.agentflow/` ở gốc repo git của dự án. Thư mục này chỉ ở local: init ghi `.agentflow/` vào `.git/info/exclude` của dự án, không sửa `.gitignore`.

```
.agentflow/
  state.json      nguồn sự thật về trạng thái (kiểm theo state.schema.json)
  STATE.md        sinh lại từ state.json mỗi lần ghi, không sửa tay
  config.yaml     family, source_path và sha256 của workflow gốc lúc chép
  workflow.yaml   bản chép của workflow: status/next dùng bản này
  decisions/      mỗi lần người duyệt tiếp một task bị blocked ghi một file
  tasks/T-001/reports/<bước>.md   báo cáo của từng bước (agentflow report)
  project/  knowledge/
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
| `agentflow task new "<tiêu đề>" --type feature\|bugfix\|hotfix` | Tạo nhánh gitflow `<type>/T-001-<slug>` và ghi task | Cây làm việc chưa sạch, đã có task mở, thiếu nhánh gốc |
| `agentflow task advance --result pass\|fail` | Ghi kết quả bước hiện tại | Không có task, bước không ở trạng thái cho phép |
| `agentflow task approve [--reason ...]` | Duyệt bước đang chờ; với task `blocked` là người cho làm tiếp (ghi `decisions/`) | Như trên |
| `agentflow task cancel` | Hủy task đang mở | Không có task đang mở |
| `agentflow task seal <id>` | Việc của người: ghi `summary.md` và tag duyệt cho task đã xong mà chưa có (`--commit <sha>` khi nhánh đã xóa) | Task chưa xong, đã có tag, không thấy commit |
| `agentflow scan [--all]` | Chạy trong container các scan của bước hiện tại (bước `security`: Semgrep, Trivy, Gitleaks; plugin có thể thêm tool cho bước khác). Ghi `tasks/<task>/scans/` | Có phát hiện chặn (`SCAN_BLOCKED`), cây làm việc chưa sạch, engine container không chạy |
| `agentflow decide --suppress <id> --reason ...` | Việc của người: ghi `decisions/<task>-suppress-<mã>.md` để bỏ qua một báo nhầm của scan | Không có phát hiện đó trong kết quả scan, thiếu `--reason` |
| `agentflow plan check [--file f]` | Kiểm kế hoạch: mã `C<n>`, role hợp lệ, `done-when`, `docs` | Có mục sai (mã `PLAN_INVALID`) |
| `agentflow report --step <bước>` | Ghi stdin vào `tasks/<task>/reports/<bước>.md` | Bước không có trong workflow, nội dung rỗng |
| `agentflow commit "<nội dung>" [--item C1]` | Scan secret rồi commit với tiền tố `T-001: `; `--item` ghi trailer `Plan-Item: C1` | Sai nhánh, không có gì staged, thấy secret, engine container không chạy, mục không có trong plan |
| `agentflow guard` | Đọc `{"command","cwd"}` từ stdin, in `{"decision","rule","reason"}` | Input không phải JSON hợp lệ |

### Vòng đời task

`task new` → mỗi bước: `task advance --result pass` → (bước cần duyệt) `task approve` → bước kế. Fail ở `test`/`security`/`review` quay thẳng về `implement`, đếm vòng; hết `max_rounds` (mặc định 3) thì task `blocked` và chỉ người mới `task approve` để cho làm tiếp (vòng reset về 0, ghi một file vào `decisions/`) hoặc `task cancel`. Đi hết bước cuối thì task `done`. Chỉ một task mở tại một thời điểm.

### commit và guard

`agentflow commit` chỉ chạy khi đang ở nhánh của task và có file staged. Gitleaks (image ghim phiên bản, chạy qua Docker, dự phòng Podman, mount chỉ đọc) quét phần staged; engine không chạy hoặc có secret thì báo lỗi và **không commit**.

`agentflow guard` chặn: `git push` mọi dạng; mọi dạng `git commit` trong dự án đã có `.agentflow/` (chỉ cho commit qua `agentflow commit`; repo không có `.agentflow/` thì không chặn); `merge`/`commit`/`rebase`/`cherry-pick`/`revert`/`am` khi đang ở `main` hoặc `develop`; `reset --hard`; `clean` có cả `-f` và `-d`; `branch -D` (và `-d -f`); xóa tag; tạo tag hoặc ref dưới `agentflow/` (tag duyệt chỉ do `task approve` tạo); các lệnh của người (`decide`, `ext add`, `ext sync`, `config set`, `task seal`) khi agent tự chạy. Hiểu lệnh ghép (`&&`, `;`, `|`), `git -C`, `bash -c "..."` và việc `git switch` sang nhánh được bảo vệ ngay trong chuỗi lệnh. Đây là lưới an toàn cho agent, không phải sandbox: alias git, script hay biến môi trường vẫn có thể vượt qua.

### Kế hoạch, gate và tag duyệt

- Mỗi mục kế hoạch là một khối `### C1 - tiêu đề` kèm `role:`, `files:`, `done-when:`, `docs:` (xem README). `plan check` đòi mã duy nhất, role thuộc bộ role hợp lệ (role của workflow cộng role extension đăng ký), `done-when` không rỗng, `docs` là link hoặc `không có — <lý do>`.
- Gate `plan-valid` gắn vào bước `plan` trong `workflow.yaml`: `task advance --result pass` bị từ chối (mã `GATE_FAILED`) nếu báo cáo plan không qua kiểm tra. Gate chỉ áp dụng cho kết quả `pass`.
- Khi task chuyển sang `done` (duyệt bước cuối, hoặc bước cuối pass mà không cần duyệt), `agentflow` ghi `tasks/<task>/summary.md` rồi tạo annotated tag `agentflow/<task>/approved` ở commit cuối của nhánh task, **trước** khi lưu state: nếu việc đó lỗi thì task không bị đánh dấu xong. `task new` từ chối khi task `done` gần nhất thiếu tag.
### Scan

- Mỗi tool chạy trong container với image ghim phiên bản, repo mount **chỉ đọc**, kết quả lấy từ stdout và do `agentflow` ghi vào `.agentflow/tasks/<task>/scans/` (`<tool>.json` và `summary.json` có sha commit đã quét). Engine container không chạy là lỗi cứng, không bao giờ tính là "sạch".
- **Semgrep** (`semgrep/semgrep:1.180.0`, `--network none`): chỉ quét các file task đã đổi so với nhánh gốc; chặn khi mức `ERROR`. Rule tải lúc chạy từ Semgrep Registry vào cache của người dùng (ngoài repo; xem `docs/scan-notes.md`) vì giấy phép không cho phân phối lại.
- **Trivy** (`aquasec/trivy:0.75.0`, `fs --scanners vuln`, volume cache `agentflow-trivy-cache` cho DB): chặn khi `HIGH`/`CRITICAL` **đã có bản vá** (`FixedVersion`).
- **Gitleaks** (`v8.24.0`): quét các commit của task (`base..HEAD`); bất kỳ phát hiện nào cũng chặn.
- Gate `scans-clean` gắn vào bước `security`: `advance --result pass` bị từ chối nếu thiếu kết quả, kết quả cũ (HEAD đã đổi) hoặc còn phát hiện chặn chưa được bỏ qua.
- Báo nhầm chỉ được bỏ qua bằng file trong `decisions/` do `agentflow decide --suppress` tạo; lệnh này chỉ người chạy được (hook từ chối khi agent tự chạy). Agent không có đường nào hạ mức. Giới hạn: agent có công cụ ghi file vẫn *về kỹ thuật* tạo được file trong `decisions/`; prompt cấm việc đó nhưng hook chưa chặn.
- Cấu hình bộ rule Semgrep bằng khóa `scan.semgrep.rulesets` (mặc định `p/default`).

- Hook Stop chỉ nhắc khi bước đang `in_progress` và đã có báo cáo của bước ghi sau lúc bước bắt đầu.

Mã lỗi nằm trong `ExitCode` (`foundation/src/agentflow/constants.py`).
