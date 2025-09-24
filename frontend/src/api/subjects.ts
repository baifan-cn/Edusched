import { apiRequest, PaginationParams, PaginatedResponse } from './index'
import type { Subject, CreateSubjectRequest, UpdateSubjectRequest, SubjectQueryParams } from '@/types'

// 学科API服务
export const subjectsApi = {
  // 获取学科列表
  getSubjects: async (params?: SubjectQueryParams): Promise<PaginatedResponse<Subject>> => {
    return apiRequest.get('/subjects', { params })
  },

  // 获取单个学科详情
  getSubject: async (id: string): Promise<Subject> => {
    return apiRequest.get(`/subjects/${id}`)
  },

  // 创建学科
  createSubject: async (data: CreateSubjectRequest): Promise<Subject> => {
    return apiRequest.post('/subjects', data)
  },

  // 更新学科
  updateSubject: async (id: string, data: UpdateSubjectRequest): Promise<Subject> => {
    return apiRequest.put(`/subjects/${id}`, data)
  },

  // 删除学科
  deleteSubject: async (id: string): Promise<void> => {
    return apiRequest.delete(`/subjects/${id}`)
  },

  // 批量删除学科
  bulkDeleteSubjects: async (ids: string[]): Promise<void> => {
    return apiRequest.post('/subjects/bulk-delete', { ids })
  },

  // 激活/停用学科
  toggleSubjectStatus: async (id: string, is_active: boolean): Promise<Subject> => {
    return apiRequest.patch(`/subjects/${id}/status`, { is_active })
  },

  // 获取所有活跃学科（用于选择器）
  getActiveSubjects: async (): Promise<Subject[]> => {
    return apiRequest.get('/subjects/active')
  },

  // 检查学科代码是否重复
  checkSubjectCode: async (code: string, excludeId?: string): Promise<{
    is_available: boolean
    message: string
  }> => {
    return apiRequest.get('/subjects/check-code', {
      params: { code, exclude_id: excludeId }
    })
  },

  // 获取学科统计信息
  getSubjectStats: async (): Promise<{
    total_subjects: number
    active_subjects: number
    subjects_by_category: Record<string, number>
    recent_created: Subject[]
  }> => {
    return apiRequest.get('/subjects/stats')
  },

  // 导入学科数据
  importSubjects: async (file: File): Promise<{
    success_count: number
    error_count: number
    errors: Array<{
      row: number
      message: string
    }>
  }> => {
    const formData = new FormData()
    formData.append('file', file)

    return apiRequest.post('/subjects/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 导出学科数据
  exportSubjects: async (params?: SubjectQueryParams): Promise<Blob> => {
    return apiRequest.get('/subjects/export', {
      params,
      responseType: 'blob'
    })
  }
}