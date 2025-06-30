# -*- coding: utf-8 -*-
# Mihomo TUN 模式設置腳本

import os
import sys
import ctypes
import subprocess
import urllib.request
import zipfile
import shutil
import winreg
import time
import colorama
import yaml
from colorama import Fore, Style

# 初始化colorama
colorama.init()

# 定義檔案路徑
script_dir = os.path.dirname(os.path.realpath(__file__))

# 統一讀取 script_config.yaml
SCRIPT_CONFIG_PATH = os.path.join(script_dir, "script_config.yaml")
with open(SCRIPT_CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

config_path = config.get('config_file')
if not config_path:
    config_path = os.path.join(script_dir, 'config.yaml')
config_path = os.path.normpath(os.path.join(script_dir, config_path)) if not os.path.isabs(config_path) else os.path.normpath(config_path)
data_dir = config.get('data_dir')
if not data_dir:
    data_dir = os.path.join(script_dir, 'data')
data_dir = os.path.normpath(os.path.join(script_dir, data_dir)) if not os.path.isabs(data_dir) else os.path.normpath(data_dir)

wintun_dir = os.path.join(script_dir, "wintun")
wintun_zip_path = os.path.join(script_dir, "wintun.zip")
wintun_dll_path = os.path.join(wintun_dir, "wintun.dll")
wintun_dll_system_path = r"C:\Windows\System32\wintun.dll"

# WinTUN 下載 URL
WINTUN_URL = "https://www.wintun.net/builds/wintun-0.14.1.zip"

def write_color_output(message, color=Fore.WHITE):
    """彩色輸出函數"""
    print(f"{color}{message}{Style.RESET_ALL}")

def check_is_admin():
    """檢查是否以管理員權限運行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def check_wintun_installation():
    """檢查 WinTUN 是否已安裝"""
    # 方法1：檢查系統路徑中是否存在 wintun.dll
    if os.path.exists(wintun_dll_system_path):
        return True, "WinTUN 已安裝在系統路徑中"
    
    # 方法2：檢查當前目錄或臨時提取目錄是否有 wintun.dll
    if os.path.exists(wintun_dll_path):
        return True, "WinTUN 在本地目錄中可用"
        
    # 方法3：嘗試通過註冊表檢查
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\WinTun") as key:
            return True, "WinTUN 服務已註冊"
    except:
        pass
    
    return False, "WinTUN 未安裝"

def download_wintun():
    """下載 WinTUN 安裝包"""
    write_color_output(f"正在從 {WINTUN_URL} 下載 WinTUN...", Fore.YELLOW)
    try:
        # 建立網絡請求
        with urllib.request.urlopen(WINTUN_URL) as response, open(wintun_zip_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        write_color_output(f"下載完成，文件保存至: {wintun_zip_path}", Fore.GREEN)
        return True
    except Exception as e:
        write_color_output(f"下載 WinTUN 失敗: {str(e)}", Fore.RED)
        return False

def extract_wintun():
    """解壓 WinTUN 安裝包"""
    if not os.path.exists(wintun_zip_path):
        write_color_output(f"未找到 WinTUN 安裝包: {wintun_zip_path}", Fore.RED)
        return False

    # 確保解壓目錄存在
    if not os.path.exists(wintun_dir):
        os.makedirs(wintun_dir)

    try:
        with zipfile.ZipFile(wintun_zip_path, 'r') as zip_ref:
            zip_ref.extractall(wintun_dir)
        write_color_output(f"WinTUN 解壓成功至: {wintun_dir}", Fore.GREEN)
        return True
    except Exception as e:
        write_color_output(f"解壓 WinTUN 失敗: {str(e)}", Fore.RED)
        return False

def install_wintun():
    """安裝 WinTUN 驅動"""
    # 檢查是否以管理員權限運行
    if not check_is_admin():
        write_color_output("安裝 WinTUN 需要管理員權限，請以管理員身份運行此腳本", Fore.RED)
        return False

    # 尋找 x64 目錄下的 wintun.dll
    wintun_dll_source = None
    for root, dirs, files in os.walk(wintun_dir):
        if "wintun.dll" in files and "amd64" in root.lower():
            wintun_dll_source = os.path.join(root, "wintun.dll")
            break

    if not wintun_dll_source:
        write_color_output("未在解壓目錄中找到 wintun.dll", Fore.RED)
        return False

    try:
        # 複製 DLL 到系統目錄
        shutil.copy2(wintun_dll_source, wintun_dll_system_path)
        write_color_output(f"已複製 wintun.dll 到系統目錄: {wintun_dll_system_path}", Fore.GREEN)
        return True
    except Exception as e:
        write_color_output(f"安裝 WinTUN 失敗: {str(e)}", Fore.RED)
        return False

def check_tun_config(config_file_path):
    """檢查配置文件中是否啟用 TUN 模式"""
    try:
        if not os.path.exists(config_file_path):
            return False, "配置文件不存在"
        
        # 讀取配置文件查找 tun 配置
        with open(config_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'tun:' in content:
                if 'enable: true' in content:
                    return True, None
                else:
                    return False, "TUN 模式在配置文件中存在但未啟用"
            else:
                return False, "配置文件中未設置 TUN 模式"
    except Exception as e:
        return False, f"檢查配置文件時發生錯誤: {str(e)}"

def get_tun_config_details(config_file_path):
    """獲取配置文件中 TUN 模式的詳細設置"""
    details = {
        "stack": "未設置",
        "dns-hijack": "未設置",
        "auto-route": "未設置",
        "auto-detect-interface": "未設置"
    }
    
    try:
        if not os.path.exists(config_file_path):
            return details
        
        with open(config_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split("\n")
            in_tun_section = False
            
            for line in lines:
                line = line.strip()
                if not in_tun_section and line == "tun:":
                    in_tun_section = True
                    continue
                    
                if in_tun_section:
                    if line.startswith("  ") or line.startswith("\t"):
                        if "stack:" in line:
                            details["stack"] = line.split("stack:")[1].strip()
                        elif "dns-hijack:" in line:
                            details["dns-hijack"] = "已設置"
                        elif "auto-route:" in line:
                            details["auto-route"] = line.split("auto-route:")[1].strip()
                        elif "auto-detect-interface:" in line:
                            details["auto-detect-interface"] = line.split("auto-detect-interface:")[1].strip()
                    elif not line.startswith(" ") and not line.startswith("\t") and line.strip():
                        # 已離開 tun 部分
                        break
        
        return details
    except Exception as e:
        write_color_output(f"獲取 TUN 配置詳情時發生錯誤: {str(e)}", Fore.RED)
        return details

def create_tun_config_template():
    """創建 TUN 模式配置模板"""
    template = """# TUN 模式配置示例
tun:
  enable: true
  stack: gvisor  # 網絡協議棧類型，可選 gvisor 或 system
  dns-hijack:
    - 0.0.0.0:53  # 劫持所有 DNS 請求
  auto-route: true  # 自動配置路由
  auto-detect-interface: true  # 自動檢測網絡接口
"""
    template_file = os.path.join(script_dir, "tun_config_template.yaml")
    
    try:
        with open(template_file, "w", encoding="utf-8") as f:
            f.write(template)
        write_color_output(f"TUN 配置模板已創建: {template_file}", Fore.GREEN)
        return True
    except Exception as e:
        write_color_output(f"創建 TUN 配置模板失敗: {str(e)}", Fore.RED)
        return False

def check_network_interfaces():
    """檢查系統網絡接口"""
    try:
        output = subprocess.check_output("ipconfig", shell=True).decode("gbk", errors="ignore")
        write_color_output("系統網絡接口信息:", Fore.CYAN)
        print(output)
        return True
    except Exception as e:
        write_color_output(f"獲取網絡接口信息失敗: {str(e)}", Fore.RED)
        return False

def main():
    """主函數"""
    # 檢查是否以管理員權限運行
    is_admin = check_is_admin()
    
    write_color_output("Mihomo TUN 模式設置工具", Fore.GREEN)
    write_color_output("=========================================", Fore.GREEN)
    write_color_output(f"時間: {time.strftime('%Y-%m-%d %H:%M:%S')}", Fore.CYAN)
    write_color_output(f"管理員權限: {'是' if is_admin else '否'}", Fore.CYAN)
    
    if not is_admin:
        write_color_output("警告: TUN 模式設置需要管理員權限，請以管理員身份運行此腳本", Fore.YELLOW)
        proceed = input("是否繼續? (Y/N): ")
        if proceed.lower() != 'y':
            write_color_output("操作已取消", Fore.CYAN)
            return 1
    
    # 檢查配置文件
    write_color_output("\n檢查 Mihomo 配置文件...", Fore.BLUE)
    config_exists = os.path.exists(config_path)
    write_color_output(f"配置文件 ({config_path}): {'存在' if config_exists else '不存在'}", Fore.CYAN if config_exists else Fore.YELLOW)
    
    if config_exists:
        tun_enabled, tun_error = check_tun_config(config_path)
        if tun_enabled:
            write_color_output("配置文件中已啟用 TUN 模式", Fore.GREEN)
            # 獲取詳細配置
            details = get_tun_config_details(config_path)
            write_color_output("TUN 模式配置詳情:", Fore.CYAN)
            write_color_output(f"  網絡協議棧: {details['stack']}", Fore.CYAN)
            write_color_output(f"  DNS 劫持: {details['dns-hijack']}", Fore.CYAN)
            write_color_output(f"  自動配置路由: {details['auto-route']}", Fore.CYAN)
            write_color_output(f"  自動檢測接口: {details['auto-detect-interface']}", Fore.CYAN)
        else:
            write_color_output(f"TUN 模式未啟用: {tun_error}", Fore.YELLOW)
            create_template = input("是否要創建 TUN 模式配置模板? (Y/N): ")
            if create_template.lower() == 'y':
                create_tun_config_template()
    
    # 檢查 WinTUN 驅動
    write_color_output("\n檢查 WinTUN 驅動...", Fore.BLUE)
    wintun_installed, wintun_status = check_wintun_installation()
    write_color_output(f"WinTUN 狀態: {wintun_status}", Fore.GREEN if wintun_installed else Fore.YELLOW)
    
    # 如果 WinTUN 未安裝，提供安裝選項
    if not wintun_installed:
        install_option = input("是否下載並安裝 WinTUN 驅動? (Y/N): ")
        if install_option.lower() == 'y':
            if download_wintun() and extract_wintun():
                if install_wintun():
                    write_color_output("WinTUN 驅動安裝成功！", Fore.GREEN)
                else:
                    write_color_output("WinTUN 驅動安裝失敗。", Fore.RED)
            else:
                write_color_output("無法下載或解壓 WinTUN。", Fore.RED)
    
    # 檢查網絡接口
    write_color_output("\n檢查系統網絡接口...", Fore.BLUE)
    check_network_interfaces()
    
    write_color_output("\n=========================================", Fore.GREEN)
    write_color_output("TUN 模式設置檢查完成", Fore.GREEN)
    
    if not is_admin and ((config_exists and tun_enabled) or not wintun_installed):
        write_color_output("\n重要提示：要使 TUN 模式正常工作，請以管理員身份運行 Mihomo。", Fore.YELLOW)
    
    input("\n按 Enter 鍵退出...")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        write_color_output("\n程序已被中斷", Fore.YELLOW)
        sys.exit(0)
    except Exception as e:
        write_color_output(f"\n發生錯誤: {str(e)}", Fore.RED)
        input("按 Enter 鍵退出...")
        sys.exit(1)
