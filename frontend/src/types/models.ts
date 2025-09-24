// 业务模型类型定义

// 学校模型
export interface School {
  id: string
  name: string
  code: string
  address?: string
  phone?: string
  email?: string
  website?: string
  description?: string
  logo_url?: string
  is_active: boolean
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

// 教师模型
export interface Teacher {
  id: string
  school_id: string
  employee_id: string
  first_name: string
  last_name: string
  email: string
  phone?: string
  department?: string
  title?: string
  specialization?: string[]
  max_hours_per_week?: number
  preferred_time_slots?: string[]
  unavailable_time_slots?: string[]
  is_active: boolean
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

// 课程模型
export interface Course {
  id: string
  school_id: string
  code: string
  name: string
  description?: string
  credits: number
  hours_per_week: number
  total_hours: number
  is_required: boolean
  is_active: boolean
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

// 教学段模型
export interface Section {
  id: string
  school_id: string
  course_id: string
  name: string
  code: string
  class_group_id: string
  teacher_id: string
  room_id?: string
  max_students: number
  current_students: number
  weekly_hours: number
  hours_per_week: number
  semester: string
  academic_year: string
  is_active: boolean
  is_locked: boolean
  period_type: 'regular' | 'lab' | 'physical' | 'art' | 'special'
  notes?: string
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

// 教学段请求类型
export interface CreateSectionRequest {
  course_id: string
  class_group_id: string
  teacher_id: string
  room_id?: string
  name: string
  code: string
  hours_per_week: number
  period_type: 'regular' | 'lab' | 'physical' | 'art' | 'special'
  is_locked?: boolean
  notes?: string
}

export interface UpdateSectionRequest extends Partial<CreateSectionRequest> {
  id: string
}

export interface SectionQueryParams {
  course_id?: string
  teacher_id?: string
  class_group_id?: string
  room_id?: string
  name?: string
  code?: string
  is_active?: boolean
  is_locked?: boolean
  period_type?: string
  page?: number
  size?: number
  sort?: string
  order?: 'asc' | 'desc'
}

// 班级模型
export interface ClassGroup {
  id: string
  school_id: string
  name: string
  grade: number
  department?: string
  student_count: number
  homeroom_teacher_id?: string
  is_active: boolean
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

// 教室模型
export interface Room {
  id: string
  school_id: string
  name: string
  code: string
  type: 'classroom' | 'lab' | 'lecture_hall' | 'office' | 'other'
  capacity: number
  building?: string
  floor?: string
  equipment?: string[]
  is_active: boolean
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

// 时间表模型
export interface Timetable {
  id: string
  school_id: string
  name: string
  semester: string
  academic_year: string
  description?: string
  status: 'draft' | 'published' | 'archived'
  is_active: boolean
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

// 时间表条目模型
export interface TimetableEntry {
  id: string
  timetable_id: string
  section_id: string
  teacher_id: string
  room_id: string
  day_of_week: number
  start_time: string
  end_time: string
  is_locked: boolean
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

// 任务分配模型
export interface Assignment {
  id: string
  school_id: string
  timetable_id: string
  section_id: string
  timeslot_id: string
  room_id: string
  week_pattern_id?: string
  is_locked: boolean
  notes?: string
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

// 任务分配请求类型
export interface CreateAssignmentRequest {
  section_id: string
  timeslot_id: string
  room_id: string
  week_pattern_id?: string
  is_locked?: boolean
  notes?: string
}

export interface UpdateAssignmentRequest extends Partial<CreateAssignmentRequest> {
  id: string
}

export interface AssignmentQueryParams {
  timetable_id?: string
  section_id?: string
  teacher_id?: string
  room_id?: string
  timeslot_id?: string
  week_pattern_id?: string
  is_locked?: boolean
  search?: string
  page?: number
  size?: number
  sort?: string
  order?: 'asc' | 'desc'
}

// 调度任务模型
export interface SchedulingTask {
  id: string
  school_id: string
  name: string
  description?: string
  timetable_id: string
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed' | 'cancelled'
  progress: number
  start_time?: string
  end_time?: string
  error_message?: string
  config: SchedulingConfig
  result?: SchedulingResult
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

// 调度配置模型
export interface SchedulingConfig {
  max_duration_seconds: number
  solver_parameters: Record<string, any>
  constraints: ConstraintConfig
  objectives: ObjectiveConfig
}

// 约束配置模型
export interface ConstraintConfig {
  // 硬约束
  hard_constraints: {
    teacher_conflicts: boolean
    room_conflicts: boolean
    class_conflicts: boolean
    room_capacity: boolean
    teacher_availability: boolean
    room_availability: boolean
    consecutive_classes: boolean
    travel_time: boolean
  }
  // 软约束
  soft_constraints: {
    teacher_preferences: boolean
    room_preferences: boolean
    balanced_distribution: boolean
    compact_schedule: boolean
    preferred_times: boolean
  }
  // 约束权重
  weights: {
    teacher_preferences: number
    room_preferences: number
    balanced_distribution: number
    compact_schedule: number
    preferred_times: number
  }
}

// 目标配置模型
export interface ObjectiveConfig {
  primary_objective: 'feasibility' | 'teacher_satisfaction' | 'resource_utilization' | 'balanced_schedule'
  secondary_objectives: string[]
  optimization_direction: 'minimize' | 'maximize'
}

// 调度结果模型
export interface SchedulingResult {
  is_feasible: boolean
  total_penalty: number
  constraint_violations: ConstraintViolation[]
  solution_quality: number
  computation_time_seconds: number
  statistics: {
    total_sections: number
    scheduled_sections: number
    unscheduled_sections: number
    teacher_utilization: number
    room_utilization: number
  }
}

// 约束违反模型
export interface ConstraintViolation {
  constraint_type: string
  constraint_name: string
  severity: 'hard' | 'soft'
  penalty: number
  details: any
  affected_resources: string[]
}

// 调度日志模型
export interface SchedulingLog {
  id: string
  task_id: string
  level: 'info' | 'warning' | 'error' | 'debug'
  message: string
  timestamp: string
  details?: any
}

// 校区模型
export interface Campus {
  id: string
  school_id: string
  name: string
  code: string
  address?: string
  latitude?: number
  longitude?: number
  is_active: boolean
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

// 学期模型
export interface Semester {
  id: string
  school_id: string
  name: string
  academic_year: string
  start_date: string
  end_date: string
  is_active: boolean
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

// 学部模型
export interface Department {
  id: string
  school_id: string
  name: string
  code: string
  head_teacher_id?: string
  description?: string
  is_active: boolean
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}