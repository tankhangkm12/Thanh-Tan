# Hướng dẫn dùng design-core và design-architecture

Chỉ nói cách dùng. Quy trình, quyền agent và tiêu chí nằm ở [PLAN.md](../PLAN.md) và `workflow/`.

## Cần có trước

- `uv` (chạy mọi script), `git`, Claude Code.
- Docker hoặc Podman, đang chạy: để chạy spike (mức XL bắt buộc).
- `agy` (Antigravity CLI): tùy chọn, chỉ cần khi hội đồng gọi thành viên qua CLI ngoài.

## Cài đặt

Marketplace chưa có (làm sau chạy thử), nên nạp plugin từ thư mục repo. `--plugin-dir` lặp được (theo `claude --help`), mỗi plugin một cờ:

```text
claude --plugin-dir <repo>/families/design-system/core --plugin-dir <repo>/families/design-system/design-architecture
```

Chạy trong repo thiết kế của dự án (không phải repo plugin). `design-architecture` cần `design-core` cùng được nạp.

## Chạy

```text
claude --agent design-core:orchestrator
```

Phiên chính là Orchestrator. Lần đầu nó chạy `init_workspace.py` tạo `.agent-workspace/` (đã vào `.gitignore`); các phiên sau nó đọc `state.md` để biết đang ở đâu. Orchestrator tự gọi Planner, Researcher, Designer, Reviewer và hội đồng.

## Luồng G0–G10

| Gate | Việc | Bạn duyệt |
|---|---|---|
| G0 | Khởi tạo, hồ sơ dự án, mức S/M/L/XL, model | Mức, các phần áp dụng, danh mục model |
| G1 | Context | FR, NFR có số, ràng buộc, giả định |
| G2 | Tiêu chí lựa chọn TC | Tiêu chí và trọng số |
| G3 | Kiểu kiến trúc | Kiểu và giai đoạn scale |
| G4 | Stack và phiên bản | Từng lớp, ma trận phiên bản |
| G5 | Capacity sơ bộ | Tải, dung lượng, chi phí |
| G6 | Luồng chính | Luồng |
| G7 | Thiết kế chi tiết | Service, database, app frontend |
| G8 | Bảo mật, hạ tầng, quy trình | Từng phần |
| G9 | Rủi ro và roadmap | Sổ rủi ro |
| G10 | Kiểm tra chéo, phát hành | Phát hành vN |

Mỗi phiên làm trọn một giai đoạn và dừng ở gate. Không có gate nào tự qua: thiếu lời duyệt của bạn thì dừng.

## Khuôn yêu cầu task

Bốn prompt mẫu. Dòng "Chạy với" là ghi chú cho bạn; đổi model hoặc effort theo nhu cầu.

**1. Thiết kế mới**

```text
Chạy với: Claude Code · model Sonnet · effort high

Dùng plugin design-architecture, chế độ THIẾT KẾ MỚI.

Dự án: <tên> — <1–2 câu mô tả>
Repo thiết kế: <đường dẫn>
Stack bắt buộc (nếu có): <ví dụ: backend phải là NestJS> | không có
Ràng buộc đã biết: ngân sách <…>/tháng · team <n> người (<kỹ năng>) · hạn <ngày> · hạ tầng <…> · tuân thủ <…>
Thiết bị người dùng chính (nếu biết): <…>
Tài liệu UI của designer (nếu có): <đường dẫn danh sách SCR>

Tài liệu BA đã duyệt:
<dán nội dung, hoặc liệt kê đường dẫn từng file>

Yêu cầu:
- Lưu tài liệu BA vào .agent-workspace/inputs/ba/ và chỉ đọc từ đó.
- Dò các model gọi được, ghi .agent-workspace/models.md.
- Làm hết G0 rồi dừng: trình hồ sơ dự án, mức áp dụng và danh mục model để tôi duyệt.
- Chỗ nào chưa rõ thì ghi vào questions.md và hỏi tôi, không tự giả định.
```

**2. Nâng cấp từ thiết kế cũ**

```text
Chạy với: Claude Code · model Sonnet · effort high

Dùng plugin design-architecture, chế độ NÂNG CẤP.

Repo thiết kế: <đường dẫn> · phiên bản hiện có: v<N>
Bản thiết kế cũ: <đường dẫn architecture/ cũ>
Lý do nâng cấp: <…>
Giữ nguyên, không xét lại: <…> | không có

Tài liệu BA mới hoặc phần thay đổi:
<dán nội dung, hoặc liệt kê đường dẫn>

Yêu cầu:
- Đọc bản cũ và archive/ (nếu còn) trước khi đề xuất gì.
- Liệt kê phần giữ, phần đổi, phần thêm.
- Dừng ở G0 để tôi duyệt phạm vi nâng cấp.
```

**3. Tiếp tục ở session mới**

```text
Chạy với: Claude Code · model Sonnet · effort medium

Tiếp tục design-architecture ở repo này.
(Tuỳ chọn) Tôi đã trả lời trong questions.md các mục: CH-003, CH-005.
```

**4. Duyệt gate và quyết định**

```text
Chạy với: Claude Code · model Sonnet · effort medium

G4: duyệt.            (hoặc: G4: chưa duyệt — lý do: …)
D-007: chọn B. Ghi chú: …
R-04: chấp nhận rủi ro.
CH-006: <câu trả lời>
```

## Trả lời theo ID

Orchestrator chỉ ghi lời duyệt, quyết định và rủi ro chấp nhận khi bạn nói rõ theo ID, nguyên văn sẽ được lưu lại.

| Tiền tố | Nghĩa | Ví dụ |
|---|---|---|
| `G` | Gate | `G4: duyệt` |
| `D` | Quyết định (có phương án) | `D-007: chọn B` |
| `R` | Rủi ro | `R-04: chấp nhận rủi ro` |
| `CH` | Câu hỏi của agent | `CH-006: dùng giờ Việt Nam` |
| `S` | Spike (chạy thử trong container) | `S-02: chạy` |

## Nhắc khi kiểm tra

`check_profile.py` cần template: Orchestrator và Reviewer phải truyền `--templates` rõ ràng, trỏ tới `design-architecture/templates`. Không tìm thấy template là lỗi; `--no-templates` chỉ để thử, báo cáo ghi "Chưa kiểm mục bắt buộc" và không đủ để qua gate. Nếu thấy agent chạy `check_profile.py` mà không có `--templates`, nhắc nó.
