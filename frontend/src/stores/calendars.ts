import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Calendar, CreateCalendarRequest, UpdateCalendarRequest } from '@/types'
import { calendarApi } from '@/api/calendar'

export const useCalendarsStore = defineStore('calendars', () => {
  const calendars = ref<Calendar[]>([])
  const loading = ref(false)
  const error = ref('')

  // 计算属性
  const activeCalendars = computed(() =>
    calendars.value.filter(calendar => calendar.is_active)
  )

  const calendarCount = computed(() => calendars.value.length)

  // 清除错误
  const clearError = () => {
    error.value = ''
  }

  // 获取日历列表
  const fetchCalendars = async () => {
    try {
      loading.value = true
      clearError()
      const response = await calendarApi.getAll()
      calendars.value = response
    } catch (err: any) {
      error.value = err.message || '获取日历列表失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取日历详情
  const fetchCalendar = async (id: string) => {
    try {
      loading.value = true
      clearError()
      const response = await calendarApi.getById(id)
      return response
    } catch (err: any) {
      error.value = err.message || '获取日历详情失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 创建日历
  const createCalendar = async (data: CreateCalendarRequest) => {
    try {
      loading.value = true
      clearError()
      const response = await calendarApi.create(data)
      calendars.value.push(response)
      return response
    } catch (err: any) {
      error.value = err.message || '创建日历失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 更新日历
  const updateCalendar = async (id: string, data: UpdateCalendarRequest) => {
    try {
      loading.value = true
      clearError()
      const response = await calendarApi.update(id, data)
      const index = calendars.value.findIndex(calendar => calendar.id === id)
      if (index !== -1) {
        calendars.value[index] = response
      }
      return response
    } catch (err: any) {
      error.value = err.message || '更新日历失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 删除日历
  const deleteCalendar = async (id: string) => {
    try {
      loading.value = true
      clearError()
      await calendarApi.delete(id)
      calendars.value = calendars.value.filter(calendar => calendar.id !== id)
    } catch (err: any) {
      error.value = err.message || '删除日历失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 批量删除日历
  const batchDeleteCalendars = async (ids: string[]) => {
    try {
      loading.value = true
      clearError()
      await calendarApi.batchDelete(ids)
      calendars.value = calendars.value.filter(calendar => !ids.includes(calendar.id))
    } catch (err: any) {
      error.value = err.message || '批量删除日历失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    calendars,
    loading,
    error,

    // 计算属性
    activeCalendars,
    calendarCount,

    // 方法
    clearError,
    fetchCalendars,
    fetchCalendar,
    createCalendar,
    updateCalendar,
    deleteCalendar,
    batchDeleteCalendars
  }
})