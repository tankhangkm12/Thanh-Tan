# Ghi chú MCP (đã thử thật, 2026-10-10)

Thử bằng một plugin tạm có `.mcp.json` / `mcp_config.json` trỏ tới một server stdio dựng bằng SDK `mcp` 2.3.0.

## Claude Code 2.1.296

- Server của plugin đăng ký là `plugin:<plugin>:<server>` và tool có tên `mcp__plugin_<plugin>_<server>__<tool>` (ví dụ `mcp__plugin_probe-mcp_agentflow__ok`). `claude -p` gọi được khi tên đó nằm trong `--allowedTools`.
- Subagent của plugin có `tools:` là danh sách cho phép: ghi đúng tên đầy đủ trên là subagent gọi được tool, không ghi thì không. Vì vậy `tools/build.py` ghi tên tool MCP vào từng agent theo role.
- `--allowedTools` nhận nhiều giá trị, nên prompt phải đi qua stdin.

## Antigravity 1.3.3

- Plugin khai báo server ở `mcp_config.json` (cùng dạng `mcpServers`); server hiện ra với tên `<plugin>_<server>` (ví dụ `probe-mcp_agentflow`), tool giữ tên gốc (`ok`). `agy -p` gọi được.
- Trường `tools:` của agent **chỉ nhận tool dựng sẵn**. Ghi tên tool MCP dưới bất kỳ dạng nào (`ok`, `server/ok`, `mcp_server_ok`, `mcp(server/ok)`, tên server) đều làm agent không khởi động được: `unknown component: tool "..." not found in registry`.
- Agent có `tools:` vẫn gọi được tool MCP (thử với `tools: [view_file]`). Nghĩa là **không giới hạn tool MCP theo role được** trong Antigravity.
- Hệ quả: các luật phải do server tự kiểm (xem `project_write`: chỉ ghi khi không có task đang mở; nội dung quy ước phải đúng định dạng). Quyền theo role chỉ có ở Claude Code.
- Tài liệu không có biến "gốc plugin", nên `command` của server là `agentflow` (cần cài global, như hook).
