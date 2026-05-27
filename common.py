# -*- coding: utf-8 -*-
"""Mihomo 腳本共用工具。"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

import requests
import yaml
from colorama import Fore, Style, init

init()

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPT_CONFIG_PATH = SCRIPT_DIR / "script_config.yaml"
SCRIPT_CONFIG_EXAMPLE_PATH = SCRIPT_DIR / "script_config.example.yaml"


def write_color_output(message: str, color: str = Fore.WHITE) -> None:
    print(f"{color}{message}{Style.RESET_ALL}")


def fail(message: str, exit_code: int = 1) -> None:
    write_color_output(message, Fore.RED)
    raise SystemExit(exit_code)


def ensure_script_config_exists() -> None:
    if SCRIPT_CONFIG_PATH.exists():
        return

    example_hint = (
        f"請先複製 {SCRIPT_CONFIG_EXAMPLE_PATH.name} 為 {SCRIPT_CONFIG_PATH.name}，"
        "再依實際環境修改 core_file、config_file、data_dir。"
    )
    fail(f"找不到 {SCRIPT_CONFIG_PATH}\n{example_hint}")


def load_yaml_file(path: os.PathLike[str] | str, default: Any = None) -> Any:
    path = Path(path)
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return default if data is None else data


def load_script_config(*, required: bool = True) -> dict[str, Any]:
    if required:
        ensure_script_config_exists()
    elif not SCRIPT_CONFIG_PATH.exists():
        return {}
    data = load_yaml_file(SCRIPT_CONFIG_PATH, {})
    if not isinstance(data, dict):
        fail(f"{SCRIPT_CONFIG_PATH} 格式錯誤：頂層內容必須是 YAML 物件。")
    return data


def resolve_path(value: str | os.PathLike[str] | None, default: str) -> Path:
    raw = Path(value or default)
    if not raw.is_absolute():
        raw = SCRIPT_DIR / raw
    return raw.resolve()


def get_runtime_paths(config: dict[str, Any] | None = None) -> dict[str, Path]:
    if config is None:
        config = load_script_config()
    return {
        "core_file": resolve_path(config.get("core_file"), "mihomo.exe"),
        "config_file": resolve_path(config.get("config_file"), "config.yaml"),
        "data_dir": resolve_path(config.get("data_dir"), "data"),
    }


def get_optional_path(config: dict[str, Any], key: str) -> Path | None:
    value = config.get(key)
    if not isinstance(value, str) or not value.strip():
        return None
    return resolve_path(value.strip(), "")


def get_effective_config_path(config: dict[str, Any] | None = None) -> Path | None:
    if config is None:
        config = load_script_config(required=False)
    return get_optional_path(config, "config_file")


def get_default_data_config_path(data_dir: os.PathLike[str] | str) -> Path:
    return Path(data_dir) / "config.yaml"


def get_proxy_url(config: dict[str, Any] | None = None) -> str | None:
    config = config or load_script_config()
    proxy = config.get("proxy") or config.get("download_proxy")
    if proxy is False:
        return None
    if isinstance(proxy, str) and proxy.strip():
        return proxy.strip()
    env_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
    return env_proxy.strip() if env_proxy else None


def get_requests_proxies(config: dict[str, Any] | None = None) -> dict[str, str] | None:
    proxy = get_proxy_url(config)
    if not proxy:
        return None
    return {"http": proxy, "https": proxy}


def build_url_opener(config: dict[str, Any] | None = None) -> urllib.request.OpenerDirector:
    proxy = get_proxy_url(config)
    if not proxy:
        return urllib.request.build_opener()
    return urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": proxy, "https": proxy})
    )


def download_file_requests(
    url: str,
    dest_path: os.PathLike[str] | str,
    *,
    config: dict[str, Any] | None = None,
    timeout: int = 30,
) -> bool:
    dest = Path(dest_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp_fd, temp_name = tempfile.mkstemp(prefix=dest.name + ".", suffix=".tmp", dir=dest.parent)
    os.close(temp_fd)
    temp_path = Path(temp_name)
    try:
        with requests.get(
            url,
            stream=True,
            timeout=timeout,
            proxies=get_requests_proxies(config),
        ) as response:
            response.raise_for_status()
            with temp_path.open("wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 256):
                    if chunk:
                        f.write(chunk)
        os.replace(temp_path, dest)
        return True
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise


def download_file_urllib(
    url: str,
    dest_path: os.PathLike[str] | str,
    *,
    config: dict[str, Any] | None = None,
    timeout: int = 30,
) -> bool:
    dest = Path(dest_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp_fd, temp_name = tempfile.mkstemp(prefix=dest.name + ".", suffix=".tmp", dir=dest.parent)
    os.close(temp_fd)
    temp_path = Path(temp_name)
    try:
        opener = build_url_opener(config)
        with opener.open(url, timeout=timeout) as response, temp_path.open("wb") as f:
            shutil.copyfileobj(response, f)
        os.replace(temp_path, dest)
        return True
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise


def parse_mihomo_config(config_path: os.PathLike[str] | str) -> dict[str, Any]:
    data = load_yaml_file(config_path, {})
    if not isinstance(data, dict):
        return {}
    return data


def get_tun_config(config_path: os.PathLike[str] | str) -> dict[str, Any]:
    config = parse_mihomo_config(config_path)
    tun = config.get("tun")
    return tun if isinstance(tun, dict) else {}


def is_tun_enabled(config_path: os.PathLike[str] | str) -> tuple[bool, str | None]:
    path = Path(config_path)
    if not path.exists():
        return False, "配置檔案不存在"
    tun = get_tun_config(path)
    if not tun:
        return False, "配置檔案中未設定 TUN 模式"
    if tun.get("enable") is True:
        return True, None
    return False, "TUN 模式存在但未啟用"


def run_python_script(script_name: str) -> int:
    env = os.environ.copy()
    env["MIHOMO_CHILD_SCRIPT"] = script_name
    return subprocess.call([sys.executable, str(SCRIPT_DIR / script_name)], env=env)
