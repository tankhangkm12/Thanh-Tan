# Ma trận phiên bản và tính năng

## Ma trận phiên bản
<!-- required -->

| Công nghệ | Phiên bản chốt | Vòng đời (phát hành; hết hỗ trợ) | Tính năng dự án dựa vào (phiên bản tối thiểu) | Giới hạn và lỗi đã biết | Thay đổi phá vỡ ở bản lớn kế tiếp | Tương thích | Rủi ro |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Node.js — runtime cho order-service | 24.0; nhận bản vá 24.x | 2025-05-06; hết hỗ trợ 2028-04-30 [lịch phát hành](https://nodejs.org/en/about/previous-releases) | fetch tích hợp (từ 18.0) | [release notes](https://nodejs.org/en/blog/release/v24.0.0) | xem release notes bản kế tiếp | driver pg từ 8.0 | không có |
| React — thư viện dựng ứng dụng order-web | 19.2; nhận bản vá 19.x | 2025-10-01; chưa công bố [chính sách phiên bản](https://react.dev/versions) | JSX và hook (từ 19.0) | [release notes](https://react.dev/blog) | xem bản chính kế tiếp ở blog React | Vite 7.3 | không có |
| Vite — công cụ build order-web | 7.3; nhận bản vá 7.3.x | 2025-12-15; chưa công bố [chính sách phát hành](https://vite.dev/releases) | chia gói mã theo route (từ 7.0) | [release notes](https://github.com/vitejs/vite/releases) | xem bản chính kế tiếp ở trang phát hành | Node.js 24.0 | không có |
| Ubuntu Server LTS — hệ điều hành của máy ảo | 24.04; nhận bản vá bảo mật | 2024-04-25; hết hỗ trợ 2029-05-01 [vòng đời](https://ubuntu.com/about/release-cycle) (giả định: nguồn chỉ ghi tháng 5/2029, lấy ngày đầu tháng) | Node.js và PostgreSQL 16 chạy trên bản này (từ 24.04) | [ghi chú phát hành](https://wiki.ubuntu.com/NobleNumbat/ReleaseNotes) | xem ghi chú phát hành bản LTS kế tiếp | Node.js 24.0; PostgreSQL 16.4 | R-003 |
| GitHub Actions — CI/CD | SaaS, không phiên bản | SaaS; [changelog](https://github.blog/changelog/) | chạy workflow trên runner Linux | [giới hạn dùng](https://docs.github.com/en/actions/administering-github-actions/usage-limits-billing-and-administration) | xem changelog | không có | không có |
| PostgreSQL — database quan hệ cho order-db | 16.4; nhận bản vá 16.x | 2023-09-14; hết hỗ trợ 2028-11-09 [chính sách phiên bản](https://www.postgresql.org/support/versioning/) | khóa ngoại, index B-tree (từ 16.0) | [release notes](https://www.postgresql.org/docs/release/16.4/) | xem release notes bản 17 | driver pg từ 8.0 | không có |

## Chính sách bản vá
<!-- required -->

| Lớp | Cách nhận bản vá | Tần suất kiểm tra (ngày) | Người chịu trách nhiệm | Cơ sở |
| --- | --- | --- | --- | --- |
| backend | cập nhật bản vá theo thông báo bảo mật | 30 ngày | thành viên vận hành | D-002 |
| frontend | cập nhật bản vá theo thông báo của React và Vite | 30 ngày | thành viên vận hành | D-003 |
| infrastructure | cập nhật bản vá bảo mật của Ubuntu | 30 ngày | thành viên vận hành | D-004 |
| data | cập nhật bản vá nhỏ theo lịch của PostgreSQL | 30 ngày | thành viên vận hành | D-002 |
