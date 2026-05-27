# -*- coding: utf-8 -*-
"""
自動下載 Mihomo 所需數據檔案（geoip.metadb、geosite.db）
"""
import os
from colorama import Fore, Style, init

from common import download_file_requests, get_runtime_paths, load_script_config

init()

def write_color_output(message, color=Fore.WHITE):
    print(f"{color}{message}{Style.RESET_ALL}")

def download_file(url, dest_path):
    try:
        download_file_requests(url, dest_path, config=load_script_config(required=False))
        write_color_output(f"下載完成: {os.path.basename(dest_path)}", Fore.GREEN)
        return True
    except Exception as e:
        write_color_output(f"下載失敗: {e}", Fore.RED)
        return False

def main():
    config = load_script_config(required=False)
    data_dir = str(get_runtime_paths(config)["data_dir"])
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    files = [
        {
            'name': 'geoip.metadb',
            'url': 'https://fastly.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/geoip.metadb'
        },
        {
            'name': 'geosite.db',
            'url': 'https://fastly.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/geosite.db'
        },
        {
            'name': 'geosite.dat',
            'url': 'https://github.com/MetaCubeX/meta-rules-dat/releases/download/latest/geosite.dat'
        }
    ]


    print("\n請選擇操作模式：")
    print("1. 僅下載缺失檔案（預設）")
    print("2. 強制全部重新下載/覆蓋")
    mode = input("請輸入 1 或 2，直接 Enter 採用預設: ").strip()
    force_update = (mode == '2')

    for fitem in files:
        dest = os.path.join(data_dir, fitem['name'])
        if os.path.exists(dest) and not force_update:
            write_color_output(f"已存在: {fitem['name']}，跳過下載。", Fore.YELLOW)
        else:
            if os.path.exists(dest) and force_update:
                write_color_output(f"已存在: {fitem['name']}，將重新下載並覆蓋。", Fore.CYAN)
            else:
                write_color_output(f"正在下載: {fitem['name']} ...", Fore.CYAN)
            download_file(fitem['url'], dest)

    write_color_output("所有數據檔案處理完畢。", Fore.GREEN)
    input("按 Enter 鍵退出...")

if __name__ == "__main__":
    main()
