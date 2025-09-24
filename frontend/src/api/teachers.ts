import { apiRequest, PaginationParams, PaginatedResponse } from './index'

// 教师相关类型定义
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

// 创建教师请求
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

// 更新教师请求
export interface UpdateTeacherRequest extends Partial<CreateTeacherRequest> {
  id: string
}

// 查询教师参数
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

// 教师API服务
export const teachersApi = {
  // 获取教师列表
  getTeachers: async (params?: TeacherQueryParams): Promise<PaginatedResponse<Teacher>> => {
    return apiRequest.get('/teachers', { params })
  },

  // 获取单个教师详情
  getTeacher: async (id: string): Promise<Teacher> => {
    return apiRequest.get(`/teachers/${id}`)
  },

  // 创建教师
  createTeacher: async (data: CreateTeacherRequest): Promise<Teacher> => {
    return apiRequest.post('/teachers', data)
  },

  // 更新教师
  updateTeacher: async (id: string, data: UpdateTeacherRequest): Promise<Teacher> => {
    return apiRequest.put(`/teachers/${id}`, data)
  },

  // 删除教师
  deleteTeacher: async (id: string): Promise<void> => {
    return apiRequest.delete(`/teachers/${id}`)
  },

  // 批量删除教师
  bulkDeleteTeachers: async (ids: string[]): Promise<void> => {
    return apiRequest.post('/teachers/bulk-delete', { ids })
  },

  // 激活/停用教师
  toggleTeacherStatus: async (id: string, is_active: boolean): Promise<Teacher> => {
    return apiRequest.patch(`/teachers/${id}/status`, { is_active })
  },

  // 更新教师偏好设置
  updateTeacherPreferences: async (
    id: string,
    preferences: {
      preferred_time_slots?: string[]
      unavailable_time_slots?: string[]
      max_hours_per_week?: number
    }
  ): Promise<Teacher> => {
    return apiRequest.patch(`/teachers/${id}/preferences`, preferences)
  },

  // 获取教师工作负载统计
  getTeacherWorkload: async (school_id: string): Promise<TeacherWorkload[]> => {
    return apiRequest.get(`/teachers/workload`, { params: { school_id } })
  },

  // 获取教师时间安排
  getTeacherSchedule: async (
    id: string,
    params?: {
      start_date?: string
      end_date?: string
    }
  ): Promise<Array<{
    id: string
    course_name: string
    class_name: string
    room_name: string
    start_time: string
    end_time: string
    day_of_week: number
  }>> => {
    return apiRequest.get(`/teachers/${id}/schedule`, { params })
  },

  // 检查教师时间冲突
  checkTeacherConflicts: async (
    id: string,
    schedule: Array<{
      start_time: string
      end_time: string
      day_of_week: number
    }>
  ): Promise<{
    has_conflicts: boolean
    conflicts: Array<{
      existing_schedule: any
      new_schedule: any
    }>
  }> => {
    return apiRequest.post(`/teachers/${id}/check-conflicts`, { schedule })
  },

  // 导入教师数据
  importTeachers: async (school_id: string, file: File): Promise<{
    success_count: number
    error_count: number
    errors: Array<{
      row: number
      message: string
    }>
  }> => {
    const formData = new FormData()
    formData.append('file', file)

    return apiRequest.post(`/teachers/import`, formData, {
      params: { school_id },
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 导出教师数据
  exportTeachers: async (params: TeacherQueryParams): Promise<Blob> => {
    return apiRequest.get('/teachers/export', {
      params,
      responseType: 'blob'
    })
  }
}