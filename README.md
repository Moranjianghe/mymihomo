# Mihomo 脚本

## 專案簡介

本專案包含一系列腳本，便於日常使用 Mihomo 核心。

## 使用流程與腳本說明

### 1. 編輯配置文件

- **文件**：`script_config.yaml`
- **作用**：配置 Mihomo 相關路徑、UI 下載地址、數據目錄等，供各腳本讀取。
- **腳本介紹**：
  1. 複製 `script_config.example.yaml` 為 `script_config.yaml`。
  2. 根據實際需求修改各項參數（如 `core_file`、`config_file`、`data_dir` 等）。

### 2. 下載核心文件

- **腳本**：`download_mihomo.py`
- **功能**：自動下載 Mihomo 的核心執行檔，根據系統平台選擇適合的版本。
- **腳本介紹**：
  1. 執行腳本，腳本會自動判斷系統平台並下載對應的執行檔。
  2. 下載完成後，執行檔會存放於指定目錄中。

### 4. 設置 TUN 模式

- **腳本**：`setup_tun.py`
- **功能**：設置 Mihomo 的 TUN 模式，包含下載必要的驅動和配置。
- **腳本介紹**：
  1. 執行腳本，腳本會自動下載並配置所需的 TUN 驅動。
  2. 驅動安裝完成後，會自動設置相關參數。

### 5. 創建捷徑

- **腳本**：`create_shortcut.py`
- **功能**：適用於 Windows，自動創建一個啟動 `start_visible.py` 的捷徑，並設置為以管理員模執行。(TUN 模式需要管理員權限)
- **腳本介紹**：
  1. 執行腳本後，捷徑會自動生成於「開始選單」中。
  2. 捷徑名稱為 `Mihomo-Admin.lnk`。

### 6. 啟動服務

- **腳本**：`start_visible.py`
- **功能**：啟動 Mihomo 的前台服務，並加載相關配置。
- **腳本介紹**：
  1. 執行腳本，腳本會根據 `script_config.yaml` 中的配置啟動核心執行檔。
  2. TUN 模式需要管理員權限，可以使用 `start_admin.ps1`、`start_admin.bat`，或者上一步創建的快捷方式。

## 其它腳本

### 下載 UI 資源

- **腳本**：`download_ui.py`
- **功能**：自動下載並解壓 Mihomo 的外部 UI 資源。
- **腳本介紹**：
  1. 一般來說，mihomo 會自動下載 ui，但偶爾會出錯，可以嘗試使用這個腳本。
  2. 確保 `script_config.yaml` 中的 `config_file` 指向的配置檔（如 `config.yaml`）內，已正確設置 `external-ui-url` 和 `external-ui`。
  3. 執行腳本，腳本會根據該配置下載並解壓 UI 資源。

### 檢查配置

- **腳本**：`check_mihomo_config.py`
- **功能**：用於檢查 Mihomo 的當前配置。
- **腳本介紹**：
  1. 啟動腳本後，輸入 API 地址、端口和密碼（可選）。
  2. 腳本會嘗試連接 API 並顯示當前的配置內容。
  3. 可選擇將配置保存到本地檔案。

--

## 配置檔案範例

以下為 `script_config.yaml` 範例內容，請依實際需求修改：

```yaml
core_file: ./mihomo.exe
config_file: ./config.yaml
data_dir: ./data
```
