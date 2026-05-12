---
name: project-ux-infrastructure
description: 靜怡的工具鏈現況：jingyi_agent.py 腳本、design/ux/ 目錄結構、jingyi_context/ 知識庫
metadata:
  type: project
---

靜怡現在有完整的 DeepSeek 工具鏈，不再依賴 Claude Sonnet token。

**Why:** 2026-05-12 完成升級，降低成本並提升獨立產出能力。

**How to apply:** 需要生成 UX Spec 時，告知製作人使用以下指令，不要在 Claude Code session 內直接生成（節省 token）：

```bash
python tools/jingyi_agent.py --task [任務類型] [--screen 畫面名稱]
```

可用任務：
- `screen-spec` —— 指定畫面 UX Spec（搭配 --screen）
- `hud-design` —— 主遊戲 HUD 總規格
- `status-effects-hud` —— 傷勢/狀態效果 HUD
- `flow-mapping` —— 玩家流程圖（搭配 --screen）
- `onboarding-design` —— 新手引導設計
- `accessibility-audit` —— 無障礙規格
- `interaction-patterns` —— 互動模式庫

知識庫位置：`tools/jingyi_context/`（4 個檔案，每次任務自動載入）
Spec 輸出位置：`design/ux/`（含 README 狀態索引）
模板位置：`design/ux/_template.md`
