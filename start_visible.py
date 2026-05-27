# -*- coding: utf-8 -*-
# Mihomo前台啟動腳本 - Python版本

import os
import sys
import subprocess
import signal
import datetime
import ctypes
import json
from colorama import Fore, Style
from pathlib import Path

from common import (
    SCRIPT_DIR,
    get_default_data_config_path,
    get_effective_config_path,
    get_runtime_paths,
    is_tun_enabled,
    load_script_config,
    write_color_output,
)

# 定義檔案路徑
script_dir = str(SCRIPT_DIR)
script_config = load_script_config()
runtime_paths = get_runtime_paths(script_config)
exe_path = str(runtime_paths["core_file"])
config_path = get_effective_config_path(script_config)
data_dir = str(runtime_paths["data_dir"])
config_check_path = config_path or get_default_data_config_path(data_dir)

# 定義腳本緩存目錄
cache_dir = os.path.join(script_dir, "cache")
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

# 合併狀態與PID到一個檔案
status_file_path = os.path.join(cache_dir, "mihomo_status.json")

# 確保data目錄存在
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

def check_is_admin():
    """檢查是否以管理員權限運行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def relaunch_as_admin():
    """透過 UAC 重新以管理員權限啟動目前腳本"""
    script_path = os.path.abspath(__file__)
    args = subprocess.list2cmdline([script_path, *sys.argv[1:]])
    try:
        result = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            args,
            script_dir,
            1,
        )
        return result > 32
    except Exception as e:
        write_color_output(f"請求管理員權限失敗: {e}", Fore.RED)
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

def main():
    """主函數"""
    # 檢查是否以管理員權限運行（TUN模式需要管理員權限）
    is_admin = check_is_admin()
    
    # 顯示標題和設置
    write_color_output("Mihomo前台運行模式", Fore.GREEN)
    write_color_output("=========================================", Fore.GREEN)
    write_color_output(f"執行檔路徑: {exe_path}", Fore.CYAN)
    if config_path:
        write_color_output(f"配置文件: {config_path}", Fore.CYAN)
    else:
        write_color_output(
            f"配置文件: 未指定，啟動時不傳 -f；預檢會嘗試讀取 {config_check_path}",
            Fore.CYAN,
        )
    write_color_output(f"數據目錄: {data_dir}", Fore.CYAN)  # 添加數據目錄顯示
    write_color_output(f"時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Fore.CYAN)
    write_color_output(f"管理員權限: {'是' if is_admin else '否'}", Fore.CYAN)
    
    # 檢查配置文件中的TUN模式設置
    if config_check_path and os.path.exists(config_check_path):
        tun_enabled, tun_error = is_tun_enabled(config_check_path)
        if tun_enabled:
            write_color_output(f"TUN模式: 配置文件中已啟用 ({config_check_path})", Fore.CYAN)
            if not is_admin:
                write_color_output("警告: TUN模式需要管理員權限才能正常工作，請以管理員身份運行此腳本", Fore.YELLOW)
                answer = input("是否重新以管理員權限啟動? (Y/N): ")
                if answer.lower() == 'y':
                    if relaunch_as_admin():
                        write_color_output("已發出管理員權限啟動請求，當前視窗將退出。", Fore.GREEN)
                        return 120
                    write_color_output("無法自動請求管理員權限，將繼續目前流程。", Fore.RED)
        else:
            write_color_output(f"TUN模式: 未啟用 ({tun_error if tun_error else '配置文件中未指定'})", Fore.CYAN)
    else:
        tun_enabled = False
        write_color_output(f"TUN模式: 未檢查（找不到預檢配置 {config_check_path}）", Fore.CYAN)
    
    write_color_output("=========================================", Fore.GREEN)
    
    # 檢查執行檔是否存在
    if not os.path.exists(exe_path):
        write_color_output(f"錯誤: Mihomo執行檔不存在: {exe_path}", Fore.RED)
        input("按任意鍵退出")
        return 1
        
    # 檢查配置文件是否存在
    if config_path and not os.path.exists(config_path):
        write_color_output(f"錯誤: 配置文件不存在: {config_path}", Fore.RED)
        input("按任意鍵退出")
        return 1
    
    # 檢查是否已經有mihomo實例在運行
    process_name = Path(exe_path).name
    if is_process_running(process_name):
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
        write_color_output("TUN模式可能無法正常工作，建議重新以管理員身份運行。", Fore.RED)
        answer = input("是否繼續啟動? (Y/N): ")
        if answer.lower() != 'y':
            write_color_output("操作已取消。", Fore.CYAN)
            return 0
    
    try:
        # 啟動進程 (使用標準的命令行參數)
        cmd = [exe_path, "-d", data_dir]
        if config_path:
            cmd.extend(["-f", str(config_path)])
        
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
