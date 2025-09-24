import { apiRequest } from './index'
import type { Constraint, CreateConstraintRequest, UpdateConstraintRequest } from '@/types'

export const constraintApi = {
  // 获取约束列表
  getAll: async (params?: Record<string, any>): Promise<Constraint[]> => {
    return apiRequest.get<Constraint[]>('/constraints', { params })
  },

  // 获取约束详情
  getById: async (id: string): Promise<Constraint> => {
    return apiRequest.get<Constraint>(`/constraints/${id}`)
  },

  // 创建约束
  create: async (data: CreateConstraintRequest): Promise<Constraint> => {
    return apiRequest.post<Constraint>('/constraints', data)
  },

  // 更新约束
  update: async (id: string, data: UpdateConstraintRequest): Promise<Constraint> => {
    return apiRequest.put<Constraint>(`/constraints/${id}`, data)
  },

  // 删除约束
  delete: async (id: string): Promise<void> => {
    return apiRequest.delete(`/constraints/${id}`)
  },

  // 批量删除约束
  batchDelete: async (ids: string[]): Promise<void> => {
    return apiRequest.delete('/constraints/batch', { data: { ids } })
  },

  // 验证约束
  validate: async (data: any): Promise<any> => {
    return apiRequest.post<any>('/constraints/validate', data)
  },

  // 获取约束建议
  getSuggestions: async (context: any): Promise<any[]> => {
    return apiRequest.post<any[]>('/constraints/suggestions', context)
  },

  // 获取约束类型
  getTypes: async (): Promise<string[]> => {
    return apiRequest.get<string[]>('/constraints/types')
  },

  // 获取约束统计
  getStats: async (): Promise<any> => {
    return apiRequest.get<any>('/constraints/stats')
  }
}