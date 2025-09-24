import { apiRequest, PaginationParams, PaginatedResponse } from './index'
import type {
  Assignment,
  CreateAssignmentRequest,
  UpdateAssignmentRequest,
  AssignmentQueryParams
} from '../types/models'

// 任务分配API服务
export const assignmentsApi = {
  // 获取分配列表
  getAssignments: async (params?: AssignmentQueryParams): Promise<PaginatedResponse<Assignment>> => {
    return apiRequest.get('/assignments', { params })
  },

  // 获取单个分配详情
  getAssignment: async (id: string): Promise<Assignment> => {
    return apiRequest.get(`/assignments/${id}`)
  },

  // 创建分配
  createAssignment: async (data: CreateAssignmentRequest): Promise<Assignment> => {
    return apiRequest.post('/assignments', data)
  },

  // 更新分配
  updateAssignment: async (id: string, data: UpdateAssignmentRequest): Promise<Assignment> => {
    return apiRequest.put(`/assignments/${id}`, data)
  },

  // 删除分配
  deleteAssignment: async (id: string): Promise<void> => {
    return apiRequest.delete(`/assignments/${id}`)
  },

  // 批量删除分配
  bulkDeleteAssignments: async (ids: string[]): Promise<void> => {
    return apiRequest.post('/assignments/bulk-delete', { ids })
  },

  // 锁定/解锁分配
  toggleAssignmentLock: async (id: string, is_locked: boolean): Promise<Assignment> => {
    return apiRequest.patch(`/assignments/${id}/lock`, { is_locked })
  },

  // 获取时间表的分配列表
  getTimetableAssignments: async (timetableId: string, params?: AssignmentQueryParams): Promise<PaginatedResponse<Assignment>> => {
    return apiRequest.get(`/timetables/${timetableId}/assignments`, { params })
  },

  // 获取教学段的分配列表
  getSectionAssignments: async (sectionId: string, params?: AssignmentQueryParams): Promise<PaginatedResponse<Assignment>> => {
    return apiRequest.get(`/sections/${sectionId}/assignments`, { params })
  },

  // 获取教师的分配列表
  getTeacherAssignments: async (teacherId: string, params?: AssignmentQueryParams): Promise<PaginatedResponse<Assignment>> => {
    return apiRequest.get(`/teachers/${teacherId}/assignments`, { params })
  },

  // 获取教室的分配列表
  getRoomAssignments: async (roomId: string, params?: AssignmentQueryParams): Promise<PaginatedResponse<Assignment>> => {
    return apiRequest.get(`/rooms/${roomId}/assignments`, { params })
  },

  // 获取时间段的分配列表
  getTimeslotAssignments: async (timeslotId: string, params?: AssignmentQueryParams): Promise<PaginatedResponse<Assignment>> => {
    return apiRequest.get(`/timeslots/${timeslotId}/assignments`, { params })
  },

  // 批量创建分配
  bulkCreateAssignments: async (assignments: CreateAssignmentRequest[]): Promise<Assignment[]> => {
    return apiRequest.post('/assignments/bulk-create', { assignments })
  },

  // 批量更新分配
  bulkUpdateAssignments: async (updates: Array<{
    id: string
    data: UpdateAssignmentRequest
  }>): Promise<Assignment[]> => {
    return apiRequest.put('/assignments/bulk-update', { updates })
  },

  // 复制分配
  duplicateAssignment: async (id: string, data: {
    section_id?: string
    timeslot_id?: string
    room_id?: string
  }): Promise<Assignment> => {
    return apiRequest.post(`/assignments/${id}/duplicate`, data)
  },

  // 移动分配到新的时间段
  moveAssignment: async (id: string, data: {
    timeslot_id: string
    room_id?: string
    notes?: string
  }): Promise<Assignment> => {
    return apiRequest.patch(`/assignments/${id}/move`, data)
  },

  // 获取分配统计信息
  getAssignmentStats: async (params?: {
    timetable_id?: string
    teacher_id?: string
    room_id?: string
    course_id?: string
  }): Promise<any> => {
    return apiRequest.get('/assignments/stats', { params })
  },

  // 获取分配冲突检测
  getAssignmentConflicts: async (data: {
    section_id: string
    timeslot_id: string
    room_id: string
    exclude_assignment_id?: string
  }): Promise<any> => {
    return apiRequest.post('/assignments/check-conflicts', data)
  },

  // 获取分配建议
  getAssignmentSuggestions: async (sectionId: string, params?: {
    preferred_teacher_id?: string
    preferred_room_id?: string
    preferred_times?: string[]
  }): Promise<any> => {
    return apiRequest.get(`/sections/${sectionId}/assignment-suggestions`, { params })
  }
}

// 导出类型
export type {
  Assignment,
  CreateAssignmentRequest,
  UpdateAssignmentRequest,
  AssignmentQueryParams
}