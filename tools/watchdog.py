"""
怡嘉 Watchdog — 確保所有服務持續運行
監管：Python 腳本 + Node.js 服務（ws-server、Next.js）
"""
import subprocess
import time
import os
import sys
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AGENT_VRM_DIR = os.path.join(SCRIPT_DIR, "..", "..", "AgentVRM")
LOCK_FILE = os.path.join(SCRIPT_DIR, ".watchdog.lock")

CHECK_INTERVAL = 15  # 每15秒檢查一次

# Python 腳本（用 sys.executable 啟動）
PYTHON_SCRIPTS = [
    os.path.join(SCRIPT_DIR, "telegram_qwen_bot.py"),
    os.path.join(SCRIPT_DIR, "telegram_watcher.py"),
    os.path.join(SCRIPT_DIR, "vrm_speak_watcher.py"),
    os.path.join(SCRIPT_DIR, "telegram_reply_watcher.py"),
]

# Node.js 服務（用 node 啟動）
NODE_EXE  = r"C:\Program Files\nodejs\node.exe"
NPM_CMD   = r"C:\Program Files\nodejs\npm.cmd"

NODE_SERVICES = [
    {
        "name": "ws-server",
        "cmd": [NODE_EXE, "server/ws-server.js"],
        "cwd": os.path.abspath(AGENT_VRM_DIR),
        "delay": 0,
    },
    {
        "name": "next-dev",
        "cmd": [NPM_CMD, "run", "dev"],
        "cwd": os.path.abspath(AGENT_VRM_DIR),
        "delay": 120,  # 登入後 2 分鐘再啟動，不影響開機速度
    },
]


def acquire_lock():
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE) as f:
                old_pid = int(f.read().strip())
            os.kill(old_pid, 0)
            print(f"Watchdog 已在運行中 (PID {old_pid})，退出")
            sys.exit(0)
        except (OSError, ValueError):
            pass
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))


def release_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)


def start_python(path):
    print(f"啟動 Python：{os.path.basename(path)}")
    kwargs = dict(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    return subprocess.Popen([sys.executable, path], **kwargs)


def clean_next_cache():
    """清除 Next.js 損壞快取"""
    import shutil
    next_dir = os.path.join(AGENT_VRM_DIR, ".next")
    if os.path.exists(next_dir):
        try:
            shutil.rmtree(next_dir)
            print("已清除 .next 快取")
        except Exception as e:
            print(f"清除快取失敗：{e}")


def start_node(service):
    print(f"啟動 Node：{service['name']}")
    # Next.js 啟動前先清快取，避免損壞導致 404
    if service["name"] == "next-dev":
        clean_next_cache()
    # 確保 Node.js 在 PATH 中（開機時 PATH 可能不完整）
    env = os.environ.copy()
    env["PATH"] = r"C:\Program Files\nodejs" + os.pathsep + env.get("PATH", "")
    kwargs = dict(
        cwd=service["cwd"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
    )
    if sys.platform == "win32":
        kwargs["shell"] = True
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    return subprocess.Popen(service["cmd"], **kwargs)


def main():
    acquire_lock()
    print("Watchdog 啟動，監看中...")

    # 啟動所有 Python 腳本
    python_procs = {path: start_python(path) for path in PYTHON_SCRIPTS}

    # 等 Node 服務有時間初始化（立即啟動的先跑）
    def start_node_delayed(service):
        delay = service.get("delay", 0)
        if delay > 0:
            time.sleep(delay)
        return start_node(service)

    import threading
    node_procs = {}
    for s in NODE_SERVICES:
        if s.get("delay", 0) == 0:
            node_procs[s["name"]] = (s, start_node(s))
        else:
            # 延遲啟動放到背景執行緒
            def delayed_start(svc=s):
                time.sleep(svc["delay"])
                proc = start_node(svc)
                node_procs[svc["name"]] = (svc, proc)
            threading.Thread(target=delayed_start, daemon=True).start()

    try:
        while True:
            time.sleep(CHECK_INTERVAL)

            # 檢查 Python 腳本
            for path, proc in python_procs.items():
                if proc.poll() is not None:
                    print(f"重啟 Python：{os.path.basename(path)}")
                    python_procs[path] = start_python(path)

            # 檢查 Node 服務
            for name, (service, proc) in node_procs.items():
                if proc.poll() is not None:
                    print(f"重啟 Node：{name}")
                    node_procs[name] = (service, start_node(service))

    finally:
        release_lock()


if __name__ == "__main__":
    main()
