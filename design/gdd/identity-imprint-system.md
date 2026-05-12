# 江湖一生 — 身份印刻系統 GDD
*策劃：陳品霖 | 版本：v1.0 | 審核：怡嘉 | 狀態：已審核 | 2026-05-12*
*系統編號：#47 | 層級：Foundation*
*設計方法：情境先行 — 20情境→9屬性→規格*
*依賴系統：#14 NPC行為、#15 NPC關係、#13 庫存管理、#21 事件敘事*

---

## 1. 概述

身份印刻系統讓遊戲世界透過「器物、肉體標記、持有物、暗語、繼承身份」等印刻，主動識別玩家及其關聯身份，並觸發態度、行為、事件、機關等反饋。身份不是玩家主動宣告的面板屬性，而是世界對玩家的「讀取結果」——NPC 根據自身群組的識別能力，對印刻做出各自不同的反應。遮蓋、展示、偽造、繼承，都是玩家與世界博弈的手段。

---

## 2. 玩家體驗

- **「身份是刻進身體與器物裡的」** — 它不是你選的稱號，是別人看你時讀取的東西
- **「世界有眼睛，但不是所有人看見同一件事」** — 丐幫船夫認得暗記、鐵匠認得刀、廟祝認得腰牌，認識的是不同的你
- **「遮與露都是選擇」** — 遮住烙印可以通過城門，但遲早有人叫你露出手腕
- **「有些東西永遠洗不掉」** — 那把刀，那個名字，那個死了三年的人——它們會自己找到你

**刻意不追求：**
- 不是「玩家按技能亮身分證」
- 不是 UI 清單讓玩家自己選取展示
- 不是所有 NPC 都能認出所有印刻

---

## 3. 詳細規則

### 3.1 印刻資料結構（MVP）

每個印刻是一筆資料：

| 欄位 | 類型 | 說明 |
|------|------|------|
| ImprintID | String | 唯一識別碼，如 `IMP_BLADE_FAMILY_SLAYER` |
| ImprintType | Enum | ArtefactMark / BodyMark / Possession / MartialImprint / CipherMark / InheritedIdentity |
| OwnerID | String\|null | 歸屬角色ID（null = 無主印刻）|
| RecognizerGroups | String[] | 可識別此印刻的 NPC 群組 ID 列表 |
| RecognitionDistance | Float | 最大識別距離（cm），預設 150.0 |
| TriggerBehaviors | BehaviorRecord[] | 識別後觸發的行為集合 |
| VisibilityCondition | Enum | AlwaysVisible / OnDisplay / AtLocation / AtTime / InLight |
| IsConcealed | Bool | 當前是否被遮蓋，預設 false |
| Durability | Enum | Permanent / Removable / Forgeable |

### 3.2 印刻類型行為差異（MVP）

| 類型 | 識別方式 | 特殊規則 |
|------|----------|----------|
| ArtefactMark | 視錐+距離 | 需 OnDisplay（玩家從背包拿出展示）才觸發 |
| BodyMark | 視錐+距離 | AlwaysVisible 但可被遮蓋；裹手布等需展示部位 |
| Possession | 視錐+距離 | 手中道具/刀直接觸發 |
| MartialImprint | 施展武學時 | 施展時觸發，識別距離為施展範圍+視覺特效 |
| CipherMark | 特定位置+展示 | 需在特定位置展示；可能需特定光線 |
| InheritedIdentity | 常時 | 繼承前主人惡名/身份；與 OwnerID 連動 |

### 3.3 遮蓋與展示機制（MVP）

**遮蓋（BodyMark）：**
- 玩家選擇 BodyMark → 消耗布條/化妝品、需時間 → IsConcealed = true
- IsConcealed = true 時，該印刻不被識別
- 遮蓋物有耐久度，戰鬥破損後 IsConcealed 自動 = false

**展示（ArtefactMark）：**
- 玩家選擇 ArtefactMark → 設為展示狀態（即時）→ OnDisplay 條件滿足

### 3.4 印刻識別主循環（MVP）

```
每個 NPC 每幀：
1. 取得視錐內所有角色
2. 對每個角色取得所有印刻
3. 對每個印刻：
   if 識別公式 = true AND NPC 尚未識別過此印刻：
     執行 TriggerBehaviors
     寫入 NPC 記憶
```

### 3.5 TriggerBehavior 類型（MVP）

| 行為類型 | 說明 |
|---------|------|
| `attitude_change` | 調整 NPC 群組對玩家的態度值（delta）|
| `dialogue_tree_switch` | 切換 NPC 對話樹為指定 tree_id |
| `access_grant` / `access_deny` | 開放/封鎖特定區域或功能 |
| `trigger_event` | 觸發 #21 事件敘事系統的指定事件 |
| `mechanism_toggle` | 觸發場景機關（開門/解鎖/毒刺縮回）|

### 3.6 NPC 識別記憶（V2）

- NPC 識別後記住該印刻（記入記憶系統）
- 再次遇到時可直接觸發，不需重新滿足 VisibilityCondition
- 記憶可被遺忘（時間、事件）

### 3.7 印刻繼承關聯（V2）

```
若 InheritedIdentity 型印刻的 OwnerID 已死亡：
  觸發「惡名繼承」事件
  NPC 將玩家視為原 OwnerID 的繼承者
  態度修正 = 原態度修正 × 繼承係數（0.5–1.5）
```

---

## 4. 公式

### 4.1 印刻識別公式（MVP）

```
識別觸發 =
  (NPC所屬群組 ∈ RecognizerGroups)
  ∧ (玩家與NPC實際距離 ≤ RecognitionDistance)
  ∧ (VisibilityCondition_Check() = true)
  ∧ (IsConcealed = false)
```

**VisibilityCondition_Check()：**
- `AlwaysVisible` → 恆真
- `OnDisplay(itemID)` → 玩家展示狀態為 true
- `AtLocation(locID)` → 玩家當前位置 == locID
- `AtTime(start, end)` → 遊戲時間 in [start, end]
- `InLight(lightType)` → 場景光源符合 lightType

**範例：** 玩家持有 `IMP_BLADE_FAMILY_SLAYER`，鐵匠NPC（群組=鐵匠公會）距離 100cm，RecognitionDistance=200，VisibilityCondition=AlwaysVisible，IsConcealed=false
→ 識別觸發，切換對話樹為「認出刀」

### 4.2 態度變化公式（MVP）

```
新態度值 = clamp(基礎態度 + 印刻態度修正, -100, 100)
印刻態度修正 = Σ(所有觸發印刻的 attitude_delta)
```

**變數定義：**

| 變數 | 說明 | 範圍 |
|------|------|------|
| 基礎態度 | 勢力/關係系統中 NPC 群組對玩家當前態度 | -100–100 |
| attitude_delta | 單個印刻觸發的態度變化量（策劃配置）| -100–100 |

**範例：** 基礎態度=10，漕幫暗記觸發 delta=+30 → 新態度=40（友善）。若同時識別惡名印記 delta=-80 → 40-80=-40（敵對）

---

## 5. 邊界條件

| 情境 | 處理方式 |
|------|---------|
| 印刻 OwnerID 已被刪除 | 保留印刻，OwnerID 設為 null；Owner 相關觸發跳過 |
| 同一 NPC 同幀多個印刻觸發 | 依優先序執行（Possession > BodyMark > InheritedIdentity）；態度修正累加 |
| 玩家死亡後印刻狀態 | BodyMark 保留；ArtefactMark 留在屍體上可被拾取 |
| 遮蓋物在戰鬥中破損 | IsConcealed 自動 = false |
| NPC 死亡但記憶中有識別記錄 | 識別記錄保留，可供其他 NPC 發現（如搜查遺物）|
| 偽造印刻被識破（V2）| 觸發「偽造敗露」事件，態度暴跌 |

---

## 6. 系統依賴

### 本系統依賴的系統

| 系統 | 編號 | 依賴內容 | MVP/V2 |
|------|------|---------|--------|
| NPC 行為系統 | #14 | NPC 視錐感知、NPC 群組歸屬 | MVP |
| NPC 人際關係系統 | #15 | 接收態度修正、讀取基礎態度值 | MVP |
| 庫存管理系統 | #13 | 讀取玩家持有物品；展示狀態切換 | MVP |
| 事件敘事系統 | #21 | 接收 trigger_event 行為、渲染對話樹 | MVP |

### 本系統對外廣播的事件

| 事件 | 觸發時機 |
|------|---------|
| `imprint_recognized(imprint_id, npc_id)` | NPC 成功識別印刻 |
| `imprint_concealed(imprint_id, player_id)` | 玩家遮蓋印刻 |
| `imprint_revealed(imprint_id, player_id)` | 遮蓋解除（主動或被動）|
| `inheritance_triggered(imprint_id, original_owner_id)` | 繼承身份事件觸發 |

---

## 7. 可調參數

**外部化至：`assets/data/identity-imprint/config.json`**

| 參數 | 預設值 | 安全範圍 | 影響 |
|-----|--------|---------|------|
| `default_recognition_distance` | 150.0 cm | 50–500 | NPC 識別印刻的預設最大距離 |
| `concealment_duration_hours` | 2 | 0.5–8 | 遮蓋操作所需遊戲小時 |
| `cloth_durability` | 3 | 1–10 | 布料遮蓋物的戰鬥耐久次數 |
| `inheritance_coefficient` | 1.0 | 0.5–1.5 | 繼承惡名時態度修正的衰減/放大係數 |
| `npc_recognition_cooldown_h` | 24 | 0–168 | 同一 NPC 對同一印刻再次完整識別的冷卻 |

---

## 8. 驗收標準

| 編號 | 驗收項目 | 預期結果 | 阻斷 |
|-----|---------|---------|-----|
| AC1 | ArtefactMark 展示觸發 | 玩家未展示木牌→NPC 無反應；展示後→態度改變 | 是 |
| AC2 | BodyMark 遮蓋有效 | IsConcealed=true → NPC 同距離內無識別觸發 | 是 |
| AC3 | 遮蓋物破損後自動暴露 | 布料耐久歸零 → IsConcealed=false → 下幀 NPC 識別觸發 | 是 |
| AC4 | 群組識別限制 | 漕幫印刻只有漕幫群組 NPC 識別，官府 NPC 不識別 | 是 |
| AC5 | 距離限制 | 超過 RecognitionDistance → 不觸發；進入範圍後觸發 | 是 |
| AC6 | 態度多印刻累加 | 同時觸發兩個印刻（delta=+30, delta=-80）→ 新態度 = 基礎 + 30 - 80 | 是 |
| AC7 | MartialImprint 施展觸發 | 施展對應武學時才觸發識別，未施展時不觸發 | 是 |
| AC8 | CipherMark 位置條件 | 玩家不在指定地點→不觸發；到達地點後展示→觸發 | 是 |
| AC9 | Possession 識別+對話切換 | 持有滅門刀接近鐵匠→對話樹切換為「認出刀」 | 是 |
| AC10 | 印刻永久性 | Permanent 印刻無法透過任何操作移除 | 否 |
