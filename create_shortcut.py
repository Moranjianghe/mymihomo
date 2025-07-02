import os
from win32com.client import Dispatch

# 1. 捷徑名稱與目標
shortcut_name = "Mihomo-Admin.lnk"
start_menu = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs")
shortcut_path = os.path.join(start_menu, shortcut_name)

# 2. 設定目標與參數（直接啟動 python 腳本，無需 PowerShell 包裹）
script_dir = os.path.dirname(os.path.abspath(__file__))
target = "python.exe"
arguments = "start_visible.py"
working_dir = script_dir
icon = "python.exe"

# 3. 建立捷徑
shell = Dispatch("WScript.Shell")
shortcut = shell.CreateShortcut(shortcut_path)
shortcut.TargetPath = target
shortcut.Arguments = arguments
shortcut.WorkingDirectory = working_dir
shortcut.IconLocation = icon
shortcut.Save()


# 4. 用 PowerShell 設置捷徑為「以管理員身份執行」
import subprocess

# 修正 PowerShell 腳本語法，移除 r 前綴
ps_script = f'''
$shortcutPath = "{shortcut_path}"
$bytes = [System.IO.File]::ReadAllBytes($shortcutPath)
$bytes[0x15] = $bytes[0x15] -bor 0x20
[System.IO.File]::WriteAllBytes($shortcutPath, $bytes)
'''
subprocess.run(["powershell", "-Command", ps_script], check=True)

print(f"捷徑已建立並設為管理員模式：{shortcut_path}")
