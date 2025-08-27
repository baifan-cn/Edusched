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

## Phase 1 脚手架（待实施清单）

- 目录：
  - `frontend/src/pages/`（路由视图）
  - `frontend/src/components/`（UI 组件：表格、表单、对话框、栅格）
  - `frontend/src/stores/`（Pinia 模块：teachers/rooms/sections/timetable）
  - `frontend/src/services/`（OpenAPI Typed 客户端与请求封装）
  - `frontend/src/router/`（Vue Router 4：路由与守卫）
  - `frontend/src/i18n/`（vue-i18n 词条与懒加载）
  - `frontend/src/styles/`（全局样式与 Element Plus 主题变量）

- 工具链：
  - 构建：Vite（Node 版本要求按定版）
  - 代码质量：ESLint（typescript-eslint + vue）+ Prettier
  - 测试：Vitest（组件/单元）+ Playwright（E2E）
  - 包管理：pnpm（workspace 准备）

- 配置：
  - 环境变量：`VITE_API_BASE_URL`、`VITE_OIDC_ISSUER`、`VITE_OIDC_CLIENT_ID`
  - 访问控制：路由守卫基于 OIDC/JWT 与角色
