# 江湖一生 — 事件敘事系統 GDD
*策劃：陳品霖 | 版本：v1.0 | 審核：怡嘉 | 狀態：已審核 | 2026-05-12*
*系統編號：#21 | 層級：Feature（Vertical Slice）*
*設計方法：情境先行 — 20情境→10屬性→規格*
*依賴系統：#47 身份印刻、#14 NPC行為、#19 任務系統、#20 隨機事件*

---

## 1. 概述

事件敘事系統將世界中的故事、謎團、身份錯位、因果碎片，分佈在 NPC、場景、道具、時間點上，透過「觸發→錨定→身份覆蓋→敘事載體→資訊釋放」的管線，讓玩家在探索中拼湊、誤解、或直接撞見屬於自己的敘事。它接收 #19 任務系統和 #20 隨機事件系統的骨架資料，將機制邏輯轉換為玩家感知的故事體驗。

---

## 2. 玩家體驗

- **「故事不是任務清單，是你走進去的東西」** — 靠近說書人，才發現他講的故事和你腰間玉佩的名字相同
- **「世界對你說話，有時說實話，有時認錯人」** — 瞎子婦人把你當成別人、燈上只有你的名字和明天的日期，沒有任何解釋
- **「你在拼一幅你不知道邊界的拼圖」** — 三年前給乞丐一兩銀子，今天那個人說你長相不一樣了
- **「有些謎團沒有答案」** — 棺材旁穿嫁衣的女子，你能做的只有走過

**刻意不追求：**
- 不是任務日誌的變體形式
- 所有事件不一定有任務獎勵或解答
- 不保證所有謎團都能被解開

---

## 3. 詳細規則

### 3.1 事件資料結構（MVP）

| 欄位 | 類型 | 說明 |
|------|------|------|
| EventID | String | 唯一識別碼 |
| TriggerConditions | Condition[] | 觸發條件組合（AND/OR）|
| AnchorEntity | String | 事件錨點實體 ID（NPC/Item/Location/Time）|
| NarrativeDepth | Enum | SurfaceRumor / LivedExperience / DeepTruth |
| IdentityOverlay | Object\|null | 事件將玩家覆蓋為何種身份 |
| NarrativeCarrier | Enum | Dialogue / SceneText / ItemDescription / Environmental / Wordless |
| InfoCompleteness | Enum | Full / Partial / Misleading / None |
| EventChainID | String\|null | 所屬事件鏈 ID |
| PlayerAgency | Enum | None / DialogueChoice / ActionIntervention |
| Repeatability | Enum | Once / Repeatable / RepeatableWithVariation |

### 3.2 觸發條件類型（MVP）

| 條件類型 | 說明 | 對應情境 |
|----------|------|---------|
| `enter_radius` | 玩家進入錨點實體半徑 | 靠近說書人、走到棺材旁 |
| `has_item` | 持有特定物品 | 持有同名玉佩 |
| `imprint_recognized` | #47 印刻系統觸發識別 | 鐵匠認出刀 |
| `time_range` | 遊戲時間區間 | 燈只在特定日期點亮 |
| `npc_memory_trigger` | NPC 記憶中特定標籤 | 乞丐記得三年前的你 |
| `location_state` | 場景狀態條件 | 燈籠被點亮時 |

### 3.3 敘事深度與資訊釋放（MVP）

| 層級 | 玩家獲得 | 釋放規則 |
|------|----------|----------|
| SurfaceRumor | 故事/傳聞，別人口中的版本 | 首次觸發釋放，可重複 |
| LivedExperience | 親身遭遇，NPC 直接反應 | 一次性觸發，改變 NPC 關係 |
| DeepTruth | 隱藏真相 | 需滿足多個條件才解鎖（前置事件+印刻+時間）|

### 3.4 身份覆蓋類型（MVP）

| 類型 | 說明 | 範例情境 |
|------|------|---------|
| NameMatch | 玩家某欄位 == 事件中名字 | 玉佩名字和說書人故事相同 |
| MistakenIdentity | NPC 把玩家誤認為別人 | 瞎子婦人認錯人 |
| Inheritance | 持有物的 OwnerID ≠ 玩家 | 鐵匠認出滅門刀的前主人 |
| FateMapping | 世界直接對玩家說話，無 NPC 參與 | 燈上你的名字+明天日期 |

### 3.5 敘事載體呈現規則（MVP）

| 載體類型 | 呈現方式 | 可中斷 |
|---------|---------|--------|
| Dialogue | 推動對話系統，切換對話樹 | 可中斷，下次重來 |
| SceneText | 世界空間 UI，掛在錨點實體上 | 一次性展示後消失 |
| ItemDescription | 更新物品描述文字 | 永久更改 |
| Environmental | 場景演出（落葉、風聲、燈亮）| 一次性播放 |
| Wordless | 不呈現文字，僅場景狀態改變（棺材旁花枯了）| 靜默發生 |

### 3.6 動態目標修改（MVP，接收 #19 指令）

依 task-system.md 3.5 節，#19 任務系統可發送 `task_modify_objective` 事件。本系統負責將修改渲染為玩家可感知的敘事：
- `REPLACE_OBJECTIVE` → 顯示「你突然意識到⋯⋯」類型的過場文字，更新任務說明
- 修改的新目標描述由本系統的敘事池提供，不由任務系統硬編碼

### 3.7 事件連鎖（V2）

```
EventChainID 相同的事件組成一條故事鏈
觸發條件可加入「previous_event_check」（前置事件已完成）
玩家在不同時間/地點觸發的碎片，最終可能拼成同一個故事
```

---

## 4. 公式

### 4.1 觸發檢測公式（MVP）

```
觸發 = ∃ 事件：所有 TriggerConditions 均為 true

條件檢測：
  enter_radius(entity, radius) → 玩家距錨點 ≤ radius
  has_item(item_id)            → 玩家背包含 item_id
  imprint_recognized(imp_id)   → #47 已寫入「NPC識別 imp_id」記憶
  time_range(start, end)       → 遊戲時間 ∈ [start, end]
  npc_memory_trigger(tag)      → NPC 記憶含 tag
  location_state(entity, val)  → 場景狀態變數 == val
```

**範例：**
```
事件 EVT_LANTERN_NAME_TOMORROW
觸發條件：
  enter_radius(ITEM_LANTERN_03, 300)
  location_state(ITEM_LANTERN_03, "lit")
→ 玩家走近且燈已點亮 → 顯示場景文字：燈上你的名字，明天的日期
→ NarrativeCarrier = SceneText
→ InfoCompleteness = None（純氛圍，無解答）
```

### 4.2 敘事版本選擇公式（MVP）

當 NarrativeCarrier = Dialogue 時，從對話樹池選取版本：

```
可用版本 = 所有滿足 required_bindings 的 NarrativeVariant
選取結果 = 在可用版本中，依 tone 過濾後隨機取一條
佔位符替換 = 將 {npc_name}、{location_name} 等用 bindings 值替換
```

**變數定義：**

| 變數 | 說明 |
|------|------|
| required_bindings | 此版本需要的 bindings key 列表（如 `["npc_name", "item_name"]`）|
| tone | NEUTRAL / TENSE / HUMOROUS / SORROWFUL |
| bindings | EventInstance 的具體綁定值（NPC名字、地點名等）|

---

## 5. 邊界條件

| 情境 | 處理方式 |
|------|---------|
| 事件錨點實體被破壞/移除 | 事件設為「不可觸發」，在見聞錄標記為 Lost |
| 玩家 Dialogue 中途離開範圍 | 可中斷，下次進入範圍重新開始；重複性為 Once 的不重播 |
| 同幀多事件觸發 | 依 NarrativeDepth 優先：LivedExperience > DeepTruth > SurfaceRumor |
| NPC 錨點死亡 | 事件永久失效；若設有備用傳播者（V2），轉移給備用 NPC |
| Once 事件被玩家中途打斷 | 事件不標記為已完成，允許再次觸發 |
| MistakenIdentity 與其他 NPC 衝突 | 覆蓋為暫時性，只在該事件範圍內有效；其他 NPC 不受影響 |
| 動態目標修改（#19 來源）渲染失敗 | 任務目標仍在資料層修改，敘事文字使用預設模板代替 |

---

## 6. 系統依賴

### 本系統依賴的系統

| 系統 | 編號 | 依賴內容 | MVP/V2 |
|------|------|---------|--------|
| 身份印刻系統 | #47 | `imprint_recognized` 觸發條件；繼承身份敘事 | MVP |
| NPC 行為/記憶系統 | #14 | `npc_memory_trigger` 觸發條件；NPC 對話樹 | MVP |
| 任務系統 | #19 | 接收 `task_modify_objective` 事件；渲染任務轉折敘事 | MVP |
| 隨機事件系統 | #20 | 接收 `narrative_pool` 查詢；為隨機事件提供敘事文本 | MVP |
| 日誌記事系統 | #24 | 將觸發過的事件寫入見聞錄 | V2 |

### 本系統對外廣播的事件

| 事件 | 觸發時機 |
|------|---------|
| `narrative_event_triggered(event_id, anchor_id)` | 事件觸發 |
| `narrative_event_completed(event_id, choice_id)` | 玩家完成選擇/觸發完畢 |
| `clue_added(clue_id, completeness)` | 新增見聞錄線索 |
| `identity_overlay_applied(overlay_type, player_id)` | 身份覆蓋生效 |

---

## 7. 可調參數

**外部化至：`assets/data/narrative-events/config.json`**

| 參數 | 預設值 | 安全範圍 | 影響 |
|-----|--------|---------|------|
| `default_trigger_radius` | 400 cm | 100–1000 | enter_radius 預設半徑 |
| `max_concurrent_events` | 1 | 1–3 | 同時展示的最大事件數（超過則排隊）|
| `dialogue_resume_timeout_h` | 24 | 1–168 | 中斷對話事件允許再次觸發的冷卻時間 |
| `scene_text_display_seconds` | 4 | 2–10 | SceneText 顯示持續秒數（現實時間）|
| `rumor_truth_ratio` | 0.7 | 0.3–1.0 | SurfaceRumor 中真實資訊的概率（0.7=70%概率是真的）|

---

## 8. 驗收標準

| 編號 | 驗收項目 | 預期結果 | 阻斷 |
|-----|---------|---------|-----|
| AC1 | enter_radius 觸發 | 玩家進入錨點 400cm 範圍 → 事件觸發；離開後重新進入不重複（Once）| 是 |
| AC2 | imprint_recognized 觸發 | #47 識別後寫入記憶 → 事件條件滿足 → 對話樹切換 | 是 |
| AC3 | Dialogue 中斷後可重觸發 | 玩家離開範圍中斷對話 → 重新進入 → 對話從頭開始 | 是 |
| AC4 | NarrativeDepth 優先級 | 同幀同時觸發 LivedExperience 和 SurfaceRumor → 前者先執行 | 是 |
| AC5 | SceneText 一次性展示 | SceneText 事件觸發 → 文字顯示 4 秒後消失；Once 事件不再觸發 | 是 |
| AC6 | 身份覆蓋 NameMatch | 玩家持有名字匹配道具 + 進入說書人半徑 → 對話引用玩家名字 | 是 |
| AC7 | Wordless 事件靜默 | Wordless 類型觸發後場景狀態改變，無文字或 UI 呈現 | 否 |
| AC8 | 錨點死亡→事件失效 | 錨點 NPC 死亡後，依賴該 NPC 的事件無法再觸發 | 是 |
| AC9 | 動態目標修改敘事 | #19 發送 REPLACE_OBJECTIVE → 本系統顯示過場文字 + 更新任務說明文字 | 是 |
| AC10 | time_range 條件 | 事件設定為特定遊戲時辰 → 不在時辰內不觸發；進入時辰後觸發 | 是 |
