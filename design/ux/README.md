# UX Spec 目錄

*李靜怡主導 | 更新：2026-05-12*

---

## 目錄規範

| 類型 | 檔名格式 | 說明 |
|------|---------|------|
| 畫面 Spec | `[screen-slug].md` | 單一畫面的完整 UX 規格 |
| HUD 設計 | `hud.md` | 主遊戲 HUD 總規格 |
| 互動模式庫 | `interaction-patterns.md` | 全局重複使用的互動模式 |
| 無障礙規格 | `accessibility-requirements.md` | 全局無障礙設計要求 |
| 模板 | `_template.md` | 新 Spec 的起始模板 |

---

## Spec 狀態追蹤

| 檔案 | 內容 | 狀態 | 優先級 |
|------|------|------|--------|
| `status-effects-hud-2026-05-12.md` | 傷勢/狀態效果 HUD | ✅ 草稿完成 | P0 |
| `hud-design-2026-05-12.md` | 主遊戲 HUD 總規格 | ✅ 草稿完成 | P0 |
| `interaction-patterns-2026-05-12.md` | 互動模式庫 | ✅ 草稿完成 | P1 |
| `accessibility-audit-2026-05-12.md` | 無障礙規格 | ✅ 草稿完成 | P1 |
| `角色創建.md` | 角色創建畫面 | ✅ 草稿完成 | P1 |
| `死亡結算.md` | 死亡結算畫面 | ✅ 草稿完成 | P2 |
| `main-game.md` | 主遊戲畫面 | 🔲 待生成 | P2 |
| `task-log.md` | 任務記錄介面 | 🔲 待生成 | P2 |

---

## 生成方式

```bash
# 指定畫面 Spec
python tools/jingyi_agent.py --task screen-spec --screen "角色創建"

# HUD 總覽
python tools/jingyi_agent.py --task hud-design

# 互動模式庫
python tools/jingyi_agent.py --task interaction-patterns

# 無障礙規格
python tools/jingyi_agent.py --task accessibility-audit

# 狀態效果 HUD（已有研究，優先生成）
python tools/jingyi_agent.py --task status-effects-hud
```
