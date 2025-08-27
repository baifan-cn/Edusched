# Data Model

## Core entities

- School, Campus, Term, WeekPattern, Calendar
- Grade, ClassGroup, StudentGroup
- Subject, CourseOffering, Section
- Teacher, TeacherAvailability, TeacherContract
- Room, RoomFeature
- Timeslot, PeriodTemplate
  - Timeslot 支持 `week_parity`（odd/even/both）与节次索引；跨节次由 `Assignment.block_length` 表达
  - PeriodTemplate 定义每天的节次边界；用于生成 Timeslot
- Constraint, WeightProfile
- Timetable, Assignment, Lock/Pin, SwapSuggestion

## Relationships

- One School → many Campuses → Rooms
- Term → Calendar → WeekPattern
- CourseOffering → multiple Sections
- Section ↔ Teacher(s) ↔ Room(s)
- StudentGroup ↔ Sections (avoid clashes)
 - Campus 行程：`Campus × Campus → minutes` 距离矩阵，用于教师跨校区硬约束（含缓冲）

## Storage strategy

- Postgres normalized core; JSONB extensions for flexible constraints
- Index lookup‑heavy columns; optimistic locking on timetables
- Event audit tables for changes
 - RLS（可选）：强制 `tenant_id`；`campus_id` 作为细粒度筛选（读/写策略示例见 `backend/database-schema.md` 与 `backend/auth-and-rbac.md`）
