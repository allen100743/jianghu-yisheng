"""
青霞夜間任務佇列執行器
從 qingxia_tasks/overnight_queue.md 逐一執行任務
完成每個任務後發 Telegram 通知
收到停止信號（qingxia_tasks/STOP）後優雅收尾

用法：
  python tools/qingxia_overnight.py

停止方式：
  在 VS Code 告訴怡嘉「讓青霞停下」→ 怡嘉建立 STOP 信號 → 青霞完成當前任務後停止
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
import datetime
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
TASKS_DIR    = os.path.join(SCRIPT_DIR, "qingxia_tasks")
QUEUE_FILE   = os.path.join(TASKS_DIR, "overnight_queue.md")
STOP_SIGNAL  = os.path.join(TASKS_DIR, "STOP")
RESULTS_DIR  = os.path.join(TASKS_DIR, "results")
LOG_FILE     = os.path.join(SCRIPT_DIR, "qingxia_log.md")

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
            f.write(f"[{ts}] [佇列] {msg}\n")
    except Exception:
        pass


def check_stop() -> bool:
    return os.path.exists(STOP_SIGNAL)


def clear_stop():
    if os.path.exists(STOP_SIGNAL):
        os.remove(STOP_SIGNAL)


def parse_queue() -> list[dict]:
    """
    解析佇列文件，格式：
    ## Task: [任務名稱]
    Status: pending | done | skipped
    TaskFile: qingxia_tasks/xxx.md
    ---
    """
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
                current = {"name": line[8:].strip(), "status": "pending", "task_file": "", "output_file": ""}
            elif line.startswith("Status:"):
                current["status"] = line[7:].strip()
            elif line.startswith("TaskFile:"):
                current["task_file"] = line[9:].strip()
            elif line.startswith("OutputFile:"):
                current["output_file"] = line[11:].strip()
    if current:
        tasks.append(current)
    return tasks


def update_task_status(task_name: str, status: str):
    """更新佇列文件中指定任務的狀態"""
    if not os.path.exists(QUEUE_FILE):
        return
    with open(QUEUE_FILE, encoding="utf-8") as f:
        content = f.read()

    # 找到對應任務區塊並更新狀態
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


def run_task_file(task_file: str, task_name: str) -> bool:
    """執行單個任務文件，返回是否成功"""
    # 動態 import 避免循環依賴
    import subprocess
    agent_script = os.path.join(SCRIPT_DIR, "qingxia_agent.py")
    task_path = os.path.join(SCRIPT_DIR, "..", task_file) if not os.path.isabs(task_file) else task_file
    task_path = os.path.normpath(task_path)

    if not os.path.exists(task_path):
        write_log(f"❌ 任務文件不存在：{task_file}")
        return False

    write_log(f"▶️ 開始任務：{task_name}")
    result = subprocess.run(
        [sys.executable, agent_script, "--task-file", task_path],
        capture_output=False,
        timeout=1800  # 30 分鐘上限
    )
    return result.returncode == 0


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    clear_stop()  # 清除舊的停止信號

    tasks = parse_queue()
    pending = [t for t in tasks if t["status"] == "pending"]

    if not pending:
        print("[青霞佇列] 沒有待執行的任務")
        write_log("佇列空，結束")
        return

    send_telegram(f"🌙 青霞夜間任務開始\n待執行：{len(pending)} 個任務")
    write_log(f"佇列啟動，{len(pending)} 個任務")

    completed = 0
    for task in pending:
        # 每個任務開始前檢查停止信號
        if check_stop():
            write_log("收到停止信號，優雅停止")
            send_telegram(
                f"🛑 青霞收到停止信號\n"
                f"已完成：{completed}/{len(pending)} 個任務\n"
                f"剩餘任務保留在佇列中，下次繼續"
            )
            clear_stop()
            return

        name = task["name"]
        task_file = task["task_file"]

        try:
            success = run_task_file(task_file, name)

            # 驗證輸出文件（如有指定）
            output_file = task.get("output_file", "")
            if success and output_file:
                project_root = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
                output_path = os.path.join(project_root, output_file)
                if not os.path.exists(output_path) or os.path.getsize(output_path) < 50:
                    success = False
                    write_log(f"⚠️ 輸出文件不存在或為空：{output_file}")

            status = "done" if success else "failed"
            completed += success
            update_task_status(name, status)
            icon = "✅" if success else "❌"
            write_log(f"{icon} 任務結束：{name}（{status}）")
            send_telegram(f"{icon} 青霞完成任務：{name}")

        except subprocess.TimeoutExpired:
            update_task_status(name, "timeout")
            write_log(f"⏰ 任務超時：{name}")
            send_telegram(f"⏰ 青霞任務超時：{name}")

        except Exception as e:
            update_task_status(name, "error")
            write_log(f"💥 任務錯誤：{name} — {e}")

    send_telegram(
        f"🌙 青霞夜間任務全部完成\n"
        f"成功：{completed}/{len(pending)}\n"
        f"查看日誌：tools/qingxia_log.md"
    )
    write_log(f"佇列結束，{completed}/{len(pending)} 成功")


if __name__ == "__main__":
    main()
