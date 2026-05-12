請依序讀取以下GDD文件，從設計一致性和邏輯角度進行評閱，找出問題並整理報告：

1. design/gdd/time-aging-system.md
2. design/gdd/character-creation-system.md
3. design/gdd/talent-system.md
4. design/gdd/combat-system.md
5. design/gdd/inventory-management-system.md
6. design/gdd/status-effects-system.md
7. design/gdd/resistance-system.md
8. design/gdd/personality-system.md
9. design/gdd/jianghu-ranking-system.md
10. design/gdd/task-system.md

評閱重點：

(1) 跨文件術語一致性：同一個概念在不同文件中叫法是否一致？例如「體魄」「內力」等屬性名稱，「severity」等技術術語

(2) 公式屬性名稱統一性：各文件的公式中引用的屬性縮寫（BOD、NRI、AGL等）是否和屬性系統定義的縮寫一致？

(3) 系統依賴對稱性：如果文件A說「依賴系統B」，那麼文件B的「依賴本系統」部分是否也提到了A？找出所有不對稱的依賴聲明。

(4) 驗收標準可測試性：逐條檢查驗收標準，找出「感受類」或「模糊類」的標準（例如「玩家感覺好」這種無法量化的），列出需要改寫為可測試標準的條目。

(5) 數值自洽性：文件中的範例計算結果是否和公式一致？找出計算錯誤。

⚠️ 重要：你必須先呼叫 write_file 將完整報告寫入 design/gdd/drafts/qingxia-review-2026-05-12.md，確認寫入成功後，才可以呼叫 finish_task。不寫入文件直接 finish_task 是不完整的任務執行。

報告格式使用繁體中文Markdown，結構如下：

# 青霞 GDD 評閱報告
日期：2026-05-12

## 術語不一致清單
## 依賴關係不對稱清單
## 模糊驗收標準清單
## 計算錯誤清單
## 整體觀察
