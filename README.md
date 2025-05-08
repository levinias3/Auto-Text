# Ứng dụng Auto Text

Ứng dụng này giúp bạn tự động thay thế các cụm từ tắt thành văn bản dài khi gõ, và giờ đây còn có thể chuyển đổi thành ảnh!

## Cài đặt

1. Đảm bảo bạn đã cài đặt Python 3.6 trở lên
2. Cài đặt các thư viện cần thiết:
   ```
   pip install -r requirements.txt
   ```

## Cách sử dụng

1. Chạy ứng dụng:
   ```
   python main.py
   ```

2. Thêm các cụm từ tắt và văn bản thay thế:
   - Nhập cụm từ tắt vào ô "Shortcut"
   - Chọn loại thay thế (Văn bản hoặc Ảnh)
   - Đối với văn bản: Nhập văn bản thay thế vào ô "Văn bản thay thế"
   - Đối với ảnh: Nhấn "Chọn ảnh" để chọn file ảnh từ máy tính
   - Nhấn nút "Thêm"

3. Khi gõ văn bản trong bất kỳ ứng dụng nào:
   - Nếu bạn gõ một cụm từ tắt liên kết với văn bản, văn bản tương ứng sẽ được chèn vào.
   - Nếu bạn gõ một cụm từ tắt liên kết với ảnh, ảnh tương ứng sẽ được dán vào vị trí con trỏ.

4. Nhấn "Lưu cấu hình" để lưu các thay đổi của bạn.

## Ví dụ

Mặc định đã cài đặt sẵn một số cụm từ tắt:
- `Hl@` sẽ thay thế thành `Hello`
- `GM@` sẽ thay thế thành `Good morning`
- `GE@` sẽ thay thế thành `Good evening`
- `TY@` sẽ thay thế thành `Thank you very much`
- `BRG@` sẽ thay thế thành `Best regards`

Bạn có thể tạo thêm các cụm từ tắt mới liên kết với ảnh, ví dụ:
- `PIC@` có thể liên kết với một ảnh chữ ký
- `LOGO@` có thể liên kết với logo công ty
- `EMO@` có thể liên kết với ảnh biểu cảm

## Lưu ý

- Ứng dụng này hoạt động bằng cách theo dõi các phím bạn nhấn, nên có thể yêu cầu quyền truy cập đặc biệt trên một số hệ thống.
- Đối với tính năng ảnh, ứng dụng sẽ đưa ảnh vào clipboard và thực hiện tổ hợp phím Ctrl+V để dán.
- Một số ứng dụng có thể không hỗ trợ dán ảnh, trong trường hợp đó hãy thử với ứng dụng khác (như Microsoft Word, PowerPoint, hoặc các trình soạn thảo hỗ trợ ảnh).
- Nếu bạn gặp vấn đề với quyền truy cập bàn phím, hãy thử chạy ứng dụng với quyền quản trị viên. 