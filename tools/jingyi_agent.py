"""
UX 部門腳本 — 李靜怡
按需觸發，非夜間自動。DeepSeek 主力，Qwen 備援。
用法: python tools/jingyi_agent.py --task <任務名稱> [--screen <畫面名稱>]
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

import json
import sys
import argparse
import datetime
import urllib.request
import urllib.error

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = "5129331122"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:32b"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_FILE = os.path.join(SCRIPT_DIR, "jingyi_prompt.md")
CONTEXT_DIR = os.path.join(SCRIPT_DIR, "jingyi_context")
UX_SPEC_FILE = os.path.join(SCRIPT_DIR, "..", "design", "gdd", "ux-spec.md")
GDD_DIR = os.path.join(SCRIPT_DIR, "..", "design", "gdd")
UX_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "design", "ux")

TASKS = {
    "screen-spec": {
        "title": "畫面 UX Spec",
        "prompt": """請為指定畫面輸出完整的 UX Spec。畫面名稱在任務說明的 --screen 參數中指定。

按以下結構輸出，每個章節都必須具體（不能寫「合適的反饋」，要寫「顯示 X 秒的動畫，然後 Y」）：

## 1. 目的與觸發時機
- 這個畫面/元素在什麼情境下出現？
- 玩家的心理狀態（目標/情緒）是什麼？

## 2. 資訊架構（優先層次）
- P1（必須立即可見）：
- P2（需要時展開）：
- P3（進階/設定）：

## 3. 互動流程
列出所有可能的操作，每個操作說明：觸發方式 → 結果 → 狀態變化

## 4. 狀態定義
| 狀態 | 視覺表現 | 行為差異 |
|------|---------|---------|

## 5. 輸入映射
| 操作 | 鍵鼠 | 手把 |
|------|------|------|

## 6. 無障礙要求
- 特定於此畫面的無障礙規格

## 7. 驗收標準
| # | 測試項目 | 預期結果 | 阻斷 |
|---|---------|---------|------|

## 8. MVP / V2 邊界
- MVP 必做：
- V2 追加：
- 明確不做：

繁體中文，武俠語言，數值具體。""",
    },
    "hud-design": {
        "title": "HUD 設計規格",
        "prompt": """請為《江湖一生》的主要遊戲 HUD 輸出完整設計規格。

參考已有的狀態效果 UI 研究結論（三層視覺語言：圖示填充度 + micro-bar + 脈衝動畫）。

請輸出：

## 1. HUD 設計原則（本作專屬）
- 哪些資訊永遠可見？哪些按需顯示？
- HUD 與沉浸感的平衡策略

## 2. HUD 元素清單
| 元素 | 位置 | 觸發時機 | 消失時機 | 優先級 |
|------|------|---------|---------|--------|

## 3. 狀態效果區（6種狀態的 HUD 呈現）
依據傷勢與狀態效果 GDD（severity 0.0-1.0 連續值）設計：
- 顯示邏輯（何時出現、排序規則）
- 三層視覺語言規格（圖示 / micro-bar / 脈衝）
- 懸停浮框內容規格

## 4. 時間/年齡顯示
- 遊戲時間的呈現方式（季節/年份/角色年齡）
- 老化視覺錨點的設計思路

## 5. 戰鬥 HUD 狀態
- 進入戰鬥時 HUD 如何變化
- 退出戰鬥時的過渡

## 6. 輸入映射
- 手把操作 HUD 的快捷鍵（若有）

## 7. 驗收標準

## 8. MVP / V2 邊界

繁體中文，武俠語言，具體數值（位置用百分比或格子座標描述）。""",
    },
    "status-effects-hud": {
        "title": "狀態效果 HUD Spec（依據已有研究）",
        "prompt": """請依據已完成的業界研究結論，為《江湖一生》的傷勢與狀態效果 HUD 輸出完整 UX Spec。

已有研究結論（直接應用，不需重新研究）：
- 三層視覺語言：圖示填充度（0-100% 反映 severity）+ 3px micro-bar（顏色隨段位）+ 脈衝動畫（≥0.9 時）
- 自動排序：按緊急度評分（severity × 惡化速率係數 × 致死風險係數），≥0.9 強制置頂
- 危急觸發：首次進入閾值時一次性動畫，之後靜態光暈
- 漸進揭露：HUD 只顯示圖示，懸停展開浮框，主動開啟面板顯示最終屬性
- 顏色語義：外傷暖紅、內傷深紫、中毒毒綠、疲勞冷灰、飢餓土黃、疾病病黃藍

6 種狀態（來自 status-effects-system.md）：外傷、內傷、中毒、疲勞、飢餓、疾病

請輸出標準 UX Spec 格式（7節），重點在：
- P1/P2/P3 資訊架構（圖示/浮框/詳細面板三層）
- 具體的 severity 閾值觸發規則（0.3/0.6/0.9）
- 懸停浮框的武俠文案格式（含情境描述句範例）
- 6 種狀態的個別顏色和圖示描述規格
- 驗收標準（QA 可逐條測試）

繁體中文，武俠語言。""",
    },
    "flow-mapping": {
        "title": "玩家流程圖",
        "prompt": """請為指定遊戲流程輸出完整的玩家流程圖與 UX 分析。

請輸出以下內容：

## 1. 流程概覽
用 Mermaid flowchart 語法畫出完整玩家流程（包含所有分支和錯誤狀態）。

## 2. 關鍵決策點分析
| 決策點 | 玩家需要的資訊 | 玩家的心理狀態 | 設計風險 |
|--------|-------------|-------------|---------|

## 3. 摩擦點識別
列出所有可能讓玩家困惑或放棄的時刻，以及建議的解決方向。

## 4. 資訊揭露時機規劃
哪些資訊在流程的哪個節點揭露？為什麼？

## 5. 失敗路徑設計
玩家在各節點失敗時的流程如何？情感如何被接住？

## 6. MVP 流程 vs 完整流程
MVP 版本流程的精簡邊界。

繁體中文，武俠語言。流程名稱在 --screen 參數中指定。""",
    },
    "onboarding-design": {
        "title": "新手引導設計",
        "prompt": """請為《江湖一生》設計完整的新手引導（前 15 分鐘）UX 方案。

設計約束：
- 玩家首次進入遊戲，對武俠 RPG 有基本認知但不熟悉本作
- 15 分鐘內必須讓玩家感受到「江湖有人、選擇有代價」兩個核心支柱
- 不能用傳統教學彈窗打斷沉浸感
- 系統數量龐大，必須決定哪些延後出現

請輸出：

## 1. 引導設計原則（本作專屬）
- 如何在不打斷沉浸的前提下教學？
- 哪些系統「先感受、後理解」？

## 2. 前 15 分鐘資訊密度規劃
| 時間節點 | 玩家行為 | 系統引入 | 隱藏的系統 |
|---------|---------|---------|-----------|

## 3. 被動學習設計（情境式引導）
每個核心系統第一次出現時的引導方式（情境觸發 + 系統解說 + 反饋確認）

## 4. 系統延後出現清單
| 系統 | 何時出現 | 延後理由 |
|------|---------|---------|

## 5. 「江湖有人」的感知設計
前 15 分鐘如何讓玩家感受到 NPC 是活的，而不是靜態布景？

## 6. 驗收標準（可用空場景測試）

繁體中文，武俠語言。""",
    },
    "accessibility-audit": {
        "title": "無障礙設計審查",
        "prompt": """請針對《江湖一生》輸出完整的無障礙設計規範與審查清單。

參考既有設定：
- 平台：PC Steam
- 輸入：鍵鼠（主）+ 手把（部分）
- 目標：通過 Steam 無障礙標籤要求

請輸出：

## 1. 無障礙分類與優先級
| 類別 | MVP 必做 | V2 追加 | 說明 |
|------|---------|---------|------|

## 2. 視覺無障礙規格
- 字體大小規範（最小/推薦/大字模式）
- 顏色對比要求（WCAG AA 標準）
- 色盲模式規格（三種色盲類型對應）
- UI 縮放支援規格

## 3. 輸入無障礙規格
- 按鍵重映射規範（哪些必須可重映射）
- 單手模式建議
- 滑鼠敏感度/無障礙輸入選項

## 4. 認知無障礙規格
- 字幕規範（對話/環境音/系統訊息分類）
- 暫停容忍設計
- 資訊重複確認機制

## 5. 審查清單（QA 可逐條測試）
| # | 測試項目 | 測試方法 | 通過標準 | 阻斷 |
|---|---------|---------|---------|------|

繁體中文。""",
    },
    "interaction-patterns": {
        "title": "互動模式庫",
        "prompt": """請為《江湖一生》建立互動模式庫（Interaction Pattern Library）。

這份文件定義本作所有重複使用的 UX 互動模式，確保設計一致性。

請輸出：

## 1. 對話互動模式
- 對話框標準結構（說話人/文字/繼續/選項）
- 選項有代價時的特殊呈現
- 對話中斷（被攻擊/時間流逝）的處理

## 2. 確認/警告模式
- 不可逆操作的確認流程（選拜師、結義、仇恨等）
- 警告等級分類（一般/重要/不可逆）

## 3. 通知/事件模式
- 世界事件通知（NPC 死亡、關係變化、任務更新）
- 通知優先級與堆疊規則
- 通知的武俠文案格式

## 4. 清單/背包模式
- 物品清單的標準互動（選擇/排序/過濾）
- 多選操作模式

## 5. 地圖互動模式
- 移動目的地的選擇流程
- 距離和時間成本的呈現方式

## 6. 時間流逝感知模式
- 等待/行動中時間如何可感知
- 截止日臨近的警示呈現

每個模式包含：觸發條件 + 互動流程 + 狀態定義 + 輸入映射 + 武俠文案範例

繁體中文，具體可實作。""",
    },
}


def load_system_prompt():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def load_context_dir():
    """讀取 jingyi_context/ 下所有知識庫檔案"""
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
    return "\n\n".join(parts) if parts else ""


def load_ux_spec():
    try:
        with open(UX_SPEC_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def load_relevant_gdds(task_name):
    """依任務類型載入相關 GDD 片段"""
    relevant = {
        "status-effects-hud": ["status-effects-system.md", "resistance-system.md"],
        "hud-design": ["status-effects-system.md", "combat-system.md", "time-aging-system.md"],
        "onboarding-design": ["character-creation-system.md", "core-gdd.md"],
        "flow-mapping": ["task-system.md", "narrative-event-system.md"],
    }
    files = relevant.get(task_name, [])
    parts = []
    for fname in files:
        path = os.path.join(GDD_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                # 只取前 200 行避免 context 過長
                lines = content.split("\n")[:200]
                parts.append(f"=== {fname}（前200行）===\n" + "\n".join(lines))
        except Exception:
            pass
    return "\n\n".join(parts)


def call_deepseek(system_prompt, user_prompt):
    payload = json.dumps({
        "model": "deepseek-v4-pro",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 8000
    }).encode("utf-8")

    req = urllib.request.Request(
        DEEPSEEK_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]


def call_qwen(system_prompt, user_prompt):
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": f"[SYSTEM]\n{system_prompt}\n\n[USER]\n{user_prompt}",
        "stream": False
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("response", "")


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


def save_spec(task_name, content, screen_name=None):
    os.makedirs(UX_OUTPUT_DIR, exist_ok=True)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    if screen_name:
        slug = screen_name.lower().replace(" ", "-").replace("/", "-")
        filename = f"{slug}.md"
    else:
        filename = f"{task_name}-{date_str}.md"

    filepath = os.path.join(UX_OUTPUT_DIR, filename)
    task_title = TASKS[task_name]["title"]
    header = f"# UX Spec：{screen_name or task_title}\n"
    header += f"*李靜怡 | {date_str} | 狀態：草稿*\n\n---\n\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(header + content)

    return filepath


def main():
    parser = argparse.ArgumentParser(description="UX 部門 — 李靜怡")
    parser.add_argument("--task", required=True, choices=list(TASKS.keys()),
                        help=f"任務名稱：{list(TASKS.keys())}")
    parser.add_argument("--screen", default=None,
                        help="畫面名稱（配合 screen-spec / flow-mapping 使用）")
    args = parser.parse_args()

    task = TASKS[args.task]
    screen_label = f"（{args.screen}）" if args.screen else ""
    print(f"[靜怡] 開始執行任務：{task['title']}{screen_label}")

    system_prompt = load_system_prompt()
    context = load_context_dir()
    ux_spec = load_ux_spec()
    relevant_gdds = load_relevant_gdds(args.task)

    context_block = ""
    if context:
        context_block += f"\n\n---\n\n【靜怡知識庫】\n\n{context}\n\n"
    if ux_spec:
        context_block += f"\n\n---\n\n【現有 UX Spec（待填項目）】\n\n{ux_spec}\n\n"
    if relevant_gdds:
        context_block += f"\n\n---\n\n【相關 GDD 參考】\n\n{relevant_gdds}\n\n"

    screen_section = ""
    if args.screen:
        screen_section = f"\n\n---\n\n【本次指定畫面/流程】：{args.screen}\n\n"

    user_prompt = (
        f"{context_block}"
        f"{screen_section}"
        f"\n\n---\n\n任務：\n{task['prompt']}"
    )

    result = None

    try:
        print("[靜怡] 呼叫 DeepSeek...")
        result = call_deepseek(system_prompt, user_prompt)
        print("[靜怡] DeepSeek 完成")
    except Exception as e:
        print(f"[靜怡] DeepSeek 失敗：{e}，切換 Qwen...")

    if not result:
        try:
            result = call_qwen(system_prompt, user_prompt)
            print("[靜怡] Qwen 完成")
        except Exception as e:
            print(f"[靜怡] Qwen 也失敗：{e}")
            sys.exit(1)

    filepath = save_spec(args.task, result, screen_name=args.screen)
    print(f"[靜怡] Spec 已存至：{filepath}")

    rel_path = os.path.relpath(filepath,
                               os.path.join(SCRIPT_DIR, "..")).replace("\\", "/")
    send_telegram(
        f"🎨 *靜怡 UX Spec 完成*\n\n"
        f"任務：{task['title']}{screen_label}\n"
        f"檔案：`{rel_path}`\n\n"
        f"請怡嘉審核後呈報製作人。"
    )
    print("[靜怡] Telegram 通知已發送")


if __name__ == "__main__":
    main()
