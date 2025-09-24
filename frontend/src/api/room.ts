import { apiRequest } from './index'
import type { Room, CreateRoomRequest, UpdateRoomRequest } from '@/types'

export const roomsApi = {
  // 获取教室列表
  getRooms: async (params?: any): Promise<Room[]> => {
    return apiRequest.get<Room[]>('/rooms', { params })
  },

  // 获取教室详情
  getRoom: async (id: string): Promise<Room> => {
    return apiRequest.get<Room>(`/rooms/${id}`)
  },

  // 创建教室
  createRoom: async (data: CreateRoomRequest): Promise<Room> => {
    return apiRequest.post<Room>('/rooms', data)
  },

  // 更新教室
  updateRoom: async (id: string, data: UpdateRoomRequest): Promise<Room> => {
    return apiRequest.put<Room>(`/rooms/${id}`, data)
  },

  // 删除教室
  deleteRoom: async (id: string): Promise<void> => {
    return apiRequest.delete(`/rooms/${id}`)
  },

  // 批量删除教室
  bulkDeleteRooms: async (ids: string[]): Promise<void> => {
    return apiRequest.delete('/rooms/bulk', { data: { ids } })
  },

  // 切换教室状态
  toggleRoomStatus: async (id: string, isActive: boolean): Promise<void> => {
    return apiRequest.patch(`/rooms/${id}/status`, { is_active: isActive })
  },

  // 获取校区教室
  getRoomsByCampus: async (campusId: string, params?: any): Promise<Room[]> => {
    return apiRequest.get<Room[]>(`/campuses/${campusId}/rooms`, { params })
  },

  // 获取学校教室
  getRoomsBySchool: async (schoolId: string, params?: any): Promise<Room[]> => {
    return apiRequest.get<Room[]>(`/schools/${schoolId}/rooms`, { params })
  },

  // 获取活跃教室
  getActiveRooms: async (schoolId?: string): Promise<Room[]> => {
    return apiRequest.get<Room[]>('/rooms/active', { params: { school_id: schoolId } })
  },

  // 检查教室代码
  checkRoomCode: async (code: string, schoolId: string, excludeId?: string): Promise<any> => {
    return apiRequest.get('/rooms/check-code', {
      params: { code, school_id: schoolId, exclude_id: excludeId }
    })
  },

  // 获取教室可用性
  getRoomAvailability: async (roomId: string, params: any): Promise<any> => {
    return apiRequest.get(`/rooms/${roomId}/availability`, { params })
  },

  // 获取教室统计
  getRoomStats: async (schoolId?: string): Promise<any> => {
    return apiRequest.get('/rooms/stats', { params: { school_id: schoolId } })
  },

  // 导入教室
  importRooms: async (schoolId: string, file: File): Promise<any> => {
    const formData = new FormData()
    formData.append('file', file)
    return apiRequest.post(`/schools/${schoolId}/rooms/import`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 导出教室
  exportRooms: async (params: any): Promise<Blob> => {
    return apiRequest.get('/rooms/export', {
      params,
      responseType: 'blob'
    })
  }
}

export const campusesApi = {
  // 获取校区列表
  getCampuses: async (schoolId?: string): Promise<any[]> => {
    return apiRequest.get('/campuses', { params: { school_id: schoolId } })
  },

  // 获取校区详情
  getCampus: async (id: string): Promise<any> => {
    return apiRequest.get(`/campuses/${id}`)
  },

  // 创建校区
  createCampus: async (data: any): Promise<any> => {
    return apiRequest.post('/campuses', data)
  },

  // 更新区区
  updateCampus: async (id: string, data: any): Promise<any> => {
    return apiRequest.put(`/campuses/${id}`, data)
  },

  // 删除校区
  deleteCampus: async (id: string): Promise<void> => {
    return apiRequest.delete(`/campuses/${id}`)
  },

  // 切换校区状态
  toggleCampusStatus: async (id: string, isActive: boolean): Promise<void> => {
    return apiRequest.patch(`/campuses/${id}/status`, { is_active: isActive })
  },

  // 获取学校校区
  getCampusesBySchool: async (schoolId: string): Promise<any[]> => {
    return apiRequest.get(`/schools/${schoolId}/campuses`)
  }
}