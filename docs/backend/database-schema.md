# Database Schema

## Overview

- Postgres 16+ as primary store
- Normalized core with JSONB extensions for constraints/preferences
- Event/audit tables for changes

## ERD (to be drafted)

- Entities: School, Campus, Term, WeekPattern, Calendar, Grade, ClassGroup, StudentGroup, Subject, CourseOffering, Section, Teacher, TeacherAvailability, TeacherContract, Room, RoomFeature, Timeslot, PeriodTemplate, Constraint, WeightProfile, Timetable, Assignment, Lock, SwapSuggestion

## Migration policy

- Alembic versioned migrations
- Backwards-compatible changes first; destructive changes gated

## Tables and key fields (draft)

> 提示：以下为草案，字段名与约束会随 ERD 推进而细化。

### Common

- 通用字段：`id (uuid)`, `tenant_id (uuid)`, `created_at`, `updated_at`, `created_by`, `updated_by`
- 约束：
  - 主键：`PRIMARY KEY (id)`
  - 多租户隔离：`tenant_id` 非空，建议联合索引 `(tenant_id, id)`
  - 审计：`created_by`, `updated_by` 记录主体（用户或系统）
  - 软删除（可选）：`deleted_at` + 视图隔离

### Organization

- `school`：`name`, `code`, `settings (jsonb)`
  - 约束：`UNIQUE (tenant_id, code)`；`CHECK (code ~ '^[A-Z0-9_-]+$')`
  - 索引：`(tenant_id, name)`
- `campus`：`school_id`, `name`, `code`, `address`, `metadata (jsonb)`
  - 外键：`FOREIGN KEY (school_id) REFERENCES school(id)`
  - 约束：`UNIQUE (tenant_id, school_id, code)`

### Terms and calendar

- `term`：`school_id`, `name`, `start_date`, `end_date`, `week_count`, `settings (jsonb)`
  - 外键：`FOREIGN KEY (school_id) REFERENCES school(id)`
  - 约束：`CHECK (end_date >= start_date)`；`UNIQUE (tenant_id, school_id, name)`
- `calendar_day`：`term_id`, `date`, `day_type (enum: teaching/holiday/event)`, `notes`
  - 外键：`FOREIGN KEY (term_id) REFERENCES term(id)`
  - 约束：`UNIQUE (tenant_id, term_id, date)`
- `week_pattern`：`term_id`, `week_index`, `pattern (jsonb)`
  - 约束：`UNIQUE (tenant_id, term_id, week_index)`；`CHECK (week_index >= 1)`
- `period_template`：`school_id`, `day_of_week`, `period_index`, `start_time`, `end_time`, `label`
  - 约束：`CHECK (day_of_week BETWEEN 1 AND 7)`；`CHECK (start_time < end_time)`；`UNIQUE (tenant_id, school_id, day_of_week, period_index)`
  - 说明：用于描述每天节次时间；支持块排通过 `label`/`metadata` 补充

### People and resources

- `teacher`：`school_id`, `name`, `code`, `email`, `campus_id (nullable)`, `metadata (jsonb)`
  - 外键：`FOREIGN KEY (school_id) REFERENCES school(id)`；`FOREIGN KEY (campus_id) REFERENCES campus(id)`
  - 约束：`UNIQUE (tenant_id, school_id, code)`；`CHECK (email ~* '^[^@]+@[^@]+\.[^@]+$')`
- `teacher_availability`：`teacher_id`, `rule (jsonb)`
  - 外键：`FOREIGN KEY (teacher_id) REFERENCES teacher(id) ON DELETE CASCADE`
  - 说明：规则示例如黑名单/白名单时段，周单双周，节次集合
- `teacher_contract`：`teacher_id`, `max_hours_per_week`, `max_consecutive`, `preferences (jsonb)`
  - 外键：`FOREIGN KEY (teacher_id) REFERENCES teacher(id) ON DELETE CASCADE`
  - 约束：`CHECK (max_hours_per_week BETWEEN 0 AND 80)`；`CHECK (max_consecutive BETWEEN 1 AND 10)`
- `room`：`campus_id`, `name`, `code`, `capacity`, `metadata (jsonb)`
  - 外键：`FOREIGN KEY (campus_id) REFERENCES campus(id)`
  - 约束：`UNIQUE (tenant_id, campus_id, code)`；`CHECK (capacity >= 0)`
- `room_feature`：`room_id`, `feature_key`, `feature_value`
  - 外键：`FOREIGN KEY (room_id) REFERENCES room(id) ON DELETE CASCADE`
  - 约束：`UNIQUE (tenant_id, room_id, feature_key)`

### Courses and groups

- `grade`：`school_id`, `name`, `order`
  - 外键：`FOREIGN KEY (school_id) REFERENCES school(id)`
  - 约束：`UNIQUE (tenant_id, school_id, name)`；`CHECK (order BETWEEN 1 AND 20)`
- `class_group`：`grade_id`, `name`, `code`, `size`
  - 外键：`FOREIGN KEY (grade_id) REFERENCES grade(id)`
  - 约束：`UNIQUE (tenant_id, grade_id, code)`；`CHECK (size >= 0)`
- `student_group`：`school_id`, `name`, `code`, `size`, `membership (jsonb)`
  - 约束：`UNIQUE (tenant_id, school_id, code)`；`CHECK (size >= 0)`
- `subject`：`school_id`, `name`, `code`
  - 约束：`UNIQUE (tenant_id, school_id, code)`
- `course_offering`：`term_id`, `subject_id`, `grade_id (nullable)`, `hours_per_week`, `metadata (jsonb)`
  - 外键：`FOREIGN KEY (term_id) REFERENCES term(id)`；`FOREIGN KEY (subject_id) REFERENCES subject(id)`
  - 约束：`CHECK (hours_per_week BETWEEN 0 AND 60)`
- `section`：`offering_id`, `name`, `index`, `target_groups (jsonb)`
  - 外键：`FOREIGN KEY (offering_id) REFERENCES course_offering(id)`
  - 约束：`UNIQUE (tenant_id, offering_id, index)`
- `section_teacher`：`section_id`, `teacher_id`, `role`, `hours_share`
  - 外键：`FOREIGN KEY (section_id) REFERENCES section(id) ON DELETE CASCADE`；`FOREIGN KEY (teacher_id) REFERENCES teacher(id)`
  - 约束：`CHECK (hours_share BETWEEN 0 AND 1)`

### Timeslots

- `timeslot`：`term_id`, `day_of_week`, `period_index`, `week_parity (enum: odd/even/both)`
  - 外键：`FOREIGN KEY (term_id) REFERENCES term(id)`
  - 约束：`CHECK (day_of_week BETWEEN 1 AND 7)`；`CHECK (period_index >= 1)`；`UNIQUE (tenant_id, term_id, day_of_week, period_index, week_parity)`
  - 说明：支持单双周通过 `week_parity`；跨节次课程由 `assignment.block_length`（见下）支持

### Constraints and weights

- `constraint_def`：`school_id`, `key`, `type (hard/soft)`, `schema (jsonb)`
  - 约束：`UNIQUE (tenant_id, school_id, key)`；`CHECK (type IN ('hard','soft'))`
- `weight_profile`：`school_id`, `name`, `weights (jsonb)`
  - 约束：`UNIQUE (tenant_id, school_id, name)`

### Timetables and results

- `timetable`：`term_id`, `name`, `status (draft/published)`, `lock_version`, `score (nullable)`
  - 外键：`FOREIGN KEY (term_id) REFERENCES term(id)`
  - 约束：`UNIQUE (tenant_id, term_id, name)`；`CHECK (lock_version >= 0)`
- `assignment`：`timetable_id`, `section_id`, `timeslot_id`, `room_id`, `teacher_id`, `status (fixed/pinned/auto)`, `block_length INT DEFAULT 1`, `lock_version INT DEFAULT 0`
  - 外键：`FOREIGN KEY (timetable_id) REFERENCES timetable(id) ON DELETE CASCADE`
  - 约束：`CHECK (block_length >= 1)`；唯一性：`UNIQUE (tenant_id, timetable_id, section_id)`；`CHECK (lock_version >= 0)`
  - 说明：通过 `block_length` 支持跨节次；同一 `section` 在同一 `timetable` 仅有一个主安排
- `lock_pin`：`timetable_id`, `assignment_id`, `reason`, `created_by`
  - 约束：`UNIQUE (tenant_id, assignment_id)`
- `swap_suggestion`：`timetable_id`, `payload (jsonb)`, `expected_delta_score`
  - 索引：`(timetable_id)`

### Jobs and audit

- `job`：`tenant_id`, `timetable_id`, `status`, `progress`, `started_at`, `finished_at`, `checkpoint (jsonb)`, `idempotency_key`
  - 约束：`UNIQUE (tenant_id, idempotency_key)`（非空时）
  - 索引：`(tenant_id, timetable_id)`, `(tenant_id, status)`
- `audit_event`：`tenant_id`, `actor`, `action`, `entity`, `entity_id`, `diff (jsonb)`, `created_at`
  - 索引：`(tenant_id, created_at DESC)`；`(tenant_id, entity, entity_id)`

## Indexing and performance

- 高频检索：`teacher.code`, `room.code`, `subject.code`, `section.offering_id`
- 时间过滤：`calendar_day.date`, `timeslot (term_id, day_of_week, period_index)`
- 多租户隔离：`(tenant_id, id)` 复合索引；可选 RLS 策略
- 行程矩阵：若建模 `campus_travel_time(src_campus_id, dst_campus_id, minutes)`，需 `UNIQUE (tenant_id, src_campus_id, dst_campus_id)`，并在算法读取端强制作为硬约束（教师跨校区课程需满足缓冲时间）。

## JSONB 扩展字段规范（草案）

- 所有 `jsonb` 字段需在应用层进行 JSON Schema 校验；可选启用 `pg_jsonschema` 提高数据面约束。
- 结构稳定字段（如 `constraint_def.schema`, `weight_profile.weights`）提供版本号 `schema_version` 以支持演进。
- 禁止存储可索引的核心字段于 jsonb（避免查询退化）；需查询的键应提升为列并建立索引。
