import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { TimeSlot, CreateTimeSlotRequest, UpdateTimeSlotRequest } from '@/types'
import { timeslotApi } from '@/api/timeslot'

export const useTimeslotsStore = defineStore('timeslots', () => {
  const timeslots = ref<TimeSlot[]>([])
  const loading = ref(false)
  const error = ref('')

  // 计算属性
  const activeTimeslots = computed(() =>
    timeslots.value.filter(timeslot => timeslot.is_active)
  )

  const timeslotCount = computed(() => timeslots.value.length)

  // 按星期分组
  const timeslotsByDay = computed(() => {
    const groups: Record<number, TimeSlot[]> = {}
    timeslots.value.forEach(timeslot => {
      if (!groups[timeslot.day_of_week]) {
        groups[timeslot.day_of_week] = []
      }
      groups[timeslot.day_of_week].push(timeslot)
    })
    return groups
  })

  // 按时间排序
  const sortedTimeslots = computed(() => {
    return [...timeslots.value].sort((a, b) => {
      if (a.day_of_week !== b.day_of_week) {
        return a.day_of_week - b.day_of_week
      }
      return a.start_time.localeCompare(b.start_time)
    })
  })

  // 清除错误
  const clearError = () => {
    error.value = ''
  }

  // 获取时间段列表
  const fetchTimeslots = async (params?: Record<string, any>) => {
    try {
      loading.value = true
      clearError()
      const response = await timeslotApi.getAll(params)
      timeslots.value = response
    } catch (err: any) {
      error.value = err.message || '获取时间段列表失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取时间段详情
  const fetchTimeslot = async (id: string) => {
    try {
      loading.value = true
      clearError()
      const response = await timeslotApi.getById(id)
      return response
    } catch (err: any) {
      error.value = err.message || '获取时间段详情失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 创建时间段
  const createTimeslot = async (data: CreateTimeSlotRequest) => {
    try {
      loading.value = true
      clearError()
      const response = await timeslotApi.create(data)
      timeslots.value.push(response)
      return response
    } catch (err: any) {
      error.value = err.message || '创建时间段失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 更新时间段
  const updateTimeslot = async (id: string, data: UpdateTimeSlotRequest) => {
    try {
      loading.value = true
      clearError()
      const response = await timeslotApi.update(id, data)
      const index = timeslots.value.findIndex(timeslot => timeslot.id === id)
      if (index !== -1) {
        timeslots.value[index] = response
      }
      return response
    } catch (err: any) {
      error.value = err.message || '更新时间段失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 删除时间段
  const deleteTimeslot = async (id: string) => {
    try {
      loading.value = true
      clearError()
      await timeslotApi.delete(id)
      timeslots.value = timeslots.value.filter(timeslot => timeslot.id !== id)
    } catch (err: any) {
      error.value = err.message || '删除时间段失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 批量删除时间段
  const batchDeleteTimeslots = async (ids: string[]) => {
    try {
      loading.value = true
      clearError()
      await timeslotApi.batchDelete(ids)
      timeslots.value = timeslots.value.filter(timeslot => !ids.includes(timeslot.id))
    } catch (err: any) {
      error.value = err.message || '批量删除时间段失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 切换时间段状态
  const toggleTimeslotStatus = async (id: string) => {
    try {
      loading.value = true
      clearError()
      const timeslot = timeslots.value.find(t => t.id === id)
      if (timeslot) {
        const response = await timeslotApi.update(id, { is_active: !timeslot.is_active })
        const index = timeslots.value.findIndex(t => t.id === id)
        if (index !== -1) {
          timeslots.value[index] = response
        }
        return response
      }
    } catch (err: any) {
      error.value = err.message || '切换时间段状态失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 检查时间段冲突
  const checkTimeSlotConflict = async (data: any) => {
    try {
      loading.value = true
      clearError()
      const response = await timeslotApi.checkConflict(data)
      return response
    } catch (err: any) {
      error.value = err.message || '检查时间段冲突失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取时间段统计
  const getTimeslotStats = async () => {
    try {
      loading.value = true
      clearError()
      const response = await timeslotApi.getStats()
      return response
    } catch (err: any) {
      error.value = err.message || '获取时间段统计失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    timeslots,
    loading,
    error,

    // 计算属性
    activeTimeslots,
    timeslotCount,
    timeslotsByDay,
    sortedTimeslots,

    // 方法
    clearError,
    fetchTimeslots,
    fetchTimeslot,
    createTimeslot,
    updateTimeslot,
    deleteTimeslot,
    batchDeleteTimeslots,
    toggleTimeslotStatus,
    checkTimeSlotConflict,
    getTimeslotStats
  }
})