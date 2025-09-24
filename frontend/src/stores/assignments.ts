import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { assignmentsApi, type Assignment, CreateAssignmentRequest, UpdateAssignmentRequest, AssignmentQueryParams } from '../api/assignments'
import type { PaginatedResponse } from '../types/index'

export const useAssignmentsStore = defineStore('assignments', () => {
  // 状态
  const assignments = ref<Assignment[]>([])
  const currentAssignment = ref<Assignment | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const queryParams = ref<AssignmentQueryParams>({})

  // 计算属性
  const hasAssignments = computed(() => assignments.value.length > 0)
  const assignmentOptions = computed(() =>
    assignments.value
      .map(assignment => ({
        label: `Assignment ${assignment.id}`,
        value: assignment.id,
        section_id: assignment.section_id,
        timeslot_id: assignment.timeslot_id,
        room_id: assignment.room_id,
        is_locked: assignment.is_locked
      }))
  )
  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  // 统计数据
  const stats = computed(() => ({
    total: assignments.value.length,
    locked: assignments.value.filter(assignment => assignment.is_locked).length,
    unlocked: assignments.value.filter(assignment => !assignment.is_locked).length,
    withNotes: assignments.value.filter(assignment => assignment.notes).length,
    byTimetable: assignments.value.reduce((acc, assignment) => {
      acc[assignment.timetable_id] = (acc[assignment.timetable_id] || 0) + 1
      return acc
    }, {} as Record<string, number>)
  }))

  // 动作
  const setAssignments = (newAssignments: Assignment[]) => {
    assignments.value = newAssignments
  }

  const setCurrentAssignment = (assignment: Assignment | null) => {
    currentAssignment.value = assignment
  }

  const setLoading = (status: boolean) => {
    loading.value = status
  }

  const setPagination = (page: number, size: number) => {
    currentPage.value = page
    pageSize.value = size
  }

  const setQueryParams = (params: AssignmentQueryParams) => {
    queryParams.value = { ...params }
  }

  // 获取分配列表
  const fetchAssignments = async (params?: AssignmentQueryParams) => {
    try {
      setLoading(true)
      const mergedParams = { ...queryParams.value, ...params }
      const response = await assignmentsApi.getAssignments(mergedParams)

      setAssignments(response.items)
      total.value = response.total
      currentPage.value = response.page
      pageSize.value = response.size

      return response
    } catch (error) {
      ElMessage.error('获取分配列表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取单个分配详情
  const fetchAssignment = async (id: string) => {
    try {
      setLoading(true)
      const assignment = await assignmentsApi.getAssignment(id)
      setCurrentAssignment(assignment)
      return assignment
    } catch (error) {
      ElMessage.error('获取分配详情失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 创建分配
  const createAssignment = async (data: CreateAssignmentRequest) => {
    try {
      setLoading(true)
      const newAssignment = await assignmentsApi.createAssignment(data)

      // 更新列表
      if (assignments.value.length < pageSize.value) {
        assignments.value.unshift(newAssignment)
      } else {
        await fetchAssignments()
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
  const updateAssignment = async (id: string, data: UpdateAssignmentRequest) => {
    try {
      setLoading(true)
      const updatedAssignment = await assignmentsApi.updateAssignment(id, data)

      // 更新列表中的分配
      const index = assignments.value.findIndex(assignment => assignment.id === id)
      if (index !== -1) {
        assignments.value[index] = updatedAssignment
      }

      // 如果是当前选中的分配，也更新它
      if (currentAssignment.value?.id === id) {
        setCurrentAssignment(updatedAssignment)
      }

      ElMessage.success('分配信息更新成功')
      return updatedAssignment
    } catch (error) {
      ElMessage.error('更新分配信息失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 删除分配
  const deleteAssignment = async (id: string) => {
    try {
      setLoading(true)
      await assignmentsApi.deleteAssignment(id)

      // 从列表中移除
      assignments.value = assignments.value.filter(assignment => assignment.id !== id)

      // 如果删除的是当前选中的分配，清除选中
      if (currentAssignment.value?.id === id) {
        setCurrentAssignment(null)
      }

      // 更新总数
      total.value = Math.max(0, total.value - 1)

      ElMessage.success('分配删除成功')
    } catch (error) {
      ElMessage.error('删除分配失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 批量删除分配
  const bulkDeleteAssignments = async (ids: string[]) => {
    try {
      setLoading(true)
      await assignmentsApi.bulkDeleteAssignments(ids)

      // 从列表中移除
      assignments.value = assignments.value.filter(assignment => !ids.includes(assignment.id))

      // 如果删除的分配包含当前选中的分配，清除选中
      if (currentAssignment.value && ids.includes(currentAssignment.value.id)) {
        setCurrentAssignment(null)
      }

      // 更新总数
      total.value = Math.max(0, total.value - ids.length)

      ElMessage.success(`成功删除 ${ids.length} 个分配`)
    } catch (error) {
      ElMessage.error('批量删除分配失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 锁定/解锁分配
  const toggleAssignmentLock = async (id: string, is_locked: boolean) => {
    try {
      setLoading(true)
      const updatedAssignment = await assignmentsApi.toggleAssignmentLock(id, is_locked)

      // 更新列表中的分配
      const index = assignments.value.findIndex(assignment => assignment.id === id)
      if (index !== -1) {
        assignments.value[index] = updatedAssignment
      }

      // 如果是当前选中的分配，也更新它
      if (currentAssignment.value?.id === id) {
        setCurrentAssignment(updatedAssignment)
      }

      ElMessage.success(`分配已${is_locked ? '锁定' : '解锁'}`)
      return updatedAssignment
    } catch (error) {
      ElMessage.error('切换分配锁定状态失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取时间表的分配列表
  const fetchTimetableAssignments = async (timetableId: string, params?: AssignmentQueryParams) => {
    try {
      setLoading(true)
      const response = await assignmentsApi.getTimetableAssignments(timetableId, params)
      return response
    } catch (error) {
      ElMessage.error('获取时间表分配列表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取教学段的分配列表
  const fetchSectionAssignments = async (sectionId: string, params?: AssignmentQueryParams) => {
    try {
      setLoading(true)
      const response = await assignmentsApi.getSectionAssignments(sectionId, params)
      return response
    } catch (error) {
      ElMessage.error('获取教学段分配列表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取教师的分配列表
  const fetchTeacherAssignments = async (teacherId: string, params?: AssignmentQueryParams) => {
    try {
      setLoading(true)
      const response = await assignmentsApi.getTeacherAssignments(teacherId, params)
      return response
    } catch (error) {
      ElMessage.error('获取教师分配列表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取教室的分配列表
  const fetchRoomAssignments = async (roomId: string, params?: AssignmentQueryParams) => {
    try {
      setLoading(true)
      const response = await assignmentsApi.getRoomAssignments(roomId, params)
      return response
    } catch (error) {
      ElMessage.error('获取教室分配列表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取时间段的分配列表
  const fetchTimeslotAssignments = async (timeslotId: string, params?: AssignmentQueryParams) => {
    try {
      setLoading(true)
      const response = await assignmentsApi.getTimeslotAssignments(timeslotId, params)
      return response
    } catch (error) {
      ElMessage.error('获取时间段分配列表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 批量创建分配
  const bulkCreateAssignments = async (assignments: CreateAssignmentRequest[]) => {
    try {
      setLoading(true)
      const newAssignments = await assignmentsApi.bulkCreateAssignments(assignments)

      // 更新列表
      await fetchAssignments()

      ElMessage.success(`成功创建 ${newAssignments.length} 个分配`)
      return newAssignments
    } catch (error) {
      ElMessage.error('批量创建分配失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 批量更新分配
  const bulkUpdateAssignments = async (updates: Array<{
    id: string
    data: UpdateAssignmentRequest
  }>) => {
    try {
      setLoading(true)
      const updatedAssignments = await assignmentsApi.bulkUpdateAssignments(updates)

      // 更新列表中的分配
      updatedAssignments.forEach(updatedAssignment => {
        const index = assignments.value.findIndex(assignment => assignment.id === updatedAssignment.id)
        if (index !== -1) {
          assignments.value[index] = updatedAssignment
        }
      })

      // 如果更新了当前选中的分配，也更新它
      if (currentAssignment.value) {
        const updatedCurrent = updatedAssignments.find(assignment => assignment.id === currentAssignment.value?.id)
        if (updatedCurrent) {
          setCurrentAssignment(updatedCurrent)
        }
      }

      ElMessage.success(`成功更新 ${updatedAssignments.length} 个分配`)
      return updatedAssignments
    } catch (error) {
      ElMessage.error('批量更新分配失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 复制分配
  const duplicateAssignment = async (id: string, data: {
    section_id?: string
    timeslot_id?: string
    room_id?: string
  }) => {
    try {
      setLoading(true)
      const newAssignment = await assignmentsApi.duplicateAssignment(id, data)

      // 更新列表
      if (assignments.value.length < pageSize.value) {
        assignments.value.unshift(newAssignment)
      } else {
        await fetchAssignments()
      }

      ElMessage.success('分配复制成功')
      return newAssignment
    } catch (error) {
      ElMessage.error('复制分配失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 移动分配到新的时间段
  const moveAssignment = async (id: string, data: {
    timeslot_id: string
    room_id?: string
    notes?: string
  }) => {
    try {
      setLoading(true)
      const updatedAssignment = await assignmentsApi.moveAssignment(id, data)

      // 更新列表中的分配
      const index = assignments.value.findIndex(assignment => assignment.id === id)
      if (index !== -1) {
        assignments.value[index] = updatedAssignment
      }

      // 如果是当前选中的分配，也更新它
      if (currentAssignment.value?.id === id) {
        setCurrentAssignment(updatedAssignment)
      }

      ElMessage.success('分配移动成功')
      return updatedAssignment
    } catch (error) {
      ElMessage.error('移动分配失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取分配统计信息
  const fetchAssignmentStats = async (params?: {
    timetable_id?: string
    teacher_id?: string
    room_id?: string
    course_id?: string
  }) => {
    try {
      setLoading(true)
      const stats = await assignmentsApi.getAssignmentStats(params)
      return stats
    } catch (error) {
      ElMessage.error('获取分配统计信息失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取分配冲突检测
  const getAssignmentConflicts = async (data: {
    section_id: string
    timeslot_id: string
    room_id: string
    exclude_assignment_id?: string
  }) => {
    try {
      setLoading(true)
      const conflicts = await assignmentsApi.getAssignmentConflicts(data)
      return conflicts
    } catch (error) {
      ElMessage.error('检测分配冲突失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取分配建议
  const getAssignmentSuggestions = async (sectionId: string, params?: {
    preferred_teacher_id?: string
    preferred_room_id?: string
    preferred_times?: string[]
  }) => {
    try {
      setLoading(true)
      const suggestions = await assignmentsApi.getAssignmentSuggestions(sectionId, params)
      return suggestions
    } catch (error) {
      ElMessage.error('获取分配建议失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 刷新分配列表
  const refreshAssignments = async () => {
    await fetchAssignments()
  }

  // 搜索分配
  const searchAssignments = async (searchTerm: string) => {
    const params = { ...queryParams.value, search: searchTerm, page: 1 }
    await fetchAssignments(params)
  }

  // 重置查询参数
  const resetQueryParams = () => {
    setQueryParams({})
    setPagination(1, 20)
    return fetchAssignments()
  }

  // 初始化
  const init = async () => {
    await fetchAssignments()
  }

  return {
    // 状态
    assignments,
    currentAssignment,
    loading,
    total,
    currentPage,
    pageSize,
    queryParams,
    stats,

    // 计算属性
    hasAssignments,
    assignmentOptions,
    totalPages,

    // 动作
    setAssignments,
    setCurrentAssignment,
    setLoading,
    setPagination,
    setQueryParams,
    fetchAssignments,
    fetchAssignment,
    createAssignment,
    updateAssignment,
    deleteAssignment,
    bulkDeleteAssignments,
    toggleAssignmentLock,
    fetchTimetableAssignments,
    fetchSectionAssignments,
    fetchTeacherAssignments,
    fetchRoomAssignments,
    fetchTimeslotAssignments,
    bulkCreateAssignments,
    bulkUpdateAssignments,
    duplicateAssignment,
    moveAssignment,
    fetchAssignmentStats,
    getAssignmentConflicts,
    getAssignmentSuggestions,
    refreshAssignments,
    searchAssignments,
    resetQueryParams,
    init
  }
})