import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Constraint, CreateConstraintRequest, UpdateConstraintRequest } from '@/types'
import { constraintApi } from '@/api/constraint'

export const useConstraintsStore = defineStore('constraints', () => {
  const constraints = ref<Constraint[]>([])
  const loading = ref(false)
  const error = ref('')

  // 计算属性
  const activeConstraints = computed(() =>
    constraints.value.filter(constraint => constraint.is_active)
  )

  const constraintCount = computed(() => constraints.value.length)

  // 按类型分组
  const constraintsByType = computed(() => {
    const groups: Record<string, Constraint[]> = {}
    constraints.value.forEach(constraint => {
      if (!groups[constraint.constraint_type]) {
        groups[constraint.constraint_type] = []
      }
      groups[constraint.constraint_type].push(constraint)
    })
    return groups
  })

  // 按权重分组
  const hardConstraints = computed(() =>
    constraints.value.filter(constraint => constraint.weight === 1.0)
  )

  const softConstraints = computed(() =>
    constraints.value.filter(constraint => constraint.weight < 1.0)
  )

  // 清除错误
  const clearError = () => {
    error.value = ''
  }

  // 获取约束列表
  const fetchConstraints = async (params?: Record<string, any>) => {
    try {
      loading.value = true
      clearError()
      const response = await constraintApi.getAll(params)
      constraints.value = response
    } catch (err: any) {
      error.value = err.message || '获取约束列表失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取约束详情
  const fetchConstraint = async (id: string) => {
    try {
      loading.value = true
      clearError()
      const response = await constraintApi.getById(id)
      return response
    } catch (err: any) {
      error.value = err.message || '获取约束详情失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 创建约束
  const createConstraint = async (data: CreateConstraintRequest) => {
    try {
      loading.value = true
      clearError()
      const response = await constraintApi.create(data)
      constraints.value.push(response)
      return response
    } catch (err: any) {
      error.value = err.message || '创建约束失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 更新约束
  const updateConstraint = async (id: string, data: UpdateConstraintRequest) => {
    try {
      loading.value = true
      clearError()
      const response = await constraintApi.update(id, data)
      const index = constraints.value.findIndex(constraint => constraint.id === id)
      if (index !== -1) {
        constraints.value[index] = response
      }
      return response
    } catch (err: any) {
      error.value = err.message || '更新约束失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 删除约束
  const deleteConstraint = async (id: string) => {
    try {
      loading.value = true
      clearError()
      await constraintApi.delete(id)
      constraints.value = constraints.value.filter(constraint => constraint.id !== id)
    } catch (err: any) {
      error.value = err.message || '删除约束失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 批量删除约束
  const batchDeleteConstraints = async (ids: string[]) => {
    try {
      loading.value = true
      clearError()
      await constraintApi.batchDelete(ids)
      constraints.value = constraints.value.filter(constraint => !ids.includes(constraint.id))
    } catch (err: any) {
      error.value = err.message || '批量删除约束失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 验证约束
  const validateConstraint = async (data: any) => {
    try {
      loading.value = true
      clearError()
      const response = await constraintApi.validate(data)
      return response
    } catch (err: any) {
      error.value = err.message || '验证约束失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取约束建议
  const getConstraintSuggestions = async (context: any) => {
    try {
      loading.value = true
      clearError()
      const response = await constraintApi.getSuggestions(context)
      return response
    } catch (err: any) {
      error.value = err.message || '获取约束建议失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    constraints,
    loading,
    error,

    // 计算属性
    activeConstraints,
    constraintCount,
    constraintsByType,
    hardConstraints,
    softConstraints,

    // 方法
    clearError,
    fetchConstraints,
    fetchConstraint,
    createConstraint,
    updateConstraint,
    deleteConstraint,
    batchDeleteConstraints,
    validateConstraint,
    getConstraintSuggestions
  }
})