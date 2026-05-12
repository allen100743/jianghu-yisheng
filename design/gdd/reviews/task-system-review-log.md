# 任務系統 GDD — 審查記錄
*design/gdd/task-system.md*

---

## Review — 2026-05-12 — Verdict: MAJOR REVISION NEEDED

**Scope signal:** L（多系統整合，依賴 #35/#20/#21，可能需要新 ADR）
**Specialists:** game-designer, systems-designer, narrative-director, economy-designer, qa-lead, creative-director
**Blocking items:** 8 | Recommended: 6
**Prior verdict resolved:** N/A（首次審查）

**Summary（creative-director）：** 核心概念方向正確，INVALIDATED≠FAILED 的設計直覺是亮點，8/8 章節齊備。但存在 4 個未定義 Type（BranchCondition/WorldStateCondition/Condition/任務注冊機制）阻擋實作，加上 INVALIDATED 玩家感知層完全缺席、3 項設計違反「選擇有重量」支柱（max_active_tasks/ABANDONED/conflict_group 解決時機）。「機制層有區分，玩家層看不到」是最根本的問題。

---

## 製作人決策記錄（2026-05-12）

| 決策 | 問題 | 決定 |
|------|------|------|
| A | INVALIDATED 呈現規格歸屬 | **先定介面契約**（任務系統定規格坑位，#21填內容）|
| B | MVP 是否含目標修改 | **MVP 包含最簡版**（至少支援 REPLACE_OBJECTIVE）|
| C | max_active_tasks | **屬性可解鎖配合15上限**，加其他方式創造取捨感 |

---

## P0 阻擋清單修復狀態（v3.0 完成）

- [x] B1 定義 `BranchCondition` 介面契約 ← 3.1節
- [x] B2 定義 `WorldStateCondition` + 雙路徑說明 ← 3.1節
- [x] B3 定義 `Condition` 聯合型別 ← 3.1節
- [x] B4 補任務創建/注冊機制規格 ← 3.3節（新增）
- [x] B5 INVALIDATED 感知規格（3.8節）+ AC10 拆三類遺憾（AC10-A/B/C）
- [x] B6 ABANDONED 後果（3.7節）+ conflict_group 選邊時機改為完成時（3.6節）+ max_active_tasks 屬性解鎖（7節）
- [x] B7 公式 4.2 修復（除零、config param、clamp）
- [x] B8 E9/E10 死亡日執行順序修復

## P1 建議清單

- [ ] R1 ENV_OBSTACLE 改為 NPC-mediated（已在 3.3.1 說明中修正定義）✅
- [ ] R2 MVP 含最簡目標修改（REPLACE_OBJECTIVE）← 3.5節確認 ✅
- [ ] R3 reward_bundle skill_unlocks 欄位（待 technical-director ADR）⏳
- [ ] R4 speed_bonus 稀有 opt-in + 不顯示公式 ← 3.10節 + 4.2節 ✅
- [ ] R5 E11 DELIVER_ITEM 失敗道具歸屬 ← 加入邊界條件表，標「待製作人決定」✅

## P1 高優先清單

- [ ] R1 ENV_OBSTACLE 改為 NPC-mediated
- [ ] R2 MVP 加入最簡目標修改（REPLACE_OBJECTIVE）
- [ ] R3 reward_bundle 補 skill_unlocks 欄位（協調 technical-director 出 ADR）
- [ ] R4 apply_speed_bonus 改為稀有 opt-in 標記，不向玩家顯示精確公式
- [ ] R5 補 E11（DELIVER_ITEM 失敗物品歸屬）
- [ ] R6 DORMANT 觸發傾向 NPC 主動推送
