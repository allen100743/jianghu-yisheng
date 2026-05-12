"""
靜怡批次任務執行器
從 jingyi_tasks/queue.md 逐一執行 UX Spec 生成任務
完成每個任務後發 Telegram 通知
收到停止信號（jingyi_tasks/STOP）後優雅收尾

用法：
  python tools/jingyi_overnight.py

停止方式：
  在 VS Code 告訴怡嘉「讓靜怡停下」→ 怡嘉建立 STOP 信號 → 靜怡完成當前任務後停止
"""
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

import sys
import io
import subprocess
import datetime
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
TASKS_DIR   = os.path.join(SCRIPT_DIR, "jingyi_tasks")
QUEUE_FILE  = os.path.join(TASKS_DIR, "queue.md")
STOP_SIGNAL = os.path.join(TASKS_DIR, "STOP")
LOG_FILE    = os.path.join(SCRIPT_DIR, "jingyi_log.md")
AGENT       = os.path.join(SCRIPT_DIR, "jingyi_agent.py")

TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = "5129331122"
TELEGRAM_API     = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def send_telegram(text: str):
    url = f"{TELEGRAM_API}/sendMessage"
    body = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": text}).encode()
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


def write_log(msg: str):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


def check_stop() -> bool:
    return os.path.exists(STOP_SIGNAL)


def clear_stop():
    if os.path.exists(STOP_SIGNAL):
        os.remove(STOP_SIGNAL)


def parse_queue() -> list:
    if not os.path.exists(QUEUE_FILE):
        return []

    tasks = []
    current = {}
    with open(QUEUE_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("## Task:"):
                if current:
                    tasks.append(current)
                current = {
                    "name":   line[8:].strip(),
                    "status": "pending",
                    "task":   "",
                    "screen": "",
                }
            elif line.startswith("Status:"):
                current["status"] = line[7:].strip()
            elif line.startswith("Task:"):
                current["task"] = line[5:].strip()
            elif line.startswith("Screen:"):
                current["screen"] = line[7:].strip()
    if current:
        tasks.append(current)
    return tasks


def update_status(task_name: str, status: str):
    if not os.path.exists(QUEUE_FILE):
        return
    with open(QUEUE_FILE, encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    in_task = False
    updated = []
    for line in lines:
        if line.strip().startswith("## Task:") and task_name in line:
            in_task = True
        if in_task and line.strip().startswith("Status:"):
            line = f"Status: {status}"
            in_task = False
        updated.append(line)

    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(updated))


def run_task(task: dict) -> bool:
    cmd = [sys.executable, AGENT, "--task", task["task"]]
    if task["screen"]:
        cmd += ["--screen", task["screen"]]

    write_log(f"執行：{task['name']} ({' '.join(cmd[2:])})")
    try:
        result = subprocess.run(cmd, timeout=300)  # 5 分鐘上限
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        write_log(f"超時：{task['name']}")
        return False


def main():
    os.makedirs(TASKS_DIR, exist_ok=True)
    clear_stop()

    # 初始化 log
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"# 靜怡工作日誌\n開始：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

    tasks   = parse_queue()
    pending = [t for t in tasks if t["status"] == "pending"]

    if not pending:
        print("[靜怡] 沒有待執行的任務")
        write_log("佇列空，結束")
        return

    send_telegram(
        f"🎨 靜怡批次任務開始\n"
        f"待執行：{len(pending)} 個 UX Spec"
    )
    write_log(f"佇列啟動，{len(pending)} 個任務")

    completed = 0
    for task in pending:
        if check_stop():
            write_log("收到停止信號，優雅停止")
            send_telegram(
                f"🛑 靜怡收到停止信號\n"
                f"已完成：{completed}/{len(pending)}\n"
                f"剩餘任務保留在佇列，下次繼續"
            )
            clear_stop()
            return

        success = run_task(task)
        status  = "done" if success else "failed"
        update_status(task["name"], status)
        completed += success

        icon = "✅" if success else "❌"
        write_log(f"{icon} {task['name']}（{status}）")
        send_telegram(f"{icon} 靜怡完成：{task['name']}")

    send_telegram(
        f"🎨 靜怡批次任務全部完成\n"
        f"成功：{completed}/{len(pending)}\n"
        f"Spec 位置：design/ux/"
    )
    write_log(f"全部完成，{completed}/{len(pending)} 成功")


if __name__ == "__main__":
    main()
