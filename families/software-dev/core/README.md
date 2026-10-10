# dev-core

Plugin lõi của nhóm **software-dev**. Giữ những gì mọi plugin `dev-*` dùng chung. Các plugin `dev-*` còn lại phụ thuộc vào `dev-core`.

## Có gì bên trong

| Thành phần | Vị trí | Việc làm |
|---|---|---|
| Workflow 6 bước | `workflow.yaml` | Đọc bởi `agentflow init --workflow` |
| 4 skill | `skills/{start,continue,status,approve}/SKILL.md` | Bắt đầu task, làm tiếp, xem trạng thái, duyệt |
| 6 role (agent) | nguồn `src/roles/*.md` | `orchestrator`, `planner`, `implementer`, `tester`, `security`, `reviewer` |
| Hook | `hooks/hooks.json` (Claude Code), `hooks.json` (Antigravity) | Chặn lệnh git nguy hiểm, nạp tóm tắt task đầu phiên, nhắc cập nhật trạng thái khi dừng |

Skill gọi lệnh `agentflow` và không bao giờ sửa tay file trong `.agentflow/`. Hook chỉ hoạt động trong dự án đã có `.agentflow/`.

Trong Claude Code, tên đầy đủ của skill là `/dev-core:start`, `/dev-core:continue`, `/dev-core:status`, `/dev-core:approve`.

## Agent được sinh từ một nguồn

Sửa role ở `src/roles/<role>.md` (frontmatter `name`, `description`, `capabilities: [read, edit, run]` + nội dung prompt), rồi chạy:

```
uv run tools/build.py           # sinh claude/agents/*.md, agents/*.md và cập nhật danh sách agents trong manifest
uv run tools/build.py --check   # báo lỗi nếu file sinh ra đã cũ
```

Không sửa tay `claude/agents/` và `agents/`. `build.py` đổi quyền trừu tượng thành tên tool thật của từng CLI, từ chối tên tool lạ và từ chối cấp quyền sửa file cho `orchestrator`, `planner`, `security`, `reviewer`.

| Quyền | Claude Code | Antigravity |
|---|---|---|
| `read` | Read, Glob, Grep | view_file, list_dir, find_by_name, grep_search |
| `edit` | Edit, Write | write_to_file, replace_file_content, multi_replace_file_content |
| `run` | Bash, PowerShell | run_command |

Lưu ý: tool chạy lệnh về lý thuyết vẫn có thể ghi file. Với các role chỉ đọc, đây là giới hạn của hai CLI chứ không phải của plugin; prompt của role cấm việc đó.

## Cài đặt

```
/plugin install dev-core --marketplace tankhangkm12/Thanh-Tan-
```

Chi tiết cả hai CLI: [README gốc](../../../README.md#cài-đặt). Cần cài `agentflow` trước thì hook mới chạy.
