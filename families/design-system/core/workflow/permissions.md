# Quyền của agent

Mỗi việc giao cho một agent chạy trong ngữ cảnh riêng, chỉ được đọc đúng file Orchestrator truyền cho task đó và chỉ được ghi vào vùng của mình. Không agent nào được ghi trạng thái "Đã duyệt": chỉ người dùng duyệt. Nguồn: [PLAN.md](../../PLAN.md), mục "Các agent và quyền ghi". Các gate xem [stages.md](stages.md).

Đường dẫn tính từ `.agent-workspace/` trừ khi ghi `architecture/`.

## Bảng quyền

| Agent | Được đọc | Được ghi vào | Model / effort |
| --- | --- | --- | --- |
| Orchestrator (phiên chính) | `state.md`, `models.md`, `questions.md`, `plan/`, kết quả `checks/`; chỉ dùng để điều phối và chọn file truyền cho agent khác | `state.md`, `models.md`, `inputs/` (lưu input người dùng đưa), `questions.md` (chuyển câu trả lời), `decisions/decision-log.md`, phần "Quyết định của người dùng" trong `decision.md`, `risks/acceptance.md` (chỉ theo quy tắc 2), duy nhất dòng "Trạng thái" trong `plan/tasks/*.md` (không sửa nội dung khác của file task) | Model của phiên bạn mở / medium |
| Planner | `inputs/`, `state.md`, `models.md`, hồ sơ dự án đã duyệt | `plan/` (`plan.md`, `tasks/`), `questions.md`, bản nháp `drafts/00-context/project-profile.md` | Theo `models.md` / high |
| Researcher | Task được giao, tiêu chí TC đã duyệt, `~/knowledge/stacks/<stack>/`; không đọc `brief.md`, phiếu bầu hay `decision.md`, để giữ dữ kiện trung lập | `stack/` | Model có tìm web trong `models.md` / medium |
| Designer | Task được giao; input và context đã duyệt; `stack/`, `capacity/`, `drafts/` của giai đoạn; quyết định cuối của người dùng (không đọc phiếu từng người) | `decisions/*/brief.md`, `drafts/`, `capacity/` | Theo `models.md` / high |
| Hội đồng (3 hoặc 5 thành viên) | Chỉ `brief.md` và phần context được trích; vòng 2 thêm `r1-summary.md` ẩn danh | `decisions/*/votes/` (mỗi thành viên một file phiếu) | Mỗi thành viên một model khác nhau trong `models.md` |
| Reviewer | Bản nháp cần soát, template, checklist, nguồn gốc (BA, `capacity/assumptions.yaml`), kết quả script; không đọc brief hay lý luận của Designer | `reviews/` | Khác model với Designer / high |
| Script | Tùy script (xem bảng "Các script kiểm tra" trong PLAN.md) | `decisions/*/tally.md`, `decisions/*/votes/r1-summary.md` (do `tally_votes.py` sinh: gom nguyên văn phần "Lý do" của phiếu vòng 1, bỏ member/model/perspective, xáo thứ tự ngẫu nhiên; không tóm tắt bằng model), phần hội đồng trong `decision.md` (do `tally_votes.py` sinh), `checks/`, `architecture/`, `archive/` | Không phải agent |
| Người dùng | Mọi thứ | Duyệt gate, quyết định, chấp nhận rủi ro | — |

## Quy tắc

1. **Chỉ script `promote_drafts.py` được ghi vào `architecture/`**, và chỉ chạy sau khi người dùng duyệt gate. Đầu ra nhờ vậy chỉ chứa nội dung đã chốt.
2. **Chỉ người dùng duyệt; Orchestrator chỉ ghi lại.** Orchestrator chỉ ghi trạng thái duyệt (gate, quyết định, chấp nhận rủi ro) khi người dùng nói rõ theo ID trong tin nhắn, ví dụ `G4: duyệt`, `D-007: chọn B`, `R-04: chấp nhận`. Orchestrator trích nguyên văn câu đó kèm ngày vào nơi ghi: phần "Quyết định của người dùng" trong `decision.md`, `decisions/decision-log.md`, `risks/acceptance.md`, `state.md`. "ok", "được", im lặng hay câu mơ hồ **không phải** duyệt; khi đó Orchestrator phải hỏi lại. Quyết định nói trong chat được ghi trước khi làm tiếp.
3. **`decision.md` có hai phần.** Phần hội đồng (phương án đề xuất, tỉ lệ phiếu, ý kiến thiểu số) do `tally_votes.py` sinh từ `tally.md`, không agent nào viết tay. Phần "Quyết định của người dùng" do Orchestrator ghi theo quy tắc 2.
4. **Không ghi chéo vùng.** Reviewer không sửa bản nháp; Designer không sửa `reviews/` hay `votes/`; hội đồng chỉ ghi phiếu của chính mình; script không viết lý luận.
5. **Ngữ cảnh độc lập.** Agent không mang lịch sử trò chuyện hay suy luận của agent khác. Agent trao đổi với nhau chỉ qua file trong workspace, không truyền tin trực tiếp.
6. **Cô lập phiếu.** Vòng 1 thành viên hội đồng không thấy phiếu nào khác; vòng 2 chỉ thấy bản tóm tắt ẩn danh. Designer không thấy phiếu từng người, chỉ thấy quyết định cuối của người dùng.
7. **Reviewer soát như người ngoài.** Chỉ đọc bản nháp, template, checklist và nguồn gốc; luôn khác model với Designer của phần đang soát.
8. **Chọn model.** Orchestrator chọn model từ `models.md`. Hội đồng: mỗi thành viên một model khác nhau; không đủ model thì dùng chung model với góc nhìn khác nhau và `decision.md` ghi rõ độ đa dạng bị giảm. Model gọi lỗi bị đánh dấu không dùng được và thay bằng model khác.
