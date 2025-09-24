import { apiRequest, PaginationParams, PaginatedResponse } from './index'
import type {
  Course,
  CreateCourseRequest,
  UpdateCourseRequest,
  CourseQueryParams,
  Subject
} from '@/types'

// 课程API服务
export const coursesApi = {
  // 获取课程列表
  getCourses: async (params?: CourseQueryParams): Promise<PaginatedResponse<Course>> => {
    return apiRequest.get('/courses', { params })
  },

  // 获取单个课程详情
  getCourse: async (id: string): Promise<Course> => {
    return apiRequest.get(`/courses/${id}`)
  },

  // 创建课程
  createCourse: async (data: CreateCourseRequest): Promise<Course> => {
    return apiRequest.post('/courses', data)
  },

  // 更新课程
  updateCourse: async (id: string, data: UpdateCourseRequest): Promise<Course> => {
    return apiRequest.put(`/courses/${id}`, data)
  },

  // 删除课程
  deleteCourse: async (id: string): Promise<void> => {
    return apiRequest.delete(`/courses/${id}`)
  },

  // 批量删除课程
  bulkDeleteCourses: async (ids: string[]): Promise<void> => {
    return apiRequest.post('/courses/bulk-delete', { ids })
  },

  // 激活/停用课程
  toggleCourseStatus: async (id: string, is_active: boolean): Promise<Course> => {
    return apiRequest.patch(`/courses/${id}/status`, { is_active })
  },

  // 获取学科列表（用于课程表单中的学科选择）
  getSubjects: async (params?: {
    name?: string
    code?: string
    is_active?: boolean
  }): Promise<Subject[]> => {
    return apiRequest.get('/subjects', { params })
  },

  // 获取课程统计信息
  getCourseStats: async (): Promise<{
    total_courses: number
    active_courses: number
    inactive_courses: number
    total_credits: number
    total_hours: number
    courses_by_subject: Array<{
      subject_name: string
      course_count: number
      total_credits: number
    }>
  }> => {
    return apiRequest.get('/courses/stats')
  }
}