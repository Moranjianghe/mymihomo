# -*- coding: utf-8 -*-
# Mihomo前台啟動腳本 - Python版本

import os
import sys
import time
import subprocess
import signal
import datetime
import ctypes
import colorama
import yaml
import json
from colorama import Fore, Style

# 初始化colorama
colorama.init()

# 定義檔案路徑
script_dir = os.path.dirname(os.path.realpath(__file__))

# 統一讀取 script_config.yaml
SCRIPT_CONFIG_PATH = os.path.join(script_dir, "script_config.yaml")
with open(SCRIPT_CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 取得核心執行檔路徑，若 script_config.yaml 未設置則使用預設值
exe_path = config.get('core_file')
if not exe_path:
    exe_path = os.path.join(script_dir, 'mihomo-windows-amd64.exe')
# 處理相對路徑，並正規化
exe_path = os.path.normpath(os.path.join(script_dir, exe_path)) if not os.path.isabs(exe_path) else os.path.normpath(exe_path)

config_path = config.get('config_file')
if not config_path:
    config_path = os.path.join(script_dir, 'config.yaml')
config_path = os.path.normpath(os.path.join(script_dir, config_path)) if not os.path.isabs(config_path) else os.path.normpath(config_path)

data_dir = config.get('data_dir')
if not data_dir:
    data_dir = os.path.join(script_dir, 'data')
# 處理相對路徑，並正規化
data_dir = os.path.normpath(os.path.join(script_dir, data_dir)) if not os.path.isabs(data_dir) else os.path.normpath(data_dir)

# 定義腳本緩存目錄
cache_dir = os.path.join(script_dir, "cache")
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

# 合併狀態與PID到一個檔案
status_file_path = os.path.join(cache_dir, "mihomo_status.json")

# 確保data目錄存在
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

def write_color_output(message, color=Fore.WHITE):
    """彩色輸出函數"""
    print(f"{color}{message}{Style.RESET_ALL}")

def check_is_admin():
    """檢查是否以管理員權限運行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def is_process_running(process_name):
    """檢查進程是否在運行"""
    try:
        # Windows平台使用tasklist命令
        output = subprocess.check_output('tasklist /FI "IMAGENAME eq ' + process_name + '" /NH', shell=True).decode()
        return process_name.lower() in output.lower()
    except:
        return False

def save_status_and_pid(pid):
    """保存進程ID和啟動狀態到JSON檔案"""
    status = {
        "status": "started",
        "start_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "pid": pid
    }
    with open(status_file_path, 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)

def check_tun_config(config_file_path):
    """檢查配置文件中是否啟用TUN模式"""
    try:
        if not os.path.exists(config_file_path):
            return False, "配置文件不存在"
        
        # 簡單讀取配置文件查找tun配置
        with open(config_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'tun:' in content and 'enable: true' in content:
                return True, None
            else:
                return False, "配置文件中未找到啟用的TUN模式配置"
    except Exception as e:
        return False, f"檢查配置文件時發生錯誤: {str(e)}"

def main():
    """主函數"""
    # 檢查是否以管理員權限運行（TUN模式需要管理員權限）
    is_admin = check_is_admin()
    
    # 顯示標題和設置
    write_color_output("Mihomo前台運行模式", Fore.GREEN)
    write_color_output("=========================================", Fore.GREEN)
    write_color_output(f"執行檔路徑: {exe_path}", Fore.CYAN)
    write_color_output(f"配置文件: {config_path}", Fore.CYAN)
    write_color_output(f"數據目錄: {data_dir}", Fore.CYAN)  # 添加數據目錄顯示
    write_color_output(f"時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Fore.CYAN)
    write_color_output(f"管理員權限: {'是' if is_admin else '否'}", Fore.CYAN)
    
    # 檢查配置文件中的TUN模式設置
    tun_enabled, tun_error = check_tun_config(config_path)
    if tun_enabled:
        write_color_output(f"TUN模式: 配置文件中已啟用", Fore.CYAN)
        if not is_admin:
            write_color_output("警告: TUN模式需要管理員權限才能正常工作，請以管理員身份運行此腳本", Fore.YELLOW)
    else:
        write_color_output(f"TUN模式: 未啟用 ({tun_error if tun_error else '配置文件中未指定'})", Fore.CYAN)
    
    write_color_output("=========================================", Fore.GREEN)
    
    # 檢查執行檔是否存在
    if not os.path.exists(exe_path):
        write_color_output(f"錯誤: Mihomo執行檔不存在: {exe_path}", Fore.RED)
        input("按任意鍵退出")
        return 1
        
    # 檢查配置文件是否存在
    if not os.path.exists(config_path):
        write_color_output(f"錯誤: 配置文件不存在: {config_path}", Fore.RED)
        input("按任意鍵退出")
        return 1
    
    # 檢查是否已經有mihomo實例在運行
    if is_process_running("mihomo-windows-amd64.exe"):
        write_color_output("警告: 發現Mihomo已在運行，繼續將啟動額外的實例", Fore.YELLOW)
        answer = input("是否繼續? (Y/N): ")
        if answer.lower() != 'y':
            write_color_output("操作已取消。", Fore.CYAN)
            return 0
      # 使用前台模式啟動Mihomo
    write_color_output("正在啟動Mihomo...", Fore.GREEN)
    write_color_output("在下方將顯示Mihomo的實時輸出...", Fore.YELLOW)
    write_color_output("要停止運行，請按 Ctrl+C", Fore.YELLOW)
    write_color_output("=========================================", Fore.GREEN)
    
    # TUN模式警告（如果配置文件啟用了TUN但沒有管理員權限）
    if tun_enabled and not is_admin:
        write_color_output("\n警告: 配置文件中啟用了TUN模式，但當前未以管理員身份運行", Fore.RED)
        write_color_output("TUN模式可能無法正常工作，請嘗試右鍵點擊此腳本並選擇「以管理員身份運行」", Fore.RED)
        answer = input("是否繼續啟動? (Y/N): ")
        if answer.lower() != 'y':
            write_color_output("操作已取消。", Fore.CYAN)
            return 0
    
    try:
        # 啟動進程 (使用標準的命令行參數)
        cmd = [exe_path, "-f", config_path, "-d", data_dir]  # 添加-d參數指定數據目錄
        
        # 根據源碼分析，mihomo不支持直接通過命令行啟用TUN模式
        # TUN模式必須在配置文件中配置，這裡只顯示相關信息
        if tun_enabled:
            write_color_output("使用配置文件中的TUN模式設置啟動Mihomo", Fore.GREEN)
            
        process = subprocess.Popen(cmd, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.STDOUT, 
                                   universal_newlines=True, 
                                   bufsize=1,
                                   encoding="utf-8",
                                   errors="replace")
        
        # 保存進程ID和記錄啟動信息
        pid = process.pid
        save_status_and_pid(pid)
        write_color_output(f"Mihomo已啟動，進程ID: {pid}", Fore.GREEN)
        
        # 設置Ctrl+C處理
        def signal_handler(sig, frame):
            write_color_output("\n進程被中斷，正在嘗試關閉Mihomo...", Fore.YELLOW)
            process.terminate()
            try:
                process.wait(timeout=5)  # 等待進程結束
                write_color_output("Mihomo已停止運行", Fore.RED)
                if os.path.exists(status_file_path):
                    os.remove(status_file_path)
            except subprocess.TimeoutExpired:
                write_color_output("Mihomo未能在超時時間內關閉，可能需要手動終止", Fore.RED)
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 即時顯示輸出
        for line in process.stdout:
            print(line, end='')
            sys.stdout.flush()
        
        # 等待進程結束
        return_code = process.wait()
        
        if return_code == 0:
            write_color_output("Mihomo正常退出", Fore.GREEN)
        else:
            write_color_output(f"Mihomo異常退出，返回碼: {return_code}", Fore.RED)
        
    except Exception as e:
        write_color_output(f"啟動Mihomo時發生錯誤: {str(e)}", Fore.RED)
        return 1
    finally:
        # 刪除PID檔案
        if os.path.exists(status_file_path):
            os.remove(status_file_path)
        # 保留控制台不立即關閉
        write_color_output("=========================================", Fore.GREEN)
        answer = input("按Enter鍵退出，或輸入 Y 重新啟動 Mihomo: ")
        if answer.strip().lower() == 'y':
            write_color_output("正在重新啟動 Mihomo...", Fore.GREEN)
            return main()  # 重新啟動
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        write_color_output("\n程序已中斷", Fore.YELLOW)
        sys.exit(0)
