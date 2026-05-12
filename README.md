# 《江湖一生》— AI 多 Agent 協作遊戲設計工廠

> 武俠沙盒生涯 RPG | Solo 開發 | 48 個 AI 子 Agent 協同 | Godot 4.6

---

## 這是什麼？

《江湖一生》是由**單人開發者 + AI 多 Agent 架構**共同打造的武俠沙盒 RPG。玩家扮演一個活在明朝洪武年間的武俠角色，從出生到死亡走完完整一生。

本倉庫的核心創新：**一套讓 Solo 開發者擁有整個遊戲工作室能力的 AI Agent 作業系統**。

---

## 四層 AI Agent 架構

```
製作人（人類）
    │
    ▼
第零層：主控決策層  ─  怡嘉（Claude Sonnet 4.6）
         任務拆解、Agent 調度、審核決策
    │
    ├─► 第一層：品霖（DeepSeek V4）  ─  策劃系統設計 → GDD
    ├─► 第一層：靜怡（DeepSeek V4）  ─  UX 交互設計 → UX Spec
    └─► 第二層：青霞（Qwen2.5:32B 本地）─ 夜間批量執行佇列
    
第三層：自建通訊工具鏈
  Telegram ↔ VS Code 雙向橋接
  截圖自動下載 + Claude 視覺識別
  Inline Keyboard 按鈕 → 決策回調
```

---

## 長鏈推理工作流

```
製作人 Telegram 指令
  → 怡嘉拆解任務
    → 品霖/靜怡設計（DeepSeek）
    → 青霞批量執行（Qwen 本地，夜間無人值守）
  → 怡嘉審核 → 帶按鈕 Telegram 通知
    → 製作人點按鈕決策
      → 決策自動寫回文件 → 下一個 Agent 繼續
```

涉及 **3 個雲端模型 API + 1 個本地模型 + 自建工具鏈**精確協作。

---

## 自建工具腳本

| 腳本 | 功能 |
|------|------|
| `tools/planning_dept.py` | 品霖策劃腳本（10+ 任務類型） |
| `tools/jingyi_agent.py` | 靜怡 UX 設計腳本（7 種 Spec 類型） |
| `tools/qingxia_agent.py` | 青霞任務執行框架（Function Calling） |
| `tools/qingxia_overnight.py` | 青霞夜間批次佇列 |
| `tools/jingyi_overnight.py` | 靜怡 UX Spec 批次執行器 |
| `tools/telegram_qwen_bot.py` | Telegram 接收中繼（含圖片下載） |
| `tools/telegram_watcher.py` | 青霞自主回覆 + 怡嘉備援路由 |
| `tools/yijia_notify.py` | 怡嘉主動通知（4 種類型 + 按鈕）|
| `tools/watchdog.py` | 全服務守護程序 |

---

## 可量化成果

- **42 個系統 GDD**（遊戲設計文件，約 6 萬字），AI 協作生成並審核
- **6 份 UX Spec**（HUD、互動模式庫、無障礙、角色創建、死亡結算等）
- **完整通訊基礎設施**：Telegram ↔ VS Code、截圖識別、按鈕決策
- **無人值守夜間批次**：單次掃描 8+ GDD，自動輸出一致性報告

---

## 技術棧

- **引擎**：Godot 4.6 + GDScript
- **主控 AI**：Claude Sonnet 4.6
- **策劃/UX AI**：DeepSeek V4-flash / V4-pro  
- **批量執行 AI**：Qwen2.5:32B（本地 Ollama，RTX 4090）
- **通訊**：Telegram Bot API + Python 自建橋接

---

## 環境設定

```bash
cp .env.example .env
# 填入 TELEGRAM_TOKEN / TELEGRAM_CHAT_ID / DEEPSEEK_API_KEY
```

---

## 遊戲核心設計

**四大支柱**：這是我的一生 · 選擇有代價 · 江湖有人 · 時間可見

背景：明朝洪武年間，武俠非修仙，人終究會老死。

---

*本倉庫展示 AI Agent 協作開發工作流，遊戲本體仍在開發中。*
