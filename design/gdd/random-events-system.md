# 江湖一生 — 隨機事件系統 GDD
*策劃：陳品霖 | 版本：v1.1 | 狀態：修訂中 | 2026-05-12*
*系統編號：#20 | 層級：Feature（Vertical Slice）*
*設計方法：情境先行 — 20情境→7屬性→規格*
*依賴系統：#14 NPC行為、#15 NPC關係、#16 世界感知、#1 時間與老化、#19 任務系統、#47 身份印刻（待設計）*
*v1.1 修訂：依設計評審補齊 4 個未定義型別、MVP 邊界、依賴更新、AC7 機制化*

---

## 1. 概述

隨機事件系統是《江湖一生》世界動態演進的核心引擎，它負責在遊戲進程中基於玩家狀態、世界狀態、NPC 意志與既定因果，即時生成有意義的遭遇。有別於傳統的無上下文隨機遭遇，本系統貫徹七項底層機制屬性——因果餘波、身份印刻、關係張力、信息迷霧、世界剛性、NPC 主體性與時空節點——使得每個事件都是世界對玩家行為的迴響，而非孤立雜訊。

系統採取 Severity 連續值評估、修飾詞疊加權重、資料驅動的條件判定，確保觸發邏輯透明、可調且具備敘事深度。所有事件模板均標註 MVP 或 V2 分級，保證交付節奏。

---

## 2. 玩家體驗

- **因果的重量感**：玩家在過去幫助過的乞丐，可能在數日後於另一城鎮遞來救命情報；曾袖手旁觀的劫鏢，最終導致熟識的鏢師死亡。世界記得玩家的選擇。
- **身份被世界辨識**：身上的門派徽記、官府通緝令、邪教暗語會改變 NPC 的態度，甚至引來追殺或求援。玩家行走江湖時，身份不僅是數值，更是事件觸媒。
- **關係的動態拉扯**：與 NPC 的恩怨情仇會積累張力值，高張力可能觸發 NPC 的告白、背叛或復仇。玩家感受到 NPC 是擁有記憶與目標的個體。
- **信息的不對稱**：玩家可能因為掌握一個秘密而避開陷阱，也可能因聽信謠言而踏入圈套。事件揭露的真相與謊言，會重塑玩家對世界的認知。
- **無法回頭的選擇**：殺死一名 NPC 或燒毀一座村莊是永久不可逆的，世界剛性讓每一次決定都充滿後果感。
- **時空編織的舞台**：中秋月圓、華山之巔這類時空節點會強制觸發關鍵事件，形成江湖傳說的「大事件」節奏，確保世界因聚集而沸騰。

---

## 3. 詳細規則

### 3.1 資料結構

隨機事件系統核心由「事件模板」與「事件實例」構成，由事件管理器統一調度。所有欄位標示支撐的七屬性（縮寫：餘波／印刻／張力／迷霧／剛性／NPC主／節點）。

#### EventTemplate（事件模板）

| 欄位 | 類型 | 說明 | 屬性對映 |
|------|------|------|---------|
| template_id | String | 唯一模板ID，如 `EVT_CHIVALROUS_RESCUE` | — |
| tier | Enum | MVP / V2 | — |
| trigger_condition | ConditionTree | 觸發條件樹（詳見 3.2）| 全部 |
| base_weight | Float | 基礎觸發權重 (0–1)，作為 Severity 計算起點 | — |
| modifiers | Modifier[] | 權重修飾詞列表，各類世界狀態轉化為權重增減 | 全部 |
| narrative_pool | NarrativeVariant[] | 事件敘述變體池，支持依參數動態替換 | 迷霧 |
| choices | ChoiceBranch[] | 玩家選擇分支，每分支攜帶效果集合 | — |
| cooldown_hours | Int | 全局冷卻（遊戲內小時），避免同一模板濫觸 | — |
| max_instances | Int | 同一時間此模板最大並行實例數 | — |
| required_systems | String[] | 依賴的系統模組，如 `["identity", "relationship"]` | — |

#### EventInstance（事件實例）

| 欄位 | 類型 | 說明 | 屬性對映 |
|------|------|------|---------|
| instance_id | String | 唯一實例ID | — |
| template_ref | String | 對應模板ID | — |
| bindings | Dict<String, ID> | 具體綁定：npc_id, location_id, item_id 等 | 印刻、張力、節點 |
| time_window | TimeWindow | 可觸發的時間範圍（null 表示隨時）| 節點 |
| severity_value | Float | 經修飾詞計算後的當前觸發 Severity (0–1) | 全部 |
| status | Enum | pending / active / completed / expired | — |
| causal_chain | CausalLink | 因果鏈：前置事件 ID + 後效標記 | 餘波 |
| player_awareness | AwarenessLevel | 玩家是否感知此事件正在醞釀 | 迷霧 |

#### ConditionTree 結構

遞迴定義：

```
ConditionNode = AndNode | OrNode | NotNode | LeafCondition

LeafCondition = {
  type: "identity_check"       // 身份印刻：檢查 tag
         | "relationship_check" // 關係張力：關係數值門檻
         | "npc_goal_check"     // NPC主體性：NPC 是否具有目標
         | "time_check"         // 時空節點：時間窗口
         | "location_check"     // 時空節點：地點
         | "world_state_check"  // 世界剛性：永久狀態
         | "secret_known_check" // 信息迷霧：玩家是否已知秘密
         | "previous_event_check" // 因果餘波：前置事件是否完成
  params: {...}                 // 各類型具體參數
}
```

#### Modifier 結構

```json
{
  "source": "identity_tag" | "relationship" | "npc_memory" | "rumor_presence" | ...,
  "effect": "multiply" | "add" | "threshold_boost",
  "value": float,
  "condition": ConditionLeaf
}
```

修飾詞疊加採用：`基礎權重 × Π乘法修飾詞 + Σ加法修飾詞`，最後 clamp(0, 1)。`threshold_boost` 直接設定 Severity = 1.0（強制觸發）。

#### 效果集合（EffectSet）

每個選擇分支定義一系列效果原子，覆蓋全部七屬性操作：

| 效果類型 | 說明 | 屬性 |
|---------|------|------|
| `add_identity_tag` / `remove_identity_tag` | 給實體加/移除標記 | 印刻 |
| `modify_relationship` | 增減關係數值 | 張力 |
| `reveal_secret` / `spawn_rumor` | 揭露秘密 / 製造謠言 | 迷霧 |
| `set_world_state` / `kill_npc` / `destroy_location` | 永久改變世界狀態 | 剛性 |
| `set_npc_goal` / `add_npc_memory` | 更新 NPC 目標與記憶 | NPC主 |
| `add_causal_mark` | 新增因果標記（可觸發後續事件） | 餘波 |
| `force_event` | 強制觸發特定事件（時空強制鏈接）| 節點 |

效果可設定**延遲觸發**（delay_days），支撐因果餘波。

---

#### 輔助型別定義（B2）

**CausalLink（因果鏈連結）：**
```
CausalLink {
  source_event_id: String | null    // 觸發本實例的前置事件 ID（null = 首發）
  causal_mark_ids: String[]         // 本事件完成後產生的因果標記 ID 列表
  chain_depth: Int                  // 因果鏈深度（首發=0，每傳一代+1），防止無限遞迴
  is_critical: Bool                 // 若 true，當實例池滿時此實例不被刪除
}
```

**TimeWindow（時間窗口）：**
```
TimeWindow {
  type: Enum { GAME_DAY_RANGE, FESTIVAL, TIME_OF_DAY, OPEN }
  start_day: Int | null             // GAME_DAY_RANGE 用
  end_day: Int | null               // GAME_DAY_RANGE 用
  festival_id: String | null        // FESTIVAL 用（如 "MID_AUTUMN"）
  time_of_day: Enum { DAWN, MORNING, NOON, AFTERNOON, DUSK, NIGHT, MIDNIGHT } | null
  // OPEN = 無時間限制
}
```

**NarrativeVariant（敘述變體）：**
```
NarrativeVariant {
  variant_id: String
  template_text: String             // 包含 {npc_name}、{location_name} 等佔位符
  required_bindings: String[]       // 此變體需要 bindings 中有哪些 key
  tone: Enum { NEUTRAL, TENSE, HUMOROUS, SORROWFUL }
}
```
敘述渲染時：從 `narrative_pool` 中選取所有 `required_bindings` 均在 `EventInstance.bindings` 中存在的變體，依 tone 篩選後隨機取一條，將佔位符替換為 bindings 的實際值。

**AwarenessLevel（玩家感知級別）：**
```
AwarenessLevel: Enum {
  HIDDEN,          // 玩家完全不知道事件正在醞釀（預設）
  HINT,            // 玩家收到模糊提示（如「你感覺有人在跟蹤你」）
  VISIBLE          // 玩家可在任務/事件日誌中看到「有事即將發生」的提示
}
```

---

### 3.2 事件觸發流程

**步驟一：實例生成時機**

系統在以下時機將模板實例化並放入待評估池：
- 玩家進入新場景（檢測 location_check 相關模板）
- 遊戲時間推進（定時掃描所有模板，符合時間窗的生成實例）
- 某因果標記被激活（鏈式生成後續事件實例）
- NPC 目標更新（NPC主相關模板）

**步驟二：Severity 計算（每遊戲小時）**

```
raw = template.base_weight
for mod in template.modifiers:
  if mod.condition is met:
    if mod.effect == "multiply": raw *= mod.value
    elif mod.effect == "add":    raw += mod.value
    elif mod.effect == "threshold_boost": return 1.0  // 強制觸發，跳出

severity = clamp(raw, 0.0, 1.0)
```

**步驟三：觸發判定**

- `severity >= global_trigger_threshold`（預設 0.8）→ 觸發，狀態改為 `active`
- 多個同時達標 → 依 severity 降序排列，每遊戲小時最多觸發 `max_events_per_hour`（預設 3）個

**步驟四：過期處理**

超過時間窗口未觸發 → `expired`。重要因果實例可轉為永久背景影響，或轉化為另一模板的觸發條件（餘波不滅）。

**步驟五：玩家交互**

`active` 事件以對話/敘述呈現，玩家選擇後執行 EffectSet，實例狀態改為 `completed`，並根據效果生成新因果標記或更新世界狀態。

---

### 3.2.1 MVP 核心機制範圍（B3）

| 功能 | MVP 必須 | V2 追加 |
|------|---------|--------|
| ConditionTree 葉節點類型 | `relationship_check`、`location_check`、`time_check`、`previous_event_check`（4種）| `identity_check`（依賴 #47）、`world_state_check`、`secret_known_check`、`npc_goal_check`（4種）|
| Severity 計算 | 完整公式（乘法 + 加法 + threshold_boost）| — |
| causal_chain 機制 | 1 代鏈（source_event_id + causal_mark_ids）| 多代鏈（chain_depth > 1）防迴圈 |
| NPC 主體性事件 | 靜態「NPC 主動接觸」觸發（source_type = NPC_CONTACT）| 動態 NPC 目標生成事件模板 |
| 最大 pending 實例 | **50**（MVP 輕量）| 500（V2 擴容）|
| 信息迷霧（player_awareness）| HIDDEN / VISIBLE | HINT（模糊提示）|

> **效能說明（R4）：** MVP 實例池上限 50，ConditionTree 最多 4 種葉節點，每遊戲小時最多評估 50×4 = 200 次條件判定，在 Godot 4.6 GDScript 下可在 1 ms 內完成，不構成效能瓶頸。V2 擴容到 500 實例 + 8 種葉節點前，需先做效能 benchmark。

---

### 3.3 信息迷霧與事件感知

- `player_awareness = hidden` → 事件突然觸發，無預告，增強懸念。
- 事件內容可包含未驗證消息：NPC 提供的消息可能為 `rumor`（假），存入玩家信息庫並標記為未驗證。後續事件可基於此觸發（玩家聽信謠言前往陷阱）。
- `reveal_secret` 效果：將 `world_secret` 從隱藏狀態變為玩家已知，可做後續條件依據。

---

### 3.4 NPC 主體性事件

- NPC 可作為事件發起方。模板中 `trigger_condition` 可設為 `npc_initiative` 類型，以特定 NPC 為施動者評估條件。
- NPC 的目標系統自動生成「目標事件模板」。例如 NPC 想報仇，生成對玩家伏擊的事件實例，其 severity 由 NPC 決心值與雙方實力差計算。
- 此類實例綁定該 NPC，玩家與 NPC 同場景或滿足其他條件時觸發，實現 NPC 主動干涉玩家。

---

### 3.5 事件模板範例（節選）

**模板1：路遇舊識（MVP）**
- 條件：玩家在城鎮場景，且存在與玩家關係值（好感或仇恨）≥30 的 NPC
- 修飾詞：關係張力值越高，severity 加成越多
- 選擇：寒暄 / 無視；效果影響關係與小量信息交換
- 屬性：張力、印刻（NPC 可提及玩家過往事跡）

**模板2：血債因果（V2）**
- 條件：玩家曾殺死某 NPC（因果標記存在），且該 NPC 的親友知曉玩家所為（秘密揭露狀態），親友具有「復仇」目標
- 修飾詞：親友仇恨值突破閾值可直接強制觸發（threshold_boost）
- 敘述：埋伏刺殺，選擇迎戰 / 逃脫 / 贖罪
- 效果：永久死亡（剛性）、關係極端化、新因果標記
- 屬性：餘波、剛性、NPC主、迷霧

**模板3：中秋英雄宴（V2）**
- 條件：時間為中秋節，玩家位於岳陽樓場景
- 時空節點強制觸發（severity = 1.0，無視冷卻）
- 多個門派 NPC 齊聚，事件分支影響江湖聲望與身份印刻
- 屬性：節點、印刻、張力

---

## 4. 公式

### 4.1 Severity 計算公式

```
S(instance) = clamp( B × Π(M_mult) + Σ(M_add), 0, 1 )
```

**變數定義：**

| 變數 | 說明 | 範圍 |
|------|------|------|
| B | 模板 base_weight（策劃配置）| 0–1 |
| M_mult | 所有生效的乘法修飾詞（遍歷 modifiers，condition 為真且 effect = "multiply" 的 value 連乘）| 1.0 起 |
| M_add | 所有生效的加法修飾詞（condition 為真且 effect = "add" 的 value 加總）| 累加 |

若某修飾詞 `effect = "threshold_boost"` 且 condition 為真，直接返回 S=1.0，跳過後續計算。

**範例計算：**

模板「路遇舊識」，B=0.4。玩家身份「惡名昭彰」+ 與 NPC 關係值 60：
- 修飾詞1：身份tag「惡名昭彰」存在 → 乘法修飾 ×1.3
- 修飾詞2：關係值 > 50 → 乘法修飾 ×1.4
- 修飾詞3：NPC 曾被玩家幫助 → 加法修飾 +0.1

S = clamp(0.4 × 1.3 × 1.4 + 0.1, 0, 1) = clamp(0.828, 0, 1) = **0.828** → 達標觸發（閾值 0.8）

---

### 4.2 關係張力轉換公式（用於修飾詞計算）

```
tension_norm = clamp( |current_relation - neutral_point| / max_tension_range, 0, 1 )
mod_value    = 1 + tension_norm × k
```

**變數定義：**

| 變數 | 預設值 | 說明 |
|------|--------|------|
| neutral_point | 0 | 不愛不恨的中立點 |
| max_tension_range | 100 | 關係值最大波動範圍 |
| k | 0.5 | 張力強度係數（可調）|

**範例：** 關係值 -75（深仇），neutral=0，range=100，k=0.5
→ tension_norm = 0.75，mod_value = 1.375（乘法修飾）

> **設計意圖（R5）：** 公式以絕對值計算，意味著「深愛」與「深仇」對事件觸發的提升效果相同。這是刻意的武俠世界設計——情深似海與血海深仇同等能撼動命運，中立漠然的關係才是最安靜的。若需要區分「愛促成好事件、恨促成壞事件」，應在事件模板層通過 trigger_condition 限制，而非修改此公式。

---

## 5. 邊界條件

| 情境 | 處理方式 |
|------|---------|
| 每小時超過最大觸發數 | 依 severity 降序觸發前 N 個，其餘順延至次小時重新評估 |
| 兩事件占用同一 NPC 衝突 | severity 低者自動廢棄；其因果鏈標記設為「被阻斷」，可觸發替代事件 |
| 玩家離線期間時空節點事件 | 上線後依優先級回溯觸發（`force_event_retroactive=true` 的關鍵事件不可遺失；非關鍵事件過期記錄為「玩家錯失世界歷史」）|
| 綁定 NPC 在觸發前死亡 | 實例廢棄；若為因果鏈必要環節，生成「繼承者」實例（如弟子、族人）接續 |
| 事件必需地點已永久毀壞 | 實例廢棄（世界剛性保證不強制觸發已消失場景的事件）|
| 待評估實例超過上限（MVP=50，V2=500）| 刪除 severity 最低且 `causal_chain.is_critical = false` 的實例；`is_critical = true` 的因果關鍵實例不可刪除（R2 補充判定規則）|
| 冷卻期內再次觸發條件 | 不生成新實例，冷卻結束後才允許再次實例化 |
| 信息迷霧：玩家未知秘密 | 相關敘述隱去或替換為「不明」，但邏輯仍執行（玩家被蒙在鼓裡是設計意圖）|

---

## 6. 系統依賴

### 本系統依賴的系統

| 系統 | 說明 | MVP/V2 |
|------|------|--------|
| 身份印刻系統（#47）| 提供 entity 身上的標籤查詢、增刪（#47 GDD 待設計）| MVP |
| NPC 行為系統（#14）| 提供 NPC 記憶、NPC 目標系統（npc_goal_check 條件的數據來源）、set_npc_goal 效果接收方 | MVP |
| NPC 人際關係系統（#15）| 提供 NPC-玩家關係數值（relationship_check 條件來源、modify_relationship 效果目標）| MVP |
| 信息迷霧管理（#16 世界感知）| 維護玩家已知事實庫、世界秘密庫、謠言庫 | MVP |
| 世界狀態記錄（#16）| 永久記錄所有不可逆變更，接受 set_world_state | MVP |
| 時間與老化系統（#1）| 提供遊戲時間、節日判定 | MVP |
| 場景/地點管理（#10 地圖移動）| 提供玩家位置、場景人群清單 | MVP |
| 任務系統（#19）| 接收本系統生成的任務資料結構（TaskRegistrar 介面）| VS |
| 事件敘事系統（#21）| 呈現事件對話與選擇介面 | VS |

### 本系統對外廣播的事件

| 事件 | 觸發時機 |
|------|---------|
| `random_event_triggered(event_id, template_id)` | 事件實例轉為 active |
| `random_event_completed(event_id, choice_made)` | 玩家完成選擇 |
| `causal_mark_added(mark_id, source_event_id)` | 因果標記新增 |
| `world_state_changed(state_key, old_val, new_val)` | 世界永久狀態改變 |

---

## 7. 可調參數

**外部化至：`assets/data/random-events/event-system-config.json`**

| 參數 | 預設值 | 安全範圍 | 影響 |
|-----|--------|---------|------|
| `global_trigger_threshold` | **0.8** | 0.6–0.95 | Severity 觸發門檻 |
| `max_events_per_hour` | **3** | 1–8 | 每遊戲小時最大觸發數 |
| `severity_recalc_interval_h` | **1** | 0.5–6 | 重算 Severity 的間隔（遊戲小時）|
| `max_pending_instances` | **500** | 200–2000 | 最大待處理實例數 |
| `default_cooldown_h` | **24** | 6–168 | 模板未指定冷卻時的預設值 |
| `tension_coefficient_k` | **0.5** | 0.1–2.0 | 關係張力轉修飾詞強度係數 |
| `npc_initiative_min_determination` | **0.4** | 0.2–0.8 | NPC 自發生成事件的最低決心值 |
| `awareness_default` | **hidden** | hidden/visible | 新實例的預設玩家感知級別 |
| `causal_chain_preservation` | **true** | — | 關鍵因果鏈是否不因實例上限而刪除 |
| `force_event_retroactive` | **true** | — | 離線期間強制事件是否上線後回溯觸發 |

---

## 8. 驗收標準

| 編號 | 驗收項目 | 預期結果 | 阻斷 |
|-----|---------|---------|-----|
| AC1 | 基礎 Severity 觸發 | base_weight=0.9，無修飾詞，進入觸發場景 → severity=0.9>0.8 → 事件觸發 | 是 |
| AC2 | 修飾詞乘法疊加 | B=0.5，乘法×1.5（tag存在），加法+0.2（關係>20）→ S=0.95，觸發；移除 tag → S=0.7，不觸發 | 是 |
| AC3 | threshold_boost 強制觸發 | 關係值≥90時，無論 base_weight，S=1.0 直接觸發；關係值89時正常計算 | 是 |
| AC4 | 因果鏈事件生成 | 完成事件A → 生成事件B實例，causal_chain 指向事件A的ID；觸發B後因果標記更新 | 是 |
| AC5 | 信息迷霧：秘密揭露影響觸發 | 秘密未知 → 不生成實例；揭露秘密後 → 即時生成對應實例 | 是 |
| AC6 | NPC 主體性事件觸發 | NPC 具備「復仇」目標，玩家與 NPC 同場景且 severity 達標 → 事件觸發；殺死該 NPC → 實例廢棄 | 是 |
| AC7 | 時空節點強制觸發機制 | 任意模板設定 time_check + location_check 同時滿足時觸發 threshold_boost → severity=1.0，立即觸發且無視冷卻 | 是 |
| AC7-B | 時空節點離線回溯 | force_event_retroactive=true：玩家離線期間時空節點強制事件發生，上線後補觸發，不靜默遺失 | 是 |
| AC8 | 世界剛性效果永久性 | 事件選項導致 NPC 死亡 → set_world_state 標記 dead → 重啟後狀態仍在；需該 NPC 存活的事件無法生成 | 是 |
| AC9 | 同時多事件排序與上限 | 5 個達標實例，max=2 → 第一小時觸發 severity 最高的兩個；其餘下小時重新評估 | 是 |
| AC10 | 冷卻與並行上限 | 模板冷卻 24h，觸發後 24 遊戲小時內不生成新實例 | 是 |
| AC11 | 身份印刻施加與判定 | add_identity_tag「恩人」→ 作為另一事件條件觸發；remove_identity_tag 後不再觸發 | 是 |
| AC12 | 謠言生成與利用 | spawn_rumor 生成假謠言 → 玩家信息庫中存在且標記 unverified；另一事件以「玩家知此謠言」為條件可觸發 | 是 |

---

*品霖設計備註：*

*隨機事件系統最重要的事不是「隨機」，而是「有意義」。一個在破廟偶遇的傷者，三個月後在山頂替你擋了一刀——這不是腳本，是世界記住了你的選擇，然後以它自己的方式回話。這個系統的終極目標是讓玩家在每次遭遇時都感覺到：這個世界不是為我準備的舞台，而是一個有自己邏輯的地方，我恰好也在裡面活著。*
