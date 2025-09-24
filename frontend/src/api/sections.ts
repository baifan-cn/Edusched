import { apiRequest, PaginationParams, PaginatedResponse } from './index'
import type {
  Section,
  CreateSectionRequest,
  UpdateSectionRequest,
  SectionQueryParams
} from '../types/models'

// 教学段API服务
export const sectionsApi = {
  // 获取教学段列表
  getSections: async (params?: SectionQueryParams): Promise<PaginatedResponse<Section>> => {
    return apiRequest.get('/sections', { params })
  },

  // 获取单个教学段详情
  getSection: async (id: string): Promise<Section> => {
    return apiRequest.get(`/sections/${id}`)
  },

  // 创建教学段
  createSection: async (data: CreateSectionRequest): Promise<Section> => {
    return apiRequest.post('/sections', data)
  },

  // 更新教学段
  updateSection: async (id: string, data: UpdateSectionRequest): Promise<Section> => {
    return apiRequest.put(`/sections/${id}`, data)
  },

  // 删除教学段
  deleteSection: async (id: string): Promise<void> => {
    return apiRequest.delete(`/sections/${id}`)
  },

  // 批量删除教学段
  bulkDeleteSections: async (ids: string[]): Promise<void> => {
    return apiRequest.post('/sections/bulk-delete', { ids })
  },

  // 激活/停用教学段
  toggleSectionStatus: async (id: string, is_active: boolean): Promise<Section> => {
    return apiRequest.patch(`/sections/${id}/status`, { is_active })
  },

  // 锁定/解锁教学段
  toggleSectionLock: async (id: string, is_locked: boolean): Promise<Section> => {
    return apiRequest.patch(`/sections/${id}/lock`, { is_locked })
  },

  // 获取教学段统计信息
  getSectionStats: async (params?: {
    course_id?: string
    teacher_id?: string
    class_group_id?: string
  }): Promise<any> => {
    return apiRequest.get('/sections/stats', { params })
  },

  // 获取课程的教学段列表
  getCourseSections: async (courseId: string, params?: SectionQueryParams): Promise<PaginatedResponse<Section>> => {
    return apiRequest.get(`/courses/${courseId}/sections`, { params })
  },

  // 获取教师的教学段列表
  getTeacherSections: async (teacherId: string, params?: SectionQueryParams): Promise<PaginatedResponse<Section>> => {
    return apiRequest.get(`/teachers/${teacherId}/sections`, { params })
  },

  // 获取班级的教学段列表
  getClassGroupSections: async (classGroupId: string, params?: SectionQueryParams): Promise<PaginatedResponse<Section>> => {
    return apiRequest.get(`/class-groups/${classGroupId}/sections`, { params })
  },

  // 复制教学段
  duplicateSection: async (id: string, data: {
    name: string
    code: string
    copy_assignments?: boolean
  }): Promise<Section> => {
    return apiRequest.post(`/sections/${id}/duplicate`, data)
  },

  // 批量更新教学段
  bulkUpdateSections: async (updates: Array<{
    id: string
    data: UpdateSectionRequest
  }>): Promise<Section[]> => {
    return apiRequest.put('/sections/bulk-update', { updates })
  }
}

// 导出类型
export type {
  Section,
  CreateSectionRequest,
  UpdateSectionRequest,
  SectionQueryParams
}