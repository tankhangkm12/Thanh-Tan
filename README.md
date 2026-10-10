# Thanh-Tan-

> **MVP.** Dùng được: plugin `dev-core` (quy trình task, hook an toàn, scan bảo mật, tool MCP, quy ước và kho kiến thức, 5 skill, 7 role) và `dev-backend` (role `db-engineer`, 6 skill, Squawk, Schemathesis) cho Claude Code và Antigravity CLI, chạy trên động cơ `agentflow`. Các plugin `dev-design`, `dev-frontend`, `dev-infra` vẫn là khung.

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

Kiểm tra: `claude plugin list` phải thấy `dev-core@thanh-tan-plugins` ở trạng thái enabled. Mở lại Claude Code, gõ `/dev-core:` sẽ thấy `setup`, `start`, `continue`, `status`, `approve`. 7 agent hiện dưới tên `dev-core:orchestrator`, `dev-core:planner`, `dev-core:implementer`, `dev-core:tester`, `dev-core:security`, `dev-core:reviewer`, `dev-core:scout`. (Lệnh `claude plugin details` hiện báo `Agents (0)` do cách đếm của nó; agent vẫn được nạp.) Cập nhật: `claude plugin update dev-core@thanh-tan-plugins`.

### Bước 2b: cài vào Antigravity CLI

```
agy plugin install "<repo>/families/software-dev/core"
agy plugin list
agy agents
```

`agy plugin list` phải có `dev-core` với `skills`, `agents`, `hooks`; `agy agents` liệt kê 7 role của dev-core (thêm `db-engineer` khi cài dev-backend). `agy plugin install` chép một bản vào máy, nên sau mỗi lần `git pull` hãy chạy lại lệnh cài. Cách cài thẳng từ GitHub cho repo nhiều plugin chưa được xác nhận.

### Cài thêm dev-backend

```
claude plugin install dev-backend@thanh-tan-plugins
agy plugin install "<repo>/families/software-dev/backend"
```

Rồi trong dự án, **bạn** đăng ký extension và đặt cài đặt (xem [dev-backend](families/software-dev/backend/README.md)): `agentflow ext add`, `agentflow config set backend.*`, `agentflow config check`.

### Thay đổi từ agentflow 0.5.0 (dev-core 0.4.0, dev-backend 0.2.0)

- Hook chặn mọi tool ghi file vào `.agentflow/` (Claude Code: `Write`, `Edit`, `NotebookEdit`; Antigravity: `write_to_file`, `replace_file_content`, `multi_replace_file_content`) và các lệnh shell phổ biến ghi vào đó (mức cố gắng tốt nhất, không phải sandbox: `python -c`, script, alias vẫn qua được).
- Server MCP `agentflow mcp serve` (tool `status`, `next_step`, `plan_check`, `report_write`, `project_write`, `scan_summary`, `conventions`, `knowledge_search`, `knowledge_read`) khai báo sẵn trong dev-core; báo cáo không còn cần heredoc. `report_write` chỉ ghi báo cáo của bước hiện tại và không ghi đè báo cáo của bước đã qua.
- Skill `setup` và role `scout` hồ sơ hóa dự án có sẵn; quy ước (`PC-`, `DC-`, `KC-`), câu hỏi "Chưa có quy ước", rule Semgrep của riêng bạn, gate review theo từng quy ước, kho kiến thức cá nhân và bài học đề xuất: xem [Quy ước và kho kiến thức](#quy-ước-và-kho-kiến-thức).
- `agentflow` kéo thêm gói `mcp` (SDK chính thức). Antigravity chạy server MCP trong thư mục plugin nên tìm dự án qua `cwd`, `AGENTFLOW_PROJECT_DIR`, `PWD` rồi `~/.agentflow/active-project.txt` (xem [docs/mcp-notes.md](docs/mcp-notes.md)). Cập nhật `agentflow` khi có phiên `agy` đang mở có thể báo `Access is denied`: đóng phiên đó, hoặc `uv pip install --python <venv của tool>\Scripts\python.exe --reinstall ./foundation`.

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

Hook chỉ hoạt động trong dự án đã có `.agentflow/`; ở dự án khác chúng không làm gì. Khi hook chạy, `git push`, `git commit` trực tiếp (chỉ cho commit qua `agentflow commit`), `reset --hard`, `clean -fd`, `branch -D`, xóa tag, và merge/rebase trên `main`/`develop` bị chặn với agent. Chi tiết: [docs/architecture.md](docs/architecture.md).

### Bước 4 (BẮT BUỘC): quy tắc permissions của Claude Code

Agent chạy hàng loạt lệnh `agentflow`. Để không bị hỏi từng lệnh, thêm quy tắc **allow** cho các lệnh thường ngày. Đồng thời **bắt buộc** thêm quy tắc **ask** cho ba lệnh mang quyền của người: `agentflow task approve`, `agentflow task cancel`, `agentflow decide`. Quy tắc `ask` thắng `allow` (thứ tự đánh giá là deny, rồi ask, rồi allow), nên chúng luôn hỏi bạn dù allow có khớp. Nếu bỏ `ask`, agent có thể tự duyệt bước của chính nó, và workflow mất ý nghĩa.

Dán vào `.claude/settings.json` của dự án (hoặc `~/.claude/settings.json` cho mọi dự án). Cú pháp theo [tài liệu permissions](https://code.claude.com/docs/en/permissions): `Bash(lệnh *)` khớp lệnh có hoặc không có đối số; `Bash(lệnh:*)` là cách viết tương đương.

```json
{
  "permissions": {
    "allow": [
      "Bash(agentflow status *)",
      "Bash(agentflow next *)",
      "Bash(agentflow doctor *)",
      "Bash(agentflow init *)",
      "Bash(agentflow task new *)",
      "Bash(agentflow task advance *)",
      "Bash(agentflow plan check *)",
      "Bash(agentflow report *)",
      "Bash(agentflow commit *)",
      "Bash(agentflow scan *)",
      "Bash(agentflow config get *)",
      "Bash(agentflow config check *)",
      "Bash(agentflow ext list *)",
      "Bash(agentflow workflow sync *)",
      "mcp__plugin_dev-core_agentflow__status",
      "mcp__plugin_dev-core_agentflow__next_step",
      "mcp__plugin_dev-core_agentflow__plan_check",
      "mcp__plugin_dev-core_agentflow__report_write",
      "mcp__plugin_dev-core_agentflow__project_write",
      "mcp__plugin_dev-core_agentflow__scan_summary",
      "mcp__plugin_dev-core_agentflow__conventions",
      "mcp__plugin_dev-core_agentflow__knowledge_search",
      "mcp__plugin_dev-core_agentflow__knowledge_read",
      "PowerShell(agentflow status *)",
      "PowerShell(agentflow next *)",
      "PowerShell(agentflow task new *)",
      "PowerShell(agentflow task advance *)",
      "PowerShell(agentflow plan check *)",
      "PowerShell(agentflow report *)",
      "PowerShell(agentflow commit *)",
      "PowerShell(agentflow scan *)"
    ],
    "ask": [
      "Bash(agentflow task approve *)",
      "Bash(agentflow task cancel *)",
      "Bash(agentflow decide *)",
      "PowerShell(agentflow task approve *)",
      "PowerShell(agentflow task cancel *)",
      "PowerShell(agentflow decide *)"
    ]
  }
}
```

Ghi chú:

- Claude Code tách lệnh ghép (`&&`, `;`, `|`, xuống dòng) và đòi mỗi lệnh con khớp một quy tắc; vì vậy prompt của dev-core bắt mọi lệnh `agentflow` chạy riêng.
- Báo cáo được ghi bằng tool MCP `report_write` (tên đầy đủ có tiền tố `mcp__plugin_dev-core_agentflow__`), nên không cần heredoc. Lệnh `agentflow report` (nhận nội dung qua heredoc `<<'EOF'`) chỉ còn là dự phòng khi không có tool MCP. Đã thử thật bằng `claude -p`: quy tắc `Bash(python *)` cho phép lệnh `python - <<'EOF' ... EOF`, còn không có quy tắc thì lệnh bị từ chối; heredoc không làm quy tắc mất tác dụng.
- Tám tool MCP trong `allow` chỉ đọc workspace hoặc ghi báo cáo/hồ sơ dự án theo luật của `agentflow` (báo cáo chỉ cho bước hiện tại và không ghi đè bước đã qua; hồ sơ dự án chỉ ghi khi không có task đang mở). Không có tool MCP cho việc của người (duyệt, hủy, seal, `decide`, extension, `config set`).
- Các lệnh `agentflow decide`, `ext add`, `ext sync`, `config set`, `task seal` là việc của **người**: hook từ chối khi agent tự chạy. Bạn chạy trực tiếp: trong Claude Code gõ `! agentflow decide ...`, hoặc dùng terminal riêng (Antigravity).
- Cách viết cho Antigravity: dùng chế độ phê duyệt lệnh của chính CLI đó; tài liệu của nó không có cú pháp quy tắc tương đương.

### Kiểm tra nhanh toàn bộ

```
uv run tools/smoke.py
```

Chạy `init → task → plan check → advance/approve → commit (Gitleaks thật) → scan (Semgrep, Trivy, Gitleaks thật) → guard → hook` trên một repo tạm, không đụng repo nào khác. Cần Docker đang chạy.

```
uv run tools/smoke_backend.py                    # dev-core + dev-backend trên dự án mẫu (PostgreSQL trong Docker)
uv run tools/smoke_backend.py --only-install-check   # cài lại hai plugin vào Claude Code và Antigravity rồi kiểm tra
```

### Quy ước và kho kiến thức

Lần đầu trên một dự án có sẵn: gọi skill `setup` (xem hướng dẫn dùng thử ở cuối). Scout đọc tài liệu bạn chỉ và code, rồi viết `.agentflow/project/{profile,architecture,sources,conventions}.md`; mọi quy ước ban đầu là `unconfirmed`. Bạn đọc, trả lời câu hỏi mở (`S1`...) và xác nhận bằng `agentflow project confirm PC-01 PC-02` (hoặc `--all`). `agentflow task new` cảnh báo khi còn quy ước chưa xác nhận.

Mỗi quy ước có `check:` là `plan` (hiện có `item-order`: mục `kind: interface` đứng trước mục `kind: implement` đụng cùng file), `semgrep` (rule do **bạn** viết, để trong `.agentflow/knowledge/semgrep/`, chạy cùng scan ở bước security) hoặc `review` (reviewer ghi `PC-01: đạt` hoặc `vi phạm PC-01 ở file:dòng` cho từng mã). Ưu tiên: `decisions/` > `project/conventions.md` > `knowledge/conventions.md`. Xem bằng `agentflow conventions`.

Khi dự án chưa có quy ước cho một điều planner cần quyết, plan có mục `## Chưa có quy ước` và bị chặn tới khi bạn trả lời: `agentflow decide --answer Q1 --text "Tên bảng số ít" --check review` (thêm `--global` để ghi cả vào kho cá nhân của bạn).

Kho kiến thức cá nhân nằm ngoài mọi repo (mặc định `~/knowledge`, đường dẫn ở `~/.agentflow/user.yaml`): `agentflow knowledge init` tạo khung; `agentflow knowledge pull lessons/x.md semgrep/rule.yaml` chép file bạn chọn vào `.agentflow/knowledge/` cho agent đọc; sau task, `agentflow knowledge push .agentflow/tasks/T-001/lessons/L1.md` đưa một bài học về kho. Agent không bao giờ ghi vào kho.

### Scan bảo mật

Bước `security` chạy `agentflow scan`: Semgrep (chỉ file task đã đổi), Trivy và Gitleaks, mỗi tool trong một container với image ghim phiên bản và repo mount chỉ đọc. Bước không qua được khi Semgrep có mức ERROR, Trivy có HIGH/CRITICAL **đã có bản vá**, hoặc Gitleaks có phát hiện. Docker/Podman không chạy là lỗi cứng. Lần đầu cần mạng (kéo image, tải DB Trivy, tải rule Semgrep vào cache của bạn; rule Semgrep không nằm trong repo vì giấy phép không cho phân phối lại). Báo nhầm chỉ bỏ qua được khi **bạn** chạy `agentflow decide --suppress <id> --reason "..."` (id in trong kết quả `agentflow scan`). Chi tiết: [docs/scan-notes.md](docs/scan-notes.md).

### Kế hoạch (plan) và xác nhận cuối task

Bước `plan` bị chặn nếu kế hoạch không qua `agentflow plan check`. Mỗi mục có dạng:

```
### C1 - Tiêu đề ngắn
- role: implementer
- kind: implement      # interface | implement | other (bắt buộc khi có quy ước item-order)
- files: src/a.py, tests/test_a.py
- done-when: `uv run pytest tests/test_a.py`
- docs: https://... (hoặc: không có — <lý do>)
```

Khi bạn duyệt bước cuối, `agentflow` ghi `.agentflow/tasks/<task>/summary.md` (mục, commit, link docs, kết quả scan) và tạo **annotated tag** `agentflow/<task>/approved` (message có mã task, tiêu đề, người duyệt) trên commit cuối của nhánh task. `agentflow task new` từ chối nếu task xong gần nhất chưa có tag này; bạn tạo bù cho task cũ bằng `agentflow task seal <id>` (thêm `--commit <sha>` nếu nhánh đã bị xóa). Agent không bao giờ push, merge hay tạo PR: bạn tự làm.

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

## Dùng thử trên một dự án thật

1. Cài `agentflow`: `uv tool install --force --reinstall ./foundation` (từ thư mục repo này), rồi `agentflow doctor`.
2. Cài plugin vào Claude Code (`claude plugin marketplace add "<repo>"`, `claude plugin install dev-core@thanh-tan-plugins`, `dev-backend@thanh-tan-plugins`) và/hoặc Antigravity (`agy plugin install "<repo>/families/software-dev/core"` và `.../backend`). Mở lại CLI để nạp skill, agent, hook và server MCP.
3. Dán khối `permissions` ở **Bước 4** vào `.claude/settings.json` của dự án. Quy tắc `ask` là bắt buộc.
4. Trong dự án (repo git có `main` và `develop`, cây làm việc sạch): `agentflow init --workflow "<repo>/families/software-dev/core/workflow.yaml"`. Với dev-backend, thêm bước của **bạn**: `agentflow ext add "<repo>/families/software-dev/backend/extension.yaml"`, `agentflow config set backend.*`, `agentflow config check`.
5. **Hồ sơ hóa dự án:** gõ `/dev-core:setup` (Antigravity: nhờ agent dùng skill `setup`). Bạn đưa đường dẫn tài liệu; scout đọc rồi viết `.agentflow/project/*.md`. Mở các file đó, trả lời câu hỏi mở `S1...` bằng `agentflow decide --answer S1 --text "..." --check review`, rồi xác nhận quy ước đồng ý: `agentflow project confirm PC-01 PC-02` (hoặc `--all`).
6. **Kho kiến thức (tùy chọn):** `agentflow knowledge init`; đặt rule Semgrep của bạn vào `<kho>/semgrep/` và quy ước cá nhân vào `<kho>/conventions.md`; chép vào dự án bằng `agentflow knowledge pull semgrep/<rule>.yaml conventions.md`.
7. **Làm việc:** `/dev-core:start`, rồi `/dev-core:continue`. Agent tự chạy các bước không cần duyệt và dừng ở `confirm`, `plan`, `review` để bạn `agentflow task approve` (hoặc `/dev-core:approve`). Plan có mục `## Chưa có quy ước` thì bạn trả lời bằng `agentflow decide --answer Q1 ...` rồi để agent chạy tiếp. Phát hiện chặn của scan mà bạn xác nhận là báo nhầm: `agentflow decide --suppress <id> --reason "..."`.
8. **Sau khi xong:** xem `.agentflow/tasks/<task>/summary.md` (mục, commit, scan, "Bài học đề xuất") và tag `git tag -l "agentflow/*"`. Bài học đáng giữ: `agentflow knowledge push .agentflow/tasks/<task>/lessons/L1.md`. Merge và push là việc của bạn.

Các lệnh của người (`decide`, `project confirm`, `knowledge init|pull|push`, `ext add|sync`, `config set`, `task seal`): trong Claude Code gõ với tiền tố `!`; agent tự chạy sẽ bị hook từ chối.
