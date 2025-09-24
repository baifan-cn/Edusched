import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { teachersApi } from '@/api/teachers'
import type { Teacher, CreateTeacherRequest, UpdateTeacherRequest, TeacherQueryParams, TeacherWorkload } from '@/types'

export const useTeachersStore = defineStore('teachers', () => {
  // 状态
  const teachers = ref<Teacher[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const currentTeacher = ref<Teacher | null>(null)
  const workloadStats = ref<TeacherWorkload[]>([])

  // 计算属性
  const activeTeachers = computed(() => teachers.value.filter(t => t.is_active))
  const inactiveTeachers = computed(() => teachers.value.filter(t => !t.is_active))

  const teachersByDepartment = computed(() => {
    const groups: Record<string, Teacher[]> = {}
    teachers.value.forEach(teacher => {
      const dept = teacher.department || '未分类'
      if (!groups[dept]) groups[dept] = []
      groups[dept].push(teacher)
    })
    return groups
  })

  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  // 操作方法
  const setTeachers = (newTeachers: Teacher[]) => {
    teachers.value = newTeachers
  }

  const setLoading = (isLoading: boolean) => {
    loading.value = isLoading
  }

  const setError = (errorMessage: string | null) => {
    error.value = errorMessage
    if (errorMessage) {
      ElMessage.error(errorMessage)
    }
  }

  const setPagination = (page: number, size: number, totalItems: number) => {
    currentPage.value = page
    pageSize.value = size
    total.value = totalItems
  }

  const resetError = () => {
    error.value = null
  }

  // API调用方法
  const fetchTeachers = async (params?: TeacherQueryParams) => {
    try {
      setLoading(true)
      resetError()

      const response = await teachersApi.getTeachers({
        page: currentPage.value,
        size: pageSize.value,
        ...params
      })

      setTeachers(response.items)
      setPagination(response.page, response.size, response.total)

      return response
    } catch (err: any) {
      setError(err.message || '获取教师列表失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const fetchTeacher = async (id: string) => {
    try {
      setLoading(true)
      resetError()

      const teacher = await teachersApi.getTeacher(id)
      currentTeacher.value = teacher

      return teacher
    } catch (err: any) {
      setError(err.message || '获取教师详情失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const createTeacher = async (data: CreateTeacherRequest) => {
    try {
      setLoading(true)
      resetError()

      const newTeacher = await teachersApi.createTeacher(data)
      teachers.value.unshift(newTeacher)
      total.value += 1

      ElMessage.success('教师创建成功')
      return newTeacher
    } catch (err: any) {
      setError(err.message || '教师创建失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const updateTeacher = async (id: string, data: UpdateTeacherRequest) => {
    try {
      setLoading(true)
      resetError()

      const updatedTeacher = await teachersApi.updateTeacher(id, data)
      const index = teachers.value.findIndex(t => t.id === id)

      if (index !== -1) {
        teachers.value[index] = updatedTeacher
      }

      if (currentTeacher.value?.id === id) {
        currentTeacher.value = updatedTeacher
      }

      ElMessage.success('教师信息更新成功')
      return updatedTeacher
    } catch (err: any) {
      setError(err.message || '教师信息更新失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const deleteTeacher = async (id: string) => {
    try {
      setLoading(true)
      resetError()

      await teachersApi.deleteTeacher(id)
      teachers.value = teachers.value.filter(t => t.id !== id)
      total.value -= 1

      ElMessage.success('教师删除成功')
    } catch (err: any) {
      setError(err.message || '教师删除失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const bulkDeleteTeachers = async (ids: string[]) => {
    try {
      setLoading(true)
      resetError()

      await teachersApi.bulkDeleteTeachers(ids)
      teachers.value = teachers.value.filter(t => !ids.includes(t.id))
      total.value -= ids.length

      ElMessage.success(`成功删除 ${ids.length} 名教师`)
    } catch (err: any) {
      setError(err.message || '批量删除失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const toggleTeacherStatus = async (id: string, isActive: boolean) => {
    try {
      setLoading(true)
      resetError()

      const updatedTeacher = await teachersApi.toggleTeacherStatus(id, isActive)
      const index = teachers.value.findIndex(t => t.id === id)

      if (index !== -1) {
        teachers.value[index] = updatedTeacher
      }

      ElMessage.success(`教师已${isActive ? '复职' : '离职'}`)
      return updatedTeacher
    } catch (err: any) {
      setError(err.message || '状态切换失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const updateTeacherPreferences = async (
    id: string,
    preferences: {
      preferred_time_slots?: string[]
      unavailable_time_slots?: string[]
      max_hours_per_week?: number
    }
  ) => {
    try {
      setLoading(true)
      resetError()

      const updatedTeacher = await teachersApi.updateTeacherPreferences(id, preferences)
      const index = teachers.value.findIndex(t => t.id === id)

      if (index !== -1) {
        teachers.value[index] = updatedTeacher
      }

      if (currentTeacher.value?.id === id) {
        currentTeacher.value = updatedTeacher
      }

      ElMessage.success('教师偏好设置更新成功')
      return updatedTeacher
    } catch (err: any) {
      setError(err.message || '偏好设置更新失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const fetchTeacherWorkload = async (schoolId: string) => {
    try {
      setLoading(true)
      resetError()

      const stats = await teachersApi.getTeacherWorkload(schoolId)
      workloadStats.value = stats

      return stats
    } catch (err: any) {
      setError(err.message || '获取工作负载统计失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const getTeacherSchedule = async (
    id: string,
    params?: {
      start_date?: string
      end_date?: string
    }
  ) => {
    try {
      setLoading(true)
      resetError()

      const schedule = await teachersApi.getTeacherSchedule(id, params)
      return schedule
    } catch (err: any) {
      setError(err.message || '获取教师课表失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const checkTeacherConflicts = async (
    id: string,
    schedule: Array<{
      start_time: string
      end_time: string
      day_of_week: number
    }>
  ) => {
    try {
      setLoading(true)
      resetError()

      const result = await teachersApi.checkTeacherConflicts(id, schedule)
      return result
    } catch (err: any) {
      setError(err.message || '检查时间冲突失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const importTeachers = async (schoolId: string, file: File) => {
    try {
      setLoading(true)
      resetError()

      const result = await teachersApi.importTeachers(schoolId, file)

      if (result.error_count === 0) {
        ElMessage.success(`成功导入 ${result.success_count} 名教师`)
      } else {
        ElMessage.warning(
          `导入完成：成功 ${result.success_count} 名，失败 ${result.error_count} 名`
        )
      }

      // 刷新列表
      await fetchTeachers()
      return result
    } catch (err: any) {
      setError(err.message || '教师数据导入失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const exportTeachers = async (params: TeacherQueryParams) => {
    try {
      setLoading(true)
      resetError()

      const blob = await teachersApi.exportTeachers(params)

      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `teachers_${new Date().toISOString().split('T')[0]}.xlsx`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      ElMessage.success('教师数据导出成功')
    } catch (err: any) {
      setError(err.message || '教师数据导出失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // 重置状态
  const resetState = () => {
    teachers.value = []
    loading.value = false
    error.value = null
    total.value = 0
    currentPage.value = 1
    pageSize.value = 20
    currentTeacher.value = null
    workloadStats.value = []
  }

  return {
    // 状态
    teachers,
    loading,
    error,
    total,
    currentPage,
    pageSize,
    currentTeacher,
    workloadStats,

    // 计算属性
    activeTeachers,
    inactiveTeachers,
    teachersByDepartment,
    totalPages,

    // 操作方法
    setTeachers,
    setLoading,
    setError,
    setPagination,
    resetError,

    // API方法
    fetchTeachers,
    fetchTeacher,
    createTeacher,
    updateTeacher,
    deleteTeacher,
    bulkDeleteTeachers,
    toggleTeacherStatus,
    updateTeacherPreferences,
    fetchTeacherWorkload,
    getTeacherSchedule,
    checkTeacherConflicts,
    importTeachers,
    exportTeachers,

    // 重置
    resetState
  }
})