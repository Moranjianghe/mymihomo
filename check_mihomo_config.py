# -*- coding: utf-8 -*-
import requests

def main():
    print("Mihomo 配置查詢工具")
    api_host = input("API 地址 (預設 127.0.0.1): ").strip() or "127.0.0.1"
    api_port = input("API 端口 (預設 9090): ").strip() or "9090"
    api_secret = input("API 密碼 (如無可留空): ").strip()
    api_url = f"http://{api_host}:{api_port}/configs"
    headers = {"Authorization": f"Bearer {api_secret}"} if api_secret else {}
    print(f"\n正在請求 {api_url} ...")
    try:
        resp = requests.get(api_url, headers=headers, timeout=5)
        if resp.status_code == 200:
            print("\nMihomo 當前生效配置如下（前500字）：\n")
            print(resp.text[:500])
            save = input("\n是否將配置內容保存到本地檔案？(Y/N): ").strip().lower()
            if save == 'y':
                save_path = input("請輸入保存檔案名（預設 output_config.yaml）: ").strip() or "output_config.yaml"
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(resp.text)
                print(f"已保存到 {save_path}")
        else:
            print(f"API 請求失敗，狀態碼: {resp.status_code}")
            print("響應內容：", resp.text)
    except Exception as e:
        print("無法連接 Mihomo API，請確認 Mihomo 已啟動且 API 端口與密碼正確。")
        print("錯誤詳情：", e)

if __name__ == "__main__":
    main()
