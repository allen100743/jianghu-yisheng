"""
怡嘉 Telegram Watcher
監看 telegram_incoming.md，優先由青霞（Ollama qwen2.5:32b）自主回應。
青霞失敗或主動要求時，才通知怡嘉（VS Code Claude）接手。
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
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
import urllib.request
import urllib.error
import pyautogui
import pyperclip
import win32gui
import win32con
import win32api
import win32process
import ctypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = "5129331122"
OLLAMA_URL     = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL   = "qwen2.5:32b"
OLLAMA_TIMEOUT = 90   # 秒，超過視為失敗
TELEGRAM_API   = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
INCOMING_FILE = os.path.join(SCRIPT_DIR, "telegram_incoming.md")
HISTORY_FILE  = os.path.join(SCRIPT_DIR, "conversation_history.json")
CONTEXT_DIR   = os.path.join(SCRIPT_DIR, "qingxia_context")

POLL_INTERVAL = 5   # 每5秒輪詢一次
MAX_HISTORY   = 30  # 保留最近幾條對話


WEB_REPLY_FILE = os.path.join(SCRIPT_DIR, "web_reply.md")

def _write_web_reply(text: str):
    """網頁輸入的回覆寫到 web_reply.md，由 Next.js API 輪詢讀取"""
    try:
        with open(WEB_REPLY_FILE, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        print(f"寫入 web_reply.md 失敗：{e}")


def load_project_context() -> str:
    """載入 qingxia_context/ 目錄下所有 .md 知識檔案"""
    if not os.path.exists(CONTEXT_DIR):
        return ""
    parts = []
    for fname in sorted(os.listdir(CONTEXT_DIR)):
        if fname.endswith(".md"):
            try:
                with open(os.path.join(CONTEXT_DIR, fname), encoding="utf-8") as f:
                    parts.append(f"=== {fname} ===\n{f.read()}")
            except Exception:
                pass
    return "\n\n".join(parts)


def load_history() -> list:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_history(history: list):
    trimmed = history[-(MAX_HISTORY * 2):]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, ensure_ascii=False, indent=2)


def send_telegram(text: str):
    url = f"{TELEGRAM_API}/sendMessage"
    body = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"Telegram 發送失敗：{e}")


def call_qwen(user_message: str, history: list, context: str) -> tuple:
    """
    呼叫青霞（Ollama qwen2.5:32b）生成回覆。
    回傳 (reply: str, success: bool, reason: str)
    - success=True：正常回覆，reply 為內容
    - success=False：失敗，reason 說明原因
    - reply 以 [ESCALATE] 開頭：青霞主動要求怡嘉接手
    """
    system_prompt = f"""你是林青霞，《江湖一生》武俠沙盒 RPG 的本地 AI 助理。
製作人叫 Allen（稱他為製作人）。你現在透過 Telegram 直接跟製作人溝通。

你的職責：
- 討論遊戲設計、核心玩法、競品分析
- 幫製作人整理想法、記錄決定
- 協調品霖（策劃）和靜怡（UX）的工作

重要規則：
- 若需要修改程式碼、寫入檔案、執行複雜任務（非對話），請以 [ESCALATE] 開頭回覆，後面說明原因。
  例如：[ESCALATE] 需要改寫 telegram_watcher.py，這需要在 VS Code 執行。
- 其餘問題一律自行回答，簡潔有重點，全程繁體中文。

{context}"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "error" in data:
                return ("", False, f"model_error: {data['error']}")
            content = data.get("message", {}).get("content", "").strip()
            if not content:
                return ("", False, "empty_response")
            return (content, True, "")
    except urllib.error.URLError as e:
        reason = "timeout" if "timed out" in str(e).lower() else f"network_error: {e}"
        return ("", False, reason)
    except Exception as e:
        return ("", False, f"http_error: {e}")


def _force_focus(hwnd) -> bool:
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

    fg_hwnd = win32gui.GetForegroundWindow()
    fg_tid, _ = win32process.GetWindowThreadProcessId(fg_hwnd)
    cur_tid = win32api.GetCurrentThreadId()
    tgt_tid, _ = win32process.GetWindowThreadProcessId(hwnd)

    if fg_tid != cur_tid:
        ctypes.windll.user32.AttachThreadInput(fg_tid, cur_tid, True)
    if tgt_tid != cur_tid:
        ctypes.windll.user32.AttachThreadInput(cur_tid, tgt_tid, True)

    win32gui.SetForegroundWindow(hwnd)

    if fg_tid != cur_tid:
        ctypes.windll.user32.AttachThreadInput(fg_tid, cur_tid, False)
    if tgt_tid != cur_tid:
        ctypes.windll.user32.AttachThreadInput(cur_tid, tgt_tid, False)

    time.sleep(0.3)
    return win32gui.GetForegroundWindow() == hwnd


def notify_claude_code(raw_message: str, escalation_reason: str = "", max_retries: int = 5):
    """
    通知 VS Code 怡嘉接手。
    只在青霞失敗或主動要求時呼叫。
    """
    clean_msg = raw_message
    for prefix in ("[TG]", "[WEB]"):
        clean_msg = clean_msg.replace(prefix, "").strip()

    if escalation_reason:
        notification = f"📱 Telegram（青霞移交｜{escalation_reason}）：{clean_msg}"
    else:
        notification = f"📱 Telegram：{clean_msg}"

    def find_vscode(hwnd, results):
        title = win32gui.GetWindowText(hwnd)
        if "Visual Studio Code" in title and win32gui.IsWindowVisible(hwnd):
            results.append(hwnd)

    results = []
    win32gui.EnumWindows(find_vscode, results)

    if not results:
        print("找不到 VS Code 視窗，無法通知怡嘉")
        return False

    hwnd = results[0]
    focused = False
    for attempt in range(max_retries):
        if _force_focus(hwnd):
            focused = True
            break
        wait = 0.5 * (attempt + 1)
        print(f"焦點搶奪失敗（第{attempt+1}次），{wait}秒後重試...")
        time.sleep(wait)

    if not focused:
        print(f"⚠️ {max_retries}次重試後仍無法取得焦點")
        return False

    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'alt', 'c')
    time.sleep(0.5)
    pyperclip.copy(notification)
    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.3)
    pyautogui.press('enter')
    print(f"已通知怡嘉：{notification[:60]}")
    return True


def check_incoming() -> str:
    """原子性讀取並清空 telegram_incoming.md，防止重複觸發"""
    if not os.path.exists(INCOMING_FILE):
        return ""
    try:
        with open(INCOMING_FILE, "r+", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                f.seek(0)
                f.truncate()
        if content:
            lines = content.split("\n", 1)
            return lines[1] if len(lines) > 1 else lines[0]
    except Exception:
        pass
    return ""


def handle_message(message: str):
    """處理一則訊息：青霞優先，失敗才移交怡嘉"""
    is_web = message.startswith("[WEB]") or "[WEB]" in message
    clean_msg = message
    for prefix in ("[TG]", "[WEB]"):
        clean_msg = clean_msg.replace(prefix, "").strip()

    # 圖片訊息 → 直接升交怡嘉（青霞看不了圖）
    if clean_msg.startswith("[IMAGE:"):
        # 格式：[IMAGE:/path/to/file.jpg]caption
        end = clean_msg.find("]")
        img_path = clean_msg[7:end] if end != -1 else ""
        caption  = clean_msg[end+1:].strip() if end != -1 else ""
        label = f"截圖｜說明：{caption}" if caption else "截圖（無說明文字）"
        # 組成通知：路徑讓怡嘉可以直接 Read
        path_hint = f"圖片路徑：{img_path}" if img_path else "（路徑取得失敗）"
        escalation = f"{label}｜{path_hint}"
        print(f"圖片訊息，升交怡嘉：{label[:40]}")
        notify_claude_code(f"{message}\n{path_hint}", escalation_reason=label)
        return

    # 按鈕動作 → 直接升交怡嘉（不經青霞）
    if clean_msg.startswith("[ACTION]"):
        action = clean_msg[len("[ACTION]"):].strip()
        print(f"按鈕動作，升交怡嘉：{action}")
        notify_claude_code(message, escalation_reason=f"按鈕動作：{action}")
        return

    history = load_history()
    context = load_project_context()

    # 第一次嘗試
    reply, success, reason = call_qwen(clean_msg, history, context)

    # 失敗時重試一次
    if not success:
        print(f"青霞第一次失敗（{reason}），5秒後重試...")
        time.sleep(5)
        reply, success, reason = call_qwen(clean_msg, history, context)

    # 成功但青霞主動要求移交
    if success and reply.startswith("[ESCALATE]"):
        escalate_msg = reply[len("[ESCALATE]"):].strip()
        print(f"青霞主動移交：{escalate_msg[:60]}")
        if is_web:
            _write_web_reply("這個問題需要怡嘉在 VS Code 處理，請稍候...")
        else:
            send_telegram("這個需要怡嘉在 VS Code 處理，稍等。")
        notify_claude_code(message, escalation_reason=f"青霞移交：{escalate_msg[:40]}")
        return

    # 失敗，移交怡嘉
    if not success:
        print(f"青霞兩次失敗（{reason}），移交怡嘉")
        if is_web:
            _write_web_reply("青霞暫時無法回應，怡嘉正在接手...")
        else:
            send_telegram("青霞暫時無法回應，移交怡嘉處理。")
        notify_claude_code(message, escalation_reason=reason)
        return

    # 成功，正常回覆
    history.append({"role": "user",      "content": clean_msg})
    history.append({"role": "assistant",  "content": reply})
    save_history(history)

    if is_web:
        _write_web_reply(reply)
    else:
        reply_file = os.path.join(SCRIPT_DIR, "telegram_reply.md")
        with open(reply_file, "w", encoding="utf-8") as f:
            f.write(reply)

    print(f"青霞回覆：{reply[:80]}")


def main():
    print("怡嘉 Watcher 啟動（青霞主導 / 怡嘉備援）...")

    while True:
        try:
            message = check_incoming()
            if message:
                print(f"收到訊息：{message[:50]}")
                handle_message(message)
            time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            print("Watcher 停止")
            break
        except Exception as e:
            print(f"錯誤：{e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
