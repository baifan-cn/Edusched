// 时间表相关类型定义
import { BaseEntity, PaginationParams, SelectOption } from './index'

// 时间表状态枚举
export enum TimetableStatus {
  DRAFT = 'draft',        // 草稿
  RUNNING = 'running',    // 运行中
  FEASIBLE = 'feasible',  // 可行
  OPTIMIZED = 'optimized', // 已优化
  PUBLISHED = 'published', // 已发布
  FAILED = 'failed'       // 失败
}

// 星期枚举
export enum WeekDay {
  MONDAY = 'monday',
  TUESDAY = 'tuesday',
  WEDNESDAY = 'wednesday',
  THURSDAY = 'thursday',
  FRIDAY = 'friday',
  SATURDAY = 'saturday',
  SUNDAY = 'sunday'
}

// 课时类型枚举
export enum PeriodType {
  REGULAR = 'regular',    // 常规课时
  LAB = 'lab',           // 实验课时
  PHYSICAL = 'physical', // 体育课时
  ART = 'art',          // 艺术课时
  SPECIAL = 'special'    // 特殊课时
}

// 时间表实体
export interface Timetable extends BaseEntity {
  tenant_id: string
  calendar_id: string
  name: string
  description?: string
  status: TimetableStatus
  published_at?: string
  published_by?: string
  metadata: Record<string, any>
  assignments_count: number
  constraints_count: number
}

// 创建时间表请求
export interface CreateTimetableRequest {
  calendar_id: string
  name: string
  description?: string
  metadata?: Record<string, any>
}

// 更新时间表请求
export interface UpdateTimetableRequest extends Partial<CreateTimetableRequest> {
  id: string
}

// 查询时间表参数
export interface TimetableQueryParams extends PaginationParams {
  calendar_id?: string
  status?: TimetableStatus
  name?: string
}

// 时间表分配实体
export interface Assignment extends BaseEntity {
  tenant_id: string
  timetable_id: string
  section_id: string
  timeslot_id: string
  room_id: string
  week_pattern_id?: string
  is_locked: boolean
  notes?: string
}

// 创建分配请求
export interface CreateAssignmentRequest {
  section_id: string
  timeslot_id: string
  room_id: string
  week_pattern_id?: string
  is_locked?: boolean
  notes?: string
}

// 更新分配请求
export interface UpdateAssignmentRequest extends Partial<CreateAssignmentRequest> {
  id: string
}

// 时间段实体
export interface Timeslot extends BaseEntity {
  tenant_id: string
  week_day: WeekDay
  start_time: string
  end_time: string
  period_number: number
  is_break: boolean
  description?: string
}

// 教学段实体
export interface Section extends BaseEntity {
  tenant_id: string
  course_id: string
  class_group_id: string
  teacher_id: string
  room_id?: string
  name: string
  code: string
  hours_per_week: number
  period_type: PeriodType
  is_locked: boolean
  notes?: string
}

// 教室实体
export interface Room extends BaseEntity {
  tenant_id: string
  building_id: string
  name: string
  code: string
  floor: number
  capacity: number
  room_type: string
  features: Record<string, any>
  is_active: boolean
}

// 日历实体
export interface Calendar extends BaseEntity {
  tenant_id: string
  school_id: string
  name: string
  academic_year: string
  semester: string
  start_date: string
  end_date: string
  is_active: boolean
}

// 时间表网格单元格
export interface TimetableGridCell {
  id: string
  timeslot_id: string
  week_day: WeekDay
  start_time: string
  end_time: string
  period_number: number
  assignment?: Assignment
  section?: Section
  room?: Room
  conflicts: string[]
  is_highlighted: boolean
}

// 时间表网格数据
export interface TimetableGridData {
  week_days: WeekDay[]
  timeslots: Timeslot[]
  cells: TimetableGridCell[]
  statistics: {
    total_assignments: number
    completed_assignments: number
    conflict_count: number
    utilization_rate: number
  }
}

// 时间表统计信息
export interface TimetableStats {
  total_sections: number
  assigned_sections: number
  unassigned_sections: number
  total_teachers: number
  total_rooms: number
  average_hours_per_teacher: number
  room_utilization_rate: number
  conflict_count: number
  constraint_violations: number
}

// 发布时间表请求
export interface PublishTimetableRequest {
  id: string
  notify_teachers?: boolean
  message?: string
}

// 时间表导入导出选项
export interface TimetableExportOptions {
  format: 'pdf' | 'excel' | 'csv'
  include_stats: boolean
  include_assignments: boolean
  include_constraints: boolean
  date_range?: {
    start: string
    end: string
  }
}

// 时间表冲突信息
export interface TimetableConflict {
  id: string
  type: 'teacher' | 'room' | 'class' | 'constraint'
  severity: 'error' | 'warning' | 'info'
  message: string
  details: {
    teacher_id?: string
    room_id?: string
    class_id?: string
    timeslot_id?: string
    constraint_id?: string
  }
  suggestions: string[]
}

// 时间表选项
export interface TimetableOption extends SelectOption {
  status: TimetableStatus
  calendar_name: string
  assignment_count: number
}

// 时间表筛选参数
export interface TimetableFilterParams {
  status?: TimetableStatus
  calendar_id?: string
  date_range?: {
    start: string
    end: string
  }
  has_conflicts?: boolean
  is_published?: boolean
}

// 时间表排序选项
export interface TimetableSortOption {
  field: 'name' | 'created_at' | 'updated_at' | 'status' | 'assignments_count'
  order: 'asc' | 'desc'
}

// 时间表批量操作请求
export interface TimetableBulkActionRequest {
  action: 'publish' | 'unpublish' | 'delete' | 'duplicate'
  timetable_ids: string[]
  options?: Record<string, any>
}

// 时间表复制请求
export interface TimetableDuplicateRequest {
  source_timetable_id: string
  new_name: string
  new_description?: string
  copy_assignments: boolean
  copy_constraints: boolean
  target_calendar_id?: string
}