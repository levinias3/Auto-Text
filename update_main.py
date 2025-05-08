import os
import re

# Đọc file cũ
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Thêm import cho fix_clipboard
import_pattern = r'import json\nimport os\nimport sys\nimport keyboard\nimport time'
new_import = r'import json\nimport os\nimport sys\nimport keyboard\nimport time\nimport fix_clipboard'
content = re.sub(import_pattern, new_import, content)

# Thay thế phương thức xử lý clipboard cho văn bản định dạng
richtext_pattern = r"""            # Đặt HTML vào clipboard
            mime_data = self\.clipboard\.mimeData\(\)
            mime_data\.setHtml\(html\)
            self\.clipboard\.setMimeData\(mime_data\)
            QMessageBox\.information\(self, "Test", "Đã sao chép văn bản định dạng vào clipboard\. Bạn có thể dán vào ứng dụng khác \(Word, Outlook\.\.\.\)\."\)"""

richtext_replacement = r"""            # Dùng phương thức mới để xử lý clipboard
            success = fix_clipboard.set_clipboard_html(html, self.rich_text_editor.toPlainText())
            if success:
                QMessageBox.information(self, "Test", "Đã sao chép văn bản định dạng vào clipboard. Bạn có thể dán vào ứng dụng khác (Word, Outlook...).")
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể sao chép văn bản định dạng vào clipboard.")"""

content = re.sub(richtext_pattern, richtext_replacement, content)

# Thay thế phương thức xử lý clipboard cho ảnh
image_pattern = r"""                            # Đặt ảnh vào clipboard
                            self\.clipboard\.clear\(\)
                            self\.clipboard\.setPixmap\(pixmap\)
                            
                            # Tạm dừng để đảm bảo clipboard được cập nhật
                            time\.sleep\(0\.3\)
                            
                            # Thử sử dụng tổ hợp phím
                            keyboard\.press_and_release\('ctrl\+v'\)"""

image_replacement = r"""                            # Sử dụng phương thức mới để xử lý clipboard với ảnh
                            success = fix_clipboard.set_clipboard_image(image_path)
                            if success:
                                # Tạm dừng để đảm bảo clipboard được cập nhật
                                time.sleep(0.3)
                                # Thử sử dụng tổ hợp phím
                                keyboard.press_and_release('ctrl+v')"""

content = re.sub(image_pattern, image_replacement, content)

# Thay thế phương thức xử lý clipboard cho văn bản định dạng khi thay thế
richtext_replace_pattern = r"""                    try:
                        # Đặt HTML vào clipboard
                        mime_data = self\.clipboard\.mimeData\(\)
                        mime_data\.setHtml\(html_content\)
                        self\.clipboard\.setMimeData\(mime_data\)
                        
                        # Tạm dừng để đảm bảo clipboard được cập nhật
                        time\.sleep\(0\.3\)
                        
                        # Dán từ clipboard
                        keyboard\.press_and_release\('ctrl\+v'\)"""

richtext_replace_replacement = r"""                    try:
                        # Sử dụng phương thức mới để xử lý clipboard
                        success = fix_clipboard.set_clipboard_html(html_content, plain_text)
                        if success:
                            # Tạm dừng để đảm bảo clipboard được cập nhật
                            time.sleep(0.3)
                            # Dán từ clipboard
                            keyboard.press_and_release('ctrl+v')"""

content = re.sub(richtext_replace_pattern, richtext_replace_replacement, content)

# Ghi ra file mới
with open('main_updated.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Đã cập nhật xong file main.py và lưu vào main_updated.py")
print("Vui lòng kiểm tra file main_updated.py và đổi tên thành main.py nếu mọi thứ ổn.") 