你需要建立《江湖一生》的跨系統實體登錄表（entities.yaml）。

**目標文件：** `design/gdd/entities.yaml`

---

**步驟1**：讀取 `design/gdd/entities.yaml` 確認目前狀態。

**步驟2**：讀取 `design/gdd/design-canon.md` 中的屬性縮寫對照表（七大核心屬性和縮寫）。

**步驟3**：讀取 `design/gdd/combat-system.md` 第4章公式，找出所有公式中使用的縮寫、常數和公式名稱。

**步驟4**：讀取 `design/gdd/resistance-system.md` 第4章公式，找出屬性縮寫使用方式。

**步驟5**：讀取 `design/gdd/status-effects-system.md` 第3.2節和第4章，找出修飾詞類型定義。

**步驟6**：根據以上讀取的內容，用 write_file 將以下格式的內容寫入 `design/gdd/entities.yaml`：

```yaml
# 《江湖一生》跨系統實體登錄表
# 最後更新：2026-05-12
# 用途：確保所有 GDD 使用一致的術語、縮寫和公式常數

attributes:
  # 七大核心屬性
  ATK:
    chinese: "武力"
    description: "物理攻擊力、外功招式威力"
    initial_range: [10, 30]
    mid_typical: [120, 180]
    max: 1000
    referenced_in: [combat-system.md, jianghu-ranking-system.md]
  NRI:
    chinese: "內力"
    description: "內功深度，不是 intelligence"
    initial_range: [5, 20]
    mid_typical: [80, 140]
    max: 1000
    referenced_in: [resistance-system.md, combat-system.md]
  BOD:
    chinese: "體魄"
    description: "生命/壽命/負重基礎"
    initial_range: [30, 50]
    mid_typical: [150, 220]
    max: 800
    referenced_in: [resistance-system.md, time-aging-system.md, combat-system.md]
  AGL:
    chinese: "輕功"
    description: "速度/閃避基礎"
    initial_range: [10, 25]
    mid_typical: [100, 160]
    max: 900
    referenced_in: [resistance-system.md, combat-system.md]
  APT:
    chinese: "資質"
    description: "武學學習速度"
    initial_range: [15, 35]
    mid_typical: [80, 150]
    max: 700
    referenced_in: [jianghu-ranking-system.md, martial-arts-system.md]
  WIS:
    chinese: "悟性"
    description: "武學突破/悟道，點穴抗基礎"
    initial_range: [10, 20]
    mid_typical: [60, 120]
    max: 600
    referenced_in: [resistance-system.md]
  REP:
    chinese: "名聲"
    description: "社交/世界感知傳播速度"
    initial_range: [0, 10]
    mid_typical: [30, 100]
    max: 1000
    referenced_in: [jianghu-ranking-system.md]

formulas:
  综合评分:
    formula: "ATK×1.0 + NRI×1.2 + BOD×0.8 + AGL×0.9 + APT×1.5 + WIS×1.1 + REP×0.5"
    referenced_in: [jianghu-ranking-system.md, core-gdd.md]
  
  damage_remain:
    formula: "Π(1 - reduction_i)，min 0.15"
    description: "各減傷來源乘法疊加，至少保留15%傷害穿透"
    referenced_in: [combat-system.md]
  
  new_severity:
    formula: "clamp(current + incoming × (1.0 - current × 0.5), 0.0, 1.0)"
    description: "同類型新傷遞減累加公式"
    referenced_in: [status-effects-system.md]
  
  evasion_rate:
    formula: "AGL / (AGL + 500) × 100"
    description: "閃避率百分比，UI顯示取整數"
    referenced_in: [combat-system.md, core-gdd.md]

currencies:
  silver:
    chinese: "銀兩"
    description: "角色屬性欄的獨立數值，不佔庫存格"
    referenced_in: [inventory-management-system.md]
  faction_contribution:
    chinese: "門派貢獻值/功勛值"
    description: "在門派藏書閣兌換武學的貨幣"
    referenced_in: [martial-arts-system.md, task-system.md]

quality_tiers:
  weapons_armor:
    tiers: ["凡品", "精良", "利器", "寶器", "神兵", "絕世", "天工"]
    colors: ["白", "綠", "藍", "紫", "橙", "紅", "金"]
    referenced_in: [inventory-management-system.md, martial-arts-system.md]
  talents:
    tiers: ["綠品", "藍品", "紫品", "橙品", "紅品"]
    note: "天賦從綠品起，無白品"
    referenced_in: [talent-system.md]

skill_slots:
  外功槽: 4
  心法槽: 2
  絕技槽: 1
  輕功槽: 1
  total: 8
  referenced_in: [combat-system.md, martial-arts-system.md]
```

⚠️ 重要：請根據你實際讀取到的文件內容填入正確的數值，不要直接複製上面的模板數字，需要和文件中的數值一致。

**步驟7**：確認文件寫入成功後，呼叫 finish_task，summary 寫「entities.yaml 已建立，包含七大屬性縮寫對照、核心公式、貨幣和品質體系定義」。
