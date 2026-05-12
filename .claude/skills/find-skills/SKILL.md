---
name: find-skills
description: 高效找技能——搜尋、評估、推薦適合本專案的新 Claude Code Skills。當使用者想找新技能、想知道有什麼 Skills 可用、或想升級現有工具鏈時觸發。
user-invocable: true
allowed-tools: WebSearch, WebFetch, Bash, Read, Glob
---

# Find-Skills：高效找技能

當用戶說「找找有沒有新 Skills」、「有沒有適合 XX 的技能」、「幫我搜尋 Skills」時觸發。

## 本專案背景

- 武俠沙盒生涯 RPG（Godot 4.6 + GDScript）
- Solo + AI 製作模式
- 已安裝 Skills 類別：遊戲工作室（72+）、Superpowers、UI/UX 設計、PUA、文件格式處理

## 執行流程

### 1. 理解查詢意圖

判斷用戶是：
- **廣泛搜尋**：「有沒有新的好 Skills」→ 執行全面掃描
- **針對性搜尋**：「找個幫助 XX 的 Skill」→ 針對該功能搜尋
- **更新檢查**：「我們的 Skills 有沒有更新版本」→ 檢查已安裝 Skills 的更新

### 2. 搜尋來源（依序執行）

**主要 GitHub 來源：**
- `travisvn/awesome-claude-skills` — 社群精選
- `anthropics/skills` — Anthropic 官方
- `obra/superpowers` — Superpowers 框架更新
- `VoltAgent/awesome-agent-skills` — 跨平台 1000+ Skills
- `nextlevelbuilder/ui-ux-pro-max-skill` — 設計類更新

**補充搜尋：**
- WebSearch: `"claude code skills" site:github.com [當前年份]`
- WebSearch: 根據用戶查詢的具體功能搜尋

### 3. 評估標準

只推薦符合**所有**以下條件的 Skill：
- ✅ 我們還沒有
- ✅ 有完整的 SKILL.md 檔案（不只是 README）
- ✅ 對遊戲開發、AI 輔助製作、UI/UX、或製作人工作流有直接幫助
- ✅ GitHub 有 star 或近三個月有更新

### 4. 輸出格式

```
## 🔍 Skills 搜尋結果

### ✅ 推薦安裝
| Skill | 來源 | 用途 | 安裝指令 |
|---|---|---|---|
| [名稱] | [GitHub repo] | [一句話說明] | gh api "repos/[path]" ... |

### 👀 值得觀察
[尚未成熟但值得持續關注的]

### ℹ️ 搜尋摘要
共搜尋了 X 個來源，找到 Y 個候選，推薦安裝 Z 個。
```

### 5. 安裝協助

如果用戶說「裝」或確認要安裝，直接執行：
```bash
mkdir -p ".claude/skills/[skill-name]"
gh api "repos/[owner]/[repo]/contents/[path]/SKILL.md" --jq '.content' | base64 -d > ".claude/skills/[skill-name]/SKILL.md"
```

安裝後確認 Skill 出現在清單中才算完成。
