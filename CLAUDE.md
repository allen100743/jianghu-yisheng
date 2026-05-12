# Claude Code Game Studios -- Game Studio Agent Architecture

Indie game development managed through 48 coordinated Claude Code subagents.
Each agent owns a specific domain, enforcing separation of concerns and quality.

## ⚠️ 強制：每次任務前必須查閱

@.claude/docs/skill-dispatch.md

## Technology Stack

- **Engine**: Godot 4.6
- **Language**: GDScript
- **Version Control**: Git with trunk-based development
- **Build System**: SCons (engine), Godot Export Templates
- **Asset Pipeline**: Godot Import System + custom resource pipeline

> **Note**: Engine-specialist agents exist for Godot, Unity, and Unreal with
> dedicated sub-specialists. Use the set matching your engine.

## Project Structure

@.claude/docs/directory-structure.md

## Engine Version Reference

@docs/engine-reference/godot/VERSION.md

## Technical Preferences

@.claude/docs/technical-preferences.md

## Coordination Rules

@.claude/docs/coordination-rules.md

## Collaboration Protocol

**User-driven collaboration, not autonomous execution.**
Every task follows: **Question -> Options -> Decision -> Draft -> Approval**

- Agents MUST ask "May I write this to [filepath]?" before using Write/Edit tools
- Agents MUST show drafts or summaries before requesting approval
- Multi-file changes require explicit approval for the full changeset
- No commits without user instruction

See `docs/COLLABORATIVE-DESIGN-PRINCIPLE.md` for full protocol and examples.

> **First session?** If the project has no engine configured and no game concept,
> run `/start` to begin the guided onboarding flow.

## Coding Standards

@.claude/docs/coding-standards.md

## Context Management

@.claude/docs/context-management.md

## 主動通知製作人（Telegram）

製作人不一定在電腦旁。以下情況**必須**呼叫 `tools/yijia_notify.py` 發 Telegram：

| 情況 | 類型 | 範例 |
|------|------|------|
| 長時間任務完成（>2分鐘） | `done` | GDD 掃描完成、測試全過 |
| 錯誤/服務崩潰 | `error` | 編譯失敗、watchdog 掛掉 |
| 需要製作人拍板才能繼續 | `decide` | 設計分岔、不確定方向 |
| 重要進度里程碑 | `info` | Sprint 完成、ADR 建立 |

```bash
python tools/yijia_notify.py --type decide --title "需要你決定" --body "問題描述" --detail "補充細節（可選）"
```

**不需要發的情況**：一般對話、小修改、用戶在線時。
