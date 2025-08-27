# UI Information Architecture

## Key areas

- Auth and tenant selector
- Dashboard
- Data Management (Teachers, Rooms, Subjects, etc.)
- Constraints & Preferences
- Scheduling Jobs
- Timetable Workspace (grid, drag-drop, lock/pin)
- Reports/Exports
- Settings

## Timetable Workspace 交互要点（草案）

- 视图：周视图/日视图切换，校区/年级/班级/教师过滤
- 网格：虚拟滚动、按需渲染；拖拽分配/换位，实时校验
- 冲突可视：叠加冲突图层（教师/房间/学生组），点击查看解释
- 锁定：支持 pin/lock 固定排程；批量锁定与取消
- 撤销/重做：客户端操作历史 + 服务端校验
- 方案：保存/对比多个方案，展示评分与差异
