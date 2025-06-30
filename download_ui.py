# -*- coding: utf-8 -*-
"""
這是一個自動下載並解壓 Mihomo external-ui 的腳本
如果 mihomo 無法正常下載 external-ui，則可以使用此手動重試
"""
import os
import yaml
import urllib.request
import zipfile
import shutil
from colorama import Fore, Style, init

init()

def write_color_output(message, color=Fore.WHITE):
    print(f"{color}{message}{Style.RESET_ALL}")

def download_and_extract_ui(config_path, script_dir):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        ui_url = config.get('external-ui-url')
        ui_dir = config.get('external-ui')
        if not ui_url or not ui_dir:
            write_color_output("未設置 external-ui-url 或 external-ui，跳過 UI 下載。", Fore.YELLOW)
            return
        # 處理 external-ui 路徑（相對於 data_dir 或絕對路徑）
        SCRIPT_CONFIG_PATH = os.path.join(script_dir, "script_config.yaml")
        with open(SCRIPT_CONFIG_PATH, 'r', encoding='utf-8') as f2:
            script_config = yaml.safe_load(f2)
        data_dir = script_config.get('data_dir', script_dir)
        data_dir = os.path.normpath(os.path.join(script_dir, data_dir)) if not os.path.isabs(data_dir) else os.path.normpath(data_dir)
        if not os.path.isabs(ui_dir):
            ui_dir = os.path.join(data_dir, ui_dir)
        ui_dir = os.path.normpath(ui_dir)
        # 使用臨時目錄解壓
        import tempfile
        temp_dir = tempfile.mkdtemp(dir=script_dir)
        tmp_zip = os.path.join(script_dir, "ui_tmp.zip")
        write_color_output(f"正在下載 UI: {ui_url}", Fore.YELLOW)
        urllib.request.urlretrieve(ui_url, tmp_zip)
        write_color_output(f"下載完成，正在解壓到臨時目錄: {temp_dir}", Fore.YELLOW)
        with zipfile.ZipFile(tmp_zip, 'r') as zip_ref:
            members = zip_ref.namelist()
            top_level = os.path.commonprefix(members).split('/')[0]
            for member in members:
                target = member
                if member.startswith(top_level + '/'):
                    target = member[len(top_level)+1:]
                if target:
                    dest_path = os.path.join(temp_dir, target)
                    if member.endswith('/'):
                        if not os.path.exists(dest_path):
                            os.makedirs(dest_path)
                    else:
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        with zip_ref.open(member) as source, open(dest_path, 'wb') as target_file:
                            shutil.copyfileobj(source, target_file)
        os.remove(tmp_zip)
        # 移動到目標目錄（先刪除原有目錄)
        if os.path.exists(ui_dir):
            shutil.rmtree(ui_dir)
        shutil.move(temp_dir, ui_dir)
        write_color_output(f"UI 已解壓到: {ui_dir}", Fore.GREEN)
    except Exception as e:
        write_color_output(f"UI 下載或解壓失敗: {e}", Fore.RED)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # 統一讀取 script_config.yaml
    SCRIPT_CONFIG_PATH = os.path.join(script_dir, "script_config.yaml")
    with open(SCRIPT_CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    config_path = config['config_file']
    download_and_extract_ui(config_path, script_dir)
    input("\n按 Enter 鍵退出...")
