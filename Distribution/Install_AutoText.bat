@echo off
echo === AUTO TEXT TOOL - CAI DAT ===
echo.

set INSTALL_DIR=%USERPROFILE%\AppData\Local\AutoTextTool
set DESKTOP=%USERPROFILE%\Desktop

echo Duong dan cai dat: %INSTALL_DIR%
echo.

rem Tao thu muc cai dat
echo Dang tao thu muc cai dat...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

rem Sao chep file exe va thu muc can thiet
echo Dang sao chep file chuong trinh...
xcopy "dist\AutoText_Tool.exe" "%INSTALL_DIR%\" /Y
if exist "dist\images" xcopy "dist\images" "%INSTALL_DIR%\images\" /E /I /Y
if exist "dist\config.json" xcopy "dist\config.json" "%INSTALL_DIR%\" /Y

rem Tao shortcut tren desktop
echo Dang tao shortcut tren Desktop...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\Auto Text Tool.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\AutoText_Tool.exe'; $Shortcut.Save()"

rem Tao Start Menu shortcut
echo Dang tao shortcut trong Start Menu...
set START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs
if not exist "%START_MENU%\Auto Text Tool" mkdir "%START_MENU%\Auto Text Tool"
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\Auto Text Tool\Auto Text Tool.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\AutoText_Tool.exe'; $Shortcut.Save()"

echo.
echo === Cai dat hoan tat! ===
echo Ung dung da duoc cai dat tai: %INSTALL_DIR%
echo Shortcut da duoc tao tren Desktop va Start Menu.
echo.
echo Nhan phim bat ky de thoat...
pause > nul 