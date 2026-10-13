# Đăng nhập và phiên

## Phiên và token
<!-- required -->

| Mục | Giá trị | Cơ sở |
| --- | --- | --- |
| Cơ chế | token truy cập ngắn hạn kèm token làm mới | |
| Nơi lưu token trên client | token truy cập trong bộ nhớ, token làm mới trong cookie HttpOnly | [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) |
| Thời hạn token truy cập (giây) | 900 | [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) |
| Thời hạn phiên không hoạt động (phút) | 30 | [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) |
| Làm mới token | khi token truy cập hết hạn; mỗi lúc chỉ một tab làm mới, các tab khác chờ kết quả | |

## Phân quyền màn hình
<!-- required -->

| Màn hình (SCR) | Vai trò được vào | Hành vi khi thiếu quyền | Kiểm ở đâu |
| --- | --- | --- | --- |
| SCR-order-form | khách | chuyển tới đăng nhập | guard route phía client và kiểm lại ở API-create-order |
| SCR-order-status | khách chủ đơn | chuyển tới đăng nhập; đơn của người khác trả lỗi theo error model | guard route phía client và kiểm lại ở API-get-order |
| SCR-staff-update | nhân viên | chuyển tới đăng nhập; khách bị từ chối theo error model | guard route phía client và kiểm lại ở API-update-status |

Kiểm ở client chỉ để điều hướng; quyền thật luôn kiểm lại ở máy chủ. Ma trận đầy đủ ở `authz-matrix.md`.

## Đăng xuất và thu hồi
<!-- required -->

- Đăng xuất: xóa token truy cập khỏi bộ nhớ và cache truy vấn; máy chủ xóa cookie token làm mới
- Thu hồi phiên từ máy chủ: API trả lỗi chưa xác thực, client xóa phiên và chuyển tới đăng nhập
- Dữ liệu offline còn lại sau đăng xuất: không có, vì không hỗ trợ offline

## Bảo vệ phía client
<!-- required -->

| Mối đe dọa | Biện pháp | Tham chiếu |
| --- | --- | --- |
| XSS | chính sách CSP chặn script ngoài, không chèn HTML thô | `threat-model.md` |
| CSRF | cookie SameSite, API xác thực bằng token truy cập | `threat-model.md` |
| lộ token | không ghi token ra log, không lưu token truy cập vào localStorage | `threat-model.md` |
