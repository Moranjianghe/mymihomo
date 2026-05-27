# -*- coding: utf-8 -*-
"""下載並更新 Mihomo 配置檔。"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from colorama import Fore

from common import (
    download_file_requests,
    get_default_data_config_path,
    get_effective_config_path,
    get_runtime_paths,
    load_script_config,
    write_color_output,
)


def get_config_url(config: dict) -> str | None:
    url = config.get("config_url") or config.get("subscription_url")
    if isinstance(url, str) and url.strip():
        return url.strip()
    return None


def validate_config(core_file: Path, config_file: Path, data_dir: Path) -> bool:
    if not core_file.exists():
        write_color_output("未找到 Mihomo 核心，跳過配置檢查。", Fore.YELLOW)
        return True

    data_dir.mkdir(parents=True, exist_ok=True)
    cmd = [str(core_file), "-t", "-f", str(config_file), "-d", str(data_dir)]
    write_color_output("正在使用 Mihomo 核心檢查新配置...", Fore.CYAN)
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.stdout.strip():
        print(result.stdout)
    if result.returncode == 0:
        write_color_output("配置檢查通過。", Fore.GREEN)
        return True

    write_color_output(f"配置檢查失敗，返回碼：{result.returncode}", Fore.RED)
    return False


def backup_existing_config(config_file: Path) -> Path | None:
    if not config_file.exists():
        return None

    backup_dir = config_file.parent / "backup"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = backup_dir / f"{config_file.name}.{timestamp}.bak"
    shutil.copy2(config_file, backup_path)
    return backup_path


def main() -> int:
    script_config = load_script_config(required=False)
    config_url = get_config_url(script_config)
    if not config_url:
        write_color_output(
            "未設定 config_url。請在 script_config.yaml 加入配置訂閱地址，例如：",
            Fore.RED,
        )
        print("config_url: https://example.com/your-subscription")
        return 1

    paths = get_runtime_paths(script_config)
    core_file = paths["core_file"]
    data_dir = paths["data_dir"]
    config_file = get_effective_config_path(script_config) or get_default_data_config_path(data_dir)
    config_file.parent.mkdir(parents=True, exist_ok=True)

    fd, temp_name = tempfile.mkstemp(
        prefix=config_file.name + ".",
        suffix=".download",
        dir=config_file.parent,
    )
    os.close(fd)
    temp_config = Path(temp_name)

    try:
        write_color_output(f"正在下載配置：{config_url}", Fore.CYAN)
        download_file_requests(config_url, temp_config, config=script_config)

        if temp_config.stat().st_size == 0:
            write_color_output("下載到的配置檔為空，已取消更新。", Fore.RED)
            return 1

        if not validate_config(core_file, temp_config, data_dir):
            write_color_output("新配置未替換原配置。", Fore.RED)
            return 1

        backup_path = backup_existing_config(config_file)
        if backup_path:
            write_color_output(f"已備份原配置：{backup_path}", Fore.GREEN)

        os.replace(temp_config, config_file)
        write_color_output(f"配置已更新：{config_file}", Fore.GREEN)
        return 0
    except Exception as e:
        write_color_output(f"更新配置失敗：{e}", Fore.RED)
        return 1
    finally:
        if temp_config.exists():
            temp_config.unlink()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        write_color_output("\n操作已中斷", Fore.YELLOW)
        sys.exit(0)
