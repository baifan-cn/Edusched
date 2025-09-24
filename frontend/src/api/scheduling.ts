import { apiRequest, PaginationParams, PaginatedResponse } from './index'

// 调度任务状态枚举
export enum SchedulingJobStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

// 调度任务优先级枚举
export enum SchedulingJobPriority {
  LOW = 'low',
  NORMAL = 'normal',
  HIGH = 'high',
  URGENT = 'urgent'
}

// 约束类型枚举
export enum ConstraintType {
  HARD = 'hard',
  SOFT = 'soft'
}

// 约束类别枚举
export enum ConstraintCategory {
  TEACHER = 'teacher',
  ROOM = 'room',
  CLASS = 'class',
  TIME = 'time',
  COURSE = 'course',
  CUSTOM = 'custom'
}

// 调度任务信息接口
export interface SchedulingJob {
  id: string
  name: string
  description?: string
  status: SchedulingJobStatus
  priority: SchedulingJobPriority
  progress: number
  total_steps: number
  current_step: number
  created_at: string
  started_at?: string
  completed_at?: string
  cancelled_at?: string
  error_message?: string
  result?: SchedulingResult
  config: SchedulingConfig
  created_by: string
  tenant_id: string
}

// 调度配置接口
export interface SchedulingConfig {
  school_id: string
  academic_year: string
  semester: string
  week_days: number[]
  time_slots: TimeSlot[]
  constraints: Constraint[]
  algorithm_params: AlgorithmParams
  optimization_targets: OptimizationTarget[]
}

// 时间槽接口
export interface TimeSlot {
  id: string
  name: string
  start_time: string
  end_time: string
  is_break: boolean
  weight: number
}

// 约束接口
export interface Constraint {
  id: string
  name: string
  type: ConstraintType
  category: ConstraintCategory
  description: string
  weight: number
  enabled: boolean
  params: Record<string, any>
}

// 算法参数接口
export interface AlgorithmParams {
  max_iterations: number
  time_limit_seconds: number
  search_strategy: 'depth_first' | 'breadth_first' | 'best_first'
  enable_parallel: boolean
  parallel_workers: number
  random_seed?: number
  enable_logging: boolean
  log_level: 'debug' | 'info' | 'warn' | 'error'
}

// 优化目标接口
export interface OptimizationTarget {
  metric: string
  weight: number
  direction: 'minimize' | 'maximize'
  target_value?: number
}

// 调度结果接口
export interface SchedulingResult {
  success: boolean
  total_assignments: number
  conflict_count: number
  unassigned_count: number
  score: number
  execution_time_ms: number
  iterations: number
  statistics: {
    teacher_utilization: number
    room_utilization: number
    class_coverage: number
    constraint_satisfaction: number
  }
  assignments: Assignment[]
  conflicts: Conflict[]
  warnings: Warning[]
  logs: LogEntry[]
}

// 分配结果接口
export interface Assignment {
  id: string
  course_id: string
  teacher_id: string
  class_id: string
  room_id: string
  time_slot_id: string
  day_of_week: number
  week_number?: number
  score: number
  conflicts: string[]
}

// 冲突接口
export interface Conflict {
  id: string
  type: string
  severity: 'error' | 'warning' | 'info'
  message: string
  details: Record<string, any>
  affected_resources: string[]
}

// 警告接口
export interface Warning {
  id: string
  type: string
  message: string
  details: Record<string, any>
  suggestions: string[]
}

// 日志条目接口
export interface LogEntry {
  timestamp: string
  level: 'debug' | 'info' | 'warn' | 'error'
  message: string
  details?: Record<string, any>
}

// 进度更新接口
export interface ProgressUpdate {
  job_id: string
  progress: number
  current_step: number
  total_steps: number
  step_name: string
  message?: string
  timestamp: string
}

// 验证请求接口
export interface ValidateRequest {
  config: SchedulingConfig
  check_data_integrity: boolean
  check_constraints: boolean
  check_resource_availability: boolean
}

// 验证响应接口
export interface ValidateResponse {
  valid: boolean
  errors: ValidationError[]
  warnings: ValidationWarning[]
  suggestions: string[]
  summary: {
    total_teachers: number
    total_courses: number
    total_classes: number
    total_rooms: number
    total_time_slots: number
    total_constraints: number
  }
}

// 验证错误接口
export interface ValidationError {
  field: string
  message: string
  code: string
  details?: Record<string, any>
}

// 验证警告接口
export interface ValidationWarning {
  field: string
  message: string
  code: string
  details?: Record<string, any>
  suggestions?: string[]
}

// 查询参数接口
export interface SchedulingJobQueryParams extends PaginationParams {
  status?: SchedulingJobStatus
  priority?: SchedulingJobPriority
  school_id?: string
  created_by?: string
  date_from?: string
  date_to?: string
  search?: string
}

// 创建调度任务请求接口
export interface CreateSchedulingJobRequest {
  name: string
  description?: string
  priority: SchedulingJobPriority
  config: SchedulingConfig
}

// 更新调度任务请求接口
export interface UpdateSchedulingJobRequest {
  name?: string
  description?: string
  priority?: SchedulingJobPriority
  config?: SchedulingConfig
}

// 调度API服务
export const schedulingApi = {
  // 启动调度任务
  startJob: async (data: CreateSchedulingJobRequest): Promise<SchedulingJob> => {
    return apiRequest.post('/scheduling/start', data)
  },

  // 获取调度任务列表
  getJobs: async (params?: SchedulingJobQueryParams): Promise<PaginatedResponse<SchedulingJob>> => {
    return apiRequest.get('/scheduling/jobs', { params })
  },

  // 获取单个任务详情
  getJob: async (jobId: string): Promise<SchedulingJob> => {
    return apiRequest.get(`/scheduling/jobs/${jobId}`)
  },

  // 取消任务
  cancelJob: async (jobId: string, reason?: string): Promise<void> => {
    return apiRequest.post(`/scheduling/jobs/${jobId}/cancel`, { reason })
  },

  // 获取任务进度
  getJobProgress: async (jobId: string): Promise<ProgressUpdate> => {
    return apiRequest.get(`/scheduling/jobs/${jobId}/progress`)
  },

  // 获取任务结果
  getJobResult: async (jobId: string): Promise<SchedulingResult> => {
    return apiRequest.get(`/scheduling/jobs/${jobId}/result`)
  },

  // 验证调度配置
  validateConfig: async (data: ValidateRequest): Promise<ValidateResponse> => {
    return apiRequest.post('/scheduling/validate', data)
  },

  // 获取任务日志
  getJobLogs: async (jobId: string, params?: {
    level?: 'debug' | 'info' | 'warn' | 'error'
    limit?: number
    offset?: number
  }): Promise<LogEntry[]> => {
    return apiRequest.get(`/scheduling/jobs/${jobId}/logs`, { params })
  },

  // 重启任务
  restartJob: async (jobId: string): Promise<SchedulingJob> => {
    return apiRequest.post(`/scheduling/jobs/${jobId}/restart`)
  },

  // 删除任务
  deleteJob: async (jobId: string): Promise<void> => {
    return apiRequest.delete(`/scheduling/jobs/${jobId}`)
  },

  // 批量删除任务
  bulkDeleteJobs: async (jobIds: string[]): Promise<void> => {
    return apiRequest.post('/scheduling/jobs/bulk-delete', { job_ids: jobIds })
  },

  // 获取调度统计信息
  getSchedulingStats: async (params?: {
    school_id?: string
    date_from?: string
    date_to?: string
  }): Promise<{
    total_jobs: number
    completed_jobs: number
    failed_jobs: number
    running_jobs: number
    average_execution_time: number
    success_rate: number
    daily_stats: Array<{
      date: string
      jobs_count: number
      success_count: number
      average_score: number
    }>
  }> => {
    return apiRequest.get('/scheduling/stats', { params })
  },

  // 获取约束模板
  getConstraintTemplates: async (): Promise<Constraint[]> => {
    return apiRequest.get('/scheduling/constraints/templates')
  },

  // 创建自定义约束
  createConstraint: async (data: Omit<Constraint, 'id'>): Promise<Constraint> => {
    return apiRequest.post('/scheduling/constraints', data)
  },

  // 更新约束
  updateConstraint: async (id: string, data: Partial<Constraint>): Promise<Constraint> => {
    return apiRequest.put(`/scheduling/constraints/${id}`, data)
  },

  // 删除约束
  deleteConstraint: async (id: string): Promise<void> => {
    return apiRequest.delete(`/scheduling/constraints/${id}`)
  },

  // 获取算法预设配置
  getAlgorithmPresets: async (): Promise<Array<{
    id: string
    name: string
    description: string
    params: AlgorithmParams
  }>> => {
    return apiRequest.get('/scheduling/algorithm-presets')
  },

  // 导出调度结果
  exportResult: async (jobId: string, format: 'json' | 'csv' | 'excel' | 'pdf'): Promise<Blob> => {
    return apiRequest.get(`/scheduling/jobs/${jobId}/export`, {
      params: { format },
      responseType: 'blob'
    })
  },

  // 导入调度配置
  importConfig: async (file: File): Promise<SchedulingConfig> => {
    const formData = new FormData()
    formData.append('file', file)

    return apiRequest.post('/scheduling/import-config', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}