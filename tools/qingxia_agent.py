"""
林青霞 Agent — 自主任務執行框架
模型：Ollama qwen2.5:32b + Function Calling
用途：批量內容生成、數值驗算、文件分析（無需多輪上下文記憶的任務）

用法：
  python tools/qingxia_agent.py --task "讀取所有GDD，列出所有V2待補項目"
  python tools/qingxia_agent.py --task-file tools/qingxia_tasks/event_gen.md
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
import glob

# Windows GBK 環境強制使用 UTF-8 輸出，防止 emoji 等字符崩潰
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import argparse
import datetime
import urllib.request
import urllib.error

# ── 設定 ──────────────────────────────────────────────────────────────────────
OLLAMA_URL   = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:32b"

TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = "5129331122"
TELEGRAM_API     = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
OUTPUT_DIR   = os.path.join(PROJECT_ROOT, "design", "gdd", "drafts")

MAX_ITERATIONS = 25
MAX_FILE_READ  = 80_000   # 80KB 單次讀取上限

# ── 工具定義 ──────────────────────────────────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "讀取專案中的文件內容。路徑相對於專案根目錄。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件相對路徑，例如 design/gdd/combat-system.md"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "將內容寫入文件（覆蓋原有內容）。只能寫入專案目錄內。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path":    {"type": "string", "description": "文件相對路徑"},
                    "content": {"type": "string", "description": "要寫入的完整內容"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "append_file",
            "description": "在文件末尾追加內容（不覆蓋原有內容）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path":    {"type": "string", "description": "文件相對路徑"},
                    "content": {"type": "string", "description": "要追加的內容"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "列出目錄中的文件清單。",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "目錄相對路徑"},
                    "extension": {"type": "string", "description": "可選：只列出此副檔名的文件，例如 .md 或 .json"}
                },
                "required": ["directory"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_content",
            "description": "在目錄中搜索包含特定關鍵字的文件，返回匹配行。",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "搜索目錄"},
                    "keyword":   {"type": "string", "description": "要搜索的關鍵字"},
                    "extension": {"type": "string", "description": "可選：只搜索此副檔名"}
                },
                "required": ["directory", "keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "finish_task",
            "description": "任務已完成，呼叫此工具結束執行並報告結果。",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "任務完成的摘要，說明做了什麼、生成了什麼"
                    },
                    "files_written": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "本次任務寫入或修改的文件路徑列表"
                    }
                },
                "required": ["summary"]
            }
        }
    }
]

# ── 工具執行 ──────────────────────────────────────────────────────────────────
def safe_path(relative_path: str) -> str:
    """確保路徑在專案根目錄內，防止路徑穿越攻擊"""
    abs_path = os.path.normpath(os.path.join(PROJECT_ROOT, relative_path))
    if not abs_path.startswith(PROJECT_ROOT):
        raise ValueError(f"路徑超出專案範圍：{relative_path}")
    return abs_path


def tool_read_file(path: str) -> str:
    abs_path = safe_path(path)
    if not os.path.exists(abs_path):
        return f"[錯誤] 文件不存在：{path}"
    size = os.path.getsize(abs_path)
    if size > MAX_FILE_READ:
        return f"[警告] 文件過大（{size} bytes），只讀取前 {MAX_FILE_READ} 字元\n\n" + \
               open(abs_path, encoding="utf-8", errors="replace").read(MAX_FILE_READ)
    return open(abs_path, encoding="utf-8", errors="replace").read()


def tool_write_file(path: str, content: str) -> str:
    abs_path = safe_path(path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"[成功] 已寫入：{path}（{len(content)} 字元）"


def tool_append_file(path: str, content: str) -> str:
    abs_path = safe_path(path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "a", encoding="utf-8") as f:
        f.write(content)
    return f"[成功] 已追加至：{path}（{len(content)} 字元）"


def tool_list_files(directory: str, extension: str = "") -> str:
    abs_dir = safe_path(directory)
    if not os.path.exists(abs_dir):
        return f"[錯誤] 目錄不存在：{directory}"
    pattern = os.path.join(abs_dir, f"**/*{extension}" if extension else "**/*")
    files = glob.glob(pattern, recursive=True)
    files = [f for f in files if os.path.isfile(f)]
    rel_files = [os.path.relpath(f, PROJECT_ROOT).replace("\\", "/") for f in files]
    if not rel_files:
        return f"[空] 目錄中沒有文件：{directory}"
    return "\n".join(rel_files)


def tool_search_content(directory: str, keyword: str, extension: str = "") -> str:
    abs_dir = safe_path(directory)
    if not os.path.exists(abs_dir):
        return f"[錯誤] 目錄不存在：{directory}"
    pattern = os.path.join(abs_dir, f"**/*{extension}" if extension else "**/*")
    files = glob.glob(pattern, recursive=True)
    files = [f for f in files if os.path.isfile(f)]

    results = []
    for f in files:
        try:
            content = open(f, encoding="utf-8", errors="replace").read()
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if keyword.lower() in line.lower():
                    rel = os.path.relpath(f, PROJECT_ROOT).replace("\\", "/")
                    results.append(f"{rel}:{i+1}: {line.strip()}")
        except Exception:
            pass

    if not results:
        return f"[無結果] 在 {directory} 中未找到包含「{keyword}」的內容"
    return "\n".join(results[:100])  # 最多返回100行


def execute_tool(name: str, args: dict) -> str:
    try:
        if name == "read_file":
            return tool_read_file(args["path"])
        elif name == "write_file":
            return tool_write_file(args["path"], args["content"])
        elif name == "append_file":
            return tool_append_file(args["path"], args["content"])
        elif name == "list_files":
            return tool_list_files(args["directory"], args.get("extension", ""))
        elif name == "search_content":
            return tool_search_content(args["directory"], args["keyword"], args.get("extension", ""))
        elif name == "finish_task":
            return "__DONE__"
        else:
            return f"[錯誤] 未知工具：{name}"
    except ValueError as e:
        return f"[安全錯誤] {e}"
    except Exception as e:
        return f"[執行錯誤] {e}"

# ── Ollama 呼叫 ───────────────────────────────────────────────────────────────
def call_ollama(messages: list) -> dict:
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "messages": messages,
        "tools": TOOLS,
        "stream": False
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=600) as resp:
        return json.loads(resp.read().decode("utf-8"))

# ── Telegram 通知 ─────────────────────────────────────────────────────────────
def send_telegram(text: str):
    url = f"{TELEGRAM_API}/sendMessage"
    body = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": text}).encode()
    req = urllib.request.Request(url, data=body,
                                  headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass

# ── Agent 主迴圈 ──────────────────────────────────────────────────────────────
def _load_context() -> str:
    """載入專案知識庫，注入系統提示"""
    ctx_dir = os.path.join(SCRIPT_DIR, "qingxia_context")
    if not os.path.exists(ctx_dir):
        return ""
    parts = []
    for fname in sorted(os.listdir(ctx_dir)):
        if fname.endswith(".md"):
            try:
                path = os.path.join(ctx_dir, fname)
                content = open(path, encoding="utf-8").read()
                parts.append(f"=== {fname} ===\n{content}")
            except Exception:
                pass
    return "\n\n".join(parts)


_PROJECT_CONTEXT = _load_context()

SYSTEM_PROMPT = f"""你是林青霞，《江湖一生》武俠沙盒RPG專案的本地執行助理。

以下是你工作前必須了解的專案知識：

{_PROJECT_CONTEXT}

---

工作原則：
1. 每次只呼叫一個工具，等待結果後再決定下一步
2. 讀取文件後要真正消化內容再繼續，不要假設文件內容
3. 按照任務的步驟順序執行，完成一步再做下一步
4. 寫入文件前確認路徑正確（design/gdd/drafts/ 存草稿，tools/qingxia_tasks/results/ 存任務結果）
5. ⚠️ 必須先呼叫 write_file 寫入結果文件，確認成功後才能呼叫 finish_task
6. 使用繁體中文，武俠語言（禁用修仙詞彙）

你不需要記住對話歷史。每個任務獨立執行，專注完成眼前的任務。"""


LOG_FILE = os.path.join(SCRIPT_DIR, "qingxia_log.md")


def write_log(message: str):
    """寫一行進度到日誌文件，供製作人即時查看"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass


def run_agent(task: str) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": f"請完成以下任務：\n\n{task}"}
    ]

    # 任務開始時清空日誌，寫入任務標題
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"# 青霞工作日誌\n任務：{task[:120]}...\n開始：{datetime.datetime.now().strftime('%H:%M:%S')}\n\n")
    except Exception:
        pass

    print(f"\n[青霞] 開始執行任務：{task[:80]}...")
    finish_data = {}

    for iteration in range(MAX_ITERATIONS):
        print(f"[青霞] 第 {iteration+1} 輪推理...")
        write_log(f"第 {iteration+1} 輪推理中...")

        try:
            response = call_ollama(messages)
        except Exception as e:
            print(f"[青霞] Ollama 呼叫失敗：{e}")
            write_log(f"❌ Ollama 呼叫失敗：{e}")
            break

        msg = response.get("message", {})
        messages.append(msg)

        # 有工具呼叫
        tool_calls = msg.get("tool_calls", [])
        if tool_calls:
            for tc in tool_calls:
                fn_name = tc.get("function", {}).get("name", "")
                fn_args = tc.get("function", {}).get("arguments", {})

                print(f"[青霞] 呼叫工具：{fn_name}({list(fn_args.keys())})")
                write_log(f"→ {fn_name}({', '.join(str(v)[:40] for v in fn_args.values())})")

                if fn_name == "finish_task":
                    finish_data = fn_args
                    summary = fn_args.get('summary', '')[:100]
                    print(f"[青霞] 任務完成：{summary}")
                    write_log(f"✅ 任務完成：{summary}")
                    return finish_data

                result = execute_tool(fn_name, fn_args)
                print(f"[青霞] 工具結果：{result[:100]}...")
                write_log(f"  結果：{result[:80]}")

                messages.append({
                    "role": "tool",
                    "content": result
                })
        else:
            # 純文字回覆（沒有工具呼叫）
            content = msg.get("content", "")
            if content:
                print(f"[青霞] 思考中：{content[:100]}...")
            # 若連續沒有工具呼叫，提示她繼續
            messages.append({
                "role": "user",
                "content": "請繼續執行任務。如果已完成，請呼叫 finish_task。"
            })

    print(f"[青霞] 達到最大迭代次數（{MAX_ITERATIONS}），強制結束")
    return finish_data

# ── 主程式 ────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="林青霞 Agent — 自主任務執行")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--task",      type=str, help="直接輸入任務描述")
    group.add_argument("--task-file", type=str, help="從文件讀取任務描述")
    args = parser.parse_args()

    if args.task_file:
        task_path = safe_path(args.task_file) if not os.path.isabs(args.task_file) else args.task_file
        with open(task_path, encoding="utf-8") as f:
            task = f.read().strip()
    else:
        task = args.task

    start_time = datetime.datetime.now()
    send_telegram(f"🌸 青霞開始執行任務\n\n{task[:200]}")

    result = run_agent(task)

    elapsed = (datetime.datetime.now() - start_time).seconds
    summary = result.get("summary", "（無摘要）")
    files   = result.get("files_written", [])

    report = (
        f"✅ 青霞任務完成（{elapsed}秒）\n\n"
        f"摘要：{summary[:300]}\n"
    )
    if files:
        report += "\n寫入文件：\n" + "\n".join(f"  · {f}" for f in files)

    print(f"\n{report}")
    send_telegram(report)


if __name__ == "__main__":
    main()
