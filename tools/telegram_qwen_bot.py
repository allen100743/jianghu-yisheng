"""
Telegram 接收中繼 Bot
只負責接收訊息、寫入檔案，由 telegram_watcher.py 負責回應
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
import os
import time
import datetime
import urllib.request
import urllib.error

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = "5129331122"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
NOTES_FILE   = os.path.join(SCRIPT_DIR, "telegram_notes.md")
INCOMING_FILE = os.path.join(SCRIPT_DIR, "telegram_incoming.md")
IMAGES_DIR   = os.path.join(SCRIPT_DIR, "telegram_images")


def save_note(content: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n## {timestamp}\n{content}\n")


def write_incoming(text: str):
    """寫入新訊息供 watcher 處理"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(INCOMING_FILE, "w", encoding="utf-8") as f:
        f.write(f"{timestamp}\n{text}")


def get_updates(offset=None):
    url = f"{TELEGRAM_API}/getUpdates?timeout=30"
    if offset:
        url += f"&offset={offset}"
    try:
        resp = urllib.request.urlopen(url, timeout=35)
        return json.loads(resp.read())
    except Exception:
        return None


def send_message(text: str):
    url = f"{TELEGRAM_API}/sendMessage"
    body = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"發送失敗：{e}")


def download_photo(photo_sizes: list) -> str:
    """下載最高解析度截圖到 telegram_images/，回傳本地路徑"""
    os.makedirs(IMAGES_DIR, exist_ok=True)
    # Telegram 圖片陣列按解析度排列，最後一個最大
    file_id = photo_sizes[-1]["file_id"]

    # 1. 取得檔案路徑
    url = f"{TELEGRAM_API}/getFile?file_id={file_id}"
    try:
        resp = urllib.request.urlopen(url, timeout=10)
        data = json.loads(resp.read())
        file_path = data["result"]["file_path"]
    except Exception as e:
        print(f"getFile 失敗：{e}")
        return ""

    # 2. 下載圖片
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = file_path.split(".")[-1] if "." in file_path else "jpg"
    local_path = os.path.join(IMAGES_DIR, f"{ts}.{ext}")
    download_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
    try:
        urllib.request.urlretrieve(download_url, local_path)
        print(f"圖片已下載：{local_path}")
        return local_path
    except Exception as e:
        print(f"下載失敗：{e}")
        return ""


def answer_callback_query(callback_query_id: str):
    """回應按鈕點擊，停止 Telegram 的載入轉圈"""
    url = f"{TELEGRAM_API}/answerCallbackQuery"
    body = {"callback_query_id": callback_query_id}
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


def main():
    print("Telegram 中繼 Bot 啟動")
    send_message("🔗 中繼上線，怡嘉助理已就緒。")

    offset = None
    while True:
        try:
            updates = get_updates(offset)
            if not updates or not updates.get("ok"):
                time.sleep(5)
                continue

            for update in updates.get("result", []):
                offset = update["update_id"] + 1

                # ── Inline Keyboard 按鈕回調 ──────────────────────────────
                if "callback_query" in update:
                    cq = update["callback_query"]
                    answer_callback_query(cq["id"])
                    chat_id = str(cq.get("message", {}).get("chat", {}).get("id", ""))
                    action = cq.get("data", "").strip()
                    if chat_id == TELEGRAM_CHAT_ID and action:
                        print(f"按鈕動作：{action}")
                        write_incoming(f"[ACTION]{action}")
                        send_message(f"收到：{action}，怡嘉處理中...")
                    continue

                # ── 一般訊息 ─────────────────────────────────────────────
                msg = update.get("message", {})
                chat_id = str(msg.get("chat", {}).get("id", ""))

                if chat_id != TELEGRAM_CHAT_ID:
                    continue

                # 圖片訊息（下載後升交怡嘉）
                if msg.get("photo"):
                    caption = msg.get("caption", "").strip()
                    print(f"收到圖片，下載中...")
                    send_message("收到截圖，下載中，移交怡嘉查看...")
                    local_path = download_photo(msg["photo"])
                    if local_path:
                        write_incoming(f"[IMAGE:{local_path}]{caption}")
                    else:
                        write_incoming(f"[IMAGE:]{caption or '（截圖下載失敗）'}")
                    continue

                text = msg.get("text", "").strip()
                if not text:
                    continue

                print(f"收到：{text[:50]}")

                # 清除記憶指令
                if text in ["/clear", "/清除", "清除記憶"]:
                    history_file = os.path.join(SCRIPT_DIR, "conversation_history.json")
                    if os.path.exists(history_file):
                        os.remove(history_file)
                    send_message("🗑️ 對話記憶已清除。")
                    continue

                # 記錄筆記指令
                note_triggers = ["記下來", "告訴怡嘉", "記住", "筆記"]
                if any(t in text for t in note_triggers):
                    save_note(f"製作人：{text}")
                    send_message("✅ 已記錄，怡嘉下次開 VS Code 會看到。")
                    continue

                # 一般訊息：寫入轉傳檔，等 watcher 回應
                write_incoming(f"[TG]{text}")
                send_message("⏳ 收到，青霞正在回應...")

        except Exception as e:
            print(f"錯誤：{e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
