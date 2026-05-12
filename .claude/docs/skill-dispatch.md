# 技能調度矩陣 — 強制規範

**本文件是調度規則，不是建議。收到任務前必須對照此表。**

## 規則零：競品研究必須先於設計（最高優先）

**任何涉及競品的系統設計，必須先完成研究再設計，禁止用 LLM 印象代替真實資料。**

| 研究來源 | 可信度 | 何時使用 |
|---------|-------|---------|
| 競品安裝目錄讀取（如鬼谷八荒 XSMSX/）| ⭐⭐⭐ 最高 | 有讀取到真實文件時優先 |
| 怡嘉 WebSearch 查驗社群攻略 | ⭐⭐ 高 | 文件不可讀時，怡嘉搜尋後存入 design/intelligence/ |
| 品霖 DeepSeek 推理 | ⭐ 低 | **禁止用於競品事實描述**，只能用於設計推導 |
| 怡嘉/品霖 LLM 印象記憶 | ❌ 不可用 | **嚴格禁止**，曾造成龍胤武學設計偏差 |

### 強制流程
```
怡嘉 WebSearch 查驗 → 存入 design/intelligence/ → 品霖讀取設計 → 怡嘉審核準確性 → 製作人看結論
```

製作人不應該成為「解釋競品設計」的人。如果製作人需要解釋，說明研究沒有做到位。

---

## 規則一：任務開始前必查

| 任務類型 | 必用技能 | 禁止自行處理 |
|---------|---------|------------|
| 遊戲機制設計 | `/brainstorm` → `/quick-design` → `/design-review` | 直接寫入 GDD |
| 修訂已完成 GDD | `/propagate-design-change` → `/design-review` | 直接編輯 GDD 不通知下游 |
| 系統依賴分析 | `/map-systems` | 手動推斷依賴 |
| 數值/平衡審查 | `/balance-check` | 憑直覺調數值 |
| 新架構決策 | `/architecture-decision` | 直接改代碼 |
| 代碼實作 | `/dev-story` → `/code-review` | 跳過審查直接寫 |
| 新增 GDD 章節 | `/design-system` | 直接寫內容 |
| GDD 全面審查 | `/review-all-gdds` | 抽查幾章就算 |
| Sprint 規劃 | `/sprint-plan` | 口頭列任務 |
| 安全問題 | `/security-audit` | 手動判斷 |
| UX/介面設計 | `/ux-design` → `/ux-review` | 自行決定介面 |

## 規則二：Agent 路由

| 文件類型 | 必須派給 |
|---------|---------|
| `.gd` 文件 | `godot-gdscript-specialist` |
| `.gdshader` | `godot-shader-specialist` |
| 架構決策 | `technical-director` |
| 設計衝突 | `creative-director` |
| 跨部門協調 | `producer` |
| UX spec | `ux-designer` |

## 規則三：禁止跳過的質量關卡

1. **GDD 寫完** → 必須 `/design-review` 才能進開發
2. **代碼寫完** → 必須 `/code-review` 才能 commit
3. **數值修改** → 必須 `/balance-check` 才能確認
4. **準備開發** → 必須 `/gate-check` 通過才能進下個階段

## 規則四：ECC 安全標準（新增）

- 每次 Write/Edit 代碼文件後：security-scan.sh 自動執行
- 每次 Session 開始：讀此文件，確認當前任務對應的技能
- 敏感文件（.env, keys, tokens）：禁止讀取，settings.json 已封鎖

## 規則五：Claude Code 指令白名單

**真實存在，可直接使用：**

| 指令 | 用途 |
|------|------|
| `/compact` | 壓縮 context，保留摘要 |
| `/clear` | 完全清除對話 |
| `/model haiku\|sonnet\|opus` | 切換模型 |
| `/help` | 顯示說明 |
| 本專案 custom skills | `/brainstorm`, `/design-system`, `/map-systems` 等（見 .claude/skills/） |

**以下指令在 Claude Code 不存在，使用無效：**
`/init` `/doctor` `/view` `/search` `/diff` `/undo` `/rewind` `/lint`
`/coverage` `/commit` `/fork` `/resume` `/btw` `/rename` `/exit`
`/save` `/forget` `/effort` `/lang` `/style` `/mode` `/terminal` `/plugin`

## 自我審查清單（每次回應前）

- [ ] 這個任務有對應的 Skill 嗎？
- [ ] 需要派 Agent 嗎，還是我自己能做？
- [ ] 有沒有質量關卡需要先跑？
- [ ] 這個改動有沒有安全風險？
