"""
怡嘉主動通知工具 — 怡嘉在 VS Code 有成果或需要製作人決策時呼叫

用法：
  python tools/yijia_notify.py --type done    --title "任務完成" --body "GDD 一致性掃描完畢，發現 3 處衝突"
  python tools/yijia_notify.py --type error   --title "編譯失敗" --body "src/core/player.gd:42 型別錯誤" --detail "Cannot assign null to Player"
  python tools/yijia_notify.py --type decide  --title "需要你決定" --body "戰鬥系統要加入 V2 連擊機制嗎？" --detail "品霖草稿已完成，影響：combat-system.md 第3章"
  python tools/yijia_notify.py --type info    --title "進度更新" --body "Sprint 第3天，5/8 故事完成"

訊息類型：
  done    任務完成（測試通過、文件寫完、任務結束）
  error   錯誤/崩潰（編譯錯誤、服務掛掉、測試失敗）
  decide  需要製作人決策（設計分岔、不確定方向）
  info    一般進度更新（每日摘要、里程碑達成）
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

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import argparse
import datetime
import json
import urllib.request

TOKEN   = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID = "5129331122"

TEMPLATES = {
    "done": {
        "emoji": "✅",
        "header": "任務完成",
    },
    "error": {
        "emoji": "❌",
        "header": "錯誤報告",
    },
    "decide": {
        "emoji": "🤔",
        "header": "需要你決定",
        "footer": "→ 請回覆怡嘉你的決定，或直接在 VS Code 處理",
    },
    "info": {
        "emoji": "💬",
        "header": "進度更新",
    },
}


def format_message(msg_type: str, title: str, body: str, detail: str = "") -> str:
    t = TEMPLATES.get(msg_type, TEMPLATES["info"])
    ts = datetime.datetime.now().strftime("%H:%M")

    lines = [
        f"{t['emoji']} {title}",
        "",
        body,
    ]

    if detail:
        lines.append("")
        lines.append(f"詳細：{detail}")

    if "footer" in t:
        lines.append("")
        lines.append(t["footer"])

    lines.append("")
    lines.append(f"— 怡嘉  {ts}")

    return "\n".join(lines)


def send_telegram(text: str, buttons: list = None):
    """
    buttons: 可選，按鈕標籤清單，例如 ["修復", "忽略"]
    每個按鈕點擊後 callback_data = 按鈕標籤文字
    """
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    body = {"chat_id": CHAT_ID, "text": text}
    if buttons:
        inline_keyboard = [[{"text": b, "callback_data": b} for b in buttons]]
        body["reply_markup"] = json.dumps({"inline_keyboard": inline_keyboard})
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req, timeout=10)
        print(f"已發送：{text[:60].replace(chr(10), ' ')}")
    except Exception as e:
        print(f"發送失敗：{e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="怡嘉主動通知工具")
    parser.add_argument("--type",    required=True, choices=["done", "error", "decide", "info"],
                        help="訊息類型")
    parser.add_argument("--title",   required=True, help="標題（一行，20字內）")
    parser.add_argument("--body",    required=True, help="主要內容")
    parser.add_argument("--detail",  default="",    help="補充細節（可選）")
    parser.add_argument("--buttons", default="",    help="逗號分隔的按鈕標籤，例如 '修復,忽略'")
    args = parser.parse_args()

    msg = format_message(args.type, args.title, args.body, args.detail)
    btns = [b.strip() for b in args.buttons.split(",") if b.strip()] if args.buttons else None
    send_telegram(msg, buttons=btns)


if __name__ == "__main__":
    main()
