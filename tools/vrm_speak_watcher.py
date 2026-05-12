"""
VRM 說話 Watcher
監看 vrm_speak.md，有內容就叫怡嘉說出來
"""
import os
import time
import urllib.request
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SPEAK_FILE = os.path.join(SCRIPT_DIR, "vrm_speak.md")
API_URL = "http://localhost:3000/api/speak_text/"
POLL_INTERVAL = 2


def speak(text: str):
    payload = json.dumps({"text": text, "speakerId": 1}).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req, timeout=30)
        print(f"說話：{text[:40]}")
    except Exception as e:
        print(f"說話失敗：{e}")


def check_speak_file() -> str:
    if not os.path.exists(SPEAK_FILE):
        return ""
    try:
        with open(SPEAK_FILE, "r+", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                f.seek(0)
                f.truncate()
        return content
    except Exception:
        return ""


def main():
    print("VRM Speak Watcher 啟動...")
    while True:
        try:
            text = check_speak_file()
            if text:
                speak(text)
            time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"錯誤：{e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
