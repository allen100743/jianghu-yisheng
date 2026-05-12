# Xiaomi MiMo Orbit 百萬兆 Token 申請材料
*品霖 + 怡嘉 共同準備 | 2026-05-12*

---

## Q04 答案（直接貼入，約 1080 字）

我們申報的專案《江湖一生》，是由Solo開發者基於**多層級、異構AI多Agent協作架構**完全驅動的武俠沙盒RPG設計工程。本計劃並非單純使用一個大模型，而是建立了一套高度複雜、可自主運行的「AI遊戲設計工廠」。我們預計整合MiMo V2.5作為推理增強核心，用於競品分析與設計評審。

**1. 工程複雜度：四層AI體系與48個子Agent協同**

- **第零層 - 主控決策層（怡嘉 / Claude Sonnet 4.6）**：接收高階指令、拆解任務、分派給下層Agent，對產出審核決策。
- **第一層 - 策略設計層（品霖、靜怡 / DeepSeek V4）**：負責核心玩法與UX設計，產出GDD與UX Spec。
- **第二層 - 批量執行層（青霞 / Qwen2.5:32B本地部署）**：執行夜間無人值守任務佇列，掃描文件進行一致性檢查、批量修改，透過Telegram發送結果。
- **第三層 - 通訊感知層（自建工具鏈）**：Telegram ↔ VS Code雙向通訊橋接、截圖自動下載+Claude視覺識別流水線、Inline Keyboard按鈕回調決策鏈路。

整個架構由**48個Claude Code子Agent**構成，各自擁有獨立職責域。自建6個核心Python腳本（`planning_dept.py`, `jingyi_agent.py`, `qingxia_agent.py`, `yijia_notify.py`等）管理複雜的排程與通訊邏輯，具備狀態管理、任務佇列與錯誤恢復機制。

**2. 長鏈推理與多Agent協作流水線**

1. 製作人在Telegram下達指令
2. 怡嘉（Claude）拆解任務：讀取GDD → 分析數值 → 建立對照表 → 提出修改建議
3. 品霖（DeepSeek）規劃分析維度，靜怡定義UX格式
4. 青霞（Qwen本地）啟動`qingxia_overnight.py`，夜間接力執行掃描與輸出報告
5. 報告傳回怡嘉審核，生成帶「批准/駁回/修改」按鈕的Telegram通知
6. 製作人點選按鈕，決策自動寫回文件，觸發下一個Agent繼續執行

涉及**3個不同雲端模型服務 + 1個本地模型 + 自建工具鏈**的精確協作，實現「無人值守，遠端指揮」的開發模式。

**3. 可量化成果**

- **42份系統GDD（約6萬字）**，全由AI協作生成並交叉審核
- **6份完整UX Spec**，包含狀態效果HUD等微交互規格
- **6個自建工具腳本**，覆蓋多Agent排程、通訊、批量執行全鏈路

**MiMo整合規劃：** 利用MiMo V2.5推理能力，用於競品設計架構深度因果推斷，以及對多個設計方案進行邏輯漏洞與平衡性評估，替換第一層DeepSeek。

---

## Q05 說明文字（直接貼入）

為展現本專案工程複雜度與多Agent協作創新性，提交材料按優先級排列：**①GitHub倉庫**（含四層Agent原始碼與架構圖）；**②2-3分鐘演示影片**（完整記錄Telegram發指令→多Agent長鏈推理→製作人決策閉環的實際操作）；**③關鍵環節截圖**（夜間無人值守佇列的執行狀態與即時回饋機制）。三類材料層層遞進，完整覆蓋「工程複雜度」、「多Agent協作」及「長鏈推理」的評審需求。

---

## Q05 GitHub 連結

https://github.com/allen100743/jianghu-yisheng

---

## Q05 截圖建議（補充佐證，選擇性提交）

1. `tools/qingxia_tasks/overnight_queue.md` — 顯示夜間任務佇列執行狀態
2. Telegram Inline Keyboard 按鈕通知截圖
3. `design/gdd/systems-index.md` — 顯示 42 個系統索引

---

## 填表注意事項

- **使用的 AI 工具**：VS Code + Claude Code（主力開發環境）
- **底層模型**：Claude、DeepSeek、MiMo（計劃整合）
- **填寫郵箱**：allen100743@gmail.com（必須與帳號一致）

> VS Code 是整個工作流的核心 IDE，Claude Code 作為 VS Code 擴充套件在裡面運行，
> 所有 Agent 調度、代碼審查、文件寫入都在 VS Code 環境內完成。
> 如果表單有多選，VS Code 和 Claude Code 都要勾選。
