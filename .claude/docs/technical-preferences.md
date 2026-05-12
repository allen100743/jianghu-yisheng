# Technical Preferences

<!-- Populated by /setup-engine. Updated as the user makes decisions throughout development. -->
<!-- All agents reference this file for project-specific standards and conventions. -->

## Engine & Language

- **Engine**: Godot 4.6
- **Language**: GDScript
- **Rendering**: Forward+ (Godot 4.6 default; supports 2D and stylized 3D)
- **Physics**: Jolt Physics (Godot 4.6 default — replaces GodotPhysics as default)

## Input & Platform

<!-- Written by /setup-engine. Read by /ux-design, /ux-review, /test-setup, /team-ui, and /dev-story -->
<!-- to scope interaction specs, test helpers, and implementation to the correct input methods. -->

- **Target Platforms**: PC (Steam primary), Epic Games Store (future)
- **Input Methods**: Keyboard/Mouse, Gamepad
- **Primary Input**: Keyboard/Mouse
- **Gamepad Support**: Partial (recommended — Steam Input API for remapping)
- **Touch Support**: None
- **Platform Notes**: Steam 主平台；未來擴展 Epic；需支援 Steam Input API for gamepad remapping；UI 不可使用 hover-only 互動（確保 gamepad 可操作）

## Naming Conventions

- **Classes**: PascalCase (e.g., `PlayerController`)
- **Variables**: snake_case (e.g., `move_speed`)
- **Functions**: snake_case (e.g., `take_damage()`)
- **Signals/Events**: snake_case past tense (e.g., `health_changed`, `player_died`)
- **Files**: snake_case matching class (e.g., `player_controller.gd`)
- **Scenes/Prefabs**: PascalCase matching root node (e.g., `PlayerController.tscn`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_HEALTH`, `BASE_DAMAGE`)

## Performance Budgets

- **Target Framerate**: 60 fps
- **Frame Budget**: 16.6 ms
- **Draw Calls**: 500 (2D stylized；大量精靈但無複雜 3D)
- **Memory Ceiling**: 2 GB

## Testing

- **Framework**: GUT (Godot Unit Testing) — Godot 標準測試框架
- **Minimum Coverage**: 80%（邏輯系統）
- **Required Tests**: Balance formulas, gameplay systems, networking (if applicable)

## Core Architecture Patterns（強制）

### 資料驅動架構（HOI4 學習）
- **所有遊戲數值必須外部化**到 `assets/data/` 的 JSON/Resource 檔
- GDScript 只讀取配置，**禁止在代碼中硬編碼任何遊戲平衡數值**
- 修改數值 = 改 JSON，不改代碼，不需要程序員介入
- 配置檔路徑規範：`assets/data/[system]/[config_name].json`

### 修飾詞疊加架構（HOI4 學習）
屬性計算必須使用修飾詞疊加，**禁止使用 if-else 分支計算最終屬性**：
```gdscript
# 正確：修飾詞疊加
final_attack = base_attack
for modifier in active_modifiers:
    final_attack = modifier.apply(final_attack)

# 禁止：if-else 分支
# if has_buff: attack += 10
# elif is_wounded: attack -= 20
```
修飾詞系統支援：flat 加減、percentage 乘除、setMax 上限覆蓋。

### Severity 連續值狀態模型（RimWorld 學習）
所有狀態效果（傷勢、中毒、內傷）使用 0.0→1.0 連續 severity 值：
- **禁止**使用「輕傷/中傷/重傷」等離散枚舉
- severity 每個關鍵閾值（如 0.3 / 0.6 / 0.9）觸發新的 stage 效果
- severity ≥ 1.0 觸發瀕死或死亡事件
- 每日自然恢復 -0.01，治療加速恢復

## Forbidden Patterns

- 硬編碼遊戲平衡數值（必須外部化到 assets/data/）
- 用 if-else 分支計算角色最終屬性（必須用修飾詞疊加）
- 用離散枚舉表示狀態嚴重度（必須用 severity 連續值）

## Allowed Libraries / Addons

<!-- Add approved third-party dependencies here -->
<!-- Only add when actively integrating — do NOT add speculatively -->
- [None configured yet — add as dependencies are approved]

## Architecture Decisions Log

<!-- Quick reference linking to full ADRs in docs/architecture/ -->
- [No ADRs yet — use /architecture-decision to create one]

## Engine Specialists

<!-- Written by /setup-engine when engine is configured. -->
<!-- Read by /code-review, /architecture-decision, /architecture-review, and team skills -->
<!-- to know which specialist to spawn for engine-specific validation. -->

- **Primary**: godot-specialist
- **Language/Code Specialist**: godot-gdscript-specialist (all .gd files)
- **Shader Specialist**: godot-shader-specialist (.gdshader files, VisualShader resources)
- **UI Specialist**: godot-specialist (no dedicated UI specialist — primary covers all UI)
- **Additional Specialists**: godot-gdextension-specialist (GDExtension / native C++ bindings only)
- **Routing Notes**: Invoke primary for architecture decisions, ADR validation, and cross-cutting code review. Invoke GDScript specialist for code quality, signal architecture, static typing enforcement, and GDScript idioms. Invoke shader specialist for material design and shader code. Invoke GDExtension specialist only when native extensions are involved.

### File Extension Routing

<!-- Skills use this table to select the right specialist per file type. -->

| File Extension / Type | Specialist to Spawn |
|-----------------------|---------------------|
| Game code (.gd files) | godot-gdscript-specialist |
| Shader / material files (.gdshader, VisualShader) | godot-shader-specialist |
| UI / screen files (Control nodes, CanvasLayer) | godot-specialist |
| Scene / prefab / level files (.tscn, .tres) | godot-specialist |
| Native extension / plugin files (.gdextension, C++) | godot-gdextension-specialist |
| General architecture review | godot-specialist |
