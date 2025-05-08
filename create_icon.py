from PIL import Image, ImageDraw, ImageFont
import os

# Tạo một biểu tượng đơn giản
icon_size = 256
icon = Image.new('RGBA', (icon_size, icon_size), color=(255, 255, 255, 0))
draw = ImageDraw.Draw(icon)

# Vẽ hình tròn làm nền
draw.ellipse((10, 10, icon_size-10, icon_size-10), fill=(74, 109, 167, 255))

# Vẽ chữ "A" ở giữa
try:
    # Thử tải font, nếu không có sẽ dùng font mặc định
    font = ImageFont.truetype("arial.ttf", 140)
except:
    font = ImageFont.load_default()

# Vẽ chữ "AT" màu trắng
draw.text((icon_size//2 - 60, icon_size//2 - 70), "AT", fill=(255, 255, 255, 255), font=font)

# Lưu biểu tượng
icon.save('app_icon.ico', format='ICO', sizes=[(256, 256)])
print("Đã tạo biểu tượng app_icon.ico thành công!")

# Cập nhật file spec để sử dụng biểu tượng mới
if os.path.exists('auto_text.spec'):
    with open('auto_text.spec', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Thay thế biểu tượng NONE bằng biểu tượng mới
    content = content.replace("icon='NONE'", "icon='app_icon.ico'")
    
    with open('auto_text.spec', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Đã cập nhật file spec để sử dụng biểu tượng mới!") 