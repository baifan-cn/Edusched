import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { roomsApi, campusesApi } from '@/api/rooms'
import type { Room, CreateRoomRequest, UpdateRoomRequest, RoomQueryParams, Campus } from '@/types'

export const useRoomsStore = defineStore('rooms', () => {
  // 教室相关状态
  const rooms = ref<Room[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const currentRoom = ref<Room | null>(null)
  const activeRooms = ref<Room[]>([])

  // 校区相关状态
  const campuses = ref<Campus[]>([])
  const currentCampus = ref<Campus | null>(null)
  const campusesLoading = ref(false)

  // 教室计算属性
  const activeRoomsList = computed(() => rooms.value.filter(r => r.is_active))
  const inactiveRoomsList = computed(() => rooms.value.filter(r => !r.is_active))

  const roomsByCampus = computed(() => {
    const groups: Record<string, Room[]> = {}
    rooms.value.forEach(room => {
      const campus = getCampusName(room.campus_id)
      if (!groups[campus]) groups[campus] = []
      groups[campus].push(room)
    })
    return groups
  })

  const roomsByType = computed(() => {
    const groups: Record<string, Room[]> = {}
    rooms.value.forEach(room => {
      const type = room.room_type
      if (!groups[type]) groups[type] = []
      groups[type].push(room)
    })
    return groups
  })

  const roomsOptions = computed(() =>
    rooms.value.map(room => ({
      label: `${room.name} (${room.code})`,
      value: room.id,
      disabled: !room.is_active,
      campus_id: room.campus_id,
      capacity: room.capacity,
      room_type: room.room_type
    }))
  )

  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  // 校区计算属性
  const activeCampusesList = computed(() => campuses.value.filter(c => c.is_active))
  const campusesOptions = computed(() =>
    campuses.value.map(campus => ({
      label: campus.name,
      value: campus.id,
      disabled: !campus.is_active
    }))
  )

  // 操作方法
  const setRooms = (newRooms: Room[]) => {
    rooms.value = newRooms
  }

  const setCampuses = (newCampuses: Campus[]) => {
    campuses.value = newCampuses
  }

  const setLoading = (isLoading: boolean) => {
    loading.value = isLoading
  }

  const setCampusesLoading = (isLoading: boolean) => {
    campusesLoading.value = isLoading
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

  // 教室API方法
  const fetchRooms = async (params?: RoomQueryParams) => {
    try {
      setLoading(true)
      resetError()

      const response = await roomsApi.getRooms({
        page: currentPage.value,
        size: pageSize.value,
        ...params
      })

      setRooms(response.items)
      setPagination(response.page, response.size, response.total)

      return response
    } catch (err: any) {
      setError(err.message || '获取教室列表失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const fetchRoom = async (id: string) => {
    try {
      setLoading(true)
      resetError()

      const room = await roomsApi.getRoom(id)
      currentRoom.value = room

      return room
    } catch (err: any) {
      setError(err.message || '获取教室详情失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const createRoom = async (data: CreateRoomRequest) => {
    try {
      setLoading(true)
      resetError()

      const newRoom = await roomsApi.createRoom(data)
      rooms.value.unshift(newRoom)
      total.value += 1

      ElMessage.success('教室创建成功')
      return newRoom
    } catch (err: any) {
      setError(err.message || '教室创建失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const updateRoom = async (id: string, data: UpdateRoomRequest) => {
    try {
      setLoading(true)
      resetError()

      const updatedRoom = await roomsApi.updateRoom(id, data)
      const index = rooms.value.findIndex(r => r.id === id)

      if (index !== -1) {
        rooms.value[index] = updatedRoom
      }

      if (currentRoom.value?.id === id) {
        currentRoom.value = updatedRoom
      }

      ElMessage.success('教室信息更新成功')
      return updatedRoom
    } catch (err: any) {
      setError(err.message || '教室信息更新失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const deleteRoom = async (id: string) => {
    try {
      setLoading(true)
      resetError()

      await roomsApi.deleteRoom(id)
      rooms.value = rooms.value.filter(r => r.id !== id)
      total.value -= 1

      ElMessage.success('教室删除成功')
    } catch (err: any) {
      setError(err.message || '教室删除失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const bulkDeleteRooms = async (ids: string[]) => {
    try {
      setLoading(true)
      resetError()

      await roomsApi.bulkDeleteRooms(ids)
      rooms.value = rooms.value.filter(r => !ids.includes(r.id))
      total.value -= ids.length

      ElMessage.success(`成功删除 ${ids.length} 间教室`)
    } catch (err: any) {
      setError(err.message || '批量删除失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const toggleRoomStatus = async (id: string, isActive: boolean) => {
    try {
      setLoading(true)
      resetError()

      const updatedRoom = await roomsApi.toggleRoomStatus(id, isActive)
      const index = rooms.value.findIndex(r => r.id === id)

      if (index !== -1) {
        rooms.value[index] = updatedRoom
      }

      ElMessage.success(`教室已${isActive ? '激活' : '停用'}`)
      return updatedRoom
    } catch (err: any) {
      setError(err.message || '状态切换失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const fetchRoomsByCampus = async (campusId: string, params?: Omit<RoomQueryParams, 'campus_id'>) => {
    try {
      setLoading(true)
      resetError()

      const roomsList = await roomsApi.getRoomsByCampus(campusId, params)
      return roomsList
    } catch (err: any) {
      setError(err.message || '获取校区教室失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const fetchRoomsBySchool = async (schoolId: string, params?: Omit<RoomQueryParams, 'school_id'>) => {
    try {
      setLoading(true)
      resetError()

      const roomsList = await roomsApi.getRoomsBySchool(schoolId, params)
      return roomsList
    } catch (err: any) {
      setError(err.message || '获取学校教室失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const fetchActiveRooms = async (schoolId?: string) => {
    try {
      setLoading(true)
      resetError()

      const roomsList = await roomsApi.getActiveRooms(schoolId)
      activeRooms.value = roomsList

      return roomsList
    } catch (err: any) {
      setError(err.message || '获取活跃教室失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const checkRoomCode = async (code: string, schoolId: string, excludeId?: string) => {
    try {
      setLoading(true)
      resetError()

      const result = await roomsApi.checkRoomCode(code, schoolId, excludeId)
      return result
    } catch (err: any) {
      setError(err.message || '检查教室代码失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const getRoomAvailability = async (
    roomId: string,
    params: {
      start_date: string
      end_date: string
      day_of_week?: number
    }
  ) => {
    try {
      setLoading(true)
      resetError()

      const availability = await roomsApi.getRoomAvailability(roomId, params)
      return availability
    } catch (err: any) {
      setError(err.message || '获取教室可用时间失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const getRoomStats = async (schoolId?: string) => {
    try {
      setLoading(true)
      resetError()

      const stats = await roomsApi.getRoomStats(schoolId)
      return stats
    } catch (err: any) {
      setError(err.message || '获取教室统计失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const importRooms = async (schoolId: string, file: File) => {
    try {
      setLoading(true)
      resetError()

      const result = await roomsApi.importRooms(schoolId, file)

      if (result.error_count === 0) {
        ElMessage.success(`成功导入 ${result.success_count} 间教室`)
      } else {
        ElMessage.warning(
          `导入完成：成功 ${result.success_count} 间，失败 ${result.error_count} 间`
        )
      }

      // 刷新列表
      await fetchRooms()
      return result
    } catch (err: any) {
      setError(err.message || '教室数据导入失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const exportRooms = async (params: RoomQueryParams) => {
    try {
      setLoading(true)
      resetError()

      const blob = await roomsApi.exportRooms(params)

      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `rooms_${new Date().toISOString().split('T')[0]}.xlsx`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      ElMessage.success('教室数据导出成功')
    } catch (err: any) {
      setError(err.message || '教室数据导出失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  // 校区API方法
  const fetchCampuses = async (schoolId?: string) => {
    try {
      setCampusesLoading(true)
      resetError()

      const campusesList = await campusesApi.getCampuses(schoolId)
      setCampuses(campusesList)

      return campusesList
    } catch (err: any) {
      setError(err.message || '获取校区列表失败')
      throw err
    } finally {
      setCampusesLoading(false)
    }
  }

  const fetchCampus = async (id: string) => {
    try {
      setCampusesLoading(true)
      resetError()

      const campus = await campusesApi.getCampus(id)
      currentCampus.value = campus

      return campus
    } catch (err: any) {
      setError(err.message || '获取校区详情失败')
      throw err
    } finally {
      setCampusesLoading(false)
    }
  }

  const createCampus = async (data: any) => {
    try {
      setCampusesLoading(true)
      resetError()

      const newCampus = await campusesApi.createCampus(data)
      campuses.value.unshift(newCampus)

      ElMessage.success('校区创建成功')
      return newCampus
    } catch (err: any) {
      setError(err.message || '校区创建失败')
      throw err
    } finally {
      setCampusesLoading(false)
    }
  }

  const updateCampus = async (id: string, data: any) => {
    try {
      setCampusesLoading(true)
      resetError()

      const updatedCampus = await campusesApi.updateCampus(id, data)
      const index = campuses.value.findIndex(c => c.id === id)

      if (index !== -1) {
        campuses.value[index] = updatedCampus
      }

      if (currentCampus.value?.id === id) {
        currentCampus.value = updatedCampus
      }

      ElMessage.success('校区信息更新成功')
      return updatedCampus
    } catch (err: any) {
      setError(err.message || '校区信息更新失败')
      throw err
    } finally {
      setCampusesLoading(false)
    }
  }

  const deleteCampus = async (id: string) => {
    try {
      setCampusesLoading(true)
      resetError()

      await campusesApi.deleteCampus(id)
      campuses.value = campuses.value.filter(c => c.id !== id)

      ElMessage.success('校区删除成功')
    } catch (err: any) {
      setError(err.message || '校区删除失败')
      throw err
    } finally {
      setCampusesLoading(false)
    }
  }

  const toggleCampusStatus = async (id: string, isActive: boolean) => {
    try {
      setCampusesLoading(true)
      resetError()

      const updatedCampus = await campusesApi.toggleCampusStatus(id, isActive)
      const index = campuses.value.findIndex(c => c.id === id)

      if (index !== -1) {
        campuses.value[index] = updatedCampus
      }

      ElMessage.success(`校区已${isActive ? '激活' : '停用'}`)
      return updatedCampus
    } catch (err: any) {
      setError(err.message || '校区状态切换失败')
      throw err
    } finally {
      setCampusesLoading(false)
    }
  }

  const fetchCampusesBySchool = async (schoolId: string) => {
    try {
      setCampusesLoading(true)
      resetError()

      const campusesList = await campusesApi.getCampusesBySchool(schoolId)
      setCampuses(campusesList)

      return campusesList
    } catch (err: any) {
      setError(err.message || '获取学校校区失败')
      throw err
    } finally {
      setCampusesLoading(false)
    }
  }

  // 工具方法
  const getRoomById = (id: string): Room | undefined => {
    return rooms.value.find(r => r.id === id)
  }

  const getRoomName = (id: string): string => {
    const room = getRoomById(id)
    return room?.name || '未知教室'
  }

  const getCampusById = (id: string): Campus | undefined => {
    return campuses.value.find(c => c.id === id)
  }

  const getCampusName = (id: string): string => {
    const campus = getCampusById(id)
    return campus?.name || '未知校区'
  }

  // 重置状态
  const resetState = () => {
    // 教室状态
    rooms.value = []
    loading.value = false
    error.value = null
    total.value = 0
    currentPage.value = 1
    pageSize.value = 20
    currentRoom.value = null
    activeRooms.value = []

    // 校区状态
    campuses.value = []
    currentCampus.value = null
    campusesLoading.value = false
  }

  return {
    // 教室状态
    rooms,
    loading,
    error,
    total,
    currentPage,
    pageSize,
    currentRoom,
    activeRooms,

    // 校区状态
    campuses,
    currentCampus,
    campusesLoading,

    // 教室计算属性
    activeRoomsList,
    inactiveRoomsList,
    roomsByCampus,
    roomsByType,
    roomsOptions,
    totalPages,

    // 校区计算属性
    activeCampusesList,
    campusesOptions,

    // 操作方法
    setRooms,
    setCampuses,
    setLoading,
    setCampusesLoading,
    setError,
    setPagination,
    resetError,

    // 教室API方法
    fetchRooms,
    fetchRoom,
    createRoom,
    updateRoom,
    deleteRoom,
    bulkDeleteRooms,
    toggleRoomStatus,
    fetchRoomsByCampus,
    fetchRoomsBySchool,
    fetchActiveRooms,
    checkRoomCode,
    getRoomAvailability,
    getRoomStats,
    importRooms,
    exportRooms,

    // 校区API方法
    fetchCampuses,
    fetchCampus,
    createCampus,
    updateCampus,
    deleteCampus,
    toggleCampusStatus,
    fetchCampusesBySchool,

    // 工具方法
    getRoomById,
    getRoomName,
    getCampusById,
    getCampusName,

    // 重置
    resetState
  }
})