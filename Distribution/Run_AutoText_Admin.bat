@echo off
echo Đang khởi động Auto Text Tool với quyền Admin...
powershell -Command "Start-Process -FilePath '%~dp0dist\AutoText_Tool.exe' -Verb RunAs"
exit 