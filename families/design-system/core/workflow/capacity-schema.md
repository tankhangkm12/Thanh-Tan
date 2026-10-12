# Schema của `capacity/*.yaml`

Đầu vào của `calc_capacity.py`; Designer ghi (trừ `db-constants/`, của Researcher). Đường dẫn tính từ `.agent-workspace/capacity/`. Script kiểm toàn bộ file này và liệt kê mọi lỗi cùng lúc; có lỗi thì không tính và không ghi gì ngoài `checks/capacity-<ngày>.md`. Ví dụ đầy đủ chạy được: [`scripts/test_data/`](../scripts/test_data/) (dữ liệu mẫu cho test, không dùng cho dự án thật). Nguồn: [PLAN.md](../../PLAN.md), mục "Quy tắc số liệu và sizing".

Quy ước: 1 năm = 365 ngày, 1 tháng = 365/12 ngày, 1 ngày = 86 400 giây; KiB/MiB/GiB là lũy thừa của 1024. Mọi giá trị là số không âm. Mọi chuỗi "nguồn" không được rỗng.

## Mốc

`milestones` trong `assumptions.yaml` chọn trong `launch` (ra mắt, 0 tháng), `1y`, `3y`, `5y`, `peak` (đỉnh tải; không có thời gian, chỉ áp cho tải và tính toán). Phải có `launch` và phủ mức dự án đọc từ `00-context/project-profile.md`: S `launch, 1y`; M thêm `3y`; L thêm `5y`; XL thêm `peak`.

## `assumptions.yaml`

```yaml
version: 1
milestones: [launch, 1y, 3y]
assumptions:
  - id: A-dau                       # A-<tên>, duy nhất
    description: Người dùng hoạt động mỗi ngày
    unit: người dùng
    by_milestone: {launch: 1000, 1y: 10000, 3y: 50000}   # hoặc: value: 120 (cùng giá trị mọi mốc); đúng một trong hai
    source: inputs/ba/prd.md mục 3.1   # nguồn hoặc lý do: BA, người dùng duyệt ở G1, hoặc "ước lượng" kèm người ước lượng
    # tùy chọn: reason: "..." (bắt buộc cho giả định "không có" của database, xem dưới); platform: x86_64 | arm64 (bắt buộc cho MAXALIGN)
workload:                           # bốn khóa bắt buộc, mỗi khóa là ID giả định phủ mọi mốc (kể cả peak nếu có)
  dau: A-dau
  requests_per_user_per_day: A-requests-per-user
  peak_factor: A-peak-factor
  safety_margin: A-safety-margin    # 0.3 = cộng 30% lên tải đỉnh
database_assumptions:               # BẮT BUỘC: một khối cho mỗi database của tables.yaml, đủ bảy khóa, mỗi khóa là ID giả định
  order-db:
    maxalign: A-maxalign              # byte, lũy thừa của 2 từ 1 đến 64; giả định hằng; PHẢI có platform (x86_64 | arm64) và nguồn
    heap_bloat_factor: A-heap-bloat   # >= 1 (1 = không phình, cần reason)
    index_bloat_factor: A-index-bloat # >= 1
    wal_bytes: A-wal-bytes            # byte WAL giữ lại, >= 0 (0 cần reason)
    replicas: A-replicas              # số bản sao, nguyên >= 0 (0 cần reason)
    backups: A-backups                # số backup giữ lại, nguyên >= 0 (0 cần reason)
    toast_column_ratio: A-toast-ratio # 0..1, giả định hằng (0 cần reason); TOAST chưa được mô hình
```

Các giả định của `database_assumptions` (trừ `maxalign` và `toast_column_ratio`, phải là `value` hằng) có thể đổi theo mốc. Giá trị "không có" (0, hoặc 1 cho hệ số phình) phải kèm `reason` vì đó là một khẳng định cần lý do; thiếu khóa, thiếu nguồn hoặc lý do là lỗi chặn.

Giả định theo mốc là **trung bình mỗi ngày trong giai đoạn kết thúc ở mốc đó** khi dùng làm tốc độ (dòng/ngày, file/ngày); ở `launch` tốc độ không dùng. Từ file này `00-context/assumptions.md` được sinh, không sửa tay.

## `tables.yaml`

```yaml
databases:
  order-db:
    engine: postgresql
    major: 16                       # -> db-constants/postgresql-16.yaml
    price_item: db-storage          # khóa trong pricing.yaml, unit GB-month
    tables:
      orders:                       # khóa này là tên cặp dấu <!-- BEGIN:calc:orders --> trong tables.md
        id: TBL-orders
        rows_per_day: A-orders-per-day     # ID giả định, phủ mọi mốc có thời gian trừ launch
        initial_rows: 0                    # tùy chọn, mặc định 0
        retention_days: 1095               # tùy chọn; bỏ qua = giữ mãi
        columns:                           # đúng thứ tự cột trong DB (thứ tự ảnh hưởng đệm căn lề)
          - {name: id, type: integer, counter: true, reason: "..."}
          - {name: note, type: text, nullable: true, avg_bytes: A-note-bytes, reason: "..."}
        indexes:
          - {name: orders_pkey, columns: [id]}
```

- `type` phải có trong file hằng số. Kiểu độ dài thay đổi (`variable: true`) cần `avg_bytes` là ID giả định **hằng** (`value`).
- `reason` bắt buộc cho mỗi cột (PLAN: mỗi cột ghi kiểu, số byte và lý do).
- `counter: true` đánh dấu cột tăng dần (khóa chính tự tăng): script tính số giá trị cần ở mốc xa nhất (số dòng đã chèn × (1 + `safety_margin`)), so với giá trị tối đa của kiểu, báo kiểu nhỏ nhất đủ; không đủ thì lỗi chặn.
- Mô hình dung lượng hiện có: `postgresql-heap` (heap + B-tree). Mỗi DB khác cần một mô hình riêng trong script.

## `storage.yaml`

```yaml
buckets:
  uploads:
    id: BKT-uploads
    files_per_day: A-uploads-per-day
    avg_file_bytes: A-upload-bytes          # có thể theo mốc
    retention_days: 365                     # tùy chọn
    views_per_day: A-views-per-day          # tùy chọn; có thì cần egress_price_item
    storage_price_item: object-storage      # unit GB-month
    egress_price_item: egress               # unit GB
```

## `compute.yaml`

```yaml
services:
  order-service:
    id: SVC-order-service
    traffic_share: 0.6                       # phần req/s đỉnh (có biên an toàn) của service, trong (0, 1]; tổng các service không quá 1
    requests_per_second_per_instance:
      value: 150
      source: https://...                    # benchmark hoặc tài liệu; bắt buộc
    target_utilization: 0.7                  # trong (0, 1]
    min_instances: 2
    price_item: compute-instance             # unit instance-month
```

## `pricing.yaml`

```yaml
currency: USD
gb_bytes: {value: 1073741824, source: https://...}   # 1 GB trong bảng giá là bao nhiêu byte
items:
  compute-instance:
    description: VM 2 vCPU, 4 GB RAM
    unit: instance-month                     # instance-month | GB-month | GB
    unit_price: 70
    source: https://...                      # trang giá chính thức, bắt buộc
    looked_up: 2026-10-12                    # ngày tra cứu, bắt buộc
```

## `db-constants/<db>-<major>.yaml`

Nguồn dùng lại giữa các dự án: `~/knowledge/stacks/<db>/constants-<major>.yaml`; Researcher xác minh lại từng link rồi chép vào workspace ở G4 sau khi chốt DB. Mẫu PostgreSQL 16 (kèm link tài liệu chính thức và trích nguyên văn): [`scripts/test_data/db-constants/postgresql-16.yaml`](../scripts/test_data/db-constants/postgresql-16.yaml).

```yaml
db: postgresql
major: 16
model: postgresql-heap
looked_up: 2026-10-12
constants:                                   # đủ các khóa sau, mỗi khóa {value: số dương, source: https://..., note: tùy chọn}
  page_size_bytes: ...  page_header_bytes: ...  item_pointer_bytes: ...  tuple_header_bytes: ...
  null_bitmap_bits_per_column: ...  heap_fillfactor: ...  varlena_short_header_bytes: ...  varlena_long_header_bytes: ...
  varlena_short_max_bytes: ...  index_tuple_header_bytes: ...  btree_leaf_fillfactor: ...  btree_page_special_bytes: ...
types:
  bigint: {bytes: 8, align: 8, max: 9223372036854775807, family: integer, source: https://..., align_source: https://...}
  text: {variable: true, align: 4, source: https://..., align_source: https://...}
```

Hằng số hay kiểu thiếu `source` / `align_source` (không phải link `http(s)://`) là lỗi, như đơn giá thiếu `source` hoặc `looked_up`. Link vào mã nguồn (github.com, raw.githubusercontent.com, gitlab.com, gitweb/cgit `hb=` / `h=`) phải trỏ **tag phát hành** (như `REL_16_4`) hoặc commit; trỏ nhánh (`REL_16_STABLE`, `master`, `main`) là lỗi, vì số sẽ đổi theo thời gian. `maxalign_bytes` không được có trong file này (MAXALIGN là giả định theo nền tảng).

## Đầu ra

`drafts/03-capacity/{workload-model,data-sizing,storage-sizing,compute-sizing,cost-model}.md`, `drafts/00-context/assumptions.md`, và bảng số của mỗi bảng trong `drafts/07-data/databases/<db>/tables.md` **chỉ giữa** `<!-- BEGIN:calc:<bảng> -->` và `<!-- END:calc:<bảng> -->` (Designer đặt cặp dấu với nội dung `chờ script`; thiếu cặp dấu của một bảng là lỗi và file đó không bị ghi). Mỗi bảng số ghi công thức, giả định (ID `A-xx`), hằng số kèm link nguồn và mốc. `data-sizing.md` cho **hai con số** mỗi database: dung lượng logic (heap + index) và dung lượng cần cấp = `(heap × hệ số phình heap + index × hệ số phình index + WAL) × (1 + bản sao) + backup × dữ liệu sau phình`; `cost-model.md` tính chi phí lưu trữ database trên số cần cấp. TOAST chưa được mô hình: `data-sizing.md` nói rõ và ghi tỉ lệ đã khai.
