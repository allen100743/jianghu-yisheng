"""
怡嘉發送 Telegram 訊息的工具
用法: python tools/send_telegram.py "訊息內容"
"""
import sys
import json
import urllib.request

TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID = "5129331122"

def send(text: str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": CHAT_ID, "text": text}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=10)
    print(f"已發送：{text[:50]}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python tools/send_telegram.py '訊息'")
        sys.exit(1)
    send(" ".join(sys.argv[1:]))
