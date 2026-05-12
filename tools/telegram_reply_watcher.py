"""
Telegram 回覆 Watcher
監看 telegram_reply.md，有內容就發回 Telegram
"""
import os

# 載入本地設定（local_config.py 優先，env var 次之）
try:
    import sys as _sys, os as _os
    _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
    from local_config import TELEGRAM_TOKEN as _LC_TG, TELEGRAM_CHAT_ID as _LC_CID, DEEPSEEK_API_KEY as _LC_DS
    import os as _osenv
    if not _osenv.environ.get('TELEGRAM_TOKEN'): _osenv.environ['TELEGRAM_TOKEN'] = _LC_TG
    if not _osenv.environ.get('TELEGRAM_CHAT_ID'): _osenv.environ['TELEGRAM_CHAT_ID'] = _LC_CID
    if not _osenv.environ.get('DEEPSEEK_API_KEY'): _osenv.environ['DEEPSEEK_API_KEY'] = _LC_DS
except ImportError:
    pass

import time
import json
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPLY_FILE = os.path.join(SCRIPT_DIR, "telegram_reply.md")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = "5129331122"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
POLL_INTERVAL = 2


def send_telegram(text: str):
    url = f"{TELEGRAM_API}/sendMessage"
    body = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
        print(f"已發送 Telegram：{text[:40]}")
    except Exception as e:
        print(f"Telegram 發送失敗：{e}")


def check_reply_file() -> str:
    if not os.path.exists(REPLY_FILE):
        return ""
    try:
        with open(REPLY_FILE, "r+", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                f.seek(0)
                f.truncate()
        return content
    except Exception:
        return ""


def main():
    print("Telegram Reply Watcher 啟動...")
    while True:
        try:
            text = check_reply_file()
            if text:
                send_telegram(text)
            time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"錯誤：{e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
