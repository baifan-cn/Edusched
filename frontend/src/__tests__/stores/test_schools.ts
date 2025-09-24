import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createTestingPinia } from '@pinia/testing'
import { useSchoolsStore } from '@/stores/schools'
import { schoolsApi } from '@/api/schools'

// 模拟 API
vi.mock('@/api/schools', () => ({
  schoolsApi: {
    getSchools: vi.fn(),
    getSchoolById: vi.fn(),
    createSchool: vi.fn(),
    updateSchool: vi.fn(),
    deleteSchool: vi.fn()
  }
}))

describe('Schools Store', () => {
  let schoolsStore: any

  beforeEach(() => {
    // 创建测试 Pinia
    const pinia = createTestingPinia({ createSpy: vi.fn })
    schoolsStore = useSchoolsStore(pinia)

    // 重置 store 状态
    schoolsStore.$reset()
  })

  it('should initialize with default state', () => {
    expect(schoolsStore.schools).toEqual([])
    expect(schoolsStore.loading).toBe(false)
    expect(schoolsStore.error).toBe(null)
    expect(schoolsStore.total).toBe(0)
    expect(schoolsStore.currentPage).toBe(1)
    expect(schoolsStore.pageSize).toBe(20)
  })

  describe('fetchSchools', () => {
    it('should fetch schools successfully', async () => {
      const mockSchools = [
        {
          id: '1',
          name: '测试学校1',
          code: 'TEST001',
          address: '地址1',
          is_active: true
        },
        {
          id: '2',
          name: '测试学校2',
          code: 'TEST002',
          address: '地址2',
          is_active: true
        }
      ]

      const mockResponse = {
        items: mockSchools,
        total: 2,
        page: 1,
        size: 20
      }

      vi.mocked(schoolsApi.getSchools).mockResolvedValue(mockResponse)

      await schoolsStore.fetchSchools()

      expect(schoolsStore.loading).toBe(false)
      expect(schoolsStore.schools).toEqual(mockSchools)
      expect(schoolsStore.total).toBe(2)
      expect(schoolsStore.error).toBe(null)
      expect(schoolsApi.getSchools).toHaveBeenCalledWith()
    })

    it('should handle fetch schools error', async () => {
      const errorMessage = '获取学校列表失败'
      vi.mocked(schoolsApi.getSchools).mockRejectedValue(new Error(errorMessage))

      await schoolsStore.fetchSchools()

      expect(schoolsStore.loading).toBe(false)
      expect(schoolsStore.schools).toEqual([])
      expect(schoolsStore.error).toBe(errorMessage)
    })

    it('should fetch schools with query parameters', async () => {
      const queryParams = {
        page: 2,
        size: 10,
        is_active: true,
        search: '测试'
      }

      const mockResponse = {
        items: [],
        total: 0,
        page: 2,
        size: 10
      }

      vi.mocked(schoolsApi.getSchools).mockResolvedValue(mockResponse)

      await schoolsStore.fetchSchools(queryParams)

      expect(schoolsApi.getSchools).toHaveBeenCalledWith(queryParams)
      expect(schoolsStore.currentPage).toBe(2)
      expect(schoolsStore.pageSize).toBe(10)
    })
  })

  describe('createSchool', () => {
    it('should create school successfully', async () => {
      const newSchool = {
        name: '新学校',
        code: 'NEW001',
        address: '新地址',
        is_active: true
      }

      const createdSchool = {
        id: '3',
        ...newSchool
      }

      vi.mocked(schoolsApi.createSchool).mockResolvedValue(createdSchool)

      await schoolsStore.createSchool(newSchool)

      expect(schoolsApi.createSchool).toHaveBeenCalledWith(newSchool)
      expect(schoolsStore.schools).toContainEqual(createdSchool)
      expect(schoolsStore.total).toBe(1)
    })

    it('should handle create school error', async () => {
      const errorMessage = '创建学校失败'
      vi.mocked(schoolsApi.createSchool).mockRejectedValue(new Error(errorMessage))

      await expect(schoolsStore.createSchool({})).rejects.toThrow(errorMessage)
    })
  })

  describe('updateSchool', () => {
    it('should update school successfully', async () => {
      const schoolId = '1'
      const updateData = {
        name: '更新后的学校名称',
        address: '更新后的地址'
      }

      const updatedSchool = {
        id: schoolId,
        name: '更新后的学校名称',
        address: '更新后的地址',
        code: 'TEST001',
        is_active: true
      }

      vi.mocked(schoolsApi.updateSchool).mockResolvedValue(updatedSchool)

      await schoolsStore.updateSchool(schoolId, updateData)

      expect(schoolsApi.updateSchool).toHaveBeenCalledWith(schoolId, updateData)

      const schoolInStore = schoolsStore.schools.find(s => s.id === schoolId)
      expect(schoolInStore).toEqual(updatedSchool)
    })

    it('should handle update school error', async () => {
      const errorMessage = '更新学校失败'
      vi.mocked(schoolsApi.updateSchool).mockRejectedValue(new Error(errorMessage))

      await expect(schoolsStore.updateSchool('1', {})).rejects.toThrow(errorMessage)
    })
  })

  describe('deleteSchool', () => {
    it('should delete school successfully', async () => {
      const schoolId = '1'

      // 初始化一个学校
      schoolsStore.schools = [{
        id: schoolId,
        name: '测试学校',
        code: 'TEST001',
        address: '地址',
        is_active: true
      }]
      schoolsStore.total = 1

      vi.mocked(schoolsApi.deleteSchool).mockResolvedValue()

      await schoolsStore.deleteSchool(schoolId)

      expect(schoolsApi.deleteSchool).toHaveBeenCalledWith(schoolId)
      expect(schoolsStore.schools).not.toContainEqual(expect.objectContaining({ id: schoolId }))
      expect(schoolsStore.total).toBe(0)
    })

    it('should handle delete school error', async () => {
      const errorMessage = '删除学校失败'
      vi.mocked(schoolsApi.deleteSchool).mockRejectedValue(new Error(errorMessage))

      await expect(schoolsStore.deleteSchool('1')).rejects.toThrow(errorMessage)
    })
  })

  describe('getSchoolById', () => {
    it('should get school by id successfully', async () => {
      const schoolId = '1'
      const mockSchool = {
        id: schoolId,
        name: '测试学校',
        code: 'TEST001',
        address: '地址',
        is_active: true
      }

      vi.mocked(schoolsApi.getSchoolById).mockResolvedValue(mockSchool)

      const result = await schoolsStore.getSchoolById(schoolId)

      expect(result).toEqual(mockSchool)
      expect(schoolsApi.getSchoolById).toHaveBeenCalledWith(schoolId)
    })

    it('should handle get school by id error', async () => {
      const errorMessage = '获取学校详情失败'
      vi.mocked(schoolsApi.getSchoolById).mockRejectedValue(new Error(errorMessage))

      await expect(schoolsStore.getSchoolById('1')).rejects.toThrow(errorMessage)
    })
  })

  describe('schoolOptions computed property', () => {
    it('should return school options for select component', () => {
      schoolsStore.schools = [
        { id: '1', name: '学校A', code: 'A001', is_active: true },
        { id: '2', name: '学校B', code: 'B001', is_active: true },
        { id: '3', name: '学校C', code: 'C001', is_active: false }
      ]

      const options = schoolsStore.schoolOptions

      expect(options).toEqual([
        { label: '学校A', value: '1' },
        { label: '学校B', value: '2' }
        // 不活跃的学校不应该包含在选项中
      ])
    })

    it('should return empty array when no schools', () => {
      schoolsStore.schools = []

      const options = schoolsStore.schoolOptions

      expect(options).toEqual([])
    })
  })

  describe('pagination computed properties', () => {
    beforeEach(() => {
      schoolsStore.total = 100
      schoolsStore.currentPage = 3
      schoolsStore.pageSize = 20
    })

    it('should calculate total pages correctly', () => {
      expect(schoolsStore.totalPages).toBe(5)
    })

    it('should calculate start item correctly', () => {
      expect(schoolsStore.startItem).toBe(41)
    })

    it('should calculate end item correctly', () => {
      expect(schoolsStore.endItem).toBe(60)
    })
  })

  describe('setError and setLoading', () => {
    it('should set error message', () => {
      schoolsStore.setError('测试错误')
      expect(schoolsStore.error).toBe('测试错误')
    })

    it('should clear error', () => {
      schoolsStore.setError('测试错误')
      schoolsStore.clearError()
      expect(schoolsStore.error).toBe(null)
    })

    it('should set loading state', () => {
      schoolsStore.setLoading(true)
      expect(schoolsStore.loading).toBe(true)

      schoolsStore.setLoading(false)
      expect(schoolsStore.loading).toBe(false)
    })
  })
})