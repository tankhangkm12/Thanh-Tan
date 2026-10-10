# tools

Script build và bảo trì repo. Viết bằng Python, chạy qua uv (`uv run`), không dùng Node.

| Script | Việc làm |
|---|---|
| `build.py` | Sinh agent của Claude Code (`claude/agents/`) và Antigravity (`agents/`) từ `src/roles/` của plugin, cập nhật danh sách `agents` trong manifest. `--check` để kiểm. Xem [dev-core](../families/software-dev/core/README.md) |
| `test_build.py` | Test của `build.py` và của dev-core (role, skill, tool, file sinh ra phải khớp nguồn; quy tắc prompt: không nối lệnh, nói rõ agent không push/merge/PR; khối quy tắc permissions trong README) |
| `smoke.py` | Thử end-to-end `agentflow` (init, task, plan check, commit, scan thật, guard, hook) trên repo tạm. Cần Docker |
| `smoke_backend.py` | Thử end-to-end dev-core + dev-backend trên dự án mẫu (`sample_backend.py`: Python một endpoint, PostgreSQL trong Docker, migration lên/xuống, spec OpenAPI). `--until plan|implement` dừng sớm; `--install-check` cài lại `dev-core`, `dev-backend` vào Claude Code (marketplace local) và Antigravity (đường dẫn local) rồi xác nhận skill, agent, hook được nạp (một lượt `claude -p` ngắn) và in cảnh báo nếu settings của dự án mẫu thiếu quy tắc `ask` bắt buộc |
| `test_smoke_backend.py` | Test của các hàm phụ trợ trong smoke_backend (không cần Docker) |
| `test_backend.py` | Test của dev-backend: role `db-engineer`, 6 skill không giả định stack, agent sinh ra khớp nguồn |

```
uv run tools/build.py --check
uv run tools/build.py --plugin families/software-dev/backend --check
uv run --with pyyaml --with pytest pytest tools
```
