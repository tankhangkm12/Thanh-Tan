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
| `steps[].gates` | Gate bước phải qua trước khi `task advance --result pass` được nhận: `plan-valid` (kế hoạch qua `plan check`, kể cả quy ước `item-order` và mọi câu hỏi "Chưa có quy ước" đã được trả lời), `scans-clean` (kết quả scan không còn mục chặn), `conventions-reviewed` (báo cáo review có một dòng cho từng quy ước `check: review`) |

Các bước chạy theo thứ tự trong danh sách; không có bước "loop" riêng. Fail ở bước có `on_fail` thì task quay về bước đó và số vòng tăng 1. Hết `max_rounds`, hoặc bước không có `on_fail`, thì task chuyển `blocked`, cần người quyết định.

File được kiểm hai lớp: JSON Schema (`foundation/src/agentflow/schemas/workflow.schema.json`, editor có thể dùng qua dòng `# yaml-language-server: $schema=...`) và kiểm tham chiếu trong Python (id không trùng, `on_fail` trỏ tới bước đứng trước).

## Hợp đồng extension (plugin con ↔ foundation)

Plugin con khai báo một file `extension.yaml` (ví dụ `families/software-dev/backend/extension.yaml`). Foundation chỉ đọc file này, không import code của plugin và không biết plugin dùng để làm gì. Schema: [`foundation/src/agentflow/schemas/extension.schema.json`](../foundation/src/agentflow/schemas/extension.schema.json). `schema_version` là phiên bản của **hợp đồng** (hiện là `1`), khác với version của plugin.

| Khóa | Ý nghĩa |
|---|---|
| `name`, `family` | Tên extension; family phải trùng family của workflow đang dùng |
| `settings` | `key` (khóa gốc trong cấu hình dự án) và `schema` (JSON Schema) cho các cài đặt mà extension đọc; `config check` kiểm theo đây |
| `roles` | Role mới, thêm vào bộ role hợp lệ của `plan check` |
| `path_rules` | Đường dẫn chỉ một số role được đụng: áp lên `files` của mục kế hoạch và lên file staged khi `agentflow commit --item` |
| `plan_rules` | Mục đụng các đường dẫn đó thì `done-when` phải chứa nguyên văn các chuỗi (thường là lệnh của dự án) |
| `scan_tools` | Tool quét mới: image **ghim phiên bản**, `network` (`none` hoặc `host-gateway`), file đã đổi cần quét, `args`, `when` (điều kiện theo cài đặt) với `skip_note`, và cách đọc kết quả (`json_findings` với trường rule/mức độ và danh sách mức chặn, hoặc `exit_code`) |
| `gates` | Gate thêm cho từng bước (`plan-valid`, `scans-clean`) |

- Placeholder duy nhất: `${config:<khóa>}`, `${host_url:<khóa>}` (đổi `localhost` thành `host.docker.internal`) và `${files}` (cả một đối số). Chỉ được trỏ vào cài đặt dưới khóa của chính extension.
- Extension không chạy được code trên máy chủ: mọi tool chạy trong container, repo mount chỉ đọc, mặc định không có mạng. `host-gateway` chỉ thêm `--add-host host.docker.internal:host-gateway` để container gọi vào dịch vụ đang chạy trên máy chủ; không dùng `--network host`.
- `agentflow ext add <file>` (việc của người) kiểm schema, family, trùng role/tool, bước tham chiếu có trong workflow, rồi chép vào `.agentflow/extensions/<name>.yaml` và ghi tên, đường dẫn nguồn, sha256 vào `config.yaml`. Role/gate/tool lấy từ bản chép, không nhân đôi sang config. `ext list` báo lệch (`source_changed`/`source_missing`), `ext sync` đồng bộ lại.
- Cài đặt dự án nằm ở mục `settings` của `.agentflow/config.yaml`; `agentflow config get|set|check`. `config set` là việc của người.
- Một test (`tests/test_boundaries.py`) bảo đảm mã nguồn foundation không chứa từ vựng của plugin nào.

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
| `agentflow ext add <file>` / `ext list` / `ext sync [tên] [--force]` | Đăng ký, liệt kê, đồng bộ extension (`add`, `sync` là việc của người) | File không hợp lệ, sai family, trùng role/tool, nguồn mất |
| `agentflow config get <khóa>` / `config set <khóa> <giá trị>` / `config check` | Đọc, đặt (việc của người), kiểm cài đặt dự án theo schema của các extension | Chưa đặt (`SETTINGS_INVALID`) |
| `agentflow plan check [--file f]` | Kiểm kế hoạch: mã `C<n>`, role hợp lệ, `done-when`, `docs` | Có mục sai (mã `PLAN_INVALID`) |
| `agentflow report --step <bước>` | Ghi stdin vào `tasks/<task>/reports/<bước>.md` | Bước không có trong workflow, nội dung rỗng |
| `agentflow commit "<nội dung>" [--item C1]` | Scan secret rồi commit với tiền tố `T-001: `; `--item` ghi trailer `Plan-Item: C1` | Sai nhánh, không có gì staged, thấy secret, engine container không chạy, mục không có trong plan |
| `agentflow project confirm <mã...>\|--all` | Việc của người: đánh dấu quy ước `confirmed` trong `project/conventions.md` | Chưa có quy ước, mã không có, file có lỗi |
| `agentflow conventions` | Liệt kê quy ước đã gộp từ decisions, project và kho cá nhân (quy ước chưa xác nhận ghi rõ là gợi ý) | |
| `agentflow decide --answer <Q1\|S1> --text ... --check plan\|semgrep\|review [--rule r] [--overrides code] [--global]` | Việc của người: trả lời câu hỏi (của plan hoặc của setup), sinh quy ước `DC-NN` trong `decisions/`; `--global` ghi thêm `KC-NN` vào kho cá nhân | Không có câu hỏi đó, thiếu `--text`/`--check`, đã trả lời, quy ước không hợp lệ |
| `agentflow knowledge init [--dir D]` / `pull <file...>` / `push <file> [--as lessons\|patterns]` | Việc của người: tạo khung kho cá nhân; chép file người chọn vào `.agentflow/knowledge/`; đưa một bài học từ workspace về kho | Đường dẫn ra ngoài kho/workspace, file đã có ở đích |
| `agentflow mcp serve` | Chạy server MCP trên stdio (do Claude Code/Antigravity khởi động) | |
| `agentflow guard` | Đọc `{"command","cwd"}` từ stdin, in `{"decision","rule","reason"}` | Input không phải JSON hợp lệ |

### Vòng đời task

`task new` → mỗi bước: `task advance --result pass` → (bước cần duyệt) `task approve` → bước kế. Fail ở `test`/`security`/`review` quay thẳng về `implement`, đếm vòng; hết `max_rounds` (mặc định 3) thì task `blocked` và chỉ người mới `task approve` để cho làm tiếp (vòng reset về 0, ghi một file vào `decisions/`) hoặc `task cancel`. Đi hết bước cuối thì task `done`. Chỉ một task mở tại một thời điểm.

### commit và guard

`agentflow commit` chỉ chạy khi đang ở nhánh của task và có file staged. Gitleaks (image ghim phiên bản, chạy qua Docker, dự phòng Podman, mount chỉ đọc) quét phần staged; engine không chạy hoặc có secret thì báo lỗi và **không commit**.

`agentflow guard` chặn: `git push` mọi dạng; mọi dạng `git commit` trong dự án đã có `.agentflow/` (chỉ cho commit qua `agentflow commit`; repo không có `.agentflow/` thì không chặn); `merge`/`commit`/`rebase`/`cherry-pick`/`revert`/`am` khi đang ở `main` hoặc `develop`; `reset --hard`; `clean` có cả `-f` và `-d`; `branch -D` (và `-d -f`); xóa tag; tạo tag hoặc ref dưới `agentflow/` (tag duyệt chỉ do `task approve` tạo); các lệnh của người (`decide`, `ext add`, `ext sync`, `config set`, `task seal`) khi agent tự chạy. Hiểu lệnh ghép (`&&`, `;`, `|`), `git -C`, `bash -c "..."` và việc `git switch` sang nhánh được bảo vệ ngay trong chuỗi lệnh. Đây là lưới an toàn cho agent, không phải sandbox: alias git, script hay biến môi trường vẫn có thể vượt qua.

### Bảo vệ workspace

Mọi ghi vào `.agentflow/` chỉ đi qua lệnh `agentflow` (và tool MCP của nó). Hook `pre-tool` chặn hai đường khác:

- **Tool ghi file của CLI.** Claude Code: `Write`, `Edit`, `NotebookEdit` (và `MultiEdit` cho chắc); Antigravity: `write_to_file`, `replace_file_content`, `multi_replace_file_content`. Đường dẫn được đổi thành tuyệt đối, bỏ `.`/`..`/dấu phân cách thừa, theo symlink; trên Windows so tên không phân biệt hoa thường. Một thư mục `.agentflow` chỉ được bảo vệ khi trong nó có `config.yaml`, nên thư mục trùng tên (`.agentflow-notes`) không bị ảnh hưởng.
- **Lệnh shell ghi vào `.agentflow/`, mức cố gắng tốt nhất.** Chuyển hướng `>`, `>>`, `>|`, `&>`, `2>`; `tee`, `cp`/`copy` (chỉ đích), `mv`, `rm`, `touch`, `truncate`, `mkdir`, `sed -i`, `dd of=`; `Set-Content`, `Add-Content`, `Out-File`, `Clear-Content`, `New-Item`, `Remove-Item`, `Copy-Item`, `Move-Item` và bí danh PowerShell. Lệnh ghép, `cd` trước đó và `bash -c "..."` được hiểu. Thân heredoc được bỏ qua (đó là dữ liệu cho lệnh đọc nó), nên `agentflow report ... <<'EOF'` có dấu `>` trong nội dung không bị chặn nhầm. Đọc `.agentflow/` luôn được phép.

Đây là lưới an toàn, **không phải sandbox**. Không bị chặn: `python -c`/`node -e` và script (`bash run.sh`), alias, biến môi trường, hay một chương trình khác tự ghi file. Muốn chặn cứng cần sandbox của hệ điều hành hoặc quyền `deny` của CLI.

### Tool MCP

`agentflow mcp serve` (SDK `mcp` 2.x, stdio) cho agent tám tool, mỗi tool gọi `WorkspaceService` (`services.py`), cùng mã với CLI nên cùng luật; luật bị vi phạm trả về dưới dạng lỗi tool kèm thông báo rõ.

| Tool | Việc |
|---|---|
| `status`, `next_step` | Trạng thái task và việc tiếp theo |
| `plan_check` | Kiểm kế hoạch; plan sai là kết quả `{ok, problems}`, không phải lỗi tool |
| `report_write(step, content)` | Ghi báo cáo. **Chỉ cho bước hiện tại của task đang mở, khi bước còn `in_progress`**: từ chối bước khác và từ chối ghi đè báo cáo của bước đã qua/đang chờ duyệt (cả `agentflow report`) |
| `project_write(section, content)` | Ghi `project/{profile,architecture,sources,conventions}.md`; từ chối khi còn task mở |
| `scan_summary` | Kết quả scan và phát hiện chặn còn lại |
| `knowledge_search`, `knowledge_read` | Chỉ đọc bản chép trong `.agentflow/knowledge/` |

Không có tool cho việc của người: duyệt, hủy, seal, `decide`, extension, `config set`, push kiến thức. Một test giữ danh sách tool là danh sách đóng.

Plugin khai báo server ở `.mcp.json` (Claude Code) và `mcp_config.json` (Antigravity), cùng lệnh `agentflow mcp serve`. Điều đã thử thật nằm trong [mcp-notes.md](mcp-notes.md): tên tool ở Claude Code, tên tool của agent plugin, việc Antigravity chạy server ở thư mục plugin (nên server tìm dự án qua `cwd`, `AGENTFLOW_PROJECT_DIR`, `PWD`, rồi con trỏ `~/.agentflow/active-project.txt` mà hook Antigravity để lại), và việc Antigravity không cho giới hạn tool MCP theo role.

### Hồ sơ dự án và quy ước

Skill `setup` hỏi người đường dẫn tài liệu (không tự đi tìm), giao cho role `scout` (đọc, chạy lệnh; chỉ ghi qua `project_write`) đọc tài liệu và code rồi viết `.agentflow/project/{profile,architecture,sources,conventions}.md`. Chỉ ghi được khi không có task mở.

`conventions.md` có dạng `### PC-01 - tiêu đề` kèm `- check:` (`plan` | `semgrep` | `review`), `- rule:`, `- status:` (`unconfirmed` | `confirmed`), `- source:`, `- description:`, tùy chọn `- overrides:`; mục `## Câu hỏi mở` chứa `### S1 - ...` với `- docs:` và `- code:` cho chỗ tài liệu và code mâu thuẫn (scout không tự chọn).

Quyền xác nhận thuộc về người:
- Quy ước agent ghi luôn là `unconfirmed`. Ghi `confirmed` thì bị đưa về `unconfirmed` (tool báo trong `demoted`).
- Quy ước đã `confirmed` mà nội dung (tiêu đề, check, rule, source, description, overrides) bị đổi thì tự về `unconfirmed`; giữ nguyên thì vẫn `confirmed`.
- Xóa một quy ước đã `confirmed` bị từ chối; chỉ người làm (sửa tay file).
- `agentflow project confirm <mã...>|--all` (chỉ người chạy, guard từ chối khi agent chạy) đánh dấu `confirmed`. `agentflow task new` cảnh báo (không chặn) khi còn quy ước `unconfirmed`.

### Quy ước, kho kiến thức và bài học

**Ba nguồn quy ước**, ưu tiên từ cao xuống: `decisions/` (câu trả lời của người, `DC-NN`) > `project/conventions.md` (`PC-NN`) > `knowledge/conventions.md` (bản chép quy ước cá nhân, `KC-NN`). `agentflow conventions` (và tool MCP `conventions`) gộp chúng; một quy ước thay quy ước khác khi ghi `overrides: <mã>` và nguồn của nó ưu tiên cao hơn. Quy ước của người (DC, KC) có hiệu lực ngay; quy ước của dự án chỉ được kiểm sau khi người `project confirm`.

**Ba cách kiểm** (`check:` là tập đóng):
- `plan`: hiện có `rule: item-order`. Mục kế hoạch có thêm `kind: interface|implement|other`; mục `interface` phải đứng trước mục `implement` đụng cùng file. Khi quy ước này đang hiệu lực, `kind` là bắt buộc, và mục interface/implement phải có `files`.
- `semgrep`: `rule: <file>.yaml` là rule do **người** viết, để trong `.agentflow/knowledge/semgrep/` (người chép từ kho cá nhân bằng `knowledge pull semgrep/<file>`). Chạy cùng scan ở bước `security` như một tool riêng `semgrep-conventions` (container riêng, mount chỉ đọc, không mạng); rule chỉ chặn khi `severity` là ERROR/HIGH/CRITICAL. Thiếu hoặc hỏng file rule là lỗi cứng, không bỏ qua im lặng. Không dùng rule của Semgrep Registry ở đây.
- `review`: gate `conventions-reviewed` đòi báo cáo review có `PC-01: đạt` hoặc `vi phạm PC-01 ở file:dòng` cho **từng** quy ước hiệu lực; có vi phạm thì không cho `pass` (phải `fail` để implementer sửa).

**Câu hỏi.** Planner không đoán: mục `## Chưa có quy ước` trong plan có `### Q1 - ...` (`- ask:`, `- options:`, `- needed-by:`). Gate `plan-valid` chặn tới khi người chạy `agentflow decide --answer Q1 --text "..." --check <loại>`; câu trả lời thành quy ước `DC-NN` (`decisions/<task>-answer-Q1.md`). Câu hỏi `S1` của scout (tài liệu và code mâu thuẫn) trả lời cùng lệnh, file `decisions/project-answer-S1.md`.

**Kho cá nhân** nằm ngoài mọi repo: đường dẫn ở `~/.agentflow/user.yaml` (`knowledge_dir`, mặc định `~/knowledge`; `AGENTFLOW_HOME` đổi thư mục `~/.agentflow`). Khung gồm `index.md`, `conventions.md`, `sources.md`, `lessons/`, `patterns/`, `semgrep/`. Chỉ người chạy `knowledge init/pull/push` (guard từ chối khi agent chạy) và agent không bao giờ ghi vào kho; tool MCP `knowledge_*` chỉ đọc bản chép trong `.agentflow/knowledge/`.

**Bài học.** Cuối báo cáo review, reviewer có thể thêm `## Bài học đề xuất` (`### L1 - tiêu đề`). Khi seal, `agentflow` tách thành `tasks/<task>/lessons/L<n>.md`, liệt kê trong `summary.md`; người chọn bài nào đưa về kho bằng `agentflow knowledge push <file>`.

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
- Báo nhầm chỉ được bỏ qua bằng file trong `decisions/` do `agentflow decide --suppress` tạo; lệnh này chỉ người chạy được (hook từ chối khi agent tự chạy). Agent không có đường nào hạ mức. Hook chặn mọi tool ghi file vào `.agentflow/` (xem mục "Bảo vệ workspace"), nên agent không tự tạo được file trong `decisions/` bằng tool của CLI.
- Cấu hình bộ rule Semgrep bằng khóa `scan.semgrep.rulesets` (mặc định `p/default`).

- Hook Stop chỉ nhắc khi bước đang `in_progress` và đã có báo cáo của bước ghi sau lúc bước bắt đầu.

Mã lỗi nằm trong `ExitCode` (`foundation/src/agentflow/constants.py`).
