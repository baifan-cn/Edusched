import { apiRequest, PaginationParams, PaginatedResponse } from './index'
import type { Room, CreateRoomRequest, UpdateRoomRequest, RoomQueryParams, Campus } from '@/types'

// 教室API服务
export const roomsApi = {
  // 获取教室列表
  getRooms: async (params?: RoomQueryParams): Promise<PaginatedResponse<Room>> => {
    return apiRequest.get('/rooms', { params })
  },

  // 获取单个教室详情
  getRoom: async (id: string): Promise<Room> => {
    return apiRequest.get(`/rooms/${id}`)
  },

  // 创建教室
  createRoom: async (data: CreateRoomRequest): Promise<Room> => {
    return apiRequest.post('/rooms', data)
  },

  // 更新教室
  updateRoom: async (id: string, data: UpdateRoomRequest): Promise<Room> => {
    return apiRequest.put(`/rooms/${id}`, data)
  },

  // 删除教室
  deleteRoom: async (id: string): Promise<void> => {
    return apiRequest.delete(`/rooms/${id}`)
  },

  // 批量删除教室
  bulkDeleteRooms: async (ids: string[]): Promise<void> => {
    return apiRequest.post('/rooms/bulk-delete', { ids })
  },

  // 激活/停用教室
  toggleRoomStatus: async (id: string, is_active: boolean): Promise<Room> => {
    return apiRequest.patch(`/rooms/${id}/status`, { is_active })
  },

  // 获取校区下的教室
  getRoomsByCampus: async (campusId: string, params?: Omit<RoomQueryParams, 'campus_id'>): Promise<Room[]> => {
    return apiRequest.get(`/campuses/${campusId}/rooms`, { params })
  },

  // 获取学校下的所有教室
  getRoomsBySchool: async (schoolId: string, params?: Omit<RoomQueryParams, 'school_id'>): Promise<Room[]> => {
    return apiRequest.get(`/schools/${schoolId}/rooms`, { params })
  },

  // 获取所有活跃教室（用于选择器）
  getActiveRooms: async (schoolId?: string): Promise<Room[]> => {
    return apiRequest.get('/rooms/active', { params: { school_id: schoolId } })
  },

  // 检查教室代码是否重复
  checkRoomCode: async (code: string, schoolId: string, excludeId?: string): Promise<{
    is_available: boolean
    message: string
  }> => {
    return apiRequest.get('/rooms/check-code', {
      params: { code, school_id: schoolId, exclude_id: excludeId }
    })
  },

  // 获取教室可用时间
  getRoomAvailability: async (
    roomId: string,
    params: {
      start_date: string
      end_date: string
      day_of_week?: number
    }
  ): Promise<Array<{
    date: string
    day_of_week: number
    time_slots: Array<{
      start_time: string
      end_time: string
      is_available: boolean
      occupied_by?: string
    }>
  }>> => {
    return apiRequest.get(`/rooms/${roomId}/availability`, { params })
  },

  // 获取教室统计信息
  getRoomStats: async (schoolId?: string): Promise<{
    total_rooms: number
    active_rooms: number
    rooms_by_type: Record<string, number>
    rooms_by_campus: Array<{
      campus_name: string
      room_count: number
      capacity_sum: number
    }>
    utilization_rate: number
  }> => {
    return apiRequest.get('/rooms/stats', { params: { school_id: schoolId } })
  },

  // 导入教室数据
  importRooms: async (schoolId: string, file: File): Promise<{
    success_count: number
    error_count: number
    errors: Array<{
      row: number
      message: string
    }>
  }> => {
    const formData = new FormData()
    formData.append('file', file)

    return apiRequest.post('/rooms/import', formData, {
      params: { school_id: schoolId },
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 导出教室数据
  exportRooms: async (params: RoomQueryParams): Promise<Blob> => {
    return apiRequest.get('/rooms/export', {
      params,
      responseType: 'blob'
    })
  }
}

// 校区API服务
export const campusesApi = {
  // 获取校区列表
  getCampuses: async (schoolId?: string): Promise<Campus[]> => {
    return apiRequest.get('/campuses', { params: { school_id: schoolId } })
  },

  // 获取单个校区详情
  getCampus: async (id: string): Promise<Campus> => {
    return apiRequest.get(`/campuses/${id}`)
  },

  // 创建校区
  createCampus: async (data: any): Promise<Campus> => {
    return apiRequest.post('/campuses', data)
  },

  // 更新校区
  updateCampus: async (id: string, data: any): Promise<Campus> => {
    return apiRequest.put(`/campuses/${id}`, data)
  },

  // 删除校区
  deleteCampus: async (id: string): Promise<void> => {
    return apiRequest.delete(`/campuses/${id}`)
  },

  // 激活/停用校区
  toggleCampusStatus: async (id: string, is_active: boolean): Promise<Campus> => {
    return apiRequest.patch(`/campuses/${id}/status`, { is_active })
  },

  // 获取学校下的校区
  getCampusesBySchool: async (schoolId: string): Promise<Campus[]> => {
    return apiRequest.get(`/schools/${schoolId}/campuses`)
  }
}