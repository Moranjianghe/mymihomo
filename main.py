# -*- coding: utf-8 -*-
"""Mihomo 腳本統一入口。"""

from __future__ import annotations

import sys

from colorama import Fore

from common import run_python_script, write_color_output


MENU = [
    ("啟動 Mihomo", "start_visible.py"),
    ("更新 Mihomo 配置", "update_config.py"),
    ("下載/更新 Mihomo 核心", "download_mihomo.py"),
    ("下載/更新資料檔案", "download_mihomo_data.py"),
    ("下載 external-ui", "download_ui.py"),
    ("檢查/準備 TUN 模式", "setup_tun.py"),
    ("建立管理員捷徑", "create_shortcut.py"),
    ("查詢目前生效配置", "check_mihomo_config.py"),
]


def main() -> int:
    while True:
        write_color_output("\nMihomo 工具選單", Fore.GREEN)
        write_color_output("=========================================", Fore.GREEN)
        for index, (label, _) in enumerate(MENU, start=1):
            print(f"{index}. {label}")
        print("0. 離開")

        choice = input("請選擇操作: ").strip()
        if choice in {"0", "q", "Q"}:
            return 0
        if not choice.isdigit() or not 1 <= int(choice) <= len(MENU):
            write_color_output("無效選項，請重新輸入。", Fore.YELLOW)
            continue

        label, script_name = MENU[int(choice) - 1]
        write_color_output(f"\n正在執行：{label}", Fore.CYAN)
        result = run_python_script(script_name)
        if result == 120:
            write_color_output("已切換到管理員視窗，主選單退出。", Fore.GREEN)
            return 0
        write_color_output(f"操作結束，返回碼：{result}", Fore.CYAN if result == 0 else Fore.RED)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        write_color_output("\n操作已中斷", Fore.YELLOW)
        sys.exit(0)
