import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { subjectsApi } from '@/api/subjects'
import type { Subject, CreateSubjectRequest, UpdateSubjectRequest, SubjectQueryParams } from '@/types'

export const useSubjectsStore = defineStore('subjects', () => {
  // 状态
  const subjects = ref<Subject[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const currentSubject = ref<Subject | null>(null)
  const activeSubjects = ref<Subject[]>([])

  // 计算属性
  const activeSubjectsList = computed(() => subjects.value.filter(s => s.is_active))
  const inactiveSubjectsList = computed(() => subjects.value.filter(s => !s.is_active))

  const subjectsOptions = computed(() =>
    subjects.value.map(subject => ({
      label: subject.name,
      value: subject.id,
      disabled: !subject.is_active
    }))
  )

  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  // 操作方法
  const setSubjects = (newSubjects: Subject[]) => {
    subjects.value = newSubjects
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
  const fetchSubjects = async (params?: SubjectQueryParams) => {
    try {
      setLoading(true)
      resetError()

      const response = await subjectsApi.getSubjects({
        page: currentPage.value,
        size: pageSize.value,
        ...params
      })

      setSubjects(response.items)
      setPagination(response.page, response.size, response.total)

      return response
    } catch (err: any) {
      setError(err.message || '获取学科列表失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const fetchSubject = async (id: string) => {
    try {
      setLoading(true)
      resetError()

      const subject = await subjectsApi.getSubject(id)
      currentSubject.value = subject

      return subject
    } catch (err: any) {
      setError(err.message || '获取学科详情失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const createSubject = async (data: CreateSubjectRequest) => {
    try {
      setLoading(true)
      resetError()

      const newSubject = await subjectsApi.createSubject(data)
      subjects.value.unshift(newSubject)
      total.value += 1

      ElMessage.success('学科创建成功')
      return newSubject
    } catch (err: any) {
      setError(err.message || '学科创建失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const updateSubject = async (id: string, data: UpdateSubjectRequest) => {
    try {
      setLoading(true)
      resetError()

      const updatedSubject = await subjectsApi.updateSubject(id, data)
      const index = subjects.value.findIndex(s => s.id === id)

      if (index !== -1) {
        subjects.value[index] = updatedSubject
      }

      if (currentSubject.value?.id === id) {
        currentSubject.value = updatedSubject
      }

      ElMessage.success('学科信息更新成功')
      return updatedSubject
    } catch (err: any) {
      setError(err.message || '学科信息更新失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const deleteSubject = async (id: string) => {
    try {
      setLoading(true)
      resetError()

      await subjectsApi.deleteSubject(id)
      subjects.value = subjects.value.filter(s => s.id !== id)
      total.value -= 1

      ElMessage.success('学科删除成功')
    } catch (err: any) {
      setError(err.message || '学科删除失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const bulkDeleteSubjects = async (ids: string[]) => {
    try {
      setLoading(true)
      resetError()

      await subjectsApi.bulkDeleteSubjects(ids)
      subjects.value = subjects.value.filter(s => !ids.includes(s.id))
      total.value -= ids.length

      ElMessage.success(`成功删除 ${ids.length} 个学科`)
    } catch (err: any) {
      setError(err.message || '批量删除失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const toggleSubjectStatus = async (id: string, isActive: boolean) => {
    try {
      setLoading(true)
      resetError()

      const updatedSubject = await subjectsApi.toggleSubjectStatus(id, isActive)
      const index = subjects.value.findIndex(s => s.id === id)

      if (index !== -1) {
        subjects.value[index] = updatedSubject
      }

      ElMessage.success(`学科已${isActive ? '激活' : '停用'}`)
      return updatedSubject
    } catch (err: any) {
      setError(err.message || '状态切换失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const fetchActiveSubjects = async () => {
    try {
      setLoading(true)
      resetError()

      const subjectsList = await subjectsApi.getActiveSubjects()
      activeSubjects.value = subjectsList

      return subjectsList
    } catch (err: any) {
      setError(err.message || '获取活跃学科失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const checkSubjectCode = async (code: string, excludeId?: string) => {
    try {
      setLoading(true)
      resetError()

      const result = await subjectsApi.checkSubjectCode(code, excludeId)
      return result
    } catch (err: any) {
      setError(err.message || '检查学科代码失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const getSubjectStats = async () => {
    try {
      setLoading(true)
      resetError()

      const stats = await subjectsApi.getSubjectStats()
      return stats
    } catch (err: any) {
      setError(err.message || '获取学科统计失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const importSubjects = async (file: File) => {
    try {
      setLoading(true)
      resetError()

      const result = await subjectsApi.importSubjects(file)

      if (result.error_count === 0) {
        ElMessage.success(`成功导入 ${result.success_count} 个学科`)
      } else {
        ElMessage.warning(
          `导入完成：成功 ${result.success_count} 个，失败 ${result.error_count} 个`
        )
      }

      // 刷新列表
      await fetchSubjects()
      return result
    } catch (err: any) {
      setError(err.message || '学科数据导入失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const exportSubjects = async (params?: SubjectQueryParams) => {
    try {
      setLoading(true)
      resetError()

      const blob = await subjectsApi.exportSubjects(params)

      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `subjects_${new Date().toISOString().split('T')[0]}.xlsx`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      ElMessage.success('学科数据导出成功')
    } catch (err: any) {
      setError(err.message || '学科数据导出失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // 工具方法
  const getSubjectById = (id: string): Subject | undefined => {
    return subjects.value.find(s => s.id === id)
  }

  const getSubjectName = (id: string): string => {
    const subject = getSubjectById(id)
    return subject?.name || '未知学科'
  }

  const getSubjectCode = (id: string): string => {
    const subject = getSubjectById(id)
    return subject?.code || ''
  }

  // 重置状态
  const resetState = () => {
    subjects.value = []
    loading.value = false
    error.value = null
    total.value = 0
    currentPage.value = 1
    pageSize.value = 20
    currentSubject.value = null
    activeSubjects.value = []
  }

  return {
    // 状态
    subjects,
    loading,
    error,
    total,
    currentPage,
    pageSize,
    currentSubject,
    activeSubjects,

    // 计算属性
    activeSubjectsList,
    inactiveSubjectsList,
    subjectsOptions,
    totalPages,

    // 操作方法
    setSubjects,
    setLoading,
    setError,
    setPagination,
    resetError,

    // API方法
    fetchSubjects,
    fetchSubject,
    createSubject,
    updateSubject,
    deleteSubject,
    bulkDeleteSubjects,
    toggleSubjectStatus,
    fetchActiveSubjects,
    checkSubjectCode,
    getSubjectStats,
    importSubjects,
    exportSubjects,

    // 工具方法
    getSubjectById,
    getSubjectName,
    getSubjectCode,

    // 重置
    resetState
  }
})