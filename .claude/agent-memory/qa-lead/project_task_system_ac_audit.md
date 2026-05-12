---
name: project-task-system-ac-audit
description: 任務系統 GDD v2.0 的 12 條 AC 對抗性稽核結果：模糊 AC、關鍵路徑缺口、規格漏洞清單
metadata:
  type: project
---

任務系統（#19）GDD v2.0 的 12 條 AC 經對抗性稽核（2026-05-12），發現以下問題：

**模糊 AC（無法客觀判定）：**
- AC1：觸發來源未指定 source_type，六種觸發路徑各不同，需拆分
- AC8：依賴 #35 事件總線 stub 介面，介面未定義則廣播無法斷言
- AC10：依賴 #33 局末系統（未開始），列表範圍（ACTIVE vs ABANDONED）未定義

**規格漏洞（需先補設計再寫 AC）：**
- ABANDONED 狀態行為完全未定義（事件廣播？failure_consequence？conflict_group 處理？）
- branch_conditions 解析規則未定義（評估順序？無匹配時任務狀態？）

**關鍵路徑缺口（已有規則但無 AC）：**
- WORLD_STATE 截止類型（3.3 節）→ 需 AC13
- HOSTILE_TRIGGER 來源類型（3.1 節）→ 需 AC14
- 速度獎勵公式（4.2 節，Logic 型 BLOCKING）→ 需 AC15/AC16
- E2 同幀 conflict_group 決勝（字母序）→ 需 AC17
- DORMANT 狀態持續監聽失效條件（3.2 規則 4）→ 需 AC18

**速度獎勵公式 Bug：**
min_multiplier=0.5 在現有公式 max(0.5, 1.0+(days/total)×0.5) 下從未觸達
（days_remaining≥0 時最低輸出為 1.0）。需品霖確認是否要修正公式。

**Why:** 稽核目標是確保開發前測試策略完整，防止 Logic 型故事無測試證據。
**How to apply:** 開發前需解決 ABANDONED/branch_conditions 規格漏洞；#35 stub 就位前 AC7/AC8 不可排入 sprint。
