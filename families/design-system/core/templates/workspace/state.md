# Trạng thái

> Điểm vào duy nhất. Đọc file này trước khi làm bất cứ việc gì khác. Orchestrator cập nhật sau mỗi task và mỗi gate.

## Hiện tại

- **Dự án:** <tên dự án>
- **Chế độ:** <thiết kế mới | nâng cấp>
- **Mức áp dụng:** <chưa duyệt | S | M | L | XL>
- **Giai đoạn hiện tại:** <G0>
- **Cập nhật lần cuối:** <YYYY-MM-DD>

## Gate

Trạng thái: `chưa làm` · `đang làm` · `chờ duyệt` · `đã duyệt`. Chỉ ghi `đã duyệt` khi người dùng nói rõ theo ID (ví dụ `G4: duyệt`); trích nguyên văn và ngày. "ok", "được", im lặng hay câu mơ hồ không phải duyệt.

| Gate | Giai đoạn | Trạng thái | Người dùng nói (nguyên văn) | Ngày |
| --- | --- | --- | --- | --- |
| G0 | Khởi tạo và hồ sơ dự án | đang làm | | |
| G1 | Context | chưa làm | | |
| G2 | Tiêu chí lựa chọn TC | chưa làm | | |
| G3 | Kiểu kiến trúc | chưa làm | | |
| G4 | Stack và phiên bản | chưa làm | | |
| G5 | Capacity sơ bộ | chưa làm | | |
| G6 | Luồng chính | chưa làm | | |
| G7 | Thiết kế chi tiết | chưa làm | | |
| G8 | Bảo mật, hạ tầng, quy trình | chưa làm | | |
| G9 | Rủi ro và roadmap | chưa làm | | |
| G10 | Kiểm tra chéo và phát hành | chưa làm | | |

## Task đang mở

<!-- Một dòng mỗi task: ID, tên, trạng thái. Chi tiết ở plan/tasks/T-xxx-<tên>.md -->

| ID | Tên | Trạng thái | File |
| --- | --- | --- | --- |
| | | | |

## Câu hỏi đang chờ

<!-- Danh sách ID câu hỏi còn mở ở questions.md -->

- (không có)

## Quyết định đang chờ

<!-- Danh sách ID D-xxx chưa có quyết định của người dùng -->

- (không có)

## Việc tiếp theo

1. <việc đầu tiên session sau phải làm>
