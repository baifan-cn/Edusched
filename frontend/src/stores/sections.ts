import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { sectionsApi, type Section, CreateSectionRequest, UpdateSectionRequest, SectionQueryParams } from '../api/sections'
import type { PaginatedResponse } from '../types/index'

export const useSectionsStore = defineStore('sections', () => {
  // 状态
  const sections = ref<Section[]>([])
  const currentSection = ref<Section | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const queryParams = ref<SectionQueryParams>({})

  // 计算属性
  const hasSections = computed(() => sections.value.length > 0)
  const sectionOptions = computed(() =>
    sections.value
      .filter(section => section.is_active)
      .map(section => ({
        label: `${section.name} (${section.code})`,
        value: section.id,
        code: section.code,
        course_id: section.course_id,
        teacher_id: section.teacher_id,
        class_group_id: section.class_group_id,
        hours_per_week: section.hours_per_week,
        period_type: section.period_type
      }))
  )
  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  // 统计数据
  const stats = computed(() => ({
    total: sections.value.length,
    active: sections.value.filter(section => section.is_active).length,
    inactive: sections.value.filter(section => !section.is_active).length,
    locked: sections.value.filter(section => section.is_locked).length,
    unlocked: sections.value.filter(section => !section.is_locked).length,
    totalHours: sections.value.reduce((sum, section) => sum + section.hours_per_week, 0),
    regularSections: sections.value.filter(section => section.period_type === 'regular').length,
    labSections: sections.value.filter(section => section.period_type === 'lab').length
  }))

  // 动作
  const setSections = (newSections: Section[]) => {
    sections.value = newSections
  }

  const setCurrentSection = (section: Section | null) => {
    currentSection.value = section
  }

  const setLoading = (status: boolean) => {
    loading.value = status
  }

  const setPagination = (page: number, size: number) => {
    currentPage.value = page
    pageSize.value = size
  }

  const setQueryParams = (params: SectionQueryParams) => {
    queryParams.value = { ...params }
  }

  // 获取教学段列表
  const fetchSections = async (params?: SectionQueryParams) => {
    try {
      setLoading(true)
      const mergedParams = { ...queryParams.value, ...params }
      const response = await sectionsApi.getSections(mergedParams)

      setSections(response.items)
      total.value = response.total
      currentPage.value = response.page
      pageSize.value = response.size

      return response
    } catch (error) {
      ElMessage.error('获取教学段列表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取单个教学段详情
  const fetchSection = async (id: string) => {
    try {
      setLoading(true)
      const section = await sectionsApi.getSection(id)
      setCurrentSection(section)
      return section
    } catch (error) {
      ElMessage.error('获取教学段详情失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 创建教学段
  const createSection = async (data: CreateSectionRequest) => {
    try {
      setLoading(true)
      const newSection = await sectionsApi.createSection(data)

      // 更新列表
      if (sections.value.length < pageSize.value) {
        sections.value.unshift(newSection)
      } else {
        await fetchSections()
      }

      ElMessage.success('教学段创建成功')
      return newSection
    } catch (error) {
      ElMessage.error('创建教学段失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 更新教学段
  const updateSection = async (id: string, data: UpdateSectionRequest) => {
    try {
      setLoading(true)
      const updatedSection = await sectionsApi.updateSection(id, data)

      // 更新列表中的教学段
      const index = sections.value.findIndex(section => section.id === id)
      if (index !== -1) {
        sections.value[index] = updatedSection
      }

      // 如果是当前选中的教学段，也更新它
      if (currentSection.value?.id === id) {
        setCurrentSection(updatedSection)
      }

      ElMessage.success('教学段信息更新成功')
      return updatedSection
    } catch (error) {
      ElMessage.error('更新教学段信息失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 删除教学段
  const deleteSection = async (id: string) => {
    try {
      setLoading(true)
      await sectionsApi.deleteSection(id)

      // 从列表中移除
      sections.value = sections.value.filter(section => section.id !== id)

      // 如果删除的是当前选中的教学段，清除选中
      if (currentSection.value?.id === id) {
        setCurrentSection(null)
      }

      // 更新总数
      total.value = Math.max(0, total.value - 1)

      ElMessage.success('教学段删除成功')
    } catch (error) {
      ElMessage.error('删除教学段失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 批量删除教学段
  const bulkDeleteSections = async (ids: string[]) => {
    try {
      setLoading(true)
      await sectionsApi.bulkDeleteSections(ids)

      // 从列表中移除
      sections.value = sections.value.filter(section => !ids.includes(section.id))

      // 如果删除的教学段包含当前选中的教学段，清除选中
      if (currentSection.value && ids.includes(currentSection.value.id)) {
        setCurrentSection(null)
      }

      // 更新总数
      total.value = Math.max(0, total.value - ids.length)

      ElMessage.success(`成功删除 ${ids.length} 个教学段`)
    } catch (error) {
      ElMessage.error('批量删除教学段失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 切换教学段状态
  const toggleSectionStatus = async (id: string, is_active: boolean) => {
    try {
      setLoading(true)
      const updatedSection = await sectionsApi.toggleSectionStatus(id, is_active)

      // 更新列表中的教学段
      const index = sections.value.findIndex(section => section.id === id)
      if (index !== -1) {
        sections.value[index] = updatedSection
      }

      // 如果是当前选中的教学段，也更新它
      if (currentSection.value?.id === id) {
        setCurrentSection(updatedSection)
      }

      ElMessage.success(`教学段已${is_active ? '启用' : '停用'}`)
      return updatedSection
    } catch (error) {
      ElMessage.error('切换教学段状态失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 切换教学段锁定状态
  const toggleSectionLock = async (id: string, is_locked: boolean) => {
    try {
      setLoading(true)
      const updatedSection = await sectionsApi.toggleSectionLock(id, is_locked)

      // 更新列表中的教学段
      const index = sections.value.findIndex(section => section.id === id)
      if (index !== -1) {
        sections.value[index] = updatedSection
      }

      // 如果是当前选中的教学段，也更新它
      if (currentSection.value?.id === id) {
        setCurrentSection(updatedSection)
      }

      ElMessage.success(`教学段已${is_locked ? '锁定' : '解锁'}`)
      return updatedSection
    } catch (error) {
      ElMessage.error('切换教学段锁定状态失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取教学段统计信息
  const fetchSectionStats = async (params?: {
    course_id?: string
    teacher_id?: string
    class_group_id?: string
  }) => {
    try {
      setLoading(true)
      const stats = await sectionsApi.getSectionStats(params)
      return stats
    } catch (error) {
      ElMessage.error('获取教学段统计信息失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取课程的教学段列表
  const fetchCourseSections = async (courseId: string, params?: SectionQueryParams) => {
    try {
      setLoading(true)
      const response = await sectionsApi.getCourseSections(courseId, params)
      return response
    } catch (error) {
      ElMessage.error('获取课程教学段列表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取教师的教学段列表
  const fetchTeacherSections = async (teacherId: string, params?: SectionQueryParams) => {
    try {
      setLoading(true)
      const response = await sectionsApi.getTeacherSections(teacherId, params)
      return response
    } catch (error) {
      ElMessage.error('获取教师教学段列表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取班级的教学段列表
  const fetchClassGroupSections = async (classGroupId: string, params?: SectionQueryParams) => {
    try {
      setLoading(true)
      const response = await sectionsApi.getClassGroupSections(classGroupId, params)
      return response
    } catch (error) {
      ElMessage.error('获取班级教学段列表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 复制教学段
  const duplicateSection = async (id: string, data: {
    name: string
    code: string
    copy_assignments?: boolean
  }) => {
    try {
      setLoading(true)
      const newSection = await sectionsApi.duplicateSection(id, data)

      // 更新列表
      if (sections.value.length < pageSize.value) {
        sections.value.unshift(newSection)
      } else {
        await fetchSections()
      }

      ElMessage.success('教学段复制成功')
      return newSection
    } catch (error) {
      ElMessage.error('复制教学段失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 批量更新教学段
  const bulkUpdateSections = async (updates: Array<{
    id: string
    data: UpdateSectionRequest
  }>) => {
    try {
      setLoading(true)
      const updatedSections = await sectionsApi.bulkUpdateSections(updates)

      // 更新列表中的教学段
      updatedSections.forEach(updatedSection => {
        const index = sections.value.findIndex(section => section.id === updatedSection.id)
        if (index !== -1) {
          sections.value[index] = updatedSection
        }
      })

      // 如果更新了当前选中的教学段，也更新它
      if (currentSection.value) {
        const updatedCurrent = updatedSections.find(section => section.id === currentSection.value?.id)
        if (updatedCurrent) {
          setCurrentSection(updatedCurrent)
        }
      }

      ElMessage.success(`成功更新 ${updatedSections.length} 个教学段`)
      return updatedSections
    } catch (error) {
      ElMessage.error('批量更新教学段失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 刷新教学段列表
  const refreshSections = async () => {
    await fetchSections()
  }

  // 搜索教学段
  const searchSections = async (searchTerm: string) => {
    const params = { ...queryParams.value, name: searchTerm, page: 1 }
    await fetchSections(params)
  }

  // 重置查询参数
  const resetQueryParams = () => {
    setQueryParams({})
    setPagination(1, 20)
    return fetchSections()
  }

  // 初始化
  const init = async () => {
    await fetchSections()
  }

  return {
    // 状态
    sections,
    currentSection,
    loading,
    total,
    currentPage,
    pageSize,
    queryParams,
    stats,

    // 计算属性
    hasSections,
    sectionOptions,
    totalPages,

    // 动作
    setSections,
    setCurrentSection,
    setLoading,
    setPagination,
    setQueryParams,
    fetchSections,
    fetchSection,
    createSection,
    updateSection,
    deleteSection,
    bulkDeleteSections,
    toggleSectionStatus,
    toggleSectionLock,
    fetchSectionStats,
    fetchCourseSections,
    fetchTeacherSections,
    fetchClassGroupSections,
    duplicateSection,
    bulkUpdateSections,
    refreshSections,
    searchSections,
    resetQueryParams,
    init
  }
})