import json
import os
import sys
import keyboard
import time
import fix_clipboard
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTableWidget, QTableWidgetItem, 
                           QPushButton, QLineEdit, QLabel, QMessageBox,
                           QFileDialog, QGroupBox, QTextEdit, QToolBar,
                           QAction, QTabWidget, QSplitter, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QFont, QTextCharFormat, QTextCursor
import io
import win32clipboard
from PIL import Image
import shutil
import subprocess

class RichTextEditor(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptRichText(True)
        self.setMinimumHeight(100)
    
    def applyBold(self):
        format = QTextCharFormat()
        if self.currentCharFormat().fontWeight() == QFont.Bold:
            format.setFontWeight(QFont.Normal)
        else:
            format.setFontWeight(QFont.Bold)
        self.mergeCurrentCharFormat(format)
    
    def applyItalic(self):
        format = QTextCharFormat()
        format.setFontItalic(not self.currentCharFormat().fontItalic())
        self.mergeCurrentCharFormat(format)
    
    def applyUnderline(self):
        format = QTextCharFormat()
        format.setFontUnderline(not self.currentCharFormat().fontUnderline())
        self.mergeCurrentCharFormat(format)
    
    def addBulletList(self):
        cursor = self.textCursor()
        cursor.insertList(QTextCursor.ListDisc)
        
    def addNumberedList(self):
        cursor = self.textCursor()
        cursor.insertList(QTextCursor.ListDecimal)

class AutoTextApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Text & Image")
        self.setGeometry(300, 300, 800, 600)
        
        # Tạo thư mục images nếu chưa tồn tại
        os.makedirs("images", exist_ok=True)
        
        # Dữ liệu thay thế văn bản và ảnh
        self.replacements = {}
        self.load_config()
        
        # Cài đặt giao diện
        self.init_ui()
        
        # Bắt đầu theo dõi bàn phím
        self.buffer = ""
        self.max_shortcut_length = 10  # Độ dài tối đa của chuỗi shortcut
        self.setup_keyboard_hook()
        
        # Khởi tạo clipboard
        self.clipboard = QApplication.clipboard()
        
        # Debug mode
        self.debug_mode = True
        
        # Status message
        self.last_status = ""
        
        # Loại văn bản hiện tại
        self.current_text_type = "plain"  # plain hoặc rich

    def init_ui(self):
        # Widget chính
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Status label
        self.status_label = QLabel("Đang hoạt động - theo dõi văn bản")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        main_layout.addWidget(self.status_label)
        
        # Debug info label
        self.debug_label = QLabel("")
        self.debug_label.setStyleSheet("color: blue;")
        main_layout.addWidget(self.debug_label)
        
        # Tab widget cho các loại nội dung khác nhau
        self.tab_widget = QTabWidget()
        
        # Tab 1: Thêm mới
        add_tab = QWidget()
        add_layout = QVBoxLayout(add_tab)
        
        # Form để thêm thay thế mới
        form_group = QGroupBox("Thêm cụm từ mới")
        form_layout = QVBoxLayout(form_group)
        
        # Shortcut input
        shortcut_layout = QHBoxLayout()
        shortcut_layout.addWidget(QLabel("Cụm từ:"))
        self.shortcut_input = QLineEdit()
        self.shortcut_input.setPlaceholderText("Nhập cụm từ tắt (vd: pic@)")
        shortcut_layout.addWidget(self.shortcut_input)
        form_layout.addLayout(shortcut_layout)
        
        # Tab cho loại nội dung
        content_tabs = QTabWidget()
        
        # Tab văn bản đơn giản
        simple_text_tab = QWidget()
        simple_text_layout = QVBoxLayout(simple_text_tab)
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Nhập văn bản thay thế đơn giản")
        simple_text_layout.addWidget(self.text_input)
        content_tabs.addTab(simple_text_tab, "Văn bản đơn giản")
        
        # Tab văn bản phong phú
        rich_text_tab = QWidget()
        rich_text_layout = QVBoxLayout(rich_text_tab)
        
        # Toolbar cho định dạng văn bản
        format_toolbar = QToolBar("Định dạng")
        
        # Nút định dạng
        self.bold_action = QAction(QIcon.fromTheme("format-text-bold", QIcon("icons/bold.png")), "Đậm", self)
        self.bold_action.triggered.connect(self.apply_bold)
        format_toolbar.addAction(self.bold_action)
        
        self.italic_action = QAction(QIcon.fromTheme("format-text-italic", QIcon("icons/italic.png")), "Nghiêng", self)
        self.italic_action.triggered.connect(self.apply_italic)
        format_toolbar.addAction(self.italic_action)
        
        self.underline_action = QAction(QIcon.fromTheme("format-text-underline", QIcon("icons/underline.png")), "Gạch chân", self)
        self.underline_action.triggered.connect(self.apply_underline)
        format_toolbar.addAction(self.underline_action)
        
        format_toolbar.addSeparator()
        
        self.bullet_action = QAction(QIcon.fromTheme("format-list-unordered", QIcon("icons/bullet.png")), "Gạch đầu dòng", self)
        self.bullet_action.triggered.connect(self.add_bullet_list)
        format_toolbar.addAction(self.bullet_action)
        
        self.number_action = QAction(QIcon.fromTheme("format-list-ordered", QIcon("icons/number.png")), "Danh sách số", self)
        self.number_action.triggered.connect(self.add_numbered_list)
        format_toolbar.addAction(self.number_action)
        
        rich_text_layout.addWidget(format_toolbar)
        
        # Editor văn bản phong phú
        self.rich_text_editor = RichTextEditor()
        rich_text_layout.addWidget(self.rich_text_editor)
        
        content_tabs.addTab(rich_text_tab, "Văn bản định dạng")
        
        # Tab ảnh
        image_tab = QWidget()
        image_layout = QVBoxLayout(image_tab)
        
        image_input_layout = QHBoxLayout()
        image_input_layout.addWidget(QLabel("Ảnh:"))
        self.image_path_label = QLabel("Chưa chọn ảnh")
        image_input_layout.addWidget(self.image_path_label)
        
        self.browse_button = QPushButton("Chọn ảnh")
        self.browse_button.clicked.connect(self.browse_image)
        image_input_layout.addWidget(self.browse_button)
        
        self.preview_image_label = QLabel()
        self.preview_image_label.setFixedSize(80, 80)
        self.preview_image_label.setScaledContents(True)
        image_input_layout.addWidget(self.preview_image_label)
        
        image_layout.addLayout(image_input_layout)
        content_tabs.addTab(image_tab, "Ảnh")
        
        # Thêm tab vào form
        form_layout.addWidget(content_tabs)
        self.content_tabs = content_tabs
        
        # Button layout
        button_layout = QHBoxLayout()
        add_button = QPushButton("Thêm")
        add_button.clicked.connect(self.add_replacement)
        button_layout.addWidget(add_button)
        
        # Test button
        test_button = QPushButton("Test")
        test_button.clicked.connect(self.test_content)
        button_layout.addWidget(test_button)
        
        form_layout.addLayout(button_layout)
        add_layout.addWidget(form_group)
        
        # Bảng hiển thị các thay thế hiện tại
        table_group = QGroupBox("Thư viện cụm từ")
        table_layout = QVBoxLayout(table_group)
        
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Cụm từ", "Loại", "Nội dung", "Xem trước", "Hành động"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.update_table()
        table_layout.addWidget(self.table)
        
        # Nút lưu cấu hình
        save_button = QPushButton("Lưu cấu hình")
        save_button.clicked.connect(self.save_config)
        table_layout.addWidget(save_button)
        
        add_layout.addWidget(table_group)
        
        # Thêm tab vào tab widget chính
        self.tab_widget.addTab(add_tab, "Thêm & Quản lý")
        
        # Tab 2: Hướng dẫn
        help_tab = QWidget()
        help_layout = QVBoxLayout(help_tab)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
            <h2>Hướng dẫn sử dụng</h2>
            <p>Ứng dụng này giúp bạn tự động thay thế các cụm từ tắt thành:</p>
            <ul>
                <li><b>Văn bản đơn giản</b>: Thay thế cụm từ tắt bằng một đoạn văn bản ngắn</li>
                <li><b>Văn bản định dạng</b>: Thay thế bằng văn bản có định dạng như in đậm, in nghiêng, gạch đầu dòng...</li>
                <li><b>Ảnh</b>: Thay thế bằng một hình ảnh được dán vào vị trí con trỏ</li>
            </ul>
            
            <h3>Cách thêm cụm từ mới:</h3>
            <ol>
                <li>Nhập cụm từ tắt vào ô "Cụm từ" (ví dụ: "hl@")</li>
                <li>Chọn tab tương ứng với loại nội dung muốn thay thế</li>
                <li>Nhập hoặc định dạng nội dung thay thế</li>
                <li>Nhấn "Thêm" để lưu vào thư viện</li>
                <li>Nhấn "Lưu cấu hình" để lưu thư viện vào file</li>
            </ol>
            
            <h3>Cách sử dụng:</h3>
            <p>Khi bạn gõ một cụm từ tắt đã được cài đặt trong bất kỳ ứng dụng nào, nó sẽ tự động được thay thế bằng nội dung tương ứng.</p>
            
            <h3>Các tính năng định dạng văn bản:</h3>
            <ul>
                <li><b>In đậm</b>: Làm nổi bật văn bản</li>
                <li><i>In nghiêng</i>: Tạo phong cách nghiêng cho văn bản</li>
                <li><u>Gạch chân</u>: Gạch dưới văn bản</li>
                <li>Gạch đầu dòng:
                    <ul>
                        <li>Tạo danh sách dạng chấm</li>
                    </ul>
                </li>
                <li>Danh sách số:
                    <ol>
                        <li>Tạo danh sách có đánh số</li>
                    </ol>
                </li>
            </ul>
            
            <p><b>Lưu ý:</b> Tính năng văn bản định dạng hoạt động tốt nhất với các ứng dụng hỗ trợ văn bản RTF như Microsoft Word, Outlook, v.v.</p>
        """)
        help_layout.addWidget(help_text)
        
        self.tab_widget.addTab(help_tab, "Hướng dẫn")
        
        # Thêm tab widget vào layout chính
        main_layout.addWidget(self.tab_widget)
        
        # Lưu đường dẫn ảnh hiện tại
        self.current_image_path = None
    
    def apply_bold(self):
        self.rich_text_editor.applyBold()
    
    def apply_italic(self):
        self.rich_text_editor.applyItalic()
    
    def apply_underline(self):
        self.rich_text_editor.applyUnderline()
    
    def add_bullet_list(self):
        self.rich_text_editor.addBulletList()
    
    def add_numbered_list(self):
        self.rich_text_editor.addNumberedList()
    
    def add_debug_message(self, message):
        """Thêm thông báo debug"""
        if self.debug_mode:
            self.last_status = message
            self.debug_label.setText(f"Debug: {message}")
            print(f"DEBUG: {message}")
    
    def test_content(self):
        """Test nội dung hiện tại"""
        current_tab = self.content_tabs.currentIndex()
        
        if current_tab == 0:  # Văn bản đơn giản
            text = self.text_input.text()
            if not text:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập văn bản!")
                return
                
            self.add_debug_message(f"Test văn bản đơn giản: {text}")
            self.clipboard.setText(text)
            QMessageBox.information(self, "Test", f"Đã sao chép văn bản: '{text}' vào clipboard. Bạn có thể dán vào ứng dụng khác.")
            
        elif current_tab == 1:  # Văn bản định dạng
            html = self.rich_text_editor.toHtml()
            if self.rich_text_editor.toPlainText().strip() == "":
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập văn bản!")
                return
                
            self.add_debug_message(f"Test văn bản định dạng: {html[:50]}...")
            mime_data = self.clipboard.mimeData()
            mime_data.setHtml(html)
            self.clipboard.setMimeData(mime_data)
            QMessageBox.information(self, "Test", "Đã sao chép văn bản định dạng vào clipboard. Bạn có thể dán vào ứng dụng khác (Word, Outlook...).")
            
        elif current_tab == 2:  # Ảnh
            if not self.current_image_path or not os.path.exists(self.current_image_path):
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn ảnh trước!")
                return
                
            try:
                # Tạo QPixmap mới
                pixmap = QPixmap(self.current_image_path)
                if pixmap.isNull():
                    raise Exception("Không thể tải ảnh bằng QPixmap")
                
                # Đưa vào clipboard
                self.clipboard.setPixmap(pixmap)
                self.add_debug_message(f"Đã đưa ảnh {os.path.basename(self.current_image_path)} vào clipboard")
                
                # Thông báo cho người dùng
                QMessageBox.information(self, "Hướng dẫn", 
                    "Ảnh đã được đưa vào clipboard. Hãy mở một ứng dụng khác (như Word, Paint) và nhấn Ctrl+V để test.")
                
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể test ảnh: {str(e)}")
    
    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn ảnh", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.current_image_path = file_path
            self.image_path_label.setText(os.path.basename(file_path))
            
            # Hiển thị xem trước ảnh
            pixmap = QPixmap(file_path)
            self.preview_image_label.setPixmap(pixmap)
    
    def update_table(self):
        # Xóa bảng hiện tại
        self.table.setRowCount(0)
        
        # Thêm các thay thế vào bảng
        for row, (shortcut, data) in enumerate(self.replacements.items()):
            self.table.insertRow(row)
            
            # Thêm shortcut
            self.table.setItem(row, 0, QTableWidgetItem(shortcut))
            
            # Loại
            replacement_type = data.get("type", "text")
            type_text = "Văn bản"
            if replacement_type == "richtext":
                type_text = "Văn bản định dạng"
            elif replacement_type == "image":
                type_text = "Ảnh"
                
            self.table.setItem(row, 1, QTableWidgetItem(type_text))
            
            # Nội dung
            content_display = ""
            if replacement_type == "text":
                content = data.get("content", "")
                content_display = content if len(content) < 50 else content[:47] + "..."
            elif replacement_type == "richtext":
                content = data.get("content", "")
                plain_content = data.get("plain_content", "")
                content_display = plain_content if len(plain_content) < 50 else plain_content[:47] + "..."
            else:
                content = data.get("image_path", "")
                content_display = os.path.basename(content) if content else ""
            
            self.table.setItem(row, 2, QTableWidgetItem(content_display))
            
            # Xem trước
            preview_cell = QWidget()
            preview_layout = QHBoxLayout(preview_cell)
            preview_layout.setContentsMargins(2, 2, 2, 2)
            
            if replacement_type == "image" and content and os.path.exists(content):
                preview_label = QLabel()
                preview_label.setFixedSize(50, 50)
                preview_label.setScaledContents(True)
                pixmap = QPixmap(content)
                preview_label.setPixmap(pixmap)
                preview_layout.addWidget(preview_label)
            elif replacement_type == "richtext":
                preview_label = QLabel()
                preview_label.setText("(Văn bản định dạng)")
                preview_layout.addWidget(preview_label)
            else:
                preview_layout.addWidget(QLabel(content_display))
            
            self.table.setCellWidget(row, 3, preview_cell)
            
            # Thêm nút xóa
            delete_cell = QWidget()
            delete_layout = QHBoxLayout(delete_cell)
            delete_layout.setContentsMargins(2, 2, 2, 2)
            
            delete_button = QPushButton("Xóa")
            delete_button.clicked.connect(lambda _, s=shortcut: self.delete_replacement(s))
            delete_layout.addWidget(delete_button)
            
            self.table.setCellWidget(row, 4, delete_cell)
        
        # Điều chỉnh độ rộng cột
        self.table.resizeColumnsToContents()
    
    def generate_unique_filename(self, original_filename):
        """Tạo tên file duy nhất trong thư mục images"""
        basename = os.path.basename(original_filename)
        name, ext = os.path.splitext(basename)
        timestamp = int(time.time())
        return f"images/{name}_{timestamp}{ext}"
    
    def add_replacement(self):
        shortcut = self.shortcut_input.text().strip()
        
        if not shortcut:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập cụm từ tắt!")
            return
        
        current_tab = self.content_tabs.currentIndex()
        
        # Tạo dict cho replacement
        if current_tab == 0:  # Văn bản đơn giản
            text = self.text_input.text().strip()
            if not text:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập văn bản thay thế!")
                return
                
            replacement = {"type": "text", "content": text}
            
        elif current_tab == 1:  # Văn bản định dạng
            rich_text = self.rich_text_editor.toHtml()
            plain_text = self.rich_text_editor.toPlainText().strip()
            if not plain_text:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập văn bản định dạng!")
                return
                
            replacement = {
                "type": "richtext", 
                "content": rich_text,
                "plain_content": plain_text
            }
            
        elif current_tab == 2:  # Ảnh
            if not self.current_image_path:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn ảnh!")
                return
                
            # Sao chép ảnh vào thư mục images với tên duy nhất
            local_image_path = self.generate_unique_filename(self.current_image_path)
            try:
                # Đảm bảo thư mục tồn tại
                os.makedirs(os.path.dirname(local_image_path), exist_ok=True)
                # Sao chép ảnh
                shutil.copy2(self.current_image_path, local_image_path)
                # Lưu đường dẫn cục bộ
                replacement = {"type": "image", "image_path": local_image_path}
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể sao chép ảnh: {str(e)}")
                return
        
        self.replacements[shortcut] = replacement
        self.update_table()
        
        # Xóa form
        self.shortcut_input.clear()
        self.text_input.clear()
        self.rich_text_editor.clear()
        self.current_image_path = None
        self.image_path_label.setText("Chưa chọn ảnh")
        self.preview_image_label.clear()
        
        # Cập nhật độ dài tối đa của shortcut
        self.max_shortcut_length = max(len(s) for s in self.replacements.keys()) if self.replacements else 10
        
        # Thông báo thành công
        QMessageBox.information(self, "Thành công", f"Đã thêm cụm từ '{shortcut}' vào thư viện.")
    
    def delete_replacement(self, shortcut):
        if shortcut in self.replacements:
            # Nếu là ảnh, xóa file ảnh nếu nó nằm trong thư mục images
            data = self.replacements[shortcut]
            if data.get("type") == "image":
                image_path = data.get("image_path", "")
                if image_path and os.path.exists(image_path) and image_path.startswith("images/"):
                    try:
                        os.remove(image_path)
                    except Exception as e:
                        self.add_debug_message(f"Không thể xóa ảnh {image_path}: {str(e)}")
            
            # Xóa khỏi danh sách
            del self.replacements[shortcut]
            self.update_table()
            
            # Cập nhật độ dài tối đa của shortcut
            self.max_shortcut_length = max(len(s) for s in self.replacements.keys()) if self.replacements else 10
    
    def load_config(self):
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                    
                    # Chuyển đổi từ định dạng cũ nếu cần
                    self.replacements = {}
                    for key, value in loaded_data.items():
                        if isinstance(value, str):
                            # Định dạng cũ nhất
                            self.replacements[key] = {"type": "text", "content": value}
                        else:
                            # Định dạng mới
                            self.replacements[key] = value
                            
                            # Kiểm tra nếu là ảnh, đảm bảo file tồn tại
                            if value.get("type") == "image":
                                image_path = value.get("image_path", "")
                                if image_path and not os.path.exists(image_path):
                                    self.add_debug_message(f"Cảnh báo: Không tìm thấy ảnh {image_path} cho shortcut {key}")
                    
                    # Cập nhật độ dài tối đa của shortcut
                    self.max_shortcut_length = max(len(s) for s in self.replacements.keys()) if self.replacements else 10
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tải cấu hình: {str(e)}")
    
    def save_config(self):
        try:
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(self.replacements, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "Thành công", "Đã lưu cấu hình thành công!")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể lưu cấu hình: {str(e)}")
    
    def setup_keyboard_hook(self):
        # Bắt sự kiện nhấn phím
        keyboard.on_press(self.on_key_press)
    
    def on_key_press(self, event):
        # Bỏ qua các phím chức năng
        if event.name in ['shift', 'ctrl', 'alt', 'right shift', 'right ctrl', 'right alt']:
            return
        
        if event.name == 'space':
            self.buffer += " "
        elif event.name == 'enter':
            self.buffer = ""  # Reset buffer on enter
        elif event.name == 'backspace':
            if self.buffer:
                self.buffer = self.buffer[:-1]
        elif len(event.name) == 1:  # Chỉ xử lý các phím ký tự
            self.buffer += event.name
        
        # Giới hạn độ dài buffer
        if len(self.buffer) > self.max_shortcut_length:
            self.buffer = self.buffer[-self.max_shortcut_length:]
        
        # Kiểm tra xem có shortcut nào trong buffer không
        self.check_replacement()
    
    def check_replacement(self):
        for shortcut, data in self.replacements.items():
            if self.buffer.endswith(shortcut):
                # Xóa shortcut khỏi buffer
                keyboard.press('backspace')
                keyboard.release('backspace')
                for _ in range(len(shortcut) - 1):  # -1 vì phím hiện tại đã bị xóa
                    keyboard.press('backspace')
                    keyboard.release('backspace')
                
                # Xử lý thay thế dựa vào loại
                replacement_type = data.get("type", "text")
                
                if replacement_type == "text":  # Văn bản đơn giản
                    # Gõ văn bản thay thế
                    content = data.get("content", "")
                    self.add_debug_message(f"Đang thay thế cụm từ '{shortcut}' bằng văn bản: '{content}'")
                    keyboard.write(content)
                    
                elif replacement_type == "richtext":  # Văn bản định dạng
                    # Chèn văn bản định dạng vào clipboard và dán
                    html_content = data.get("content", "")
                    self.add_debug_message(f"Đang thay thế cụm từ '{shortcut}' bằng văn bản định dạng")
                    
                    try:
                        # Sử dụng phương thức mới để xử lý clipboard
                        success = fix_clipboard.set_clipboard_html(html_content, plain_text)
                        if success:
                            # Tạm dừng để đảm bảo clipboard được cập nhật
                            time.sleep(0.3)
                            # Dán từ clipboard
                            keyboard.press_and_release('ctrl+v')
                        self.add_debug_message("Đã dán văn bản định dạng bằng Ctrl+V")
                    except Exception as e:
                        self.add_debug_message(f"Lỗi khi dán văn bản định dạng: {str(e)}")
                    
                elif replacement_type == "image":  # Ảnh
                    # Chèn ảnh vào clipboard và dán
                    image_path = data.get("image_path", "")
                    self.add_debug_message(f"Đang thay thế cụm từ '{shortcut}' bằng ảnh: {os.path.basename(image_path)}")
                    
                    if os.path.exists(image_path):
                        try:
                            # Phương pháp 1: Sử dụng PyQt5 + tổ hợp phím Ctrl+V
                            pixmap = QPixmap(image_path)
                            if pixmap.isNull():
                                self.add_debug_message("Không thể tải ảnh bằng QPixmap")
                                raise Exception("Không thể tải ảnh")
                                
                            # Sử dụng phương thức mới để xử lý clipboard với ảnh
                            success = fix_clipboard.set_clipboard_image(image_path)
                            if success:
                                # Tạm dừng để đảm bảo clipboard được cập nhật
                                time.sleep(0.3)
                                # Thử sử dụng tổ hợp phím
                                keyboard.press_and_release('ctrl+v')
                            self.add_debug_message("Đã dán ảnh bằng Ctrl+V")
                        except Exception as e:
                            self.add_debug_message(f"Lỗi khi dán ảnh: {str(e)}")
                    else:
                        self.add_debug_message(f"Không tìm thấy ảnh: {image_path}")
                
                # Reset buffer
                self.buffer = ""
                break

def main():
    app = QApplication(sys.argv)
    window = AutoTextApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 