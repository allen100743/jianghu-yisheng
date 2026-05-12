---
name: project-event-bus-blocker
description: #35 事件總線 GDD 未完成，阻斷任務系統 AC7/AC8 測試，需技術總監先定義 stub 介面
metadata:
  type: project
---

事件總線（#35）在 systems-index.md 中狀態為「未開始」（2026-05-12）。

任務系統 #19 的 AC7（失效不廣播 failure_consequence）和 AC8（完成事件廣播）均依賴 #35 的可觀測介面。

在 #35 GDD 完成並定義以下內容前，AC7/AC8 無法寫出具體斷言：
- Signal 名稱與參數型別（e.g. quest_completed(task_id, source_entity_id)）
- 訂閱機制（direct connect？MessageBroker？AutoLoad singleton？）
- 測試環境的 mock/stub 策略（如何驗證「某事件沒有被發送」）

**Why:** 驗證「不廣播」比驗證「廣播了」更難，必須有 stub 才能做負向斷言。
**How to apply:** 排任務系統開發 sprint 前，先確認 #35 至少有測試用 stub 介面定義。相關到 [[project-task-system-ac-audit]]。
