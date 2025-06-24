# -*- coding: utf-8 -*-
"""
自動下載 Mihomo Windows 核心腳本
"""
import os
import sys
import requests
import shutil
import platform
import zipfile

def get_platform_asset_name():
    system = platform.system().lower()
    machine = platform.machine().lower()
    # Windows
    if system == 'windows':
        if 'arm' in machine:
            return 'mihomo-windows-arm64.exe'
        elif '64' in machine or machine == 'amd64' or machine == 'x86_64':
            return 'mihomo-windows-amd64.exe'
        else:
            return 'mihomo-windows-386.exe'
    # Linux
    elif system == 'linux':
        if 'arm' in machine and '64' in machine:
            return 'mihomo-linux-arm64'
        elif 'arm' in machine:
            return 'mihomo-linux-armv7'
        elif '64' in machine or machine == 'amd64' or machine == 'x86_64':
            return 'mihomo-linux-amd64'
        else:
            return 'mihomo-linux-386'
    # macOS
    elif system == 'darwin':
        if 'arm' in machine:
            return 'mihomo-darwin-arm64'
        else:
            return 'mihomo-darwin-amd64'
    else:
        return None

def get_latest_release_download_url():
    api_url = "https://api.github.com/repos/MetaCubeX/mihomo/releases/latest"
    asset_name_hint = get_platform_asset_name()
    if not asset_name_hint:
        print("不支援的作業系統或架構。")
        return None, None
    try:
        resp = requests.get(api_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        tag = data.get("tag_name", "")
        # 優先尋找純正規範名稱（不含 compatible/goXXX）
        preferred_name = asset_name_hint.replace('.exe','') + f'-{tag}.zip'
        for asset in data.get("assets", []):
            name = asset.get("name", "")
            if name == preferred_name:
                return asset["browser_download_url"], name
        # 其次尋找不含 compatible/go 的 zip
        for asset in data.get("assets", []):
            name = asset.get("name", "")
            if asset_name_hint.replace('.exe','') in name and name.endswith(f'-{tag}.zip') and 'compatible' not in name and '-go' not in name:
                return asset["browser_download_url"], name
        # 再其次，尋找任何包含 asset_name_hint 的 zip
        for asset in data.get("assets", []):
            name = asset.get("name", "")
            if asset_name_hint.replace('.exe','') in name and name.endswith(".zip"):
                return asset["browser_download_url"], name
        print(f"未找到對應平台的下載連結: {asset_name_hint}")
        return None, asset_name_hint
    except Exception as e:
        print(f"獲取最新版本資訊失敗: {e}")
        return None, asset_name_hint

def download_file(url, dest_path):
    try:
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(dest_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        return True
    except Exception as e:
        print(f"下載失敗: {e}")
        return False

def main():
    print("正在查詢 Mihomo 最新版本...")
    url, asset_name = get_latest_release_download_url()
    if not url:
        print(f"無法獲取下載連結（{asset_name}），請稍後再試。")
        return 1
    dest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), asset_name)
    print(f"下載連結: {url}")
    print(f"將下載到: {dest_path}")
    if os.path.exists(dest_path):
        print("檔案已存在，將覆蓋舊檔...")
    print("開始下載...")
    if download_file(url, dest_path):
        print(f"下載完成: {asset_name}")
        # 自動解壓並只保留 exe
        if asset_name.endswith('.zip'):
            import tempfile
            temp_dir = tempfile.mkdtemp(dir=os.path.dirname(os.path.abspath(__file__)))
            try:
                with zipfile.ZipFile(dest_path, 'r') as zip_ref:
                    exe_files = [f for f in zip_ref.namelist() if f.endswith('.exe')]
                    if not exe_files:
                        print('壓縮包中未找到 exe 檔案')
                    for f in exe_files:
                        zip_ref.extract(f, temp_dir)
                        print(f"已解壓: {f}")
                # 刪除 zip
                os.remove(dest_path)
                print(f"已刪除壓縮包: {asset_name}")
                # 移動 exe 到腳本目錄（如果在子目錄）
                for f in exe_files:
                    src = os.path.join(temp_dir, f)
                    # 目標名稱統一為 config/core_exe 或預設名
                    from pathlib import Path
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    # 嘗試讀取 script_config.yaml
                    config_path = os.path.join(script_dir, "script_config.yaml")
                    exe_dst = None
                    if os.path.exists(config_path):
                        import yaml
                        with open(config_path, 'r', encoding='utf-8') as cf:
                            config = yaml.safe_load(cf)
                        exe_dst = config.get('core_file')
                        if exe_dst and not os.path.isabs(exe_dst):
                            exe_dst = os.path.normpath(os.path.join(script_dir, exe_dst))
                        elif exe_dst:
                            exe_dst = os.path.normpath(exe_dst)
                    if not exe_dst:
                        exe_dst = os.path.join(script_dir, os.path.basename(f))
                    if os.path.exists(exe_dst):
                        os.remove(exe_dst)
                    shutil.move(src, exe_dst)
                    print(f"已移動 {src} 到 {exe_dst}")
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"自動解壓失敗: {e}")
    else:
        print("下載失敗。請檢查網路連線或稍後再試。")

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("缺少 requests 模組，正在自動安裝...")
        os.system(f'{sys.executable} -m pip install requests')
    main()
