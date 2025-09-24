import { apiRequest, PaginationParams, PaginatedResponse } from './index'
import type {
  Timetable,
  CreateTimetableRequest,
  UpdateTimetableRequest,
  TimetableQueryParams,
  Assignment,
  CreateAssignmentRequest,
  UpdateAssignmentRequest,
  TimetableGridData,
  TimetableStats,
  TimetableConflict,
  TimetableExportOptions,
  TimetableBulkActionRequest,
  TimetableDuplicateRequest,
  PublishTimetableRequest
} from '../types/timetables'

// 时间表API服务
export const timetablesApi = {
  // 获取时间表列表
  getTimetables: async (params?: TimetableQueryParams): Promise<PaginatedResponse<Timetable>> => {
    return apiRequest.get('/timetables', { params })
  },

  // 获取单个时间表详情
  getTimetable: async (id: string): Promise<Timetable> => {
    return apiRequest.get(`/timetables/${id}`)
  },

  // 创建时间表
  createTimetable: async (data: CreateTimetableRequest): Promise<Timetable> => {
    return apiRequest.post('/timetables', data)
  },

  // 更新时间表
  updateTimetable: async (id: string, data: UpdateTimetableRequest): Promise<Timetable> => {
    return apiRequest.put(`/timetables/${id}`, data)
  },

  // 删除时间表
  deleteTimetable: async (id: string): Promise<void> => {
    return apiRequest.delete(`/timetables/${id}`)
  },

  // 批量删除时间表
  bulkDeleteTimetables: async (ids: string[]): Promise<void> => {
    return apiRequest.post('/timetables/bulk-delete', { ids })
  },

  // 发布时间表
  publishTimetable: async (id: string, data?: PublishTimetableRequest): Promise<Timetable> => {
    return apiRequest.post(`/timetables/${id}/publish`, data)
  },

  // 取消发布时间表
  unpublishTimetable: async (id: string): Promise<Timetable> => {
    return apiRequest.post(`/timetables/${id}/unpublish`)
  },

  // 复制时间表
  duplicateTimetable: async (data: TimetableDuplicateRequest): Promise<Timetable> => {
    return apiRequest.post('/timetables/duplicate', data)
  },

  // 获取时间表分配列表
  getTimetableAssignments: async (
    timetableId: string,
    params?: PaginationParams
  ): Promise<PaginatedResponse<Assignment>> => {
    return apiRequest.get(`/timetables/${timetableId}/assignments`, { params })
  },

  // 创建分配
  createAssignment: async (timetableId: string, data: CreateAssignmentRequest): Promise<Assignment> => {
    return apiRequest.post(`/timetables/${timetableId}/assignments`, data)
  },

  // 更新分配
  updateAssignment: async (
    timetableId: string,
    assignmentId: string,
    data: UpdateAssignmentRequest
  ): Promise<Assignment> => {
    return apiRequest.put(`/timetables/${timetableId}/assignments/${assignmentId}`, data)
  },

  // 删除分配
  deleteAssignment: async (timetableId: string, assignmentId: string): Promise<void> => {
    return apiRequest.delete(`/timetables/${timetableId}/assignments/${assignmentId}`)
  },

  // 批量创建分配
  bulkCreateAssignments: async (
    timetableId: string,
    assignments: CreateAssignmentRequest[]
  ): Promise<Assignment[]> => {
    return apiRequest.post(`/timetables/${timetableId}/assignments/bulk`, { assignments })
  },

  // 批量删除分配
  bulkDeleteAssignments: async (timetableId: string, assignmentIds: string[]): Promise<void> => {
    return apiRequest.post(`/timetables/${timetableId}/assignments/bulk-delete`, { assignmentIds })
  },

  // 获取时间表网格数据
  getTimetableGrid: async (timetableId: string): Promise<TimetableGridData> => {
    return apiRequest.get(`/timetables/${timetableId}/grid`)
  },

  // 获取时间表统计信息
  getTimetableStats: async (timetableId: string): Promise<TimetableStats> => {
    return apiRequest.get(`/timetables/${timetableId}/stats`)
  },

  // 获取时间表冲突
  getTimetableConflicts: async (timetableId: string): Promise<TimetableConflict[]> => {
    return apiRequest.get(`/timetables/${timetableId}/conflicts`)
  },

  // 解决冲突
  resolveConflict: async (timetableId: string, conflictId: string, solution: any): Promise<void> => {
    return apiRequest.post(`/timetables/${timetableId}/conflicts/${conflictId}/resolve`, { solution })
  },

  // 导出时间表
  exportTimetable: async (timetableId: string, options: TimetableExportOptions): Promise<Blob> => {
    return apiRequest.post(`/timetables/${timetableId}/export`, options, {
      responseType: 'blob'
    })
  },

  // 导入时间表
  importTimetable: async (file: File, calendarId: string): Promise<Timetable> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('calendar_id', calendarId)

    return apiRequest.post('/timetables/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取时间表预览
  getTimetablePreview: async (timetableId: string): Promise<any> => {
    return apiRequest.get(`/timetables/${timetableId}/preview`)
  },

  // 打印时间表
  printTimetable: async (timetableId: string, options?: any): Promise<Blob> => {
    return apiRequest.post(`/timetables/${timetableId}/print`, options, {
      responseType: 'blob'
    })
  },

  // 获取时间表历史记录
  getTimetableHistory: async (
    timetableId: string,
    params?: PaginationParams
  ): Promise<PaginatedResponse<any>> => {
    return apiRequest.get(`/timetables/${timetableId}/history`, { params })
  },

  // 批量操作时间表
  bulkActionTimetables: async (data: TimetableBulkActionRequest): Promise<any> => {
    return apiRequest.post('/timetables/bulk-action', data)
  },

  // 获取时间表模板
  getTimetableTemplates: async (): Promise<any[]> => {
    return apiRequest.get('/timetables/templates')
  },

  // 从模板创建时间表
  createTimetableFromTemplate: async (templateId: string, data: any): Promise<Timetable> => {
    return apiRequest.post(`/timetables/templates/${templateId}/create`, data)
  },

  // 验证时间表数据
  validateTimetable: async (timetableId: string): Promise<{
    valid: boolean
    errors: string[]
    warnings: string[]
  }> => {
    return apiRequest.post(`/timetables/${timetableId}/validate`)
  },

  // 优化时间表
  optimizeTimetable: async (timetableId: string, options?: any): Promise<{
    success: boolean
    message: string
    improvements: any[]
  }> => {
    return apiRequest.post(`/timetables/${timetableId}/optimize`, options)
  },

  // 锁定/解锁分配
  toggleAssignmentLock: async (
    timetableId: string,
    assignmentId: string,
    is_locked: boolean
  ): Promise<Assignment> => {
    return apiRequest.patch(`/timetables/${timetableId}/assignments/${assignmentId}/lock`, {
      is_locked
    })
  },

  // 移动分配到新的时间段
  moveAssignment: async (
    timetableId: string,
    assignmentId: string,
    newTimeslotId: string,
    newRoomId?: string
  ): Promise<Assignment> => {
    return apiRequest.post(`/timetables/${timetableId}/assignments/${assignmentId}/move`, {
      new_timeslot_id: newTimeslotId,
      new_room_id: newRoomId
    })
  },

  // 获取可用时间段
  getAvailableTimeslots: async (
    timetableId: string,
    sectionId: string,
    teacherId: string,
    roomId?: string
  ): Promise<any[]> => {
    return apiRequest.get(`/timetables/${timetableId}/available-timeslots`, {
      params: { section_id: sectionId, teacher_id: teacherId, room_id: roomId }
    })
  }
}