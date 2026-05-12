# 江湖一生 — 任務系統 GDD
*策劃：陳品霖 | 版本：v3.0 | 審核：怡嘉 | 狀態：已審核 | 2026-05-12*
*系統編號：#19 | 層級：Feature（Vertical Slice）*
*依賴系統：#14 NPC行為、#12 經濟、#15 NPC關係、#16 世界感知*
*v3.0 修訂：依設計評審 P0 清單全面修訂，補齊 4 個未定義 Type、INVALIDATED 呈現規格、三項支柱違反修復、公式 bug 修復*

---

## 0. 設計過程摘要

**設計方法：** 本文件使用「情境先行」方法設計。先列出 20 個遊戲情境（而非從「任務類型」出發），再從情境差異中提取最小機制屬性集合，最後用 7 個邊界情境驗證規格覆蓋度，發現並修補 5 個規格漏洞後定稿。

**關鍵設計決定：**
- 任務不是「類型」的枚舉，而是**正交維度的組合**。一個任務就是一組維度值。
- 時間截止分為四種截止類型——因為「NPC日程繼續走」和「硬性失敗」是本質不同的兩種壓力。
- 任務失效（`INVALIDATED`）與任務失敗（`FAILED`）必須分開——前者是客觀不可完成，後者是玩家未能完成。
- `conflict_group` 允許同時持有矛盾承諾，在嘗試完成時才強制選邊。
- `objective_list` 在運行時可修改，MVP 支援最簡版（REPLACE_OBJECTIVE）。

**關鍵情境推導鏈：**
- 情境 12（七日藥材）→「強時限」截止類型
- 情境 9（燒焦密信）→「探索觸發」來源類型
- 情境 19（走私貨物）→ `branch_conditions` 多結果路徑
- 邊界情境 23 → `conflict_group`（任務矛盾承諾）
- 邊界情境 25 → `objective_list` 運行時可修改
- 邊界情境 27 → `objective_type = threshold`

---

## 1. 概述

任務系統（#19）是《江湖一生》中「玩家被要求去做某件事」的骨架機制。它負責管理任務的狀態生命週期（觸發→進行→完成/失敗/失效）、目標結構（單點/多點/分支/閾值）、時間壓力（無截止/硬截止/軟截止/狀態依賴），以及完成後果（資源獎勵 + 關係/世界變化事件廣播）。

本系統只定義任務的**骨架機制**。具體任務如何生成（#20 隨機事件系統）、任務中發生什麼對話和選項（#21 事件敘事系統）均不在本系統範圍內。

---

## 2. 玩家體驗

**核心情感：「我做的選擇，讓這個世界的某些事情發生或不發生了。」**

**MDA 目標情感：**
- **Fellowship（人際連結）：** 玩家幫助 NPC 解決真實困境，感受到自己的行動對 NPC 的生活有意義。
- **Narrative（故事推進）：** 每個任務都是這個世界正在發生的一個故事，玩家參與其中而非旁觀。
- **Challenge（挑戰感）：** 截止時限與時間老化系統的壓力——每次接受任務都是隱性的時間成本計算。

**刻意不追求的體驗：**
- 「做任務賺錢」的打工感——任務的核心動機是情境吸引力，獎勵是確認「值得」而非驅動力。
- 「任務清單收集完成感」——玩家應追求「這個選擇是我這一生的選擇」而非做完所有任務。

---

## 3. 詳細規則

### 3.1 任務資料結構

每個任務實例由以下正交維度屬性定義：

```
Task {
  // === 識別 ===
  task_id: String
  task_name: String
  conflict_group: String | null    // 矛盾承諾群組ID，同組可同時 ACTIVE，完成時才選邊

  // === 來源 ===
  source_type: Enum {
    NPC_CONTACT,       // NPC 主動接觸玩家
    BOARD_AUTO,        // 公告板系統自動生成
    EXPLORATION,       // 玩家進入特定位置觸發
    RELATION_TRIGGER,  // 關係值達門檻觸發
    HOSTILE_TRIGGER,   // 仇恨值達門檻觸發
    ENV_OBSTACLE       // 環境障礙型（NPC 媒介的世界障礙，見 3.3.1 說明）
  }
  source_entity_id: ID | null

  // === 目標 ===
  objective_list: Array<Objective>  // 支持運行時修改（MVP 支援 REPLACE_OBJECTIVE）
  objective_order: Enum { SEQUENTIAL, PARALLEL }
  branch_conditions: Array<BranchCondition> | null

  // === 時間 ===
  deadline_type: Enum {
    NONE,           // 無截止
    ABSOLUTE,       // 特定遊戲日期截止
    RELATIVE,       // 接受後 N 個遊戲日截止
    WORLD_STATE     // 特定世界狀態消失時截止
  }
  deadline_value: GameDate | Int | WorldStateCondition | null
  expiry_on_npc_death: Bool

  // === 後果 ===
  reward_bundle: {
    silver: Int,
    items: Array<ItemDrop>,
    relation_changes: Array<{npc_id, delta}>,
    reputation_changes: Array<{faction_id, delta}>
  }
  world_change_events: Array<EventID>
  failure_consequence: { world_change_events, relation_changes } | null

  // === 失效條件 ===
  invalidation_conditions: Array<InvalidationCondition>

  // === 狀態 ===
  status: Enum {
    DORMANT,       // 未觸發
    ACTIVE,        // 進行中
    COMPLETED,     // 玩家成功完成
    FAILED,        // 玩家未能在截止前完成
    INVALIDATED,   // 客觀條件消失，無法繼續（非玩家原因）
    ABANDONED      // 玩家主動放棄
  }
}
```

**Objective 子物件：**
```
Objective {
  objective_type: Enum {
    REACH_LOCATION, RETRIEVE_ITEM, DELIVER_ITEM,
    DEFEAT_TARGET, GATHER_INTEL, NEGOTIATE,
    THRESHOLD,      // 持續條件達成型
    MULTI_COLLECT   // 多點蒐集
  }
  target_id: ID | null
  required_item_id: ID | null
  threshold_condition: Condition | null
  is_completed: Bool
  is_optional: Bool
}
```

**InvalidationCondition 類型：**
- `NPC_DEAD`：目標或來源 NPC 死亡
- `ITEM_LOST`：必要道具丟失/損毀
- `WORLD_STATE_GONE`：依賴的世界狀態消失（引用 WorldStateCondition）
- `FACTION_LOST`：玩家失去陣營身份
- `DEADLINE_PASSED`：截止日超過
- `CONFLICT_RESOLVED`：conflict_group 內其他任務已完成（選邊後產生）

---

**BranchCondition 型別（B1）：**
```
BranchCondition {
  id: String
  eval_timing: Enum {
    ON_OBJECTIVE_COMPLETE,      // 某子目標完成時評估
    ON_DEADLINE_APPROACH,       // 截止日前 N 日評估
    ON_WORLD_STATE_CHANGE       // 世界狀態改變時評估
  }
  trigger_condition: Condition
  consequences: Array<BranchConsequence>
  priority: Int                 // 多條同時觸發時的優先序（1=最高）
}

BranchConsequence {
  type: Enum {
    REPLACE_OBJECTIVE,          // 替換目標（MVP 支援）
    ADD_OBJECTIVE,              // 追加目標
    REMOVE_OBJECTIVE,           // 移除指定目標
    CHANGE_DEADLINE,            // 變更截止日
    CHANGE_REWARD,              // 變更獎勵
    FORCE_COMPLETE,             // 任務立即完成（特殊劇情用）
    FORCE_FAIL                  // 任務立即失敗
  }
  payload: Objective | GameDate | RewardDelta | null
}
```

---

**WorldStateCondition 型別（B2）：**
```
WorldStateCondition {
  condition_type: Enum {
    WORLD_STATE_GONE, WORLD_STATE_ACTIVE,
    NPC_ALIVE, NPC_DEAD,
    FACTION_STATE, REGION_STATE, RELATION_THRESHOLD
  }
  target_id: String             // 監聽對象 ID
  operator: Enum { EQ, NEQ, GT, LT } | null
  value: String | Int | null
}
```

> **雙路徑說明：** `InvalidationCondition.WORLD_STATE_GONE` 是任務層的失效條件；`WorldStateCondition` 是可複用的條件型別，可用於任務觸發條件、分支觸發、NPC 行為判斷等。前者是後者的一種使用場景，兩者不構成功能重疊。實作層：`WORLD_STATE_GONE` 直接引用 `WorldStateCondition`，不重複定義。

---

**Condition 聯合型別（B3）：**
```
Condition {
  type: Enum {
    LOGIC_AND, LOGIC_OR, LOGIC_NOT,   // 邏輯組合
    WORLD_STATE,                       // 世界狀態
    PLAYER_ATTRIBUTE,                  // 玩家屬性
    NPC_RELATION,                      // NPC 關係值
    QUEST_STATUS,                      // 其他任務狀態
    TIME_ELAPSED,                      // 遊戲時間
    INVENTORY_CHECK                    // 背包檢查
  }
  sub_conditions: Array<Condition> | null   // LOGIC 型使用
  world_state:      WorldStateCondition | null
  player_attr:      { attribute: String, operator: Enum{GTE,LTE,EQ}, value: Int } | null
  npc_relation:     { npc_id: String, relation_type: String, operator: Enum{GTE,LTE,EQ}, threshold: Int } | null
  quest_status:     { quest_id: String, required_status: QuestStatus } | null
  time_elapsed:     { since_event: String, reference_id: String, elapsed_days: Int } | null
  inventory_check:  { item_id: String, operator: Enum{HAS,NOT_HAS,COUNT_GTE,COUNT_LTE}, count: Int | null } | null
}
```

---

### 3.2 任務狀態機

```
DORMANT → 觸發條件達成 → ACTIVE
ACTIVE → 所有目標達成 → COMPLETED → 廣播 world_change_events
ACTIVE → 截止日超過 → FAILED → 廣播 failure_consequence
ACTIVE → 失效條件達成 → INVALIDATED（不廣播 failure_consequence）
ACTIVE → 玩家放棄 → ABANDONED → 廣播 abandoned_consequence（見 3.6）
```

**關鍵規則：**
1. 所有終態（COMPLETED/FAILED/INVALIDATED/ABANDONED）不可逆轉。
2. `conflict_group` 非空時：組內任一任務 COMPLETED，其餘立即 INVALIDATED（原因：CONFLICT_RESOLVED）。
3. `INVALIDATED ≠ FAILED`——失效是客觀不可完成（NPC 去世/世界改變），不廣播失敗後果。
4. DORMANT 狀態的任務，其失效條件也持續被監聽。
5. ABANDONED 強制後果（見 3.6）不可跳過。

---

### 3.3 任務創建與注冊機制（B4）

#### 3.3.1 任務創建來源與 DORMANT 池位置

所有任務在玩家接受前起點為 DORMANT 狀態。各 source_type 的創建機制：

| source_type | 創建時機 | 創建者 | DORMANT 池位置 |
|---|---|---|---|
| NPC_CONTACT | NPC 生成時／劇情節點解鎖時注入 | NPC 任務池管理器 | NPC 個人任務表 |
| BOARD_AUTO | 懸賞板定時刷新（預設每 7 日） | 懸賞板系統 | 城鎮懸賞板任務池 |
| EXPLORATION | 玩家進入特定區域時即時生成 | 探索事件生成器 | 區域任務緩存 |
| RELATION_TRIGGER | 玩家與 NPC 關係值跨越閾值時 | 關係事件監聽器 | NPC 任務表 |
| HOSTILE_TRIGGER | 敵對勢力動態生成 | 敵對勢力 AI | 勢力任務池 |
| ENV_OBSTACLE | 環境事件發生時，由**受影響的 NPC** 生成委託 | NPC 行為系統 | NPC 任務表 |

> **ENV_OBSTACLE 說明：** 道路封鎖、水患、匪患等環境障礙，必須透過受影響的 NPC（嚮導、商人、難民）作為媒介生成任務。「世界障礙產生任務」必須有人在推動，符合「江湖有人」支柱。不允許純環境無媒介直接生成任務。

#### 3.3.2 任務注冊介面契約

所有任務創建者遵守以下介面：

```
TaskRegistrar {
  register_task(task: Task) → Result<TaskId, RegistrationError>
  register_with_visibility(task: Task, visible_when: Condition) → Result<TaskId, RegistrationError>
  register_batch(tasks: Array<Task>) → Array<Result<TaskId, RegistrationError>>
}
```

#### 3.3.3 DORMANT 期間行為規格

- **可見性：** DORMANT 任務預設不可見。若有 `visible_when` 條件，條件滿足時對玩家顯示為「可接受」。
- **到期清理：** DORMANT 任務超過 deadline 後最長保留 7 遊戲日，之後從池中移除（不進結算）。
- **衝突預檢：** 玩家接受任務前，系統檢查 `conflict_group` 但**不阻止接受**（允許同時持有矛盾承諾）。

---

### 3.4 截止時間規則

| deadline_type | 截止計算方式 |
|--------------|------------|
| NONE | 無截止，但 `expiry_on_npc_death` 可形成軟截止 |
| ABSOLUTE | 特定遊戲日期，每次日結算時檢查 |
| RELATIVE | 接受日期 + `deadline_value` 天數 |
| WORLD_STATE | 依賴的 WorldStateCondition 消失時立即 INVALIDATED |

**軟截止設計：** `deadline_type = NONE` + `expiry_on_npc_death = true` → NPC 死亡時自動 INVALIDATED，時間壓力來自世界本身，非系統設定。

---

### 3.5 動態目標修改

`objective_list` 在任務 ACTIVE 期間可透過事件總線（#35）發送 `task_modify_objective` 事件修改：
- `REPLACE_OBJECTIVE`：替換現有子目標（**MVP 必須支援**）
- `APPEND_OBJECTIVE`：追加新子目標（V2）
- `REMOVE_OBJECTIVE`：移除子目標（V2）

> **MVP 範圍說明：** MVP 只需支援 `REPLACE_OBJECTIVE`，即「中途發現真相、改寫目標」這一核心武俠敘事時刻。`APPEND` 和 `REMOVE` 可延至 V2。

---

### 3.6 任務矛盾承諾群組（conflict_group）— B6-2

#### 規則

**3A. 接受不衝突：**
玩家可以同時接受 `conflict_group` 內的多個任務，使其均進入 ACTIVE 狀態。接受時**不**觸發任何 INVALIDATED 判定。設計意圖：讓玩家帶著矛盾承諾前行，張力在整個執行過程中存在。

**3B. 完成即選邊（核心衝突解決時機）：**
當玩家嘗試完成 `conflict_group` 內任一任務的任一 Objective 時（嘗試提交/交付/回報的瞬間），系統觸發「選邊檢查」：
- 彈出敘事選擇介面，列舉 conflict_group 內所有 ACTIVE 任務
- 玩家選擇「繼續完成 [當前任務]」→ 其餘全部 INVALIDATED（原因：CONFLICT_RESOLVED）
- 玩家選擇「放棄 [當前任務]」→ 當前任務 ABANDONED，其他任務保持 ACTIVE
- 此選擇不可撤回

**3C. 選邊後果：**
- 被 INVALIDATED（CONFLICT_RESOLVED）的任務 NPC：套用 ABANDONED 等級的聲望後果（-5 點），生成記憶台詞規格（#21 填充內容：「我知道你選了[X]，這是你的選擇。」）
- 被 ABANDONED 的任務：套用完整 ABANDONED 後果（見 3.6 ABANDONED 後果規格）

**3D. 自然解決例外：**
若在選邊前，conflict_group 內任務因 deadline 到達或世界狀態變化自然 FAILED 或 INVALIDATED，則不觸發選邊機制，按正常流程處理。

**3E. 同幀完成衝突（E2 更新）：**
若兩個 conflict_group 任務因腳本事件在同幀同時嘗試完成，以事件佇列中 task_id 字母序較小者優先進入選邊流程，另一個暫緩至下幀。

---

### 3.7 ABANDONED 後果規格（B6-1）

ABANDONED 是玩家主動放棄承諾，**不得零後果**。強制後果（不可跳過）：

```
ABANDONED 強制後果：
- 委託 NPC 聲望扣減：-10 點（基礎值，可依任務重要度在 config 調整）
- conflict_group 內其他任務 NPC 聲望扣減：-5 點（若有）
- 記錄世界記憶事件：「[玩家名]於[時間]背棄了對[NPC名]的承諾」
- 委託 NPC 30 遊戲日內拒絕向此玩家提供新任務
- NPC 記憶台詞規格（#21 填充）：「[玩家名]曾答應過我，卻沒了下文。」

例外：BOARD_AUTO 來源的任務 ABANDONED，免除 NPC 後果，改為：
- 懸賞板聲望扣減：-3 點
- 該懸賞板任務類型冷卻 14 日
```

廣播事件：`quest_abandoned(task_id, source_entity_id, reason)`

---

### 3.8 INVALIDATED 玩家感知規格（B5）— 介面契約，#21 填充內容

> **介面契約說明：** 本節定義任務系統對外廣播的感知規格坑位，具體文案與敘事內容由 #21 事件敘事系統依此契約填充。

#### 3.8.1 失效時刻即時通知規格

| 規格項目 | 要求 |
|---------|------|
| 通知標籤 | `[失效]`（灰色 #888888，區別於失敗的暗紅 #CC3333） |
| 通知圖示 | 時鐘停止圖示（⏳🚫），不使用失敗圖示（❌） |
| 通知文字格式 | `[任務名] 已因世事變遷而不再可行` |
| 失效原因分類（#21 填充文案） | NPC_DEAD / WORLD_STATE_GONE / CONFLICT_RESOLVED / DEADLINE_EXPIRED_DORMANT |
| 可重新激活 | 否 |

#### 3.8.2 結算畫面三種遺憾分類

結算畫面（壽命歸零）依終態分三區塊展示：

| 任務終態 | 結算分類標題 | 敘事基調 |
|---------|------------|---------|
| FAILED | 「失諾之事」| 這些是你承諾過卻未能做到的。江湖記得你的失信。 |
| INVALIDATED | 「無緣之事」| 這些是世事變化讓它們再無可能的。江湖無聲地帶走了這些機會。 |
| ABANDONED | 「辜負之事」| 這些是你選擇放手的。有人記得你的轉身，在心底留下了裂痕。 |

---

### 3.9 後果廣播規則

- 任務 COMPLETED → 分配 `reward_bundle` + 廣播 `world_change_events`
- 任務 FAILED → 廣播 `failure_consequence.world_change_events`（若有）
- 任務 INVALIDATED → 廣播 `quest_invalidated(task_id, reason)`，**不**觸發 `failure_consequence`
- 任務 ABANDONED → 廣播 `quest_abandoned`，套用 3.7 強制後果

---

### 3.10 玩家可見資訊規則

| 資訊 | 可見性 | 設計意圖 |
|------|--------|---------|
| 任務名稱/說明 | 接受後可見 | |
| 截止日期 | 顯示「距截止約N日」| 不顯示精確日期，保留不確定感 |
| WORLD_STATE 截止 | 只顯示「依賴當前局勢」| 鼓勵玩家自行感知世界 |
| 失效條件清單 | 不顯示 | 玩家應自然感知 |
| 失敗後果 | 不事先顯示 | 增加選擇的重量 |
| 速度獎勵倍率公式 | 不顯示精確數值 | 防止玩家優化任務隊列；只顯示敘事結果（「委託人對你迅速行事十分感激」） |

---

## 4. 公式

### 4.1 截止日計算（RELATIVE 型）

```
deadline_date = acceptance_date + deadline_days
```

範例：第 842 天接受，`deadline_days = 7` → 截止日 = 第 849 天

### 4.2 速度獎勵計算（可選，需任務配置標記 apply_speed_bonus = true）— B7

> **設計限制：** `apply_speed_bonus = true` 應為稀有標記，僅用於高情境強度任務（如「孩子高燒今天就要找大夫」），不是常態任務的預設設定。

```
// 修訂公式（修復除零、引用 config param、加 clamp）
speed_bonus_multiplier(base_reputation, days_remaining, deadline_days):
  if deadline_days <= 0:
    return speed_bonus_max_multiplier   // 保護：無效截止日視為全速完成

  ratio = days_remaining / deadline_days
  raw = 1.0 + ratio × speed_bonus_curve_factor

  return clamp(raw, speed_bonus_min_multiplier, speed_bonus_max_multiplier)

reputation_reward = floor(base_reputation × speed_bonus_multiplier(...))
```

**變數定義：**

| 變數 | 說明 | 範圍 |
|------|------|------|
| `base_reputation` | 任務設定的基礎聲望獎勵 | 0–500 |
| `days_remaining` | 截止日 - 完成日（完成當天為 0） | 0 以上（任務 FAILED 後不適用）|
| `deadline_days` | 接受至截止的總天數 | **> 0**（由 3.3.3 保護） |

**範例：** `base_reputation = 20`，`deadline_days = 7`，第 4 天完成（剩餘 3 天）：
→ `raw = 1.0 + (3/7) × 0.5 = 1.214`
→ `clamp(1.214, 0.5, 1.5) = 1.214`
→ `reputation_reward = floor(20 × 1.214) = 24`

---

## 5. 邊界條件

| 編號 | 情境 | 處理方式 |
|-----|------|---------|
| E1 | 任務 ACTIVE 期間目標 NPC 死亡 | 監聽 `npc_died` 事件，同幀觸發失效轉態，最遲下次日結算完成 |
| E2 | conflict_group 同幀同時嘗試完成 | 事件佇列中 task_id 字母序較小者優先進入選邊流程，另一個下幀處理 |
| E3 | 玩家丟棄任務必要道具 | 顯示警告「此道具關聯進行中任務，確定丟棄？」，確認後任務 INVALIDATED |
| E4 | RELATIVE 截止，玩家長期未登入 | 以遊戲內日期計算，不受現實時間影響 |
| E5 | MULTI_COLLECT 子目標的 NPC 死亡 | is_optional=true 跳過；is_optional=false 整個任務 INVALIDATED |
| E6 | 玩家失去陣營身份，陣營任務進行中 | 若 invalidation_conditions 含 FACTION_LOST，立即 INVALIDATED |
| E7 | 超過 max_active_tasks 上限 | 新任務保持 DORMANT，UI 顯示「身負要事過多，無暇接受新委託」 |
| E8 | THRESHOLD 目標在接受前已達成 | 接受時立即標記 is_completed = true，跳過等待 |
| E9 | 截止日與死亡發生同日 — B8 | 執行順序：日常結算 → **死亡判定** → 若存活：截止日檢查；若死亡：跳過截止日 FAILED，所有 ACTIVE 進「未竟之事」結算 → 老化結算（若存活）→ 死亡時觸發結算畫面 |
| E10 | 壽命歸零時有進行中任務 — B8 | 所有 ACTIVE 任務不轉 FAILED，依 3.8.2 三種分類進結算畫面。死亡當日 deadline 到期的任務歸入「辜負之事」而非「失諾之事」 |
| E11 | DELIVER_ITEM 型任務失敗時道具歸屬 | 道具**留在玩家身上**。懲罰已由聲望扣減（-10）與 NPC 關係後果覆蓋，道具額外沒收屬於雙重懲罰。武俠邏輯：藥材找到了卻沒送達，藥還在你手上——這是你的遺憾，不是徵收。|

---

## 6. 系統依賴

### 本系統依賴的系統

| 系統 | 編號 | 依賴內容 | MVP/V2 |
|------|------|---------|--------|
| 時間與老化系統 | #1 | 當前遊戲日期；觸發日結算截止檢查；死亡判定 | MVP |
| 經濟系統 | #12 | 接收銀兩分配請求 | MVP |
| NPC行為系統 | #14 | NPC當前狀態；監聽 npc_died 事件；接收 ABANDONED 後果廣播 | MVP |
| NPC人際關係系統 | #15 | 發放/扣除關係值；讀取關係門檻；接收 ABANDONED 聲望扣減 | MVP |
| 世界感知系統 | #16 | 世界狀態（WorldStateCondition 監聽）| MVP |
| 事件總線 | #35 | 所有事件廣播和監聽 | MVP |
| 庫存管理系統 | #13 | 道具分配；監聽 item_removed 事件 | MVP |
| 隨機事件系統 | #20 | 向本系統提交任務資料結構（透過 TaskRegistrar 介面） | VS |
| 事件敘事系統 | #21 | 填充 3.8.1/3.8.2 感知規格；動態目標修改事件；conflict_group 選邊介面 | VS |

### 本系統對外廣播的事件

| 事件 | 觸發時機 |
|-----|---------|
| `quest_completed(task_id, source_entity_id)` | 玩家成功完成 |
| `quest_failed(task_id, reason)` | 截止日超過 |
| `quest_invalidated(task_id, reason)` | 客觀失效 |
| `quest_abandoned(task_id, source_entity_id, reason)` | 玩家主動放棄 |
| `quest_deadline_warning(task_id, days_remaining)` | 距截止≤3日 |

---

## 7. 可調參數

**外部化至：`assets/data/quest-system/config.json`**

| 參數 | 預設值 | 安全範圍 | 影響 |
|-----|-------|---------|------|
| `max_active_tasks_base` | **5** | 3–8 | 角色初始可承接的任務基礎數量（見下方解鎖系統） |
| `max_active_tasks_cap` | **15** | 10–20 | 任何解鎖方式的硬上限 |
| `speed_bonus_max_multiplier` | **1.5** | 1.2–3.0 | 速度獎勵上限 |
| `speed_bonus_min_multiplier` | **0.5** | 0.1–0.8 | 速度獎勵下限 |
| `speed_bonus_curve_factor` | **0.5** | 0.1–2.0 | 速度獎勵曲線陡峭度 |
| `deadline_warning_days` | **3** | 1–5 | 幾天前開始顯示截止警告 |
| `invalidation_item_warning` | **true** | — | 丟棄關聯道具時是否顯示警告 |
| `abandoned_reputation_penalty` | **-10** | -30 至 -3 | ABANDONED 聲望扣減基礎值 |
| `abandoned_npc_cooldown_days` | **30** | 7–90 | ABANDONED 後 NPC 拒絕新任務的天數 |

### max_active_tasks 屬性解鎖系統（B6-3）

基礎值 5，透過以下方式解鎖，上限 15：

**聲望解鎖（可疊加）：**
- 地區聲望達「小有名氣」→ +2
- 地區聲望達「名動一方」→ +3（累計 +5）
- 地區聲望達「江湖傳奇」→ +5（累計 +10）

**閱歷解鎖（可疊加）：**
- 完成任務總數達 20 → +1
- 完成任務總數達 50 → +2（累計 +3）

**特殊解鎖（一次性）：**
- 獲得稱號「信義之人」（完成 10 次無 deadline 超時的任務）→ +2
- 結識核心 NPC「商會會長」且好感度達 60 → +2

---

## 8. 驗收標準

| 編號 | 驗收項目 | 預期結果 | 阻斷 |
|-----|---------|---------|-----|
| AC1 | 狀態機基本流轉 | DORMANT → 觸發條件達成 → ACTIVE | 是 |
| AC2 | RELATIVE 截止計算 | 第100天接受7日任務，第107天日結算轉 FAILED | 是 |
| AC3 | 截止前完成不失敗 | 第106天完成 → COMPLETED，不觸發 FAILED | 是 |
| AC4 | NPC 死亡觸發失效 | expiry_on_npc_death=true，NPC 死亡 → INVALIDATED | 是 |
| AC5 | 道具丟失警告 | 丟棄關聯道具顯示確認彈窗，確認後 INVALIDATED | 是 |
| AC6 | conflict_group 同時接受 | A、B 同屬 conflict_group，可同時為 ACTIVE | 是 |
| AC6-B | conflict_group 選邊 | 嘗試完成 A 時，彈出選邊介面；確認後 A→COMPLETED，B→INVALIDATED(CONFLICT_RESOLVED) | 是 |
| AC7 | 失效不廣播失敗後果 | NPC 死亡致 INVALIDATED，failure_consequence 不廣播 | 是 |
| AC8 | 完成事件廣播 | COMPLETED 時，world_change_events 廣播到 #35 | 是 |
| AC9 | 達到 max_active_tasks 基礎值 | 5個ACTIVE後接第6個，任務保持DORMANT，顯示「身負要事過多」 | 是 |
| AC10-A | 結算「失諾之事」 | 死亡時 FAILED 任務顯示於結算第一區塊「失諾之事」 | 是 |
| AC10-B | 結算「無緣之事」 | 死亡時 INVALIDATED 任務顯示於結算第二區塊「無緣之事」 | 是 |
| AC10-C | 結算「辜負之事」 | 死亡時 ABANDONED 任務顯示於結算第三區塊「辜負之事」 | 是 |
| AC11 | 終態不可逆 | 嘗試將COMPLETED改回ACTIVE，系統拒絕 | 是 |
| AC12 | THRESHOLD 接受前已達成 | 接受任務時子目標立即 is_completed=true | 是 |
| AC13 | ABANDONED 強制後果 | ABANDONED 任務觸發 -10 聲望扣減，且委託 NPC 30日內拒絕新任務 | 是 |
| AC14 | 死亡日任務不進 FAILED | 角色死亡當日有截止的 ACTIVE 任務，進「辜負之事」而非「失諾之事」 | 是 |
| AC15 | 速度獎勵公式邊界（deadline=1日當天完成） | days_remaining=0, deadline_days=1 → multiplier = clamp(1.0, 0.5, 1.5) = 1.0 | 否 |
| AC16 | 速度獎勵公式保護（deadline_days=0）| multiplier 回傳 speed_bonus_max_multiplier，不拋除零異常 | 是 |

---

*品霖設計備註：*

*「失效」和「失敗」的分開，是這份設計最重要的用心。武俠世界裡，很多事情不是你做得不夠好，而是時不我與——一個任務因為老翁在你找到藥材之前就去世了而變成「失效」，那種感受和「你沒有在截止日前完成」完全不同。前者是人生的無常，後者才是玩家的失誤。把這兩種情感分開處理，才是真正的武俠沙盒設計。*

*v3.0 新增備註：「辜負之事」三字的分類，讓死亡結算畫面不再是一份任務失敗清單，而是玩家這一生承諾與選擇的側寫。三種遺憾對應三種截然不同的人生態度——失信、無緣、辜負——武俠世界的人生豈能只有成敗二字。*
