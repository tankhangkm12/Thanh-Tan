# Xong khi: 06-backend (services/{service})

Gate: G7. Trọng tâm: Q1, Q2, Q3, Q6, Q8. Checklist này phủ thư mục `06-backend/services/<service>/`; các file chung của 06-backend (`overview`, `communication`, `cross-cutting`, `repo-structure`, `contracts/`) chưa có template ở giai đoạn này.

## Mỗi service (thư mục `services/<service>/`)

- [ ] Có đủ 8 file: `responsibility.md`, `api.md`, `events.md`, `domain-model.md`, `data.md`, `dependencies.md`, `scaling.md`, `folder-structure.md` (`check_profile.py` báo `instance-file-missing`).
- [ ] Ranh giới service đã qua hội đồng (`D-xxx` ghi ở "Ranh giới") và người dùng quyết.

## responsibility.md

- [ ] `SVC-…` định nghĩa ở heading, chỉ ở file này; khớp `id` trong `capacity/compute.yaml`.
- [ ] Có dòng "Đơn vị triển khai" là `service riêng` hoặc `module trong monolith`; không có thư mục `modules/`.
- [ ] "Yêu cầu liên quan" có FR/NFR/C và luồng `FL-xx` thật sự dùng service (Q1); không thành phần "tự thêm".
- [ ] "Được dùng bởi" link mọi file nhắc `SVC-…` (`check_links.py` báo `missing-backlink`).

## api.md

- [ ] Mỗi API có heading `### API-…` (định nghĩa ở đây hoặc `contracts/`), yêu cầu vào, phản hồi, lỗi, idempotency, giới hạn tần suất.
- [ ] Mỗi API truy về ít nhất một FR; mọi `API-xx` frontend nhắc có ở đây (`check_trace.py` báo `api-not-in-backend`).
- [ ] "Tối ưu": mỗi API có chỉ số bằng số, đơn vị, NFR, cách đo (Q2).
- [ ] "Được dùng bởi" link mọi file nhắc API của file này.

## events.md

- [ ] Mỗi event phát hoặc nhận nhắc bằng `EVT-…`, và `EVT-…` có định nghĩa ở `07-data/messaging.md` (`check_trace.py` báo `data-ref-missing`/`id-undefined`).
- [ ] Có cách xử lý trùng lặp, thứ tự và thử lại; service không dùng event thì ghi "không có".

## domain-model.md, data.md, dependencies.md

- [ ] domain-model: mỗi thực thể trỏ `TBL-…`; mỗi quy tắc bất biến có nguồn FR/NFR/C và cách bảo đảm.
- [ ] data: phân biệt dữ liệu sở hữu và dữ liệu truy cập; mọi `TBL-`/`BKT-` nhắc có định nghĩa ở `07-data/`; lượng ghi trỏ giả định `A-xx`.
- [ ] data "Tối ưu": chỉ số bằng số, đơn vị, NFR (Q2).
- [ ] dependencies: mỗi phụ thuộc đồng bộ có thời gian chờ (ms), số lần thử lại và cách xử lý khi hỏng; phụ thuộc bất đồng bộ nêu hậu quả khi kênh chậm hoặc mất.

## scaling.md

- [ ] "Scale": đơn vị scale, giới hạn một instance có nguồn benchmark, điểm nghẽn tiếp theo, ngưỡng lên giai đoạn sau bằng số; số instance chỉ dẫn link `compute-sizing.md`, không chép lại (Q3, Q4).
- [ ] "Nâng cấp": runtime và framework khớp `versions-features.md`, có ngày hết hỗ trợ và đường nâng cấp (Q3).
- [ ] "Bảo trì": mỗi việc định kỳ có tần suất và giờ mỗi tháng kèm cơ sở ước tính (Q3).
- [ ] "Tối ưu": chỉ số bằng số, đơn vị, NFR (Q2).

## folder-structure.md

- [ ] Có cây thư mục và quy ước ranh giới module; không mâu thuẫn `repo-structure.md`.

## Chung

- [ ] Mỗi tham số thiết kế (số có đơn vị: thời gian chờ, giới hạn, ngưỡng, giờ bảo trì…) có ô "Cơ sở" với ID (NFR, C, A, D, R, TC) hoặc link; chữ thuần không đạt (`check_numbers.py`).
- [ ] `check_links.py`, `check_numbers.py`, `check_versions.py`, `check_trace.py --gate G7`, `check_profile.py --gate G7 --templates …`, `check_workspace.py` sạch; `calc_capacity.py --check` khớp.
- [ ] Quyết định và khoảng trống mới (ranh giới, phụ thuộc, nghẽn) đã khai vào sổ rủi ro (Q6).
- [ ] Người dùng duyệt từng service.
