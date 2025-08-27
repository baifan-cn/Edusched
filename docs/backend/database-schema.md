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

### Organization

- `school`：`name`, `code`, `settings (jsonb)`
- `campus`：`school_id`, `name`, `code`, `address`, `metadata (jsonb)`

### Terms and calendar

- `term`：`school_id`, `name`, `start_date`, `end_date`, `week_count`, `settings (jsonb)`
- `calendar_day`：`term_id`, `date`, `day_type (enum: teaching/holiday/event)`, `notes`
- `week_pattern`：`term_id`, `week_index`, `pattern (jsonb)`
- `period_template`：`school_id`, `day_of_week`, `period_index`, `start_time`, `end_time`, `label`

### People and resources

- `teacher`：`school_id`, `name`, `code`, `email`, `campus_id (nullable)`, `metadata (jsonb)`
- `teacher_availability`：`teacher_id`, `rule (jsonb)`
- `teacher_contract`：`teacher_id`, `max_hours_per_week`, `max_consecutive`, `preferences (jsonb)`
- `room`：`campus_id`, `name`, `code`, `capacity`, `metadata (jsonb)`
- `room_feature`：`room_id`, `feature_key`, `feature_value`

### Courses and groups

- `grade`：`school_id`, `name`, `order`
- `class_group`：`grade_id`, `name`, `code`, `size`
- `student_group`：`school_id`, `name`, `code`, `size`, `membership (jsonb)`
- `subject`：`school_id`, `name`, `code`
- `course_offering`：`term_id`, `subject_id`, `grade_id (nullable)`, `hours_per_week`, `metadata (jsonb)`
- `section`：`offering_id`, `name`, `index`, `target_groups (jsonb)`
- `section_teacher`：`section_id`, `teacher_id`, `role`, `hours_share`

### Timeslots

- `timeslot`：`term_id`, `day_of_week`, `period_index`, `week_parity (enum: odd/even/both)`

### Constraints and weights

- `constraint_def`：`school_id`, `key`, `type (hard/soft)`, `schema (jsonb)`
- `weight_profile`：`school_id`, `name`, `weights (jsonb)`

### Timetables and results

- `timetable`：`term_id`, `name`, `status (draft/published)`, `lock_version`, `score (nullable)`
- `assignment`：`timetable_id`, `section_id`, `timeslot_id`, `room_id`, `teacher_id`, `status (fixed/pinned/auto)`
- `lock_pin`：`timetable_id`, `assignment_id`, `reason`, `created_by`
- `swap_suggestion`：`timetable_id`, `payload (jsonb)`, `expected_delta_score`

### Jobs and audit

- `job`：`tenant_id`, `timetable_id`, `status`, `progress`, `started_at`, `finished_at`, `checkpoint (jsonb)`, `idempotency_key`
- `audit_event`：`tenant_id`, `actor`, `action`, `entity`, `entity_id`, `diff (jsonb)`, `created_at`

## Indexing and performance

- 高频检索：`teacher.code`, `room.code`, `subject.code`, `section.offering_id`
- 时间过滤：`calendar_day.date`, `timeslot (term_id, day_of_week, period_index)`
- 多租户隔离：`(tenant_id, id)` 复合索引；可选 RLS 策略
