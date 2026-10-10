# Hướng dẫn dùng nhóm software-dev

Tài liệu này nói về **quy trình và môi trường làm việc**: cài gì, chuẩn bị gì, viết yêu cầu task thế nào, duyệt ra sao, tiết kiệm token thế nào. Nó không nói về quy ước code, kiến trúc hay stack của dự án: những thứ đó nằm trong `.agentflow/project/` và do bạn xác nhận (xem [Chuẩn bị một lần cho mỗi dự án](#chuẩn-bị-một-lần-cho-mỗi-dự-án)).

Mục lục: [chọn plugin](#chọn-plugin-theo-loại-dự-án) · [chuẩn bị](#chuẩn-bị-một-lần-cho-mỗi-dự-án) · [khuôn yêu cầu task](#khuôn-yêu-cầu-task) · [chọn chế độ](#chọn-chế-độ) · [checklist khi duyệt](#checklist-khi-duyệt) · [lệnh của người](#lệnh-của-người) · [tiết kiệm token](#tiết-kiệm-token) · [xử lý tình huống](#xử-lý-tình-huống).

Cài đặt `agentflow` và plugin: xem [README gốc](../../README.md#cài-đặt-từng-bước). Mỗi plugin con có mục "Dùng cùng dev-core" trong README của nó, nói riêng dữ liệu cần thêm và ví dụ done-when cho gate của plugin đó; khuôn yêu cầu task chỉ có một, ở đây.

## Chọn plugin theo loại dự án

`dev-core` luôn có: nó giữ quy trình, hook an toàn và scan. Plugin con chỉ thêm nghiệp vụ riêng.

| Loại dự án | Cài | Ghi chú |
|---|---|---|
| Backend | `dev-core` + `dev-backend` | Dùng được. Xem [dev-backend](backend/README.md) |
| Mobile | `dev-core` + gói Google | **Chưa hỗ trợ Antigravity IDE**; đang chờ một mốc riêng. Chưa có hướng dẫn ở đây |
| Web | `dev-core` + `dev-frontend` | Khi plugin có nội dung. Hiện còn là khung |
| Hạ tầng | `dev-core` + `dev-infra` | Khi plugin có nội dung. Hiện còn là khung |

`dev-design` (thiết kế giao diện và hệ thống) cũng còn là khung.

## Chuẩn bị một lần cho mỗi dự án

Dự án phải là repo git có nhánh `main` và `develop`, cây làm việc sạch.

1. **Khởi tạo workspace.** Trong thư mục dự án:

   ```
   agentflow init --workflow "<repo>/families/software-dev/core/workflow.yaml"
   ```

2. **Đăng ký plugin con và đặt cài đặt (chỉ khi dùng dev-backend).** Đây là việc của bạn, agent không chạy được. Đặt các cài đặt `backend.*` **trước khi tạo task đầu tiên**; danh sách đầy đủ và ý nghĩa nằm trong [dev-backend](backend/README.md#dùng-với-một-dự-án).

   ```
   agentflow ext add "<repo>/families/software-dev/backend/extension.yaml"
   agentflow config set backend.test_command "<lệnh chạy test>"
   agentflow config check
   ```

3. **Hồ sơ hóa dự án.** Gõ `/dev-core:setup` (Antigravity: nhờ agent dùng skill `setup`). Skill hỏi bạn đường dẫn tài liệu rồi giao cho scout; scout chỉ đọc đúng các đường dẫn đó và code của dự án. Nên đưa cho scout:
   - tài liệu yêu cầu và phạm vi sản phẩm;
   - ghi chú kiến trúc, ADR;
   - hướng dẫn đóng góp, hướng dẫn chạy build và test;
   - README, wiki export;
   - contract API hoặc thiết kế nếu có.

   Không có tài liệu nào thì nói "không có": scout làm việc từ code.

4. **Duyệt hồ sơ và xác nhận.** Mở bốn file `profile`, `architecture`, `sources`, `conventions` trong `.agentflow/project/`. Mỗi câu hỏi mở `S1`, `S2`, ... (chỗ tài liệu và code mâu thuẫn) do bạn quyết, rồi xác nhận quy ước bạn đồng ý:

   ```
   agentflow decide --answer S1 --text "<quy ước, một dòng>" --check review
   agentflow project confirm PC-01 PC-02
   ```

   Quy ước chưa xác nhận chỉ là gợi ý cho agent, chưa được kiểm. `agentflow task new` cảnh báo khi còn quy ước chưa xác nhận.

5. **Khối permissions của Claude Code.** Bắt buộc, gồm cả quy tắc `ask` cho `task approve`, `task cancel`, `decide`. Nội dung ở [README gốc, Bước 4](../../README.md#bước-4-bắt-buộc-quy-tắc-permissions-của-claude-code); đừng chép lại vào chỗ khác để khỏi lệch.

6. **Kho kiến thức (tùy chọn).** Bài học và rule Semgrep của riêng bạn nằm ngoài mọi repo. Chép vào dự án file bạn chọn, agent chỉ đọc bản chép:

   ```
   agentflow knowledge init
   agentflow knowledge pull lessons/x.md semgrep/rule.yaml
   ```

## Khuôn yêu cầu task

Khuôn này là đầu vào của bước `confirm`. Gõ `/dev-core:start` (Antigravity: nhờ agent dùng skill `start`), rồi dán khuôn đã điền:

```
Loại: feature | bugfix | hotfix        Cỡ: normal | small
Mục tiêu: <làm gì, cho ai, 1–2 câu>
Xong khi: <tiêu chí kiểm được>
Trong phạm vi: <phần được đụng>
Ngoài phạm vi: <không làm gì>
Tài liệu: <link spec / màn hình thiết kế / contract API, hoặc "không có">
```

Mục nào bỏ trống thì orchestrator hỏi lại ở bước `confirm`, trước khi bạn duyệt. Điền càng cụ thể, `done-when` của kế hoạch càng chặt.

### Không cần viết trong prompt

| Thông tin | Agent lấy ở đâu |
|---|---|
| Kiến trúc, stack, lệnh build và lệnh test | `.agentflow/project/` (do scout viết, bạn xác nhận) |
| Quy ước | `agentflow conventions` (gộp từ `decisions/`, hồ sơ dự án và kho cá nhân) |
| Bài học từ task trước | Kho kiến thức, bản đã `knowledge pull` vào `.agentflow/knowledge/` |
| Quy trình, các bước, việc agent không được làm | Skill và hook của `dev-core` |

### Ví dụ điền sẵn

Feature (cỡ normal):

```
Loại: feature        Cỡ: normal
Mục tiêu: Cho người dùng đã đăng nhập tải về lịch sử đơn hàng của chính mình.
Xong khi: `<lệnh test của dự án>` xanh; có test cho trường hợp lịch sử rỗng; người dùng khác không lấy được dữ liệu của mình.
Trong phạm vi: màn hình lịch sử đơn hàng và phần xử lý phía sau nó.
Ngoài phạm vi: đổi định dạng dữ liệu hiện có; các loại báo cáo khác.
Tài liệu: <link spec yêu cầu tải lịch sử đơn hàng>
```

Bugfix:

```
Loại: bugfix        Cỡ: normal
Mục tiêu: Danh sách đơn hàng bị lặp dòng khi lọc theo khoảng ngày.
Xong khi: có test tái hiện lỗi, đỏ trước khi sửa và xanh sau khi sửa; `<lệnh test của dự án>` xanh.
Trong phạm vi: phần lọc theo ngày của danh sách đơn hàng.
Ngoài phạm vi: giao diện danh sách; các bộ lọc khác.
Tài liệu: không có
```

Task small:

```
Loại: bugfix        Cỡ: small
Mục tiêu: Sửa câu thông báo lỗi sai chính tả ở màn hình đăng nhập.
Xong khi: thông báo hiển thị đúng chính tả; `<lệnh test của dự án>` xanh.
Trong phạm vi: chỉ chuỗi thông báo đó.
Ngoài phạm vi: mọi thông báo khác.
Tài liệu: không có
```
