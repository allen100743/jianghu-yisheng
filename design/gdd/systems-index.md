# 《江湖一生》系統索引
*建立日期：2026-05-11 | 狀態：初版 | 版本：v1.0*
*審查：怡嘉（策劃協調）+ 靜怡（UX）+ 技術總監 | 總系統數：46*
*2026-05-11 新增：傷勢/狀態效果（43）、武俠抗性（44）、性格特質（45）、江湖風雲榜（46）*

---

## 系統總覽

| 層級 | 數量 | 說明 |
|------|------|------|
| Foundation | 4 | 無依賴的基礎層，最先設計與建置 |
| Core | 13 | 依賴 Foundation，構成玩法骨架 |
| Feature | 11 | 依賴 Core，構成遊戲深度 |
| Presentation | 6 | UI 與回饋層 |
| Meta/Polish | 4 | 跨局與收尾系統 |
| 技術基礎設施 | 8 | 技術總監補充，跨層橫切關注點 |

**MVP 系統數：26 個 | Vertical Slice：8 個 | Alpha：4 個 | Full Vision：4 個**

---

## MVP 優先級（沙盒驗證閉環）

> MVP 驗證目標：玩家在遊戲時間第 30 天內感受到「這個 NPC 世界是活的」

| # | 系統名稱 | 層級 | 依賴 | 設計狀態 | 高風險 |
|---|---------|------|------|---------|--------|
| 35 | 事件總線/信號樞紐 | 技術基礎 | — | 🔲 未開始 | |
| 36 | 資料持久化層 | 技術基礎 | — | 🔲 未開始 | |
| 37 | NPC 排程器 | 技術基礎 | — | 🔲 未開始 | ⚠️ |
| 38 | FSM/行為樹框架 | 技術基礎 | — | 🔲 未開始 | |
| 41 | 種子隨機性服務 | 技術基礎 | — | 🔲 未開始 | |
| 40 | 設定/輸入系統 | 技術基礎 | — | ✅ GDD 已審核 v1.0（settings-input-system.md）\| 怡嘉審核：2026-05-12 | |
| 1 | 時間與老化系統 | Foundation | — | ✅ GDD 完成（time-aging-system.md）| |
| 2 | 屬性/數值系統 | Foundation | — | ✅ GDD 完成（Ch14）| ⚠️ 瓶頸 |
| 3 | 存檔/讀檔系統 | Foundation | — | 🔲 未開始 | ⚠️ 高複雜度 |
| 4 | 程序化世界生成 | Foundation | — | ✅ GDD 完成（procedural-world-generation.md）| ⚠️ |
| 5 | 角色創建系統 | Core | 2, 4 | ✅ GDD 完成（character-creation-system.md）| |
| 6 | 天賦系統 | Core | 2, 5 | ✅ GDD 完成（talent-system.md）| |
| 7 | 武功修煉系統 | Core | 1, 2 | ✅ GDD 完成（Ch5）| |
| 8 | 武學技能系統 | Core | 2 | ✅ GDD 完成 v2（martial-arts-system.md）| |
| 43 | 傷勢與狀態效果系統 | Core | 1, 2, 11 | ✅ GDD 已審核 v2.1（status-effects-system.md）\| 怡嘉審核：2026-05-12，補齊後遺症機制、疾病倒數量化、非必要NPC標準 | |
| 44 | 武俠抗性體系 | Core | 2, 43 | ✅ GDD 完成（resistance-system.md）| |
| 45 | 性格特質系統 | Core | 2, 5 | ✅ GDD 完成（personality-system.md）| |
| 9 | 裝備系統 | Core | 2 | ✅ GDD 完成（Ch6）| |
| 10 | 地圖移動系統 | Core | 1, 4 | ✅ GDD 完成（Ch11）| |
| 11 | 戰鬥系統 | Core | 2, 7, 8, 9 | ✅ GDD 完成+審查（combat-system.md）\| 審查：2026-05-12 NEEDS REVISION → 修復完成 | |
| 12 | 經濟系統 | Core | 2 | ✅ GDD 完成（Ch12）| |
| 13 | 庫存管理系統 | Core | 9, 8 | ✅ GDD 完成（inventory-management-system.md）| |
| 14 | NPC 行為系統 | Feature | 1, 2, 10, 37, 38 | ✅ GDD 完成（Ch7）| ⚠️ 瓶頸 |
| 15 | NPC 人際關係系統 | Feature | 14 | ✅ GDD 完成（Ch7）| ⚠️ 瓶頸 |
| 16 | 世界感知/消息傳播 | Feature | 1, 10, 14, 15, 2 | ✅ GDD 完成（Ch9）| |
| 17 | 陣營系統（1個）| Feature | 15, 4 | ✅ GDD 完成（Ch8）| |
| 25 | 地圖 UI | Presentation | 10 | 🔲 未開始 | |
| 26 | 角色面板 UI | Presentation | 2, 9 | 🔲 未開始 | |
| 28 | 戰鬥 UI | Presentation | 11 | 🔲 未開始 | |
| 29 | 時間感知 UI | Presentation | 1, 10 | 🔲 未開始 | |

---

## Vertical Slice

| # | 系統名稱 | 層級 | 依賴 | 設計狀態 |
|---|---------|------|------|---------|
| 18 | 成就/稱號系統 | Feature | 2, 17, 15 | ✅ GDD 完成（Ch5）|
| 19 | 任務系統 | Feature | 14, 12, 15, 16 | ✅ GDD 已審核 v3.0（task-system.md）\| 怡嘉審核：2026-05-12，E11 決定：道具留在玩家身上 |
| 20 | 隨機事件系統 | Feature | 1, 10, 14, 47 | ✅ GDD 已審核 v1.1（random-events-system.md）\| 怡嘉審核：2026-05-12，補齊V2葉節點定義、防迴圈機制、時空衝突規則 |
| 21 | 事件敘事系統 | Feature | 15, 20, 47 | ✅ GDD 已審核 v1.0（narrative-event-system.md）\| 怡嘉審核：2026-05-12 |
| 27 | 關係網絡 UI | Presentation | 15 | 🔲 未開始 |
| 30 | 通知/提示系統 | Presentation | 16, 20 | 🔲 未開始 |
| 24 | 日誌/記事系統 | Feature | 1, 15, 18, 35 | 🔲 未開始 |
| 34 | 新手引導/情境提示層 | Polish | 5, 10, 14 | 🔲 未開始 |

---

## Alpha

| # | 系統名稱 | 層級 | 依賴 | 設計狀態 |
|---|---------|------|------|---------|
| 22 | 門派政治系統 | Feature | 17, 15 | ✅ GDD 完成（Ch11）|
| 46 | 江湖風雲榜系統 | Feature | 2, 14, 15, 16 | ✅ GDD 完成（jianghu-ranking-system.md）|
| 47 | 身份印刻系統 | Foundation | 14, 15, 20 | ✅ GDD 已審核 v1.0（identity-imprint-system.md）\| 怡嘉審核：2026-05-12 |
| 23 | 朝廷官場系統 | Feature | 17, 1 | ✅ GDD 完成（Ch11）|
| 39 | 本地化系統 | 技術基礎 | — | 🔲 未開始 |
| 42 | 除錯工具 | 技術基礎 | — | 🔲 未開始 |

---

## Full Vision

| # | 系統名稱 | 層級 | 依賴 | 設計狀態 |
|---|---------|------|------|---------|
| 31 | 跨局 Meta 進度系統 | Meta | 18, 5 | 📝 GDD 有框架（game-concept）|
| 32 | 傳代系統 | Meta | 1, 15, 31 | ✅ GDD 完成（Ch13）|
| 33 | 局末人生回顧系統 | Meta | 31, 18, 24 | ✅ GDD 已審核 v1.0（life-retrospect-system.md）\| 怡嘉審核：2026-05-12 |
| 43 | 壽命/老化 UI（含局末）| Presentation | 33 | 🔲 未開始 |

---

## 依賴映射（設計順序）

```
Foundation (先設計)
  ↓
技術基礎設施（事件總線→資料層→排程→FSM→RNG→輸入）
  ↓
Core（角色創建→天賦→修煉→武學→裝備→地圖→戰鬥→經濟→庫存）
  ↓
Feature-MVP（NPC行為→NPC關係→消息傳播→陣營）
  ↓
Presentation-MVP（地圖UI→角色面板→戰鬥UI→時間UI）
  ↓
Feature-VS（成就→任務→隨機事件→事件敘事）
  ↓
Presentation-VS（關係網路UI→通知→日誌）
  ↓
Alpha（門派政治→官場→i18n→Debug）
  ↓
Full Vision（Meta→傳代→人生回顧）
```

---

## 高風險系統清單

| 系統 | 風險類型 | 緩解策略 |
|------|---------|---------|
| NPC 行為系統 | 效能爆幀 | NPC 排程器 + LOD tick |
| NPC 人際關係 | 記憶體規模 | 資料持久化層抽象 |
| 存檔/讀檔 | 複雜度極高 | 最早定義存檔格式規格 |
| 程序化世界生成 | 跨局一致性 | 種子隨機服務確保可重現 |
| 傳代系統 | 跨存檔資料遷移 | 版本控制欄位設計 |

---

## 設計進度追蹤

- ✅ GDD 完成：23 個
- 📝 GDD 有框架：2 個
- 🔲 未開始：19 個
- ✅ GDD 審查完成：2 個（combat-system, status-effects）| 待二次確認：1 個（status-effects）

**下一個待設計系統（依設計順序）：** 存檔/讀檔系統（#3）

---

*CD-SYSTEMS：lean 模式跳過 | 下一步：`/design-system` 逐一設計未開始的系統*
