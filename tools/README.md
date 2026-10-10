# tools

Script build và bảo trì repo. Viết bằng Python, chạy qua uv (`uv run`), không dùng Node.

| Script | Việc làm |
|---|---|
| `build.py` | Sinh agent của Claude Code (`claude/agents/`) và Antigravity (`agents/`) từ `src/roles/` của plugin, cập nhật danh sách `agents` trong manifest. `--check` để kiểm. Xem [dev-core](../families/software-dev/core/README.md) |
| `test_build.py` | Test của `build.py` và của dev-core (role, skill, tool, file sinh ra phải khớp nguồn) |

```
uv run tools/build.py --check
uv run --with pyyaml --with pytest pytest tools
```
