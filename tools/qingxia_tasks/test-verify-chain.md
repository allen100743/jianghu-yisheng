這是一個驗證測試任務，確認夜間佇列系統運作正常。

**步驟1**：讀取 design/gdd/systems-index.md，統計已完成（✅）和未開始（🔲）的系統各有幾個。

**步驟2**：用 write_file 將結果寫入 tools/qingxia_tasks/results/test-result.md，內容為：
```
# 青霞鏈路驗證測試
時間：[當前時間]
結果：鏈路正常

## GDD 進度摘要
已完成：[數量] 個系統
未開始：[數量] 個系統

## 結論
夜間佇列系統運作正常，青霞可以執行夜間任務。
```

⚠️ 確認文件寫入成功後，呼叫 finish_task，summary 寫「鏈路驗證成功」，files_written 列出 tools/qingxia_tasks/results/test-result.md。
