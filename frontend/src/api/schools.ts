import { apiRequest, PaginationParams, PaginatedResponse } from './index'

// 学校相关类型定义
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

// 创建学校请求
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

// 更新学校请求
export interface UpdateSchoolRequest extends Partial<CreateSchoolRequest> {
  id: string
}

// 查询学校参数
export interface SchoolQueryParams extends PaginationParams {
  name?: string
  code?: string
  is_active?: boolean
}

// 学校API服务
export const schoolsApi = {
  // 获取学校列表
  getSchools: async (params?: SchoolQueryParams): Promise<PaginatedResponse<School>> => {
    return apiRequest.get('/schools', { params })
  },

  // 获取单个学校详情
  getSchool: async (id: string): Promise<School> => {
    return apiRequest.get(`/schools/${id}`)
  },

  // 创建学校
  createSchool: async (data: CreateSchoolRequest): Promise<School> => {
    return apiRequest.post('/schools', data)
  },

  // 更新学校
  updateSchool: async (id: string, data: UpdateSchoolRequest): Promise<School> => {
    return apiRequest.put(`/schools/${id}`, data)
  },

  // 删除学校
  deleteSchool: async (id: string): Promise<void> => {
    return apiRequest.delete(`/schools/${id}`)
  },

  // 批量删除学校
  bulkDeleteSchools: async (ids: string[]): Promise<void> => {
    return apiRequest.post('/schools/bulk-delete', { ids })
  },

  // 激活/停用学校
  toggleSchoolStatus: async (id: string, is_active: boolean): Promise<School> => {
    return apiRequest.patch(`/schools/${id}/status`, { is_active })
  },

  // 上传学校logo
  uploadSchoolLogo: async (id: string, file: File): Promise<{ logo_url: string }> => {
    const formData = new FormData()
    formData.append('file', file)

    return apiRequest.post(`/schools/${id}/logo`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取学校统计信息
  getSchoolStats: async (id: string): Promise<{
    teacher_count: number
    student_count: number
    course_count: number
    class_count: number
    room_count: number
  }> => {
    return apiRequest.get(`/schools/${id}/stats`)
  }
}