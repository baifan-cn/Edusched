# Component Architecture

## Structure

- `pages/` for route views
- `components/` for reusable UI (grid, dialogs, forms)
- `stores/` Pinia modules per domain
- `services/` API layer (OpenAPI client wrappers)

## Timetable workspace

- Virtualized grid with drag-drop
- Conflict overlays, filters, undo/redo

## UI 库与设计系统（已选：Element Plus）

- 组件选择：表格、表单、对话框、抽屉、树形、级联、日历等
- 主题：基于 Element Plus 主题变量定制品牌色与密度
- 可用性：键盘可达性、ARIA 属性（特别是拖拽与网格）
