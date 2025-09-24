import { apiRequest } from './index'
import type { Campus, CreateCampusRequest, UpdateCampusRequest } from '@/types'

export const campusApi = {
  // 获取校区列表
  getCampuses: async (params: any = {}): Promise<Campus[]> => {
    return apiRequest.get<Campus[]>('/campuses', { params })
  },

  // 获取校区详情
  getCampus: async (id: string): Promise<Campus> => {
    return apiRequest.get<Campus>(`/campuses/${id}`)
  },

  // 创建校区
  createCampus: async (data: CreateCampusRequest): Promise<Campus> => {
    return apiRequest.post<Campus>('/campuses', data)
  },

  // 更新区区
  updateCampus: async (id: string, data: UpdateCampusRequest): Promise<Campus> => {
    return apiRequest.put<Campus>(`/campuses/${id}`, data)
  },

  // 删除校区
  deleteCampus: async (id: string): Promise<void> => {
    return apiRequest.delete(`/campuses/${id}`)
  },

  // 批量删除校区
  bulkDeleteCampuses: async (ids: string[]): Promise<void> => {
    return apiRequest.delete('/campuses/bulk', { data: { ids } })
  }
}