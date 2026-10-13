# Nhóm design-system

> **Bản nháp (khung).** Đang ở Giai đoạn 1: mới có khung thư mục và manifest, chưa có workflow, agent hay script.

Nhóm plugin thiết kế. `design-core` giữ chuẩn chung của nhóm (workflow, tiêu chí chất lượng, agent, template, script); các plugin con phụ thuộc vào `design-core` và chỉ thêm phần riêng. Kế hoạch đầy đủ, là nguồn sự thật duy nhất: [PLAN.md](PLAN.md).

| Plugin | Phạm vi |
|---|---|
| `design-core` | Workflow G0–G10, 8 tiêu chí chất lượng, quyền ghi của agent, template workspace, script kiểm tra (chạy qua uv) |
| `design-architecture` | Biến tài liệu BA thành bộ tài liệu kiến trúc giải pháp đầy đủ, có số liệu thật; chỉ chứa template, checklist và phần "dùng với core" |

Nhóm này không chạy bằng `agentflow`: workspace là `.agent-workspace/` trong dự án và các gate do script Python kiểm.
