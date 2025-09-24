import { apiRequest } from './index'
import type { Calendar, CreateCalendarRequest, UpdateCalendarRequest } from '@/types'

export const calendarApi = {
  // 获取日历列表
  getAll: async (params?: Record<string, any>): Promise<Calendar[]> => {
    return apiRequest.get<Calendar[]>('/calendars', { params })
  },

  // 获取日历详情
  getById: async (id: string): Promise<Calendar> => {
    return apiRequest.get<Calendar>(`/calendars/${id}`)
  },

  // 创建日历
  create: async (data: CreateCalendarRequest): Promise<Calendar> => {
    return apiRequest.post<Calendar>('/calendars', data)
  },

  // 更新日历
  update: async (id: string, data: UpdateCalendarRequest): Promise<Calendar> => {
    return apiRequest.put<Calendar>(`/calendars/${id}`, data)
  },

  // 删除日历
  delete: async (id: string): Promise<void> => {
    return apiRequest.delete(`/calendars/${id}`)
  },

  // 批量删除日历
  batchDelete: async (ids: string[]): Promise<void> => {
    return apiRequest.delete('/calendars/batch', { data: { ids } })
  },

  // 获取日历事件
  getEvents: async (id: string, params?: Record<string, any>): Promise<any[]> => {
    return apiRequest.get<any[]>(`/calendars/${id}/events`, { params })
  },

  // 创建日历事件
  createEvent: async (id: string, data: any): Promise<any> => {
    return apiRequest.post<any>(`/calendars/${id}/events`, data)
  },

  // 更新日历事件
  updateEvent: async (calendarId: string, eventId: string, data: any): Promise<any> => {
    return apiRequest.put<any>(`/calendars/${calendarId}/events/${eventId}`, data)
  },

  // 删除日历事件
  deleteEvent: async (calendarId: string, eventId: string): Promise<void> => {
    return apiRequest.delete(`/calendars/${calendarId}/events/${eventId}`)
  }
}