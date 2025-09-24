import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { timetablesApi } from '@/api/timetables'
import type {
  Timetable,
  CreateTimetableRequest,
  UpdateTimetableRequest,
  TimetableQueryParams,
  Assignment,
  CreateAssignmentRequest,
  UpdateAssignmentRequest,
  TimetableGridData,
  TimetableStats,
  TimetableConflict,
  TimetableExportOptions,
  TimetableBulkActionRequest,
  TimetableDuplicateRequest,
  PublishTimetableRequest
} from '@/types/timetables'
import type { PaginatedResponse } from '@/types'

export const useTimetablesStore = defineStore('timetables', () => {
  // 状态
  const timetables = ref<Timetable[]>([])
  const currentTimetable = ref<Timetable | null>(null)
  const timetableGrid = ref<TimetableGridData | null>(null)
  const timetableStats = ref<TimetableStats | null>(null)
  const timetableConflicts = ref<TimetableConflict[]>([])
  const assignments = ref<Assignment[]>([])
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const queryParams = ref<TimetableQueryParams>({})

  // 计算属性
  const hasTimetables = computed(() => timetables.value.length > 0)
  const timetableOptions = computed(() =>
    timetables.value.map(timetable => ({
      label: timetable.name,
      value: timetable.id,
      status: timetable.status,
      calendar_name: timetable.calendar_id,
      assignment_count: timetable.assignments_count
    }))
  )
  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))
  const hasConflicts = computed(() => timetableConflicts.value.length > 0)
  const conflictCount = computed(() => timetableConflicts.value.length)
  const publishedTimetables = computed(() =>
    timetables.value.filter(t => t.status === 'published')
  )
  const draftTimetables = computed(() =>
    timetables.value.filter(t => t.status === 'draft')
  )

  // 动作
  const setTimetables = (newTimetables: Timetable[]) => {
    timetables.value = newTimetables
  }

  const setCurrentTimetable = (timetable: Timetable | null) => {
    currentTimetable.value = timetable
  }

  const setTimetableGrid = (grid: TimetableGridData | null) => {
    timetableGrid.value = grid
  }

  const setTimetableStats = (stats: TimetableStats | null) => {
    timetableStats.value = stats
  }

  const setTimetableConflicts = (conflicts: TimetableConflict[]) => {
    timetableConflicts.value = conflicts
  }

  const setAssignments = (newAssignments: Assignment[]) => {
    assignments.value = newAssignments
  }

  const setLoading = (status: boolean) => {
    loading.value = status
  }

  const setPagination = (page: number, size: number) => {
    currentPage.value = page
    pageSize.value = size
  }

  const setQueryParams = (params: TimetableQueryParams) => {
    queryParams.value = { ...params }
  }

  // 获取时间表列表
  const fetchTimetables = async (params?: TimetableQueryParams) => {
    try {
      setLoading(true)
      const mergedParams = { ...queryParams.value, ...params }
      const response = await timetablesApi.getTimetables(mergedParams)

      setTimetables(response.items)
      total.value = response.total
      currentPage.value = response.page
      pageSize.value = response.size

      return response
    } catch (error) {
      ElMessage.error('获取时间表列表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取单个时间表详情
  const fetchTimetable = async (id: string) => {
    try {
      setLoading(true)
      const timetable = await timetablesApi.getTimetable(id)
      setCurrentTimetable(timetable)
      return timetable
    } catch (error) {
      ElMessage.error('获取时间表详情失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 创建时间表
  const createTimetable = async (data: CreateTimetableRequest) => {
    try {
      setLoading(true)
      const newTimetable = await timetablesApi.createTimetable(data)

      // 更新列表
      if (timetables.value.length < pageSize.value) {
        timetables.value.unshift(newTimetable)
      } else {
        await fetchTimetables()
      }

      ElMessage.success('时间表创建成功')
      return newTimetable
    } catch (error) {
      ElMessage.error('创建时间表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 更新时间表
  const updateTimetable = async (id: string, data: UpdateTimetableRequest) => {
    try {
      setLoading(true)
      const updatedTimetable = await timetablesApi.updateTimetable(id, data)

      // 更新列表中的时间表
      const index = timetables.value.findIndex(t => t.id === id)
      if (index !== -1) {
        timetables.value[index] = updatedTimetable
      }

      // 如果是当前选中的时间表，也更新它
      if (currentTimetable.value?.id === id) {
        setCurrentTimetable(updatedTimetable)
      }

      ElMessage.success('时间表信息更新成功')
      return updatedTimetable
    } catch (error) {
      ElMessage.error('更新时间表信息失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 删除时间表
  const deleteTimetable = async (id: string) => {
    try {
      setLoading(true)
      await timetablesApi.deleteTimetable(id)

      // 从列表中移除
      timetables.value = timetables.value.filter(t => t.id !== id)

      // 如果删除的是当前选中的时间表，清除选中
      if (currentTimetable.value?.id === id) {
        setCurrentTimetable(null)
      }

      // 更新总数
      total.value = Math.max(0, total.value - 1)

      ElMessage.success('时间表删除成功')
    } catch (error) {
      ElMessage.error('删除时间表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 批量删除时间表
  const bulkDeleteTimetables = async (ids: string[]) => {
    try {
      setLoading(true)
      await timetablesApi.bulkDeleteTimetables(ids)

      // 从列表中移除
      timetables.value = timetables.value.filter(t => !ids.includes(t.id))

      // 如果删除的时间表包含当前选中的时间表，清除选中
      if (currentTimetable.value && ids.includes(currentTimetable.value.id)) {
        setCurrentTimetable(null)
      }

      // 更新总数
      total.value = Math.max(0, total.value - ids.length)

      ElMessage.success(`成功删除 ${ids.length} 个时间表`)
    } catch (error) {
      ElMessage.error('批量删除时间表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 发布时间表
  const publishTimetable = async (id: string, data?: PublishTimetableRequest) => {
    try {
      setLoading(true)
      const publishedTimetable = await timetablesApi.publishTimetable(id, data)

      // 更新列表中的时间表
      const index = timetables.value.findIndex(t => t.id === id)
      if (index !== -1) {
        timetables.value[index] = publishedTimetable
      }

      // 如果是当前选中的时间表，也更新它
      if (currentTimetable.value?.id === id) {
        setCurrentTimetable(publishedTimetable)
      }

      ElMessage.success('时间表发布成功')
      return publishedTimetable
    } catch (error) {
      ElMessage.error('发布时间表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 取消发布时间表
  const unpublishTimetable = async (id: string) => {
    try {
      setLoading(true)
      const unpublishedTimetable = await timetablesApi.unpublishTimetable(id)

      // 更新列表中的时间表
      const index = timetables.value.findIndex(t => t.id === id)
      if (index !== -1) {
        timetables.value[index] = unpublishedTimetable
      }

      // 如果是当前选中的时间表，也更新它
      if (currentTimetable.value?.id === id) {
        setCurrentTimetable(unpublishedTimetable)
      }

      ElMessage.success('时间表取消发布成功')
      return unpublishedTimetable
    } catch (error) {
      ElMessage.error('取消发布时间表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 复制时间表
  const duplicateTimetable = async (data: TimetableDuplicateRequest) => {
    try {
      setLoading(true)
      const duplicatedTimetable = await timetablesApi.duplicateTimetable(data)

      // 更新列表
      if (timetables.value.length < pageSize.value) {
        timetables.value.unshift(duplicatedTimetable)
      } else {
        await fetchTimetables()
      }

      ElMessage.success('时间表复制成功')
      return duplicatedTimetable
    } catch (error) {
      ElMessage.error('复制时间表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取时间表网格数据
  const fetchTimetableGrid = async (timetableId: string) => {
    try {
      setLoading(true)
      const grid = await timetablesApi.getTimetableGrid(timetableId)
      setTimetableGrid(grid)
      return grid
    } catch (error) {
      ElMessage.error('获取时间表网格数据失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取时间表统计信息
  const fetchTimetableStats = async (timetableId: string) => {
    try {
      setLoading(true)
      const stats = await timetablesApi.getTimetableStats(timetableId)
      setTimetableStats(stats)
      return stats
    } catch (error) {
      ElMessage.error('获取时间表统计信息失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取时间表冲突
  const fetchTimetableConflicts = async (timetableId: string) => {
    try {
      setLoading(true)
      const conflicts = await timetablesApi.getTimetableConflicts(timetableId)
      setTimetableConflicts(conflicts)
      return conflicts
    } catch (error) {
      ElMessage.error('获取时间表冲突失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取时间表分配列表
  const fetchTimetableAssignments = async (
    timetableId: string,
    params?: any
  ) => {
    try {
      setLoading(true)
      const response = await timetablesApi.getTimetableAssignments(timetableId, params)
      setAssignments(response.items)
      return response
    } catch (error) {
      ElMessage.error('获取时间表分配列表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 创建分配
  const createAssignment = async (timetableId: string, data: CreateAssignmentRequest) => {
    try {
      setLoading(true)
      const newAssignment = await timetablesApi.createAssignment(timetableId, data)

      // 更新列表
      assignments.value.unshift(newAssignment)

      // 刷新网格数据
      if (currentTimetable.value?.id === timetableId) {
        await fetchTimetableGrid(timetableId)
      }

      ElMessage.success('分配创建成功')
      return newAssignment
    } catch (error) {
      ElMessage.error('创建分配失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 更新分配
  const updateAssignment = async (
    timetableId: string,
    assignmentId: string,
    data: UpdateAssignmentRequest
  ) => {
    try {
      setLoading(true)
      const updatedAssignment = await timetablesApi.updateAssignment(
        timetableId,
        assignmentId,
        data
      )

      // 更新列表中的分配
      const index = assignments.value.findIndex(a => a.id === assignmentId)
      if (index !== -1) {
        assignments.value[index] = updatedAssignment
      }

      // 刷新网格数据
      if (currentTimetable.value?.id === timetableId) {
        await fetchTimetableGrid(timetableId)
      }

      ElMessage.success('分配更新成功')
      return updatedAssignment
    } catch (error) {
      ElMessage.error('更新分配失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 删除分配
  const deleteAssignment = async (timetableId: string, assignmentId: string) => {
    try {
      setLoading(true)
      await timetablesApi.deleteAssignment(timetableId, assignmentId)

      // 从列表中移除
      assignments.value = assignments.value.filter(a => a.id !== assignmentId)

      // 刷新网格数据
      if (currentTimetable.value?.id === timetableId) {
        await fetchTimetableGrid(timetableId)
      }

      ElMessage.success('分配删除成功')
    } catch (error) {
      ElMessage.error('删除分配失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 导出时间表
  const exportTimetable = async (timetableId: string, options: TimetableExportOptions) => {
    try {
      setLoading(true)
      const blob = await timetablesApi.exportTimetable(timetableId, options)

      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `timetable-${timetableId}.${options.format}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      ElMessage.success('时间表导出成功')
    } catch (error) {
      ElMessage.error('导出时间表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 导入时间表
  const importTimetable = async (file: File, calendarId: string) => {
    try {
      setLoading(true)
      const importedTimetable = await timetablesApi.importTimetable(file, calendarId)

      // 更新列表
      if (timetables.value.length < pageSize.value) {
        timetables.value.unshift(importedTimetable)
      } else {
        await fetchTimetables()
      }

      ElMessage.success('时间表导入成功')
      return importedTimetable
    } catch (error) {
      ElMessage.error('导入时间表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 批量操作时间表
  const bulkActionTimetables = async (data: TimetableBulkActionRequest) => {
    try {
      setLoading(true)
      const result = await timetablesApi.bulkActionTimetables(data)

      // 刷新列表
      await fetchTimetables()

      ElMessage.success(`批量操作成功，影响了 ${result.affected_count} 个时间表`)
      return result
    } catch (error) {
      ElMessage.error('批量操作失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 刷新时间表列表
  const refreshTimetables = async () => {
    await fetchTimetables()
  }

  // 搜索时间表
  const searchTimetables = async (searchTerm: string) => {
    const params = { ...queryParams.value, name: searchTerm, page: 1 }
    await fetchTimetables(params)
  }

  // 重置查询参数
  const resetQueryParams = () => {
    setQueryParams({})
    setPagination(1, 20)
    return fetchTimetables()
  }

  // 初始化
  const init = async () => {
    await fetchTimetables()
  }

  return {
    // 状态
    timetables,
    currentTimetable,
    timetableGrid,
    timetableStats,
    timetableConflicts,
    assignments,
    loading,
    total,
    currentPage,
    pageSize,
    queryParams,

    // 计算属性
    hasTimetables,
    timetableOptions,
    totalPages,
    hasConflicts,
    conflictCount,
    publishedTimetables,
    draftTimetables,

    // 动作
    setTimetables,
    setCurrentTimetable,
    setTimetableGrid,
    setTimetableStats,
    setTimetableConflicts,
    setAssignments,
    setLoading,
    setPagination,
    setQueryParams,
    fetchTimetables,
    fetchTimetable,
    createTimetable,
    updateTimetable,
    deleteTimetable,
    bulkDeleteTimetables,
    publishTimetable,
    unpublishTimetable,
    duplicateTimetable,
    fetchTimetableGrid,
    fetchTimetableStats,
    fetchTimetableConflicts,
    fetchTimetableAssignments,
    createAssignment,
    updateAssignment,
    deleteAssignment,
    exportTimetable,
    importTimetable,
    bulkActionTimetables,
    refreshTimetables,
    searchTimetables,
    resetQueryParams,
    init
  }
})