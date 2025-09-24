import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Campus } from '@/types'
import { campusApi } from '@/api/campus'

export const useCampusesStore = defineStore('campuses', () => {
  const campuses = ref<Campus[]>([])
  const loading = ref(false)
  const total = ref(0)

  const fetchCampuses = async (params: any = {}) => {
    loading.value = true
    try {
      const response = await campusApi.getCampuses(params)
      campuses.value = response.data.items || []
      total.value = response.data.total || 0
    } catch (error) {
      console.error('获取校区列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createCampus = async (campus: Partial<Campus>) => {
    try {
      const response = await campusApi.createCampus(campus)
      campuses.value.push(response.data)
      total.value += 1
      return response.data
    } catch (error) {
      console.error('创建校区失败:', error)
      throw error
    }
  }

  const updateCampus = async (id: string, campus: Partial<Campus>) => {
    try {
      const response = await campusApi.updateCampus(id, campus)
      const index = campuses.value.findIndex(c => c.id === id)
      if (index !== -1) {
        campuses.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('更新校区失败:', error)
      throw error
    }
  }

  const deleteCampus = async (id: string) => {
    try {
      await campusApi.deleteCampus(id)
      const index = campuses.value.findIndex(c => c.id === id)
      if (index !== -1) {
        campuses.value.splice(index, 1)
        total.value -= 1
      }
    } catch (error) {
      console.error('删除校区失败:', error)
      throw error
    }
  }

  const bulkDeleteCampuses = async (ids: string[]) => {
    try {
      await campusApi.bulkDeleteCampuses(ids)
      campuses.value = campuses.value.filter(c => !ids.includes(c.id))
      total.value -= ids.length
    } catch (error) {
      console.error('批量删除校区失败:', error)
      throw error
    }
  }

  const toggleCampusStatus = async (id: string, isActive: boolean) => {
    try {
      await campusApi.updateCampus(id, { is_active: isActive })
      const campus = campuses.value.find(c => c.id === id)
      if (campus) {
        campus.is_active = isActive
      }
    } catch (error) {
      console.error('切换校区状态失败:', error)
      throw error
    }
  }

  return {
    campuses,
    loading,
    total,
    fetchCampuses,
    createCampus,
    updateCampus,
    deleteCampus,
    bulkDeleteCampuses,
    toggleCampusStatus
  }
})