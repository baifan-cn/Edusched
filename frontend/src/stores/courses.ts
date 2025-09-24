import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { coursesApi, type Course, CreateCourseRequest, UpdateCourseRequest, CourseQueryParams, type Subject } from '@/api/courses'
import type { PaginatedResponse } from '@/types'

export const useCoursesStore = defineStore('courses', () => {
  // 状态
  const courses = ref<Course[]>([])
  const currentCourse = ref<Course | null>(null)
  const subjects = ref<Subject[]>([])
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const queryParams = ref<CourseQueryParams>({})

  // 计算属性
  const hasCourses = computed(() => courses.value.length > 0)
  const courseOptions = computed(() =>
    courses.value
      .filter(course => course.is_active)
      .map(course => ({
        label: `${course.name} (${course.code})`,
        value: course.id,
        code: course.code,
        credits: course.credits,
        hours_per_week: course.hours_per_week
      }))
  )
  const subjectOptions = computed(() =>
    subjects.value
      .filter(subject => subject.is_active)
      .map(subject => ({
        label: `${subject.name} (${subject.code})`,
        value: subject.id,
        code: subject.code
      }))
  )
  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  // 统计数据
  const stats = computed(() => ({
    total: courses.value.length,
    active: courses.value.filter(course => course.is_active).length,
    inactive: courses.value.filter(course => !course.is_active).length,
    totalCredits: courses.value.reduce((sum, course) => sum + course.credits, 0),
    totalHours: courses.value.reduce((sum, course) => sum + course.total_hours, 0)
  }))

  // 动作
  const setCourses = (newCourses: Course[]) => {
    courses.value = newCourses
  }

  const setCurrentCourse = (course: Course | null) => {
    currentCourse.value = course
  }

  const setSubjects = (newSubjects: Subject[]) => {
    subjects.value = newSubjects
  }

  const setLoading = (status: boolean) => {
    loading.value = status
  }

  const setPagination = (page: number, size: number) => {
    currentPage.value = page
    pageSize.value = size
  }

  const setQueryParams = (params: CourseQueryParams) => {
    queryParams.value = { ...params }
  }

  // 获取课程列表
  const fetchCourses = async (params?: CourseQueryParams) => {
    try {
      setLoading(true)
      const mergedParams = { ...queryParams.value, ...params }
      const response = await coursesApi.getCourses(mergedParams)

      setCourses(response.items)
      total.value = response.total
      currentPage.value = response.page
      pageSize.value = response.size

      return response
    } catch (error) {
      ElMessage.error('获取课程列表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取单个课程详情
  const fetchCourse = async (id: string) => {
    try {
      setLoading(true)
      const course = await coursesApi.getCourse(id)
      setCurrentCourse(course)
      return course
    } catch (error) {
      ElMessage.error('获取课程详情失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取学科列表
  const fetchSubjects = async (params?: { name?: string; code?: string; is_active?: boolean }) => {
    try {
      setLoading(true)
      const response = await coursesApi.getSubjects(params)
      setSubjects(response)
      return response
    } catch (error) {
      ElMessage.error('获取学科列表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 创建课程
  const createCourse = async (data: CreateCourseRequest) => {
    try {
      setLoading(true)
      const newCourse = await coursesApi.createCourse(data)

      // 更新列表
      if (courses.value.length < pageSize.value) {
        courses.value.unshift(newCourse)
      } else {
        await fetchCourses()
      }

      ElMessage.success('课程创建成功')
      return newCourse
    } catch (error) {
      ElMessage.error('创建课程失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 更新课程
  const updateCourse = async (id: string, data: UpdateCourseRequest) => {
    try {
      setLoading(true)
      const updatedCourse = await coursesApi.updateCourse(id, data)

      // 更新列表中的课程
      const index = courses.value.findIndex(course => course.id === id)
      if (index !== -1) {
        courses.value[index] = updatedCourse
      }

      // 如果是当前选中的课程，也更新它
      if (currentCourse.value?.id === id) {
        setCurrentCourse(updatedCourse)
      }

      ElMessage.success('课程信息更新成功')
      return updatedCourse
    } catch (error) {
      ElMessage.error('更新课程信息失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 删除课程
  const deleteCourse = async (id: string) => {
    try {
      setLoading(true)
      await coursesApi.deleteCourse(id)

      // 从列表中移除
      courses.value = courses.value.filter(course => course.id !== id)

      // 如果删除的是当前选中的课程，清除选中
      if (currentCourse.value?.id === id) {
        setCurrentCourse(null)
      }

      // 更新总数
      total.value = Math.max(0, total.value - 1)

      ElMessage.success('课程删除成功')
    } catch (error) {
      ElMessage.error('删除课程失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 批量删除课程
  const bulkDeleteCourses = async (ids: string[]) => {
    try {
      setLoading(true)
      await coursesApi.bulkDeleteCourses(ids)

      // 从列表中移除
      courses.value = courses.value.filter(course => !ids.includes(course.id))

      // 如果删除的课程包含当前选中的课程，清除选中
      if (currentCourse.value && ids.includes(currentCourse.value.id)) {
        setCurrentCourse(null)
      }

      // 更新总数
      total.value = Math.max(0, total.value - ids.length)

      ElMessage.success(`成功删除 ${ids.length} 个课程`)
    } catch (error) {
      ElMessage.error('批量删除课程失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 切换课程状态
  const toggleCourseStatus = async (id: string, is_active: boolean) => {
    try {
      setLoading(true)
      const updatedCourse = await coursesApi.toggleCourseStatus(id, is_active)

      // 更新列表中的课程
      const index = courses.value.findIndex(course => course.id === id)
      if (index !== -1) {
        courses.value[index] = updatedCourse
      }

      // 如果是当前选中的课程，也更新它
      if (currentCourse.value?.id === id) {
        setCurrentCourse(updatedCourse)
      }

      ElMessage.success(`课程已${is_active ? '启用' : '停用'}`)
      return updatedCourse
    } catch (error) {
      ElMessage.error('切换课程状态失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取课程统计信息
  const fetchCourseStats = async () => {
    try {
      setLoading(true)
      const stats = await coursesApi.getCourseStats()
      return stats
    } catch (error) {
      ElMessage.error('获取课程统计信息失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 刷新课程列表
  const refreshCourses = async () => {
    await fetchCourses()
  }

  // 搜索课程
  const searchCourses = async (searchTerm: string) => {
    const params = { ...queryParams.value, name: searchTerm, page: 1 }
    await fetchCourses(params)
  }

  // 重置查询参数
  const resetQueryParams = () => {
    setQueryParams({})
    setPagination(1, 20)
    return fetchCourses()
  }

  // 初始化
  const init = async () => {
    await Promise.all([
      fetchCourses(),
      fetchSubjects({ is_active: true })
    ])
  }

  return {
    // 状态
    courses,
    currentCourse,
    subjects,
    loading,
    total,
    currentPage,
    pageSize,
    queryParams,
    stats,

    // 计算属性
    hasCourses,
    courseOptions,
    subjectOptions,
    totalPages,

    // 动作
    setCourses,
    setCurrentCourse,
    setSubjects,
    setLoading,
    setPagination,
    setQueryParams,
    fetchCourses,
    fetchCourse,
    fetchSubjects,
    createCourse,
    updateCourse,
    deleteCourse,
    bulkDeleteCourses,
    toggleCourseStatus,
    fetchCourseStats,
    refreshCourses,
    searchCourses,
    resetQueryParams,
    init
  }
})