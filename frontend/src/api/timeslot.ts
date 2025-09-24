import { apiRequest } from './index'
import type { TimeSlot, CreateTimeSlotRequest, UpdateTimeSlotRequest } from '@/types'

export const timeslotApi = {
  // 获取时间段列表
  getAll: async (params?: Record<string, any>): Promise<TimeSlot[]> => {
    return apiRequest.get<TimeSlot[]>('/timeslots', { params })
  },

  // 获取时间段详情
  getById: async (id: string): Promise<TimeSlot> => {
    return apiRequest.get<TimeSlot>(`/timeslots/${id}`)
  },

  // 创建时间段
  create: async (data: CreateTimeSlotRequest): Promise<TimeSlot> => {
    return apiRequest.post<TimeSlot>('/timeslots', data)
  },

  // 更新时间段
  update: async (id: string, data: UpdateTimeSlotRequest): Promise<TimeSlot> => {
    return apiRequest.put<TimeSlot>(`/timeslots/${id}`, data)
  },

  // 删除时间段
  delete: async (id: string): Promise<void> => {
    return apiRequest.delete(`/timeslots/${id}`)
  },

  // 批量删除时间段
  batchDelete: async (ids: string[]): Promise<void> => {
    return apiRequest.delete('/timeslots/batch', { data: { ids } })
  },

  // 检查时间段冲突
  checkConflict: async (data: any): Promise<any> => {
    return apiRequest.post<any>('/timeslots/check-conflict', data)
  },

  // 获取时间段统计
  getStats: async (): Promise<any> => {
    return apiRequest.get<any>('/timeslots/stats')
  },

  // 获取工作日时间段
  getWeekdayTimeslots: async (dayOfWeek: number): Promise<TimeSlot[]> => {
    return apiRequest.get<TimeSlot[]>(`/timeslots/weekday/${dayOfWeek}`)
  },

  // 获取可用时间段
  getAvailableTimeslots: async (params: any): Promise<TimeSlot[]> => {
    return apiRequest.get<TimeSlot[]>('/timeslots/available', { params })
  },

  // 批量创建时间段
  batchCreate: async (data: CreateTimeSlotRequest[]): Promise<TimeSlot[]> => {
    return apiRequest.post<TimeSlot[]>('/timeslots/batch', data)
  },

  // 复制时间段
  copyTimeslots: async (sourceDay: number, targetDay: number): Promise<TimeSlot[]> => {
    return apiRequest.post<TimeSlot[]>('/timeslots/copy', { source_day: sourceDay, target_day: targetDay })
  }
}