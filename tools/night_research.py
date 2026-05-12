"""
夜間情報搜集腳本 — 情報部門
Gemini 搜集 → Qwen 整理 → 存檔供製作人確認
用法: python tools/night_research.py
"""
import os
import json
import time
import datetime
import urllib.request
import urllib.error

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = "5129331122"
GEMINI_API_KEY = "REDACTED_ROTATE_THIS_KEY"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "design", "intelligence")

RESEARCH_TASKS = [
    {
        "title": "Claude & Anthropic 最新動態",
        "prompt": "搜尋最近7天關於 Anthropic、Claude Code 的新公告、新功能、新 MCP、新 Skills。沒有新消息就說沒有。繁體中文條列式。"
    },
    {
        "title": "武俠競品動態",
        "prompt": "搜尋最近7天關於鬼谷八荒、龍胤立志傳、我來自江湖的更新或玩家反饋。繁體中文條列式。"
    },
    {
        "title": "AI 遊戲開發新工具",
        "prompt": "搜尋最近7天有沒有值得注意的 AI 遊戲開發工具、Godot AI 工具、或 AI agent 框架新發布。繁體中文條列式。"
    }
]

def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    body = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"  Telegram 發送失敗：{e}")

def call_gemini(prompt: str) -> str:
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 800}}
    data = json.dumps(body).encode()
    req = urllib.request.Request(GEMINI_URL, data=data, headers={"Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"（Gemini 搜尋失敗：{e}）"

def call_deepseek(prompt: str) -> str:
    body = {"model": "deepseek-v4-flash", "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3, "max_tokens": 600}
    data = json.dumps(body).encode()
    req = urllib.request.Request(DEEPSEEK_URL, data=data, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    })
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"（DeepSeek 失敗：{e}）"

def call_qwen(prompt: str) -> str:
    body = {"model": "qwen2.5:14b", "prompt": prompt, "stream": False,
            "options": {"temperature": 0.3, "num_predict": 500}}
    data = json.dumps(body).encode()
    req = urllib.request.Request(OLLAMA_URL, data=data, headers={"Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read())
        return result.get("response", "（無回應）")
    except Exception as e:
        return f"（Qwen 處理失敗：{e}）"

def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = datetime.date.today().strftime("%Y-%m-%d")
    output_path = os.path.join(OUTPUT_DIR, f"{today}.md")

    print(f"情報部門啟動 — {today}")
    sections = [f"# 每日情報簡報 — {today}\n\n*Gemini 搜集 + Qwen 整理，供製作人確認後採用*\n"]

    raw_results = []
    for i, task in enumerate(RESEARCH_TASKS):
        if i > 0:
            time.sleep(6)
        print(f"[Gemini] 搜集：{task['title']}...")
        result = call_gemini(task["prompt"])
        if "失敗" in result or "Error" in result:
            print(f"  ⚠️ Gemini 失敗，改用 DeepSeek...")
            result = call_deepseek(f"請根據你的知識回答（注意非即時資訊）：{task['prompt']}\n開頭標注「⚠️ 非即時資訊，由 DeepSeek 補充」")
            if "失敗" in result or "Error" in result:
                print(f"  ⚠️ DeepSeek 也失敗，改用 Qwen 本地...")
                result = call_qwen(f"請根據訓練知識回答：{task['prompt']}\n開頭標注「⚠️ 非即時資訊，由本地 Qwen 補充」")
            raw_results.append((task["title"], result))
        else:
            raw_results.append((task["title"], result))

    for title, raw in raw_results:
        print(f"[Qwen] 整理：{title}...")
        qwen_prompt = f"""以下是今天搜集到的情報，請整理成簡潔的重點摘要，標注是否需要製作人關注（標記「⚠️ 需關注」或「✅ 例行」）：

{raw}

輸出格式：條列式，繁體中文，每點不超過50字。"""
        summary = call_qwen(qwen_prompt)
        sections.append(f"## {title}\n\n{summary}\n")

    report = "\n".join(sections)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✅ 完成！報告：{output_path}")

    # 發送 Telegram 通知
    print("發送 Telegram 通知...")
    summary = f"📋 *江湖一生情報簡報 — {today}*\n\n"
    for title, _ in raw_results:
        summary += f"• {title}\n"
    summary += f"\n已存入專案資料夾，打開 VS Code 查看完整內容。"
    send_telegram(summary)

if __name__ == "__main__":
    run()
