# 隨機事件系統 GDD — 審查記錄
*design/gdd/random-events-system.md*

---

## Review — 2026-05-12 — Verdict: NEEDS REVISION → 修復完成

**Scope signal:** XL（跨系統核心引擎，5+ 依賴，3+ 公式，新系統 #47 ADR 待建）
**Specialists:** lean mode（單工作階段）
**Blocking items:** 3 → 全部修復 | Recommended: 5 → 全部修復
**Prior verdict resolved:** N/A（首次審查）

**Summary:** 設計概念紮實，從情境先行方法衍生的 7 屬性架構支撐了完整規格。主要問題是 4 個未定義型別（CausalLink/TimeWindow/NarrativeVariant/AwarenessLevel）和「身份印刻系統」的缺失依賴。v1.1 已全部補齊型別定義、MVP/V2 邊界、依賴更新，新增 #47 身份印刻系統入 systems-index。

## 製作人決策記錄（2026-05-12）

| 決策 | 問題 | 決定 |
|------|------|------|
| A | 身份印刻系統歸屬 | **獨立新系統 #47**，後續品霖設計 GDD |

## 修復清單

- [x] B1 身份印刻系統更新為 #47，依賴表補充
- [x] B2 補齊 CausalLink / TimeWindow / NarrativeVariant / AwarenessLevel 型別定義
- [x] B3 核心機制補 MVP 範圍表（3.2.1 節）+ 效能邊界說明
- [x] R1 AC7 改為測試機制，不寫死具體地點/節日
- [x] R2 「因果關鍵實例」補充 `is_critical` 欄位判定規則
- [x] R3 依賴表拆分 #14/#15，明確 NPC 目標系統歸屬
- [x] R4 MVP 效能邊界說明（50 實例 × 4 種葉節點 < 1ms）
- [x] R5 公式 4.2 補設計意圖說明（愛與仇等效是刻意設計）
