# Kế hoạch design-architecture

Oct 12, 2026

## Mục tiêu và nguyên tắc nền

Plugin `design-architecture` (family Design) biến tài liệu BA thành một bộ tài liệu kiến trúc giải pháp đầy đủ, có số liệu thật, mà agent dev nhận vào là code được, không phải tự quyết thêm.

- **Đầu ra chỉ là tài liệu**, nằm trong `architecture/`, chỉ chứa nội dung đã chốt.
- **Bạn quyết mọi lựa chọn.** Phương án, so sánh, phiếu bầu và trạng thái duyệt chỉ nằm trong `.agent-workspace/`.
- **Phù hợp nhất với dự án, không phải tốt nhất.** Mọi đánh giá chấm theo hồ sơ dự án; làm quá tay bị trừ điểm.
- **Số liệu thật, không nói mồm.** Mọi con số có công thức, giả định và nguồn; phép tính do script chạy.
- **Chốt từ đầu.** Kiểu dữ liệu, kiến trúc, stack, phiên bản và rủi ro của từng phiên bản được thống nhất trước khi thiết kế chi tiết.
- **Hai chế độ:** thiết kế mới từ BA, hoặc nâng cấp từ bộ thiết kế cũ (agent đọc bản cũ trước).
- **Plugin stack-agnostic.** Kiến thức riêng từng stack lấy từ `~/knowledge/stacks/<stack>/`.

## 8 tiêu chí chất lượng

Mọi file đầu ra phải qua 8 tiêu chí này; chúng là nội dung checklist của Reviewer ở mọi gate.

| ID | Tiêu chí | Kiểm bằng cách nào |
| --- | --- | --- |
| Q1 | Đúng FR / NFR / ràng buộc | Mọi thành phần truy về ít nhất một FR, NFR hoặc ràng buộc; script truy vết báo thiếu |
| Q2 | Tối ưu theo từng tầng: frontend, backend, lưu trữ, hạ tầng, quy trình | Mỗi phần có mục "Tối ưu" với chỉ số mục tiêu bằng số |
| Q3 | Sẵn sàng mở rộng, nâng cấp, bảo trì | Mỗi thành phần có đường scale, đường nâng cấp và gánh nặng bảo trì ước tính |
| Q4 | Số liệu thật | Mọi con số có công thức, giả định (link `assumptions.md`) và nguồn chính thức; script tính lại khớp |
| Q5 | Kiểu dữ liệu, kiến trúc, stack, phiên bản rõ từ đầu | Ma trận phiên bản và tính năng đã được bạn duyệt ở gate stack |
| Q6 | Quản lý rủi ro | Mỗi quyết định sinh rủi ro vào sổ rủi ro; rủi ro điểm cao cần bạn chấp nhận rõ ràng |
| Q7 | Frontend sâu về kiến trúc, tối ưu cho thiết bị thật; không đụng GUI | Có ma trận thiết bị và ngân sách hiệu năng; không có quyết định visual nào |
| Q8 | Phù hợp với dự án | Độ sâu tài liệu khớp hồ sơ dự án đã duyệt; không có phần thừa so với hồ sơ |

## Hồ sơ dự án và mức độ áp dụng

Bước đầu tiên của mọi dự án là lập hồ sơ dự án và chọn mức áp dụng; bạn duyệt mức này trước khi làm bất cứ thứ gì khác (tiêu chí Q8).

Hồ sơ ghi: quy mô người dùng và dữ liệu dự kiến, mức độ quan trọng (mất dịch vụ thì thiệt hại gì), số người trong team, ngân sách, thời hạn, yêu cầu tuân thủ. Từ hồ sơ, agent đề xuất một mức:

| Mức | Ví dụ dự án | Phần bắt buộc | Hội đồng | Mốc tính số liệu |
| --- | --- | --- | --- | --- |
| S | Công cụ nội bộ, MVP | context (`00-context`), system tối thiểu (`architecture-style.md`, `containers.md`), stack, capacity rút gọn, luồng chính, backend, data, rủi ro rút gọn (chỉ rủi ro ≥ 8 điểm), `implementation-plan.md` | 3 phiếu, chỉ cho stack và kiểu kiến trúc | Lúc ra mắt, 1 năm |
| M | Sản phẩm thật, một team | Như S + system đầy đủ, frontend đầy đủ, security, infra, process, rủi ro đầy đủ, `scaling-stages.md`, `upgrade-roadmap.md` | 3 phiếu | Ra mắt, 1 năm, 3 năm |
| L | Nhiều team, nhiều client | Toàn bộ 13 phần, chi tiết từng service | 3 phiếu, 5 cho quyết định khó đảo ngược | Ra mắt, 1, 3, 5 năm |
| XL | Phân tán, tải lớn, yêu cầu tuân thủ cao | Toàn bộ + spike bắt buộc cho stack, DR chi tiết | 5 phiếu | Ra mắt, 1, 3, 5 năm + đỉnh tải |

Kết quả lưu ở `architecture/00-context/project-profile.md`: mức đã chốt và danh sách phần nào áp dụng, phần nào bỏ. Script kiểm tra và Reviewer đọc file này để biết phần nào được phép vắng.

## Cấu trúc đầu ra architecture/

Đầu ra gồm 13 phần đánh số `00` đến `12`; mỗi phần link hai chiều với các phần liên quan qua ID (`FR`, `NFR`, `TC`, `FL`, `SCR`, `SVC`, `API`, `EVT`, `TBL`, `BKT`, `R`).

```
architecture/
├── README.md                      # mục lục, phiên bản, mức áp dụng
├── CHANGELOG.md                   # chế độ nâng cấp: khác gì bản trước
│
├── 00-context/
│   ├── project-profile.md         # mức S/M/L/XL, phần nào áp dụng
│   ├── requirements-trace.md      # FR/NFR → FL → SVC → TBL/BKT
│   ├── quality-attributes.md      # NFR có số: tải, latency, uptime, RPO/RTO
│   ├── constraints.md             # ngân sách, team, hạ tầng, pháp lý, thời hạn
│   ├── assumptions.md             # mọi giả định dùng để tính số (DAU, tăng trưởng…);
│   │                              #   sinh từ capacity/assumptions.yaml bằng script, không sửa tay
│   └── glossary.md
│
├── 01-system/
│   ├── system-context.md          # C4 mức 1
│   ├── containers.md              # C4 mức 2
│   ├── architecture-style.md      # kiểu kiến trúc + giai đoạn scale
│   └── integrations.md            # hệ thống ngoài: cách gọi, lỗi, fallback
│
├── 02-tech-stack/
│   ├── README.md                  # lớp → công nghệ → phiên bản → TC đáp ứng
│   ├── selection-criteria.md      # TC-xx truy về FR/NFR/ràng buộc
│   ├── layers/                    # frontend, backend, data, messaging,
│   │                              #   infrastructure, tooling, third-party
│   ├── versions-features.md       # phiên bản, EOL, tính năng dùng, lỗi đã biết
│   ├── compatibility.md           # ma trận tương thích giữa các lớp
│   ├── cost-licensing.md
│   ├── team-readiness.md
│   └── exit-strategy.md           # đường thay thế từng công nghệ
│
├── 03-capacity/
│   ├── workload-model.md          # người dùng, req/s đỉnh, tỉ lệ đọc/ghi
│   ├── data-sizing.md             # byte/dòng, số dòng, dung lượng theo mốc
│   ├── storage-sizing.md          # object store: số file, dung lượng, băng thông
│   ├── compute-sizing.md          # năng lực mỗi instance, số instance cần
│   └── cost-model.md              # chi phí tháng theo từng mốc
│
├── 04-flows/
│   ├── flow-index.md
│   └── FL-xxx-<tên>.md            # sơ đồ tuần tự, lỗi, dữ liệu chạm tới
│
├── 05-frontend/
│   ├── overview.md                # client nào, chiến lược render
│   ├── device-matrix.md           # thiết bị, trình duyệt, OS, mạng hỗ trợ
│   ├── performance-budget.md      # bundle KB, LCP/INP/CLS, bộ nhớ
│   └── <app>/                     # web/, admin/, mobile/
│       ├── architecture.md        # lớp, ranh giới module, luồng dữ liệu
│       ├── routing-navigation.md  # SCR (của designer) ↔ route ↔ API
│       ├── state-data.md
│       ├── networking-offline.md
│       ├── auth-session.md
│       ├── build-delivery.md      # code splitting, CDN, cache asset
│       └── folder-structure.md
│
├── 06-backend/
│   ├── overview.md                # bản đồ service, ranh giới, mức A/B
│   ├── communication.md           # sync/async, gateway, timeout, retry
│   ├── cross-cutting.md           # authN/Z, error model, logging, idempotency
│   ├── repo-structure.md
│   ├── contracts/
│   └── services/<service>/        # modules/ nếu là modular monolith
│       ├── responsibility.md
│       ├── api.md
│       ├── events.md
│       ├── domain-model.md
│       ├── data.md
│       ├── dependencies.md
│       ├── scaling.md             # đơn vị scale, giới hạn, số instance
│       └── folder-structure.md
│
├── 07-data/
│   ├── overview.md
│   ├── databases/<db>/
│   │   ├── erd.md
│   │   ├── tables.md              # kiểu dữ liệu + số byte từng cột
│   │   ├── access-patterns.md
│   │   ├── indexing.md
│   │   ├── partitioning-retention.md
│   │   └── migration-strategy.md
│   ├── object-storage.md
│   ├── cache.md
│   ├── messaging.md
│   ├── consistency.md
│   └── backup-recovery.md         # RPO/RTO, lịch backup, diễn tập khôi phục
│
├── 08-security/
│   ├── authz-matrix.md
│   ├── threat-model.md
│   └── secrets-compliance.md
│
├── 09-infrastructure/
│   ├── topology.md
│   ├── environments.md
│   ├── scaling-ha.md              # autoscale, HA, DR có số
│   ├── observability.md           # SLO, metric, cảnh báo
│   └── ci-cd.md
│
├── 10-process/
│   ├── delivery.md                # nhánh, release, rollback
│   ├── data-change.md             # migration, backfill
│   ├── maintenance.md             # lịch nâng cấp phiên bản, vá lỗi
│   └── operations.md              # xử lý sự cố, diễn tập backup
│
├── 11-risks/
│   └── risk-register.md
│
└── 12-roadmap/
    ├── scaling-stages.md          # ngưỡng số để lên giai đoạn sau
    ├── upgrade-roadmap.md         # nâng cấp theo ngày EOL
    └── implementation-plan.md     # gói docs giao cho từng agent dev
```

## Quy tắc số liệu và sizing

Mọi con số trong đầu ra phải tính lại được: nó có giá trị, đơn vị, công thức, giả định đầu vào và nguồn; phép tính do script chạy, không để model tính nhẩm (tiêu chí Q4).

**Năm thành phần bắt buộc của một con số**

| Thành phần | Ví dụ |
| --- | --- |
| Giá trị + đơn vị | 292 MB/năm |
| Công thức | số dòng/năm × byte/dòng |
| Giả định | 10.000 đơn/ngày (link `assumptions.md`) |
| Hằng số có nguồn | `bigint` = 8 byte (link tài liệu chính thức của DB và phiên bản đã chọn) |
| Mốc thời gian | ra mắt, 1, 3, 5 năm theo mức áp dụng |

Các từ như "nhanh", "lớn", "đủ dùng", "scale tốt" không có số đi kèm là lỗi chặn khi review.

**Kiểu dữ liệu chọn theo số, không theo thói quen.** Mỗi cột trong `tables.md` ghi kiểu, số byte và lý do. Quy tắc: chọn kiểu nhỏ nhất vẫn đủ cho mốc xa nhất cộng biên an toàn. Ví dụ với PostgreSQL: `integer` (4 byte) có giá trị lớn nhất 2.147.483.647. Bảng thêm 10.000 dòng/ngày thì dùng được hàng trăm năm, nên giữ `integer`. Bảng thêm 1 triệu dòng/ngày (365 triệu/năm) thì hết sau khoảng 5,9 năm, nên phải dùng `bigint` (8 byte) ngay từ đầu.

**Dung lượng dữ liệu** = (phần đầu dòng + con trỏ dòng + tổng byte các cột + padding căn lề) × số dòng, cộng index. Các hằng số phần đầu dòng và căn lề lấy từ tài liệu chính thức của DB đã chọn. Ví dụ: 10.000 đơn/ngày là 3,65 triệu dòng/năm; với khoảng 80 byte/dòng thì cỡ 292 MB/năm, chưa tính index.

**Tải tính toán** đi từ giả định người dùng:

```
req/s đỉnh = (DAU × request/người/ngày) / 86 400 × hệ số đỉnh
```

Hệ số đỉnh và biên an toàn cũng là giả định, nằm trong `assumptions.md` và được bạn duyệt.

**Object storage** = số file/ngày × kích thước trung bình × thời gian lưu; băng thông ra = lượt xem × kích thước. **Chi phí** lấy từ trang giá chính thức, ghi ngày tra cứu.

**Cách làm:** Designer ghi giả định và tham số vào `capacity/*.yaml` trong workspace; script `calc_capacity.py` sinh bảng số vào bản nháp; Reviewer chạy lại script và đối chiếu. Mỗi khi kiểu dữ liệu hay giả định đổi, toàn bộ số được tính lại. `capacity/assumptions.yaml` là nguồn duy nhất của giả định; `00-context/assumptions.md` sinh từ nó, và `check_numbers.py` báo lỗi nếu hai file lệch.

## Phiên bản và ma trận tính năng

Mỗi công nghệ trong stack được chốt đến phiên bản cụ thể ở gate stack, kèm những tính năng dự án dựa vào và rủi ro của chính phiên bản đó; sau gate này, đổi phiên bản phải đi qua chế độ nâng cấp và ghi vào `CHANGELOG.md` (tiêu chí Q5).

**Tiêu chí lựa chọn đi trước ứng viên.** Agent rút tiêu chí `TC-xx` từ FR, NFR và ràng buộc; bạn duyệt tiêu chí và trọng số trước khi bất kỳ ứng viên nào được nêu tên. Tiêu chí không có nguồn thì không được dùng. Tiêu chí loại trừ gạt ứng viên trước; tiêu chí có trọng số chỉ xếp hạng phần còn lại.

**Mỗi dòng trong `versions-features.md`**

| Cột | Nội dung |
| --- | --- |
| Công nghệ | Tên + vai trò (ví dụ: database quan hệ cho `order-db`) |
| Phiên bản chốt | major.minor, chính sách nhận bản vá |
| Ngày phát hành, ngày hết hỗ trợ | Link trang vòng đời chính thức |
| Tính năng dự án dựa vào | Mỗi tính năng ghi phiên bản tối thiểu cần có |
| Giới hạn và lỗi đã biết | Của đúng phiên bản này, có link issue hoặc release note |
| Thay đổi phá vỡ ở bản lớn kế tiếp | Ảnh hưởng gì khi nâng cấp sau này |
| Tương thích | Phiên bản tối thiểu của driver, SDK, lớp khác |
| Rủi ro | Link sang `R-xx` trong sổ rủi ro |

**Ai thu thập dữ kiện:** agent Researcher, bắt buộc kèm link nguồn chính thức. Dữ kiện không có nguồn là lỗi chặn; hội đồng chỉ chấm trên dữ kiện đã có nguồn.

**Kiểm tra chéo toàn stack** sau khi chốt từng lớp: tương thích giữa các phiên bản, tổng chi phí so với ngân sách, kỹ năng team. Từng lớp phù hợp riêng lẻ chưa đủ; ghép lại cũng phải khớp.

## Quản lý rủi ro

Rủi ro được ghi ngay khi nó xuất hiện, không đợi đến cuối: mỗi brief quyết định, mỗi dòng phiên bản, mỗi bảng sizing và mỗi khoảng trống kỹ năng đều phải khai rủi ro vào sổ (tiêu chí Q6).

**Mỗi dòng trong `11-risks/risk-register.md`**

| Cột | Nội dung |
| --- | --- |
| ID | `R-xx` |
| Mô tả | Điều gì có thể xảy ra, hậu quả cụ thể |
| Nhóm | Công nghệ, phiên bản, capacity, vendor, bảo mật, dữ liệu, team, tiến độ, vận hành |
| Khả năng × Tác động | Mỗi thang 1–5, điểm = tích, tối đa 25 |
| Thành phần liên quan | Link `SVC`, `TBL`, `BKT`, công nghệ trong stack |
| Dấu hiệu sớm | Chỉ số có ngưỡng bằng số, ví dụ CPU DB > 70% trong 15 phút |
| Giảm thiểu | Làm gì trước để giảm khả năng hoặc tác động |
| Phương án dự phòng | Làm gì khi rủi ro đã xảy ra |
| Trạng thái | Đang theo dõi, đang giảm thiểu, đã chấp nhận, đã đóng |

**Ngưỡng xử lý**

| Điểm | Xử lý |
| --- | --- |
| 15–25 | Bắt buộc có giảm thiểu; nếu vẫn giữ, bạn phải chấp nhận rõ ràng (ghi trong workspace) |
| 8–14 | Bắt buộc có giảm thiểu và dấu hiệu sớm |
| 1–7 | Theo dõi, có dấu hiệu sớm |

Ở mỗi gate, Reviewer soát lại sổ: rủi ro mới từ giai đoạn vừa làm đã được khai chưa, điểm có cần chấm lại không. Phát hành snapshot chỉ khi mọi rủi ro từ 15 điểm trở lên đã được giảm thiểu hoặc được bạn chấp nhận.

Sổ rủi ro có ở mọi mức áp dụng và nằm trong `architecture/` (workspace không được commit). Mức S dùng bản rút gọn: chỉ ghi rủi ro từ 8 điểm trở lên.

## Phạm vi kiến trúc frontend

Frontend được thiết kế sâu ở phần kỹ thuật và tối ưu cho thiết bị thật của người dùng; mọi thứ thuộc về giao diện nhìn thấy được để cho designer (tiêu chí Q7).

| Thuộc kiến trúc (làm) | Thuộc designer (không đụng) |
| --- | --- |
| Chiến lược render từng app (CSR, SSR, SSG, kết hợp) và lý do từ NFR | Màu, font, bố cục, khoảng cách |
| Ma trận thiết bị: OS, trình duyệt, lớp màn hình, RAM máy yếu, điều kiện mạng | Hình dáng component, icon, minh họa |
| Ngân sách hiệu năng: KB JS tải ban đầu, LCP, INP, CLS, bộ nhớ, dung lượng app mobile | Hiệu ứng chuyển động, micro-interaction |
| Lớp và ranh giới module, luồng dữ liệu, quản lý state | Nội dung chữ trên giao diện |
| Lấy dữ liệu, cache, offline và đồng bộ, retry | Thứ tự và cách sắp xếp màn hình |
| Phiên đăng nhập, nơi lưu token, phân quyền màn hình | |
| Build và phân phối: code splitting, CDN, pipeline ảnh theo kích thước thiết bị | |
| Đo thực tế người dùng (RUM), báo lỗi client | |

**Ngân sách hiệu năng phải là số.** Ví dụ dùng ngưỡng "tốt" của Core Web Vitals làm mức sàn (LCP ≤ 2,5 s, INP ≤ 200 ms, CLS ≤ 0,1), rồi siết thêm theo hồ sơ dự án và máy yếu nhất trong ma trận thiết bị.

**Nối với designer qua ID màn hình.** `routing-navigation.md` dùng `SCR-xx` lấy từ tài liệu của designer và chỉ ghi route, dữ liệu cần, API gọi. Khi kiến trúc cần designer làm thêm điều gì (ví dụ trạng thái khi mất mạng), agent ghi câu hỏi vào `questions.md`, không tự quyết phần nhìn.

## Các agent và quyền ghi

Mỗi việc giao cho một agent độc lập, chạy trong context riêng, chỉ được đọc đúng file mình cần và chỉ được ghi vào đúng vùng của mình; không agent nào được ghi trạng thái "Đã duyệt".

| Agent | Việc | Được ghi vào | Model / effort |
| --- | --- | --- | --- |
| Orchestrator (phiên chính) | Chạy workflow, dò model, gọi agent, cập nhật trạng thái; không tự thiết kế | `state.md`, `models.md` | Model của phiên bạn mở / medium |
| Planner | Đọc input, lập hồ sơ dự án, chia task, viết checklist, gom câu hỏi | `plan/`, `questions.md`, nháp `project-profile` | Theo `models.md` / high |
| Researcher | Longlist công nghệ, dữ kiện phiên bản, EOL, giấy phép, giá, giới hạn, có link nguồn | `stack/` | Model có tìm web trong `models.md` / medium |
| Designer | Viết brief phương án; sau khi bạn chốt thì viết bản nháp docs và tham số capacity | `decisions/*/brief.md`, `drafts/`, `capacity/` | Theo `models.md` / high |
| Hội đồng (3 hoặc 5) | Chấm và bỏ phiếu độc lập | `decisions/*/votes/` | Mỗi thành viên một model khác nhau trong `models.md` |
| Reviewer | Soát bản nháp theo 8 tiêu chí và checklist, chạy lại script; không sửa | `reviews/` | Khác model với Designer / high |
| Script | Đếm phiếu, tính capacity, kiểm link, truy vết, chuyển bản nháp đã duyệt | `tally.md`, `checks/`, `architecture/` | Không phải agent |

Chỉ script `promote_drafts.py` được ghi vào `architecture/`, và chỉ chạy sau khi bạn duyệt gate. Nhờ vậy đầu ra luôn đúng nghĩa "chỉ nội dung đã chốt".

**Danh mục model tự dò.** Ở G0, Orchestrator kiểm tra model nào gọi được trong môi trường hiện tại: các model của Claude Code, và CLI khác như Antigravity nếu đã cài và chạy được ở chế độ không tương tác. Kết quả ghi vào `.agent-workspace/models.md`: tên, cách gọi, có tìm web không, điểm mạnh, giới hạn. Mỗi lần gọi agent, Orchestrator chọn model từ danh mục này; model gọi lỗi thì bị đánh dấu không dùng được và được thay bằng model khác. Bạn xem danh mục ở gate G0.

Quy tắc gán model:

- Hội đồng: mỗi thành viên một model khác nhau. Không đủ model thì dùng chung model với góc nhìn khác nhau, và `decision.md` ghi rõ độ đa dạng bị giảm.
- Reviewer luôn khác model với Designer của phần đang soát.
- Ưu tiên Sonnet cho phiên chính và các bước dài để giữ giới hạn gói Pro.

**Ngữ cảnh độc lập.** Mỗi agent chạy trong ngữ cảnh riêng, không mang lịch sử trò chuyện hay suy luận của agent khác, để phản biện thật sự độc lập.

- Mỗi agent chỉ nhận đúng danh sách file Orchestrator truyền cho task đó.
- Thành viên hội đồng chỉ đọc `brief.md` và phần context được trích; vòng 1 không thấy phiếu nào khác, vòng 2 chỉ thấy bản tóm tắt ẩn danh.
- Designer không thấy phiếu từng người, chỉ thấy quyết định cuối của bạn.
- Reviewer chỉ đọc bản nháp, template, checklist và nguồn gốc (BA, `assumptions`); không đọc brief hay lý luận của Designer, để soát như người ngoài.
- Agent trao đổi với nhau chỉ qua file trong workspace, không truyền tin trực tiếp.

## Hội đồng bỏ phiếu quá bán

Trước khi một quyết định lớn đến tay bạn, một hội đồng gồm các model khác nhau, mỗi thành viên một góc nhìn, bỏ phiếu độc lập; phương án nào được hơn 50% số phiếu mới thành đề xuất, còn bạn vẫn là người quyết cuối cùng.

**Thành phần, mỗi góc nhìn gắn với tiêu chí chất lượng**

| Góc nhìn | Hỏi gì | Tiêu chí | Model | Khi nào có |
| --- | --- | --- | --- | --- |
| Phù hợp và vừa sức | Đúng hồ sơ dự án không, team và thời hạn làm nổi không | Q8, Q1 | Gán từ models.md | Luôn có |
| Chi phí và vận hành | Tốn bao nhiêu mỗi tháng, ai vận hành, lỗi thì sao | Q2 | Gán từ models.md | Luôn có |
| Số liệu và NFR | Có đạt ngưỡng trong `quality-attributes` theo số đã tính không | Q4, Q1 | Gán từ models.md | Luôn có |
| Tiến hóa | Mở rộng, nâng cấp phiên bản, bảo trì có dễ không | Q3, Q5 | Gán từ models.md | Hội đồng 5 |
| Rủi ro và dữ liệu | Toàn vẹn, mất mát, bảo mật, khóa vendor | Q6 | Gán từ models.md | Hội đồng 5 |

**Quy tắc chấm "phù hợp nhất"**

- Brief do Designer viết trình bày các phương án trung lập, không kèm khuyến nghị.
- Mỗi thành viên chấm từng phương án theo các `TC` có trọng số và chỉ thấy brief, không thấy phiếu của người khác.
- Mỗi lý do phải trích một `TC`, `NFR`, ràng buộc, con số trong `03-capacity` hoặc `R-xx`. Lý do kiểu "chuẩn ngành", "đang phổ biến" không được tính.
- Phương án vượt xa nhu cầu mà tốn thêm chi phí hoặc độ phức tạp bị trừ điểm.
- Luôn có lựa chọn "không phương án nào phù hợp".

**Đếm phiếu** (script `tally_votes.py`): quá bán nghĩa là 2/3 hoặc 3/5 phiếu.

1. Vòng 1 bỏ phiếu kín. Có phương án quá bán thì thành đề xuất.
2. Không quá bán thì sang vòng 2: mỗi thành viên đọc bản tóm tắt lý do vòng 1 đã ẩn danh, rồi bỏ phiếu lại.
3. Vẫn không quá bán thì trình bạn hai phương án dẫn đầu, ghi rõ "chưa đạt đồng thuận".
4. "Không phương án nào phù hợp" thắng thì Designer làm lại brief.

`decision.md` trình cho bạn: phương án đề xuất, tỉ lệ phiếu, ý kiến thiểu số (luôn hiển thị), rủi ro mới sinh ra.

**Việc nào đưa ra hội đồng:** kiểu kiến trúc, stack từng lớp, phiên bản chốt, ranh giới service, loại database, chiến lược nhất quán dữ liệu, kiểu dữ liệu của các bảng tăng nhanh nhất, đặc biệt khóa chính và khóa ngoại. Chi tiết nhỏ hơn do Designer viết thẳng, Reviewer soát. Điều này giữ lượt dùng trong giới hạn gói Pro.

**Quyết định khó đảo ngược** (hội đồng 5 phiếu ở mức L): đổi sau khi có dữ liệu production thì phải migrate dữ liệu hoặc tách/gộp service. Danh sách mặc định: kiểu kiến trúc, loại database, ranh giới service, chiến lược nhất quán dữ liệu, kiểu dữ liệu của các bảng tăng nhanh nhất, đặc biệt khóa chính và khóa ngoại, đặc biệt khóa chính và khóa ngoại. Planner được đề xuất thêm ở G0; bạn duyệt.

## Các giai đoạn và gate

Quy trình có 11 gate theo thứ tự cố định; mỗi gate chỉ qua khi đủ điều kiện và bạn duyệt.

| Gate | Giai đoạn | Bạn duyệt gì |
| --- | --- | --- |
| G0 | Khởi tạo và hồ sơ dự án | Mức áp dụng, các phần áp dụng và danh mục model |
| G1 | Context | FR, NFR có số, ràng buộc, giả định |
| G2 | Tiêu chí lựa chọn TC | Tiêu chí và trọng số, trước mọi ứng viên |
| G3 | Kiểu kiến trúc | Kiểu kiến trúc và giai đoạn scale (hội đồng) |
| G4 | Stack và phiên bản | Từng lớp, ma trận phiên bản, kiểm tra chéo |
| G5 | Capacity sơ bộ | Tải, dung lượng, chi phí theo từng mốc |
| G6 | Luồng chính | Luồng, trước khi thiết kế chi tiết |
| G7 | Thiết kế chi tiết | Từng service, từng database, từng app frontend (có thể quay lại G5 để tính lại capacity theo kiểu dữ liệu thật) |
| G8 | Bảo mật, hạ tầng, quy trình | Từng phần |
| G9 | Rủi ro và roadmap | Sổ rủi ro; rủi ro từ 15 điểm đã được xử lý |
| G10 | Kiểm tra chéo và phát hành | Tính lại toàn bộ số, mọi script sạch, phát hành vN |

G5 tính capacity sơ bộ, G7 tính lại theo kiểu dữ liệu thật, G10 tính lại lần cuối trước khi phát hành.

**Vòng làm việc trong mỗi giai đoạn**

1. Planner lập task và checklist "xong khi".
2. Gom câu hỏi, bạn trả lời.
3. Quyết định lớn: Designer viết brief, hội đồng bỏ phiếu, bạn quyết.
4. Designer viết bản nháp theo template, script tính số.
5. Reviewer soát theo 8 tiêu chí và chạy lại script.
6. Gate: mọi task đã đóng, không còn quyết định chờ, không còn lỗi chặn, script sạch, bạn duyệt; script chuyển bản nháp sang `architecture/`.

Ở chế độ nâng cấp, G0 đọc `previous-design/` trước, và mỗi gate chỉ làm lại phần có thay đổi.

## Mở session mới và tiếp tục

Mở session mới vẫn dùng bình thường, không cần làm gì thêm: mọi trạng thái nằm trong file, nên agent tự đọc và làm tiếp đúng chỗ đã dừng.

- `state.md` là điểm vào duy nhất: giai đoạn hiện tại, gate đã qua, task đang mở, câu hỏi đang chờ, việc tiếp theo.
- `init_workspace.py` tạo file hướng dẫn dự án mà CLI tự đọc khi mở session (ví dụ `CLAUDE.md` với Claude Code), ghi một quy tắc: đọc `.agent-workspace/state.md` trước khi làm gì khác. File này cũng nằm trong `.gitignore`, vì là thứ của agent.
- Mỗi task và mỗi gate kết thúc bằng việc cập nhật `state.md`. Session có đứt giữa chừng thì chỉ mất phần đang làm dở của task hiện tại.
- Không dựa vào lịch sử chat: quyết định bạn nói trong chat được Orchestrator ghi ngay vào `decision.md` rồi mới làm tiếp.
- Workspace chỉ ở local, nên tiếp tục phải trên cùng máy, hoặc bạn tự chép `.agent-workspace/` sang máy khác.

Nên mỗi session làm trọn một giai đoạn để ngữ cảnh phiên chính gọn.

## Cấu trúc .agent-workspace/

`.agent-workspace/` nằm cạnh `architecture/` trong repo thiết kế, chỉ ở máy local và có trong `.gitignore`; mọi thứ agent làm dở, mọi phương án và phiếu bầu nằm ở đây.

```
.agent-workspace/
├── state.md                       # ĐIỂM VÀO: giai đoạn, gate đã qua, task mở,
│                                  #   câu hỏi chờ, việc tiếp theo
├── models.md                      # model gọi được, cách gọi, tìm web, giới hạn
│
├── inputs/                        # chỉ đọc
│   ├── ba/                        # tài liệu BA bạn đưa trong prompt, Orchestrator lưu lại
│   ├── ui-design/                 # danh sách SCR-xx từ designer (nếu có)
│   └── previous-design/           # chế độ nâng cấp: bản architecture/ cũ
│
├── plan/
│   ├── plan.md                    # giai đoạn, task, phụ thuộc
│   └── tasks/T-xxx-<tên>.md       # mô tả, checklist "xong khi", trạng thái
│
├── questions.md                   # câu hỏi chờ bạn (mở / đã trả lời)
│
├── stack/
│   ├── criteria-draft.md          # nháp TC trước khi bạn duyệt
│   ├── layers/<lớp>/
│   │   ├── longlist.md            # ứng viên + dữ kiện có nguồn
│   │   ├── knockout.md            # ai bị loại, vì TC nào
│   │   ├── shortlist.md
│   │   ├── scoring.md             # bảng chấm theo trọng số
│   │   └── spikes/S-xx-<tên>.md   # thử nghiệm nhỏ trong container (tùy chọn)
│   └── cross-check.md             # kiểm tra chéo toàn stack
│
├── capacity/
│   ├── assumptions.yaml           # DAU, tăng trưởng, hệ số đỉnh, biên an toàn
│   ├── tables.yaml                # bảng, cột, kiểu, số dòng/ngày
│   ├── storage.yaml               # file/ngày, kích thước, thời gian lưu
│   ├── compute.yaml               # năng lực mỗi instance
│   └── pricing.yaml               # đơn giá + link + ngày tra cứu
│
├── decisions/
│   ├── decision-log.md            # ID, câu hỏi, trạng thái, ngày
│   └── D-xxx-<tên>/
│       ├── brief.md               # câu hỏi, bối cảnh, phương án trung lập
│       ├── votes/
│       │   ├── r1-<góc-nhìn>-<model>.md
│       │   ├── r1-summary.md      # tóm tắt ẩn danh (khi cần vòng 2)
│       │   └── r2-<góc-nhìn>-<model>.md
│       ├── tally.md               # do script tạo
│       └── decision.md            # đề xuất, tỉ lệ, thiểu số, rủi ro,
│                                  #   quyết định của bạn, trạng thái
│
├── risks/
│   └── acceptance.md              # rủi ro ≥ 15 điểm bạn đã chấp nhận
│
├── drafts/                        # bản nháp, cùng cấu trúc architecture/
│
├── reviews/R-xxx-<phần>.md        # lỗi chặn / góp ý, link file và dòng
│
├── checks/
│   ├── links-<ngày>.md
│   ├── trace-<ngày>.md
│   ├── numbers-<ngày>.md
│   └── workspace-<ngày>.md
│
└── archive/vN/                    # chụp state, plan, stack, capacity,
                                   #   decisions, reviews khi phát hành vN
```

Thư mục `archive/` giữ phần "vì sao" cho chế độ nâng cấp sau này, trong khi đầu ra vẫn sạch.

## Các script kiểm tra

Việc gì máy kiểm được thì giao cho script Python chạy qua uv, không để agent tự đọc rồi tự khen; Reviewer chạy lại các script này trước khi viết báo cáo.

| Script | Làm gì | Chặn gate khi |
| --- | --- | --- |
| `init_workspace.py` | Tạo `.agent-workspace/`, thêm vào `.gitignore`, chép template, tạo file hướng dẫn CLI | — |
| `detect_models.py` | Dò model và CLI gọi được, ghi `models.md` | — |
| `calc_capacity.py` | Đọc `capacity/*.yaml`, sinh bảng số vào `drafts/03-capacity/` và `tables.md` | YAML thiếu nguồn cho hằng số hoặc giá |
| `tally_votes.py` | Đếm phiếu từng vòng, ghi `tally.md`, xác định quá bán | Thiếu phiếu, phiếu sai định dạng |
| `check_links.py` | Link gãy, ID trùng, ID mồ côi, thiếu liên kết ngược | Có lỗi bất kỳ |
| `check_trace.py` | FR không có luồng; API frontend gọi mà backend không có; bảng, bucket, event nhắc trong luồng mà phần data không có | Có lỗi bất kỳ |
| `check_numbers.py` | Con số thiếu công thức, giả định hoặc nguồn; từ mơ hồ không kèm số | Có lỗi bất kỳ |
| `check_profile.py` | Phần bắt buộc theo `project-profile.md` còn thiếu; phần đã bỏ lại xuất hiện | Có lỗi bất kỳ |
| Kiểm mục bắt buộc theo template (gộp vào `check_profile.py` hoặc script riêng, quyết ở Giai đoạn 3) | Mỗi file đầu ra có đủ các mục mà template của nó đánh dấu bắt buộc, ví dụ "Tối ưu" (Q2), scale / nâng cấp / bảo trì (Q3) | Thiếu mục bắt buộc |
| Kiểm ma trận phiên bản (`check_versions.py` hoặc gộp, quyết ở Giai đoạn 3) | Mọi công nghệ trong `02-tech-stack/README.md` có dòng trong `versions-features.md` với phiên bản chốt, ngày EOL và link nguồn (Q5) | Thiếu dòng, thiếu phiên bản, EOL hoặc nguồn |
| `check_workspace.py` | Task chưa đóng, quyết định chưa có quyết định của bạn, rủi ro ≥ 15 chưa xử lý | Có lỗi bất kỳ |
| `promote_drafts.py` | Chép bản nháp đã qua gate sang `architecture/` | Chỉ chạy khi gate đã được bạn duyệt |
| `archive_release.py` | Chụp workspace vào `archive/vN/`, cập nhật `CHANGELOG.md` | — |

## Vị trí trong repo Thanh-Tan-

Workflow, agent, hội đồng và script nằm ở core của family Design để các plugin Design khác (UI sau này) dùng lại; plugin `design-architecture` chỉ chứa template, checklist và phần "dùng với core".

```
families/design-system/
├── README.md
├── PLAN.md                        # tài liệu này
├── core/
│   ├── USAGE.md                   # template prompt chính của family
│   ├── workflow/
│   │   ├── stages.md              # giai đoạn, gate, điều kiện qua gate
│   │   ├── permissions.md         # agent nào được ghi vào đâu
│   │   └── quality-criteria.md    # 8 tiêu chí Q1–Q8
│   ├── agents/
│   │   ├── orchestrator.md
│   │   ├── planner.md
│   │   ├── researcher.md
│   │   ├── designer.md
│   │   ├── reviewer.md
│   │   └── council/               # một file mỗi góc nhìn
│   ├── templates/workspace/       # task, brief, phiếu bầu, decision, review
│   └── scripts/                   # các script ở phần trên, môi trường uv
│
└── design-architecture/
    ├── README.md                  # phần "dùng với core": dữ liệu cần thêm, ví dụ done-when
    ├── templates/                 # form cố định cho từng file trong architecture/
    ├── checklists/                # "xong khi" cho từng phần 00–12
    └── profiles.md                # bảng mức S/M/L/XL và phần áp dụng
```

Kiến thức riêng của từng stack (cấu trúc thư mục NestJS, hằng số byte của từng DB) không nằm trong plugin mà ở `~/knowledge/stacks/<stack>/`, được chép vào dự án lúc khởi tạo.

## Prompt mẫu

Bốn prompt dưới đây là nội dung chính của `core/USAGE.md`. Tài liệu BA đưa thẳng trong prompt; Orchestrator lưu vào `inputs/ba/` để các agent sau đọc từ một chỗ cố định. Với Antigravity CLI, prompt giữ nguyên, chỉ đổi dòng "Chạy với".

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
(Tuỳ chọn) Tôi đã trả lời trong questions.md các mục: Q-03, Q-05.
```

**4. Duyệt gate và quyết định**

```text
Chạy với: Claude Code · model Sonnet · effort medium

Gate G4: duyệt.            (hoặc: chưa duyệt — lý do: …)
D-007: chọn phương án B. Ghi chú: …
R-04: chấp nhận rủi ro.
Q-06: <câu trả lời>
```

Mẹo dùng hiệu quả:

- Mỗi session làm trọn một giai đoạn, kết thúc ở gate.
- Trả lời theo ID (`G`, `D`, `R`, `Q`) để Orchestrator ghi đúng chỗ.
- Tài liệu BA càng có số (người dùng, tăng trưởng, ngưỡng hiệu năng) thì G1 càng ít câu hỏi.

## Thứ tự dựng plugin

Dựng từ khung và cơ chế kiểm soát trước, template nội dung sau, để mỗi bước dựng xong là dùng thử được ngay.

1. Khung `families/design-system/` và `init_workspace.py`.
2. Workflow: `stages.md`, `permissions.md`, `quality-criteria.md`, template task có checklist.
3. Agent Planner, Designer, Reviewer cùng `check_links.py` và `check_profile.py`.
4. Agent Researcher và template vùng `stack/`.
5. Capacity: schema các file YAML, `calc_capacity.py`, `check_numbers.py`.
6. Hội đồng: các file góc nhìn, template phiếu bầu, `tally_votes.py`.
7. Template và checklist đầu ra, làm nhóm cốt lõi trước: context, tech-stack, capacity, flow, service, database; các phần còn lại sau.
8. `check_trace.py`, `check_workspace.py`, `promote_drafts.py`, `archive_release.py`.
9. Chạy thử toàn bộ trên một dự án thật, cùng đợt chạy thử app full-stack đã lên kế hoạch.

## Các điểm đã chốt

- [x] Bảng mức S/M/L/XL: giữ như đề xuất.
- [x] File hướng dẫn cho CLI (ví dụ `CLAUDE.md`) do `init_workspace.py` tạo và đưa vào `.gitignore`.
- [x] Model: agent tự dò, ghi `models.md` và gán khi gọi.
- [x] Tài liệu BA: đưa trong prompt, Orchestrator lưu vào `inputs/ba/`.
