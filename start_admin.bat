@echo off
REM 以管理員權限啟動Mihomo (特別是TUN模式需要)
echo 正在以管理員權限啟動Mihomo...
powershell -Command "Start-Process cmd -ArgumentList '/c cd /d %~dp0 && python start_visible.py' -Verb RunAs"
