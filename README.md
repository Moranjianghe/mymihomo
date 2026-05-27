# Mihomo 輔助腳本

## 專案簡介

這個專案是一組 Windows 上使用 Mihomo / Clash Meta 核心的輔助腳本，用來下載核心、更新資料檔案、準備 TUN 模式、下載 external-ui、建立管理員捷徑，以及以前台方式啟動 Mihomo。

真正的代理規則與節點配置不在本專案內。可以由 `script_config.yaml` 的 `config_file` 明確指定，也可以留空，交由 Mihomo 在 `data_dir` 中使用預設配置。

## 安裝依賴

首次使用請先安裝 Python 依賴：

```powershell
pip install -r requirements.txt
```

本專案不再在腳本內自動安裝 Python 套件，避免修改錯誤的 Python 環境。

## 首次設定

下載核心、下載資料檔案與查詢 API 可以在沒有 `script_config.yaml` 時使用預設路徑；啟動 Mihomo、檢查 TUN 與下載 external-ui 建議先建立配置檔，避免使用錯誤的核心或配置路徑。

複製範例配置：

```powershell
Copy-Item script_config.example.yaml script_config.yaml
```

依實際環境修改 `script_config.yaml`：

```yaml
core_file: ./mihomo.exe
# 可留空。留空時啟動 Mihomo 不傳 -f，讓 Mihomo 自行在 data_dir 尋找預設配置。
# update_config.py 會把配置更新到 data_dir/config.yaml。
config_file: F:/data/clash.yaml
data_dir: ./data
# 可選：Mihomo 配置訂閱地址，用於 update_config.py
# config_url: https://example.com/your-subscription
# 下載 GitHub 資源較慢時可啟用，例如 v2rayN 混合代理：
# proxy: http://127.0.0.1:10808
```

欄位說明：

- `core_file`：Mihomo 核心執行檔路徑。
- `config_file`：Mihomo 配置檔路徑。可留空；留空時啟動腳本不傳 `-f`，只傳 `-d data_dir`，讓 Mihomo 自行在資料目錄尋找預設配置。
- `data_dir`：Mihomo 資料目錄。
- `config_url`：可選配置訂閱地址，用於下載並更新配置。若 `config_file` 留空，會更新到 `data_dir/config.yaml`。
- `proxy`：可選下載代理。若使用 v2rayN 混合代理，通常可設為 `http://127.0.0.1:10808`。

## 統一入口

建議日常使用統一入口：

```powershell
python main.py
```

選單包含：

1. 啟動 Mihomo
2. 更新 Mihomo 配置
3. 下載/更新 Mihomo 核心
4. 下載/更新資料檔案
5. 下載 external-ui
6. 檢查/準備 TUN 模式
7. 建立管理員捷徑
8. 查詢目前生效配置

## 腳本說明

### `update_config.py`

從 `script_config.yaml` 的 `config_url` 下載 Mihomo 配置，更新到 `config_file` 指定位置。若 `config_file` 留空，會更新到 `data_dir/config.yaml`。

更新流程：

1. 先下載到臨時檔。
2. 若找到 `core_file`，會執行 `mihomo -t -f 新配置 -d data_dir` 檢查配置。
3. 檢查通過後，備份原配置到配置檔同目錄下的 `backup` 資料夾。
4. 使用新配置替換原配置。

如果未找到 Mihomo 核心，腳本會跳過配置檢查，但仍會更新配置。

### `download_mihomo.py`

查詢 MetaCubeX/mihomo 的 GitHub 最新版本，依目前系統架構下載對應核心壓縮包，解壓後放到 `script_config.yaml` 的 `core_file` 指定位置。

### `download_mihomo_data.py`

下載 Mihomo 常用資料檔案到 `data_dir`：

- `geoip.metadb`
- `geosite.db`
- `geosite.dat`

可選擇只下載缺失檔案，或強制覆蓋更新。

### `download_ui.py`

讀取 Mihomo 配置檔中的 `external-ui-url` 與 `external-ui`，下載並解壓 external-ui。當 Mihomo 自動下載 UI 失敗時可以手動執行。

### `setup_tun.py`

檢查 TUN 模式配置與 WinTUN 狀態，必要時可下載並安裝 WinTUN。TUN 模式通常需要管理員權限。

TUN 配置檢查會解析 YAML，不再依賴純文字搜尋，因此能更準確判斷 `tun.enable` 是否為 `true`。

### `start_visible.py`

以前台方式啟動 Mihomo：

```powershell
python start_visible.py
```

腳本會使用：

```powershell
mihomo.exe -f config.yaml -d data
```

實際路徑由 `script_config.yaml` 決定。若 `config_file` 留空，啟動腳本會改為只傳 `-d data_dir`，不傳 `-f`，讓 Mihomo 自行在資料目錄尋找預設配置。

若配置中啟用了 TUN 但目前不是管理員權限，啟動腳本會提示是否透過 UAC 重新以管理員權限啟動。當 `config_file` 留空時，啟動腳本仍不傳 `-f`，但會嘗試預檢 `data_dir/config.yaml` 來判斷是否啟用 TUN。

### `create_shortcut.py`

在開始選單建立 `Mihomo-Admin.lnk`，並設定為以管理員身份執行。此腳本需要 `pywin32`。

### `check_mihomo_config.py`

透過 Mihomo REST API 查詢目前生效配置，預設連線到：

```text
http://127.0.0.1:9090/configs
```

如有設定 API secret，請依提示輸入。

## 管理員啟動

TUN 模式建議使用管理員權限啟動，可使用：

```powershell
.\start_admin.ps1
```

或：

```bat
start_admin.bat
```

也可以執行 `create_shortcut.py` 後，從開始選單使用 `Mihomo-Admin.lnk` 啟動。

## 常見問題

### 找不到 `script_config.yaml`

請先複製範例檔：

```powershell
Copy-Item script_config.example.yaml script_config.yaml
```

### GitHub 下載失敗或速度很慢

可以在 `script_config.yaml` 加入：

```yaml
proxy: http://127.0.0.1:10808
```

如果不需要代理，刪除這一行即可。

### 已啟用 TUN 但無法工作

請確認：

- 使用管理員權限啟動 Mihomo。
- `setup_tun.py` 檢查 WinTUN 狀態正常。
- Mihomo 配置檔內 `tun.enable` 為 `true`。
