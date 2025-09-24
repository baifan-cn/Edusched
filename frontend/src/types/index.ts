// 通用类型定义
export interface BaseEntity {
  id: string
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  total_pages: number
}

export interface PaginationParams {
  page?: number
  size?: number
  sort?: string
  order?: 'asc' | 'desc'
}

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  timestamp: number
}

export interface ApiError {
  code: number
  message: string
  details?: any
}

// 分页查询结果
export interface QueryResult<T> {
  items: T[]
  total: number
  page: number
  size: number
  total_pages: number
}

// 表单验证错误
export interface FormValidationError {
  field: string
  message: string
}

// 文件上传响应
export interface FileUploadResponse {
  url: string
  filename: string
  size: number
  mime_type: string
}

// 选择器选项
export interface SelectOption {
  label: string
  value: string | number
  disabled?: boolean
}

// 时间段
export interface TimeSlot extends BaseEntity {
  name: string
  start_time: string
  end_time: string
  day_of_week: number
  is_active: boolean
}

export interface CreateTimeSlotRequest {
  name: string
  start_time: string
  end_time: string
  day_of_week: number
  is_active?: boolean
}

export interface UpdateTimeSlotRequest extends Partial<CreateTimeSlotRequest> {
  id: string
}

export interface TimeSlotQueryParams extends PaginationParams {
  day_of_week?: number
  is_active?: boolean
  search?: string
}

// 用户相关类型
export interface User {
  id: string
  username: string
  email: string
  first_name: string
  last_name: string
  role: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  username: string
  password: string
  captcha?: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

// 系统配置类型
export interface SystemConfig {
  app_name: string
  app_version: string
  api_version: string
  maintenance_mode: boolean
  max_file_size: number
  allowed_file_types: string[]
}

// 统计数据类型
export interface DashboardStats {
  total_schools: number
  total_teachers: number
  total_students: number
  total_courses: number
  total_classes: number
  total_rooms: number
  recent_activities: Array<{
    id: string
    type: string
    message: string
    timestamp: string
  }>
}

// 通知消息类型
export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  timestamp: string
  is_read: boolean
  metadata?: any
}

// 操作日志类型
export interface OperationLog {
  id: string
  user_id: string
  username: string
  operation: string
  resource_type: string
  resource_id: string
  details: any
  ip_address: string
  user_agent: string
  timestamp: string
}

// 导出/导入任务类型
export interface ExportTask {
  id: string
  task_type: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  file_url?: string
  error_message?: string
  created_at: string
  completed_at?: string
}

export interface ImportTask {
  id: string
  task_type: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  success_count: number
  error_count: number
  error_details?: Array<{
    row: number
    message: string
  }>
  created_at: string
  completed_at?: string
}

// 课程相关类型
export interface Course extends BaseEntity {
  tenant_id: string
  subject_id: string
  name: string
  code: string
  description?: string
  credits: number
  hours_per_week: number
  total_hours: number
  is_active: boolean
}

export interface CreateCourseRequest {
  subject_id: string
  name: string
  code: string
  description?: string
  credits: number
  hours_per_week: number
  total_hours: number
}

export interface UpdateCourseRequest extends Partial<CreateCourseRequest> {
  id: string
}

export interface CourseQueryParams extends PaginationParams {
  name?: string
  code?: string
  subject_id?: string
  is_active?: boolean
}

// 学科相关类型
export interface Subject extends BaseEntity {
  name: string
  code: string
  description?: string
  is_active: boolean
}

// 学校相关类型
export interface School extends BaseEntity {
  name: string
  code: string
  address?: string
  phone?: string
  email?: string
  website?: string
  description?: string
  logo_url?: string
  is_active: boolean
}

export interface CreateSchoolRequest {
  name: string
  code: string
  address?: string
  phone?: string
  email?: string
  website?: string
  description?: string
  logo_url?: string
}

export interface UpdateSchoolRequest extends Partial<CreateSchoolRequest> {
  id: string
}

export interface SchoolQueryParams extends PaginationParams {
  name?: string
  code?: string
  is_active?: boolean
}

// 教师相关类型
export interface Teacher extends BaseEntity {
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
  assigned_hours?: number // 工作负载统计字段
}

export interface CreateTeacherRequest {
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
}

export interface UpdateTeacherRequest extends Partial<CreateTeacherRequest> {
  id: string
}

export interface TeacherQueryParams extends PaginationParams {
  school_id?: string
  name?: string
  department?: string
  title?: string
  is_active?: boolean
  search?: string
}

// 教师工作负载统计
export interface TeacherWorkload {
  id: string
  name: string
  assigned_hours: number
  max_hours: number
  utilization_rate: number
  course_count: number
  class_count: number
}

// 校区相关类型
export interface Campus extends BaseEntity {
  school_id: string
  name: string
  code: string
  address?: string
  phone?: string
  is_active: boolean
}

export interface CreateCampusRequest {
  school_id: string
  name: string
  code: string
  address?: string
  phone?: string
}

export interface UpdateCampusRequest extends Partial<CreateCampusRequest> {
  id: string
}

// 教室相关类型
export interface Room extends BaseEntity {
  school_id: string
  campus_id: string
  name: string
  code: string
  room_type: string
  capacity: number
  facilities?: string[]
  description?: string
  is_active: boolean
}

export interface CreateRoomRequest {
  school_id: string
  campus_id: string
  name: string
  code: string
  room_type: string
  capacity: number
  facilities?: string[]
  description?: string
}

export interface UpdateRoomRequest extends Partial<CreateRoomRequest> {
  id: string
}

export interface RoomQueryParams extends PaginationParams {
  school_id?: string
  campus_id?: string
  room_type?: string
  is_active?: boolean
  search?: string
}


// 日历相关类型
export interface Calendar extends BaseEntity {
  name: string
  description?: string
  academic_year: string
  semester: string
  start_date: string
  end_date: string
  is_active: boolean
  events?: CalendarEvent[]
}

export interface CreateCalendarRequest {
  name: string
  description?: string
  academic_year: string
  semester: string
  start_date: string
  end_date: string
}

export interface UpdateCalendarRequest extends Partial<CreateCalendarRequest> {
  id: string
}

export interface CalendarEvent {
  id: string
  calendar_id: string
  title: string
  description?: string
  start_time: string
  end_time: string
  event_type: string
  is_all_day: boolean
  recurrence?: string
  metadata?: any
}

// 约束相关类型
export interface Constraint extends BaseEntity {
  name: string
  description?: string
  constraint_type: string
  weight: number
  parameters: any
  is_active: boolean
  is_hard: boolean
}

export interface CreateConstraintRequest {
  name: string
  description?: string
  constraint_type: string
  weight: number
  parameters: any
  is_hard?: boolean
}

export interface UpdateConstraintRequest extends Partial<CreateConstraintRequest> {
  id: string
}

export interface ConstraintQueryParams extends PaginationParams {
  constraint_type?: string
  is_hard?: boolean
  is_active?: boolean
  search?: string
}

// 约束验证结果
export interface ConstraintValidationResult {
  is_valid: boolean
  violations: Array<{
    constraint_id: string
    constraint_name: string
    message: string
    severity: 'error' | 'warning'
  }>
  score: number
}

// 时间表相关类型
export * from './timetables'