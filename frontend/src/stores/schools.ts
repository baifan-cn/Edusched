import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { schoolsApi, type School, CreateSchoolRequest, UpdateSchoolRequest, SchoolQueryParams } from '@/api/schools'
import type { PaginatedResponse } from '@/types'

export const useSchoolsStore = defineStore('schools', () => {
  // 状态
  const schools = ref<School[]>([])
  const currentSchool = ref<School | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const queryParams = ref<SchoolQueryParams>({})

  // 计算属性
  const hasSchools = computed(() => schools.value.length > 0)
  const schoolOptions = computed(() =>
    schools.value
      .filter(school => school.is_active)
      .map(school => ({
        label: school.name,
        value: school.id,
        code: school.code
      }))
  )
  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  // 动作
  const setSchools = (newSchools: School[]) => {
    schools.value = newSchools
  }

  const setCurrentSchool = (school: School | null) => {
    currentSchool.value = school
  }

  const setLoading = (status: boolean) => {
    loading.value = status
  }

  const setPagination = (page: number, size: number) => {
    currentPage.value = page
    pageSize.value = size
  }

  const setQueryParams = (params: SchoolQueryParams) => {
    queryParams.value = { ...params }
  }

  // 获取学校列表
  const fetchSchools = async (params?: SchoolQueryParams) => {
    try {
      setLoading(true)
      const mergedParams = { ...queryParams.value, ...params }
      const response = await schoolsApi.getSchools(mergedParams)

      setSchools(response.items)
      total.value = response.total
      currentPage.value = response.page
      pageSize.value = response.size

      return response
    } catch (error) {
      ElMessage.error('获取学校列表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取单个学校详情
  const fetchSchool = async (id: string) => {
    try {
      setLoading(true)
      const school = await schoolsApi.getSchool(id)
      setCurrentSchool(school)
      return school
    } catch (error) {
      ElMessage.error('获取学校详情失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 创建学校
  const createSchool = async (data: CreateSchoolRequest) => {
    try {
      setLoading(true)
      const newSchool = await schoolsApi.createSchool(data)

      // 更新列表
      if (schools.value.length < pageSize.value) {
        schools.value.unshift(newSchool)
      } else {
        await fetchSchools()
      }

      ElMessage.success('学校创建成功')
      return newSchool
    } catch (error) {
      ElMessage.error('创建学校失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 更新学校
  const updateSchool = async (id: string, data: UpdateSchoolRequest) => {
    try {
      setLoading(true)
      const updatedSchool = await schoolsApi.updateSchool(id, data)

      // 更新列表中的学校
      const index = schools.value.findIndex(school => school.id === id)
      if (index !== -1) {
        schools.value[index] = updatedSchool
      }

      // 如果是当前选中的学校，也更新它
      if (currentSchool.value?.id === id) {
        setCurrentSchool(updatedSchool)
      }

      ElMessage.success('学校信息更新成功')
      return updatedSchool
    } catch (error) {
      ElMessage.error('更新学校信息失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 删除学校
  const deleteSchool = async (id: string) => {
    try {
      setLoading(true)
      await schoolsApi.deleteSchool(id)

      // 从列表中移除
      schools.value = schools.value.filter(school => school.id !== id)

      // 如果删除的是当前选中的学校，清除选中
      if (currentSchool.value?.id === id) {
        setCurrentSchool(null)
      }

      // 更新总数
      total.value = Math.max(0, total.value - 1)

      ElMessage.success('学校删除成功')
    } catch (error) {
      ElMessage.error('删除学校失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 批量删除学校
  const bulkDeleteSchools = async (ids: string[]) => {
    try {
      setLoading(true)
      await schoolsApi.bulkDeleteSchools(ids)

      // 从列表中移除
      schools.value = schools.value.filter(school => !ids.includes(school.id))

      // 如果删除的学校包含当前选中的学校，清除选中
      if (currentSchool.value && ids.includes(currentSchool.value.id)) {
        setCurrentSchool(null)
      }

      // 更新总数
      total.value = Math.max(0, total.value - ids.length)

      ElMessage.success(`成功删除 ${ids.length} 个学校`)
    } catch (error) {
      ElMessage.error('批量删除学校失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 切换学校状态
  const toggleSchoolStatus = async (id: string, is_active: boolean) => {
    try {
      setLoading(true)
      const updatedSchool = await schoolsApi.toggleSchoolStatus(id, is_active)

      // 更新列表中的学校
      const index = schools.value.findIndex(school => school.id === id)
      if (index !== -1) {
        schools.value[index] = updatedSchool
      }

      // 如果是当前选中的学校，也更新它
      if (currentSchool.value?.id === id) {
        setCurrentSchool(updatedSchool)
      }

      ElMessage.success(`学校已${is_active ? '启用' : '停用'}`)
      return updatedSchool
    } catch (error) {
      ElMessage.error('切换学校状态失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 上传学校logo
  const uploadSchoolLogo = async (id: string, file: File) => {
    try {
      setLoading(true)
      const response = await schoolsApi.uploadSchoolLogo(id, file)

      // 更新列表中的学校
      const index = schools.value.findIndex(school => school.id === id)
      if (index !== -1) {
        schools.value[index].logo_url = response.logo_url
      }

      // 如果是当前选中的学校，也更新它
      if (currentSchool.value?.id === id) {
        setCurrentSchool({
          ...currentSchool.value,
          logo_url: response.logo_url
        })
      }

      ElMessage.success('Logo上传成功')
      return response
    } catch (error) {
      ElMessage.error('上传Logo失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取学校统计信息
  const fetchSchoolStats = async (id: string) => {
    try {
      setLoading(true)
      const stats = await schoolsApi.getSchoolStats(id)
      return stats
    } catch (error) {
      ElMessage.error('获取学校统计信息失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 刷新学校列表
  const refreshSchools = async () => {
    await fetchSchools()
  }

  // 搜索学校
  const searchSchools = async (searchTerm: string) => {
    const params = { ...queryParams.value, name: searchTerm, page: 1 }
    await fetchSchools(params)
  }

  // 重置查询参数
  const resetQueryParams = () => {
    setQueryParams({})
    setPagination(1, 20)
    return fetchSchools()
  }

  // 初始化
  const init = async () => {
    await fetchSchools()
  }

  return {
    // 状态
    schools,
    currentSchool,
    loading,
    total,
    currentPage,
    pageSize,
    queryParams,

    // 计算属性
    hasSchools,
    schoolOptions,
    totalPages,

    // 动作
    setSchools,
    setCurrentSchool,
    setLoading,
    setPagination,
    setQueryParams,
    fetchSchools,
    fetchSchool,
    createSchool,
    updateSchool,
    deleteSchool,
    bulkDeleteSchools,
    toggleSchoolStatus,
    uploadSchoolLogo,
    fetchSchoolStats,
    refreshSchools,
    searchSchools,
    resetQueryParams,
    init
  }
})