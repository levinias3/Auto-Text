import io
import win32clipboard
import win32con
import pythoncom
from PyQt5.QtCore import QMimeData
from PyQt5.QtGui import QImage

def init_com():
    """Khởi tạo COM trước khi làm việc với clipboard"""
    try:
        pythoncom.CoInitialize()
        return True
    except Exception as e:
        print(f"Không thể khởi tạo COM: {str(e)}")
        return False

def uninit_com():
    """Giải phóng COM sau khi hoàn tất"""
    try:
        pythoncom.CoUninitialize()
        return True
    except Exception as e:
        print(f"Không thể giải phóng COM: {str(e)}")
        return False

def set_clipboard_text(text):
    """Đặt văn bản thường vào clipboard"""
    try:
        init_com()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        uninit_com()
        return True
    except Exception as e:
        print(f"Lỗi khi đặt văn bản vào clipboard: {str(e)}")
        try:
            win32clipboard.CloseClipboard()
        except:
            pass
        uninit_com()
        return False

def set_clipboard_html(html_text, plain_text=""):
    """Đặt HTML vào clipboard với định dạng"""
    try:
        init_com()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        
        # Đặt phiên bản văn bản đơn giản
        if plain_text:
            win32clipboard.SetClipboardText(plain_text, win32con.CF_UNICODETEXT)
        else:
            # Trích xuất văn bản từ HTML nếu không có văn bản thuần túy
            from html.parser import HTMLParser

            class MLStripper(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.reset()
                    self.strict = False
                    self.convert_charrefs = True
                    self.text = []
                def handle_data(self, d):
                    self.text.append(d)
                def get_data(self):
                    return ''.join(self.text)

            stripper = MLStripper()
            stripper.feed(html_text)
            plain_text = stripper.get_data()
            win32clipboard.SetClipboardText(plain_text, win32con.CF_UNICODETEXT)
            
        # Chuẩn bị định dạng HTML cho clipboard
        html_bytes = html_text.encode('utf-8')
        
        # Tạo header đúng định dạng cho clipboard HTML
        header = f"Version:0.9\r\nStartHTML:00000000\r\nEndHTML:{len(html_bytes)+97:08d}\r\nStartFragment:00000097\r\nEndFragment:{len(html_bytes)+97:08d}\r\n<html><body><!--StartFragment-->"
        footer = "<!--EndFragment--></body></html>"
        html_data = header.encode('ascii') + html_bytes + footer.encode('ascii')
        
        # Đặt HTML vào clipboard
        win32clipboard.SetClipboardData(win32clipboard.RegisterClipboardFormat("HTML Format"), html_data)
        
        win32clipboard.CloseClipboard()
        uninit_com()
        return True
    except Exception as e:
        print(f"Lỗi khi đặt HTML vào clipboard: {str(e)}")
        try:
            win32clipboard.CloseClipboard()
        except:
            pass
        uninit_com()
        return False

def set_clipboard_image(image_path):
    """Đặt ảnh vào clipboard"""
    try:
        from PIL import Image
        
        # Mở và chuyển đổi ảnh
        image = Image.open(image_path)
        output = io.BytesIO()
        image.convert('RGB').save(output, 'BMP')
        data = output.getvalue()[14:]  # Bỏ qua header BMP
        output.close()
        
        # Đặt vào clipboard
        init_com()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        uninit_com()
        return True
    except Exception as e:
        print(f"Lỗi khi đặt ảnh vào clipboard: {str(e)}")
        try:
            win32clipboard.CloseClipboard()
        except:
            pass
        uninit_com()
        return False 