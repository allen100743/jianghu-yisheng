你需要完成跨文件一致性檢查。⚠️ 重要執行原則：每完成一個步驟就立刻寫入結果，不要等到最後才寫。

**輸出文件：** design/gdd/drafts/qingxia-consistency-2026-05-12.md

---

**步驟1**：用 write_file 建立輸出文件，內容為：
```
# 青霞一致性檢查報告
日期：2026-05-12

## 屬性縮寫對照表
（分析中...）

## 系統依賴不對稱
（分析中...）

## 總結
（分析中...）
```
確認寫入成功後繼續。

---

**步驟2**：讀取 design/gdd/resistance-system.md，找出所有屬性縮寫（BOD/NRI/AGL/WIS等）和它們代表的中文屬性名。
讀完後，用 write_file 更新輸出文件，在「屬性縮寫對照表」章節下加入：
```
### resistance-system.md 使用的縮寫
[你找到的縮寫列表]
```

---

**步驟3**：讀取 design/gdd/status-effects-system.md，同樣找出屬性縮寫。
讀完後，用 append_file 在輸出文件的縮寫章節追加：
```
### status-effects-system.md 使用的縮寫
[你找到的縮寫列表]
```

---

**步驟4**：讀取 design/gdd/personality-system.md，找出屬性縮寫。
讀完後 append_file 追加：
```
### personality-system.md 使用的縮寫
[你找到的縮寫列表]
```

---

**步驟5**：比較步驟2-4中找到的所有縮寫，判斷是否一致。用 write_file 更新輸出文件的「屬性縮寫對照表」章節，寫入完整的對照分析。

---

**步驟6**：讀取 design/gdd/task-system.md 的第6節「系統依賴」，找出它聲明依賴的所有系統。
讀完後 append_file 追加：
```
## 系統依賴不對稱分析

### task-system.md 聲明的依賴
[你找到的依賴列表]
```

---

**步驟7**：讀取 design/gdd/combat-system.md 的第6節「系統依賴」，找出它聲明依賴的系統，以及哪些系統依賴它。
讀完後 append_file 追加：
```
### combat-system.md 的依賴聲明
[你找到的內容]
```

---

**步驟8**：根據步驟6-7的資料，分析有沒有「A說依賴B，但B沒有列出A依賴它」的不對稱情況。用 write_file 更新輸出文件的「系統依賴不對稱」章節，寫入分析結論。

---

**步驟9**：用 write_file 更新輸出文件的「總結」章節，寫入：發現幾個不一致、最重要的問題是什麼。

**步驟10**：⚠️ 確認 design/gdd/drafts/qingxia-consistency-2026-05-12.md 存在且有實質內容後，呼叫 finish_task，在 files_written 中列出該文件路徑。
