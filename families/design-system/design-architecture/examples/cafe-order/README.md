# Bộ nháp mẫu: CafeOrder

Dữ liệu giả để chạy thử template và script của design-architecture (Giai đoạn 4). Không dùng cho dự án thật; mọi link example.com và con số là giả.

- `drafts/`: bản nháp theo template, mức M, chỉ có các phần trong phạm vi Giai đoạn 4 (`00-context`, `02-tech-stack`, `03-capacity`, `04-flows`, `06-backend/services/order-service`, `07-data/databases/order-db`) cộng hai file tối thiểu của `01-system` viết tay (chưa có template).
- `capacity/`: đầu vào của `calc_capacity.py`; `drafts/03-capacity/`, `drafts/00-context/assumptions.md` và các khối calc trong `tables.md` do script sinh.
- `decisions/decision-log.md`: nơi `D-xx` được định nghĩa.
- Chạy: `check_profile.py --gate G6`, `check_trace.py --gate G7`, `check_links.py`, `check_numbers.py`, `check_versions.py`, `calc_capacity.py`, mỗi lệnh với `--workspace` trỏ tới bản sao của thư mục này (script ghi `checks/`).
