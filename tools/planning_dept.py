"""
策劃部門腳本 — 陳品霖
按需觸發，非夜間自動。DeepSeek 主力，Qwen 備援。
用法: python tools/planning_dept.py --task <任務名稱>
"""
import os
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
PROMPT_FILE = os.path.join(SCRIPT_DIR, "planning_dept_prompt.md")
GDD_FILE = os.path.join(SCRIPT_DIR, "..", "design", "gdd", "core-gdd.md")
QA_FILE = os.path.join(SCRIPT_DIR, "producer_qa.md")
DRAFTS_DIR = os.path.join(SCRIPT_DIR, "..", "design", "gdd", "drafts")

TASKS = {
    "concept-and-mindmap": {
        "title": "遊戲概念設計與系統腦圖",
        "prompt": """請輸出兩份內容：

## Part 1：《江湖一生》遊戲概念設計

包含以下要素：
1. **遊戲基本框架**：類型、平台、視角、核心機制一覽
2. **核心玩法**：玩家每天做什麼、一局遊戲怎麼進行、什麼讓玩家停不下來
3. **故事背景**：時代、世界觀、玩家身份、世界的運作規則
4. **四大核心支柱**：每個支柱用一段話說明它在遊戲中如何體現
5. **與競品的差異**：我們跟鬼谷八荒、龍胤立志傳的本質不同在哪

## Part 2：系統腦圖（Mermaid 格式）

用 Mermaid mindmap 或 graph 語法，畫出以下關係：
- 所有遊戲系統（成長、戰鬥、關係、陣營、世界感知、經濟、傳代等）
- 系統之間的依賴關係
- 每個系統目前的狀態（✅已設計 / 🔲待設計）

輸出格式：
- Part 1 用清晰的 Markdown
- Part 2 用 ```mermaid 代碼塊包住，確保語法正確可渲染

## 靜怡（UX）補充要求（務必納入）
Part 1 還需包含：
- **玩家情緒旅程曲線**：張力與釋放的節奏設計，不能讓自由度變成迷失感
- **關鍵決策的資訊原則**：投師、結義、仇恨這些選擇發生時，玩家能看到什麼、不能看到什麼
- **失敗與死亡後的回流體驗**：輸了之後玩家怎麼回到遊戲、情緒怎麼被接住
- **前15分鐘資訊密度控制**：哪些系統延後出現，避免新手被淹沒

這份文件給整個團隊看，讓所有人對這款遊戲有共同理解。"""
    },
    "sandbox-concept": {
        "title": "核心沙盒模擬概念文件",
        "prompt": """請輸出《江湖一生》的核心沙盒模擬概念文件。

這份文件的目的是把「沙盒世界活起來」這個目標，轉化為具體可執行的系統設計，讓程序和美術都知道要做什麼。

請按以下大綱完整輸出：

## 1. 設計目標
- 一句話定義「沙盒世界活起來」是什麼意思
- MVP驗證標準：玩家進入後能在多長時間內感受到「這個世界是活的」
- 非目標：MVP階段明確不做哪些事

## 2. NPC行為模型
- NPC的每日循環：具體活動類型（工作、練武、社交、閒逛等）及比例
- NPC的目標驅動：短期目標（今天做什麼）和長期目標（這輩子想要什麼）
- NPC的決策邏輯：如何根據屬性、關係、環境做選擇
- NPC的記憶系統：記得什麼、多久忘記

## 3. 人際關係動態
- 關係類型與初始狀態
- 關係變化觸發條件
- NPC之間自主互動的邏輯

## 4. 玩家行為→世界回應的完整鏈路
- 具體舉例：玩家做A，世界發生B、C、D
- MVP階段需要驗證的最小閉環

## 5. MVP沙盒範圍建議
- 初始NPC數量與類型
- 初始地點數量
- 初始事件類型（3-5種）
- 「活」的驗證標準

記住：需求先行，不要自我審查技術可行性。寫你認為好玩的、玩家會買單的設計。"""
    },
    "game-concept": {
        "title": "遊戲策劃概念文件",
        "prompt": """請以一個玩家和策劃的雙重視角，寫一份《江湖一生》的策劃概念文件。

這份文件的目的是讓整個製作團隊（美術、程序、策劃）在看完之後，腦子裡都有同一幅畫面：這是什麼遊戲、玩起來是什麼感覺、為什麼好玩。

不要寫系統規格，不要寫數值，不要寫技術需求。
寫的是：這款遊戲的靈魂是什麼。

【必須包含的內容】

1. **一段話描述**：如果你要向一個從來沒玩過武俠遊戲的朋友介紹這款遊戲，你會怎麼說？

2. **玩家的一天是什麼感覺**：具體描述玩家坐下來打開遊戲，在一個普通的下午，會經歷什麼？用敘事方式寫，不是條列系統。

3. **三個「讓玩家停不下來」的時刻**：這款遊戲裡，最讓玩家興奮、捨不得存檔關機的三種情境是什麼？舉具體例子，描述那個當下的感受。

4. **這款遊戲和競品的本質差異**：鬼谷八荒讓你爽，龍胤讓你模擬人生，那《江湖一生》讓你感受到什麼？用一句話說清楚。

5. **一個完整的「故事切片」**：用角色扮演的方式，描述一個玩家從零開始的前30分鐘可能發生的故事。要有選擇、後果、情感。

請用充滿畫面感的語言寫，讓讀者感覺自己身在其中。繁體中文。"""
    },
    "respond-to-qa": {
        "title": "回應製作人對焦紀錄",
        "prompt": """製作人已回答了你的8個問題，請讀取對焦紀錄後做以下三件事：

1. **確認收到**：用一段話說明你對這個專案現在的理解——我們在做什麼、為誰做、核心驗證目標是什麼。

2. **調整工作計劃**：根據製作人的回答，修正你上一份工作排序建議。哪些優先級要調整？哪些問題已經解答讓你可以往前走？

3. **提出下一步**：你認為現在最應該先輸出哪一份文件？說明理由，並列出這份文件需要包含的內容大綱。

注意製作人工作原則：需求先行，可行性後評。你的角色是提出好玩的設計，不是自我審查技術可不可行。"""
    },
    "work-plan": {
        "title": "策劃工作計劃",
        "prompt": """你是剛加入「江湖一生」專案的策劃陳品霖。製作人已完成大方向定義，GDD框架也有初步內容。

現在請你以一個資深策劃的角度，做以下兩件事：

【第一部分：了解現狀】
根據我提供的GDD摘要，評估目前這個專案處於哪個開發階段（立項期/研發前期/研發中期），
哪些策劃工作已完成、哪些缺少、哪些需要補充。

【第二部分：提出問題】
在你開始規劃工作之前，列出你需要向製作人確認的問題（5-10個），
這些問題是你作為策劃判斷接下來工作方向所必需的。
例如：目標受眾是誰？預計開發時長？MVP範圍是什麼？哪些系統是核心必做、哪些是後期可砍？

【第三部分：初步工作排序建議】
根據你的判斷，列出策劃部門接下來應該按什麼順序輸出哪些文件。
說明每份文件的目的和優先級。這份排序在製作人回答你的問題後可能會調整。

注意：這份文件的目的是讓製作人了解策劃部門的工作思路，不是最終決定。
有疑問就問，不要自己猜。"""
    },
    "numerical-design": {
        "title": "數值設計框架 V0.2",
        "prompt": """根據 system prompt 中的遊戲設定與已鎖定原則，起草數值設計框架修訂版，涵蓋以下六個項目。

【修訂指示】
- 屬性「根骨」改名為「資質」
- 境界評分門檻：參考龍胤立志傳的數值規模，把屬性值和評分區間放大（龍胤屬性通常到500-1000區間），讓數值有更細膩的成長感，四個境界稱號的門檻要對應這個放大後的規模
- 裝備品質改為七階，顏色標識：灰/白/綠/藍/紫/金/紅，每階取一個武俠風格的名稱（如「凡品」「精良」等），不要用通用遊戲術語
- 壽命：基準70歲，中位數偏差±5年，上下浮動範圍不超過±10年，額外增減留給遊戲中其他事件

【六個項目】
1. **屬性清單** — 7個核心屬性（武力/內力/體魄/輕功/資質/悟性/名聲），定義作用、初始值範圍、成長上限、影響面向
2. **境界稱號門檻** — 四個等級（江湖新丁/小有名氣/武林高手/一代宗師）的綜合評分公式與門檻，數值規模對齊龍胤立志傳
3. **壽命公式** — 基準70歲，體魄影響±10年浮動，附公式與範例
4. **鋸齒難度曲線** — 一局40-80小時，五個牆的位置/強度/間距
5. **裝備品質七階** — 灰/白/綠/藍/紫/金/紅，每階武俠命名、詞條條數、數值範圍
6. **世界感知傳播數值** — 傳播速率公式，距離衰減，名氣加速

參考中國武俠手遊的屬性規模與命名廣度，本作是PC單機，不引入任何手遊付費或膨脹設計。"""
    },
    "achievement-system": {
        "title": "成就系統設計（多維度稱號樹）",
        "prompt": """請為《江湖一生》設計完整的成就系統（稱號系統）。

核心原則：稱號不是單一等級線，而是多維度成就標籤系統。不同屬性、行為、事件對應不同稱號，玩家可同時持有多個來自不同維度的稱號。

請輸出以下內容：

## 1. 系統設計原則
- 稱號的作用：對NPC態度、可觸發內容、社會地位的影響
- 玩家同時持有多個稱號的表現方式

## 2. 稱號維度分類（至少6個維度）
每個維度包含：
- 維度名稱與說明
- 觸發條件（屬性門檻或行為累積）
- 3-5個具體稱號名稱（明朝武俠風格）
- 對應NPC反應

## 3. 特殊事件稱號（非屬性觸發）
- 至少10個由特定事件觸發的稱號
- 每個說明觸發條件與影響

## 4. 稱號衝突規則
- 哪些稱號互相排斥（如「正道盟主」vs「魔教教主」）

## 5. MVP範圍建議
- 哪些稱號必須在第一個版本實現

明朝洪武年間武俠風格，繁體中文輸出。"""
    },
    "martial-arts-system": {
        "title": "武學技能系統設計",
        "prompt": """請為《江湖一生》設計完整的武學技能系統。

已知前提：
- 裝備詞條系統採用暗黑式詞條×武俠語言包裝
- 7個核心屬性：武力/內力/體魄/輕功/資質/悟性/名聲
- 玩家自由選擇修煉路線（演習修煉+實戰修煉雙軌）

請輸出以下內容：

## 1. 武學分類體系
- 武學大類（如劍法、拳法、內功心法、輕功、暗器等）
- 每類的核心屬性關聯（練哪類長什麼屬性）

## 2. 武學學習機制
- 如何獲得武學（師父傳授、自行摸索、奪取、購買等）
- 屬性門檻：學某武學需要什麼基礎
- 熟練度系統：武學從「入門」到「大成」的成長

## 3. 武學品質層級
- 對應裝備七階（凡品→天工）
- 每個品質的特徵與稀有度

## 4. 武學組合與流派
- 同一流派的武學搭配加成
- 跨流派的特殊效果（如劍法+輕功的組合技）

## 5. MVP武學清單
- 至少10個具體武學名稱，包含：名稱、流派、屬性要求、效果描述（武俠語言）

## 6. 武學與NPC的互動
- 特定武學對特定NPC或門派的影響（如使用某派武學會影響與該派關係）

明朝洪武年間武俠風格，繁體中文輸出。"""
    },
    "faction-matrix": {
        "title": "陣營系統與衝突矩陣",
        "prompt": """請為《江湖一生》完善陣營系統，重點輸出陣營衝突矩陣。

已知框架：
- 陣營類型：武林正道門派、江湖幫會、邪派黑道、朝廷官府、隱世高人
- 朝廷 = 特殊門派，加入後與某些門派天然敵對
- 官位有上限，不能當皇帝或大將軍

請輸出以下內容：

## 1. 初始陣營清單（MVP可用，8-12個）
每個陣營包含：
- 名稱（符合明朝武俠風格）
- 類型
- 根據地
- 加入條件
- 主要特色（能給玩家什麼）

## 2. 陣營衝突矩陣
用表格形式列出各陣營間的關係：
- 友好（可同時加入或互助）
- 中立（無特殊影響）
- 敵對（加入一方則另一方天然敵視）
- 死敵（無法調和，必須選邊）

## 3. 加入與退出機制
- 加入條件（聲望/任務/拜師等）
- 退出代價（叛出門派的後果）
- 被開除的條件

## 4. 陣營間動態事件
- 3-5個陣營間會發生的週期性事件（如門派大比、聯盟/開戰）
- 玩家可介入的方式

明朝洪武年間武俠風格，繁體中文輸出。"""
    },
    "system-design": {
        "title": "單一系統 GDD 草稿",
        "prompt": """請為指定系統撰寫完整的 GDD 草稿。系統名稱和設計要求在任務說明的最後一段中指定。

輸出必須包含以下 8 個必要章節（這是不可省略的格式要求）：

## 1. 概述（Overview）
一段話說明這個系統是什麼、做什麼事。

## 2. 玩家體驗（Player Fantasy）
玩家使用這個系統時的感受和體驗目標。

## 3. 詳細規則（Detailed Rules）
無歧義的完整機制說明。每條規則要清楚到可以直接實現。

## 4. 公式（Formulas）
所有數學計算，包含：變數定義、公式、範例計算、數值取整規則。

## 5. 邊界條件（Edge Cases）
列舉所有特殊情況及處理方式（不能寫「合理處理」，要寫具體結果）。

## 6. 系統依賴（Dependencies）
這個系統依賴哪些其他系統？哪些系統會依賴它？

## 7. 可調參數（Tuning Knobs）
列出所有可以調整的數值，說明安全調整範圍和影響。

## 8. 驗收標準（Acceptance Criteria）
具體可測試的完成條件，QA 人員可以逐條驗證通過/失敗。

---
格式要求：
- 繁體中文
- 全程武俠語言，絕不使用修仙詞彙
- 數值必須具體（百分比、數字），不能模糊描述
- MVP 必做 vs V2 追加，在每節中標明
- 標注「[需測試]」的地方需說明測試方向""",
    },
    "competitor-analysis": {
        "title": "競品設計數據分析報告",
        "prompt": """你現在擁有來自競品遊戲的原始設計數據（已在上下文的【競品原始數據】區塊中提供）。

請從遊戲策劃的角度對這些數據進行分析，輸出以下內容：

## 1. 競品系統架構對照
列出從競品數據中識別出的所有系統，與《江湖一生》的設計逐一對照：
- ✅ 我們已有且設計相似
- ⚠️ 我們有但設計明顯不同（說明差異）
- ❌ 我們沒有（說明是否值得補充）

## 2. 數值設計啟示
- 競品使用的具體數值（百分比、門檻、區間）
- 對我們數值設計的具體參考建議
- 哪些數值設計值得借鑒、哪些應該避免

## 3. 技能/內容設計規律
- 競品的武學/技能命名模式與分層規律
- 對我們武學系統的具體設計建議（包括命名風格調整）

## 4. 我們 GDD 的設計空白
- 競品有但我們 GDD 未提及的重要機制（列舉每一個）
- 每項說明：是否適合武俠（非修仙）背景？如何適配？

## 5. 競品設計缺陷（我們要避免的）
- 競品數據中可見的設計問題
- 我們如何做得更好

## 6. 對現有 GDD 的具體修訂建議
- 列出需要補充的 GDD 章節與內容
- 列出需要調整的數值設計
- 列出建議新增的系統或機制

每個建議必須具體可執行，說明「為什麼」，不要泛泛而談。"""
    },
    "requirements-doc": {
        "title": "系統需求文檔（面向程序）",
        "prompt": """請根據GDD中已完成的系統設計，為程序輸出一份系統需求文檔。

目標讀者是程序，他們需要知道：做什麼、數據結構是什麼、如何配置、如何驗收。

請從 GDD 中選擇一個設計最完整的系統，按以下格式輸出：

## 系統名稱

### 一句話描述

### 功能邊界
- MVP 必須實現：（列點）
- V2 可追加：（列點）
- 明確不做：（列點）

### 數據結構
| 字段名 | 類型 | 說明 | 範圍/枚舉值 |
|-------|------|------|------------|
...

### 配置方式
策劃如何在外部配置表（JSON/資源文件）中配置此系統。說明：
- 配置文件位置
- 每個可配置參數的說明

### 核心邏輯（偽代碼）
```
輸入：...
計算過程：...
輸出：...
```

### 邊界條件
列出所有特殊情況和程序需要特別處理的 edge cases。

### 驗收標準
策劃如何在遊戲內確認這個功能做對了（具體的可觀察行為）。

注意：不指定技術方案，只描述「要什麼」。Godot 4.6 + GDScript 環境。"""
    },
    "world-locations": {
        "title": "世界地圖：城市與門派清單",
        "prompt": """請為《江湖一生》設計符合明朝洪武年間史實的初始世界地點清單。

已知框架：
- 時代：明朝洪武年間，元朝餘部在北方
- 地圖呈現：世界地圖+進入區域（參考龍胤立志傳）
- 初始規模：與龍胤立志傳相近，以中原內陸為主
- 內容優先原則：每個地區必須有事件鏈、NPC、獨特資源
- 應天府（南京）已確定為核心城市

請輸出以下內容：

## 1. 主要城市清單（8-12個）
每個城市包含：
- 城市名稱（真實明朝地名）
- 地理位置簡述
- 城市特色（商業/軍事/文化/武林）
- 初期可觸發的主要事件類型

## 2. 主要門派清單（6-8個，考慮陣營矩陣）
每個門派包含：
- 門派名稱（虛構但符合明朝武俠風格）
- 所在地區
- 武學流派（劍/拳/內功/輕功等）
- 在陣營系統中的類型
- 門派性格（正/邪/中立）

## 3. 特殊地點清單（4-6個）
- 古蹟、秘境、武林大會場所等
- 每個說明觸發條件與特色

## 4. 中後期解鎖地區預覽
- 海上/境外地區的概覽（有劇情才加的部分）

以明朝洪武年間真實地理為骨架，武俠風格填充，繁體中文輸出。"""
    }
}


def load_system_prompt():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def load_gdd_summary():
    """讀取完整GDD"""
    try:
        with open(GDD_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def load_producer_qa():
    """讀取製作人對焦紀錄"""
    try:
        with open(QA_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def load_context_file(path):
    """讀取額外上下文文件（競品數據、參考資料等）"""
    if not path:
        return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"[品霖] 無法讀取上下文文件 {path}：{e}")
        return ""


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
    """Qwen 備援，透過 Ollama"""
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


def save_draft(task_name, content, system_name=None):
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H%M%S")
    if system_name:
        filename = f"{task_name}-{date_str}-{time_str}.md"
    else:
        filename = f"{task_name}-{date_str}.md"
    filepath = os.path.join(DRAFTS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# 策劃草稿：{TASKS[task_name]['title']}\n")
        f.write(f"*陳品霖 | {date_str} | 狀態：待審核*\n\n---\n\n")
        f.write(content)
    return filepath


def main():
    parser = argparse.ArgumentParser(description="策劃部門 — 陳品霖")
    parser.add_argument("--task", required=True, choices=list(TASKS.keys()),
                        help=f"任務名稱：{list(TASKS.keys())}")
    parser.add_argument("--context-file", default=None,
                        help="額外上下文文件路徑（競品數據、參考資料等）")
    parser.add_argument("--system-name", default=None,
                        help="指定要設計的系統名稱（配合 system-design 任務使用）")
    args = parser.parse_args()

    task = TASKS[args.task]
    print(f"[品霖] 開始執行任務：{task['title']}")

    system_prompt = load_system_prompt()
    gdd_summary = load_gdd_summary()
    producer_qa = load_producer_qa()
    extra_context = load_context_file(args.context_file)

    context_section = ""
    if extra_context:
        context_section = f"\n\n---\n\n【競品原始數據】\n\n{extra_context}\n\n---\n\n"

    system_name_section = ""
    if args.system_name:
        system_name_section = f"\n\n---\n\n【本次任務指定系統】：{args.system_name}\n\n請針對以上系統輸出完整 GDD 草稿。\n\n"

    user_prompt = (
        f"以下是目前GDD的摘要供參考：\n\n{gdd_summary}\n\n---\n\n"
        f"以下是與製作人的對焦紀錄，請務必讀取並依據製作人的回答調整你的工作方向：\n\n{producer_qa}"
        f"{context_section}"
        f"{system_name_section}"
        f"\n\n---\n\n任務：\n{task['prompt']}"
    )

    result = None

    # DeepSeek 主力
    try:
        print("[品霖] 呼叫 DeepSeek...")
        result = call_deepseek(system_prompt, user_prompt)
        print("[品霖] DeepSeek 完成")
    except Exception as e:
        print(f"[品霖] DeepSeek 失敗：{e}，切換 Qwen...")

    # Qwen 備援
    if not result:
        try:
            result = call_qwen(system_prompt, user_prompt)
            print("[品霖] Qwen 完成")
        except Exception as e:
            print(f"[品霖] Qwen 也失敗：{e}")
            sys.exit(1)

    filepath = save_draft(args.task, result, system_name=args.system_name)
    print(f"[品霖] 草稿已存至：{filepath}")

    send_telegram(
        f"📋 *品霖策劃草稿完成*\n\n"
        f"任務：{task['title']}\n"
        f"檔案：`design/gdd/drafts/{os.path.basename(filepath)}`\n\n"
        f"請怡嘉審核後呈報製作人。"
    )
    print("[品霖] Telegram 通知已發送")


if __name__ == "__main__":
    main()
