import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api/auth'
import type { User, LoginRequest, LoginResponse } from '@/types'

export const useUserStore = defineStore('user', () => {
  const router = useRouter()

  // 状态
  const token = ref<string>('')
  const userInfo = ref<User | null>(null)
  const tenantId = ref<string>('')
  const permissions = ref<string[]>([])
  const roles = ref<string[]>([])
  const loading = ref(false)

  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const userName = computed(() => {
    if (!userInfo.value) return ''
    return `${userInfo.value.first_name} ${userInfo.value.last_name}`
  })
  const userAvatar = computed(() => userInfo.value?.avatar || '')
  const userRole = computed(() => userInfo.value?.role || '')
  const userEmail = computed(() => userInfo.value?.email || '')
  const hasPermission = computed(() => {
    return (permission: string) => permissions.value.includes(permission)
  })
  const hasRole = computed(() => {
    return (role: string) => roles.value.includes(role)
  })
  const isAdmin = computed(() => hasRole.value('admin'))
  const isTeacher = computed(() => hasRole.value('teacher'))
  const isStudent = computed(() => hasRole.value('student'))

  // 动作
  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const setUserInfo = (info: User) => {
    userInfo.value = info
    permissions.value = info.permissions || []
    roles.value = info.role ? [info.role] : []
    localStorage.setItem('user_info', JSON.stringify(info))
  }

  const setTenantId = (id: string) => {
    tenantId.value = id
    localStorage.setItem('tenant_id', id)
  }

  const clearUserState = () => {
    token.value = ''
    userInfo.value = null
    tenantId.value = ''
    permissions.value = []
    roles.value = []
    localStorage.removeItem('token')
    localStorage.removeItem('user_info')
    localStorage.removeItem('tenant_id')
  }

  // 登录
  const login = async (loginData: LoginRequest) => {
    try {
      loading.value = true
      const response = await authApi.login(loginData)

      // 设置用户信息
      setToken(response.access_token)
      setUserInfo(response.user)

      // 设置租户ID（从用户信息中获取）
      if (response.user.tenant_id) {
        setTenantId(response.user.tenant_id)
      }

      ElMessage.success('登录成功')
      return response
    } catch (error) {
      clearUserState()
      throw error
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = async () => {
    try {
      loading.value = true
      // 调用登出API（如果有的话）
      await authApi.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      clearUserState()
      router.push('/login')
      ElMessage.success('已安全退出')
      loading.value = false
    }
  }

  // 获取用户信息
  const getUserInfo = async () => {
    try {
      loading.value = true
      const info = await authApi.getUserInfo()
      setUserInfo(info)

      // 设置租户ID
      if (info.tenant_id) {
        setTenantId(info.tenant_id)
      }

      return info
    } catch (error) {
      clearUserState()
      router.push('/login')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 刷新token
  const refreshToken = async () => {
    try {
      const response = await authApi.refreshToken()
      setToken(response.access_token)
      return response
    } catch (error) {
      clearUserState()
      router.push('/login')
      throw error
    }
  }

  // 更新用户信息
  const updateUserInfo = async (userData: Partial<User>) => {
    try {
      loading.value = true
      const updatedInfo = await authApi.updateUserInfo(userData)
      setUserInfo(updatedInfo)
      ElMessage.success('个人信息更新成功')
      return updatedInfo
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  // 修改密码
  const changePassword = async (data: {
    old_password: string
    new_password: string
    confirm_password: string
  }) => {
    try {
      loading.value = true
      await authApi.changePassword(data)
      ElMessage.success('密码修改成功，请重新登录')
      await logout()
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  // 上传头像
  const uploadAvatar = async (file: File) => {
    try {
      loading.value = true
      const response = await authApi.uploadAvatar(file)
      if (userInfo.value) {
        setUserInfo({
          ...userInfo.value,
          avatar: response.avatar_url
        })
      }
      ElMessage.success('头像上传成功')
      return response
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  // 初始化用户状态
  const initUserState = async () => {
    const savedToken = localStorage.getItem('token')
    const savedUserInfo = localStorage.getItem('user_info')
    const savedTenantId = localStorage.getItem('tenant_id')

    if (savedToken && savedUserInfo) {
      try {
        token.value = savedToken
        tenantId.value = savedTenantId || ''

        const userInfoData = JSON.parse(savedUserInfo)
        userInfo.value = userInfoData
        permissions.value = userInfoData.permissions || []
        roles.value = userInfoData.role ? [userInfoData.role] : []

        // 验证token有效性
        await getUserInfo()
      } catch (error) {
        console.error('Failed to restore user state:', error)
        clearUserState()
      }
    }
  }

  // 检查权限
  const checkPermission = (permission: string): boolean => {
    return hasPermission.value(permission)
  }

  // 检查角色
  const checkRole = (role: string): boolean => {
    return hasRole.value(role)
  }

  // 检查多个权限
  const checkPermissions = (requiredPermissions: string[]): boolean => {
    return requiredPermissions.every(permission => checkPermission(permission))
  }

  // 检查任意一个权限
  const checkAnyPermission = (requiredPermissions: string[]): boolean => {
    return requiredPermissions.some(permission => checkPermission(permission))
  }

  return {
    // 状态
    token,
    userInfo,
    tenantId,
    permissions,
    roles,
    loading,

    // 计算属性
    isLoggedIn,
    userName,
    userAvatar,
    userRole,
    userEmail,
    hasPermission,
    hasRole,
    isAdmin,
    isTeacher,
    isStudent,

    // 动作
    setToken,
    setUserInfo,
    setTenantId,
    clearUserState,
    login,
    logout,
    getUserInfo,
    refreshToken,
    updateUserInfo,
    changePassword,
    uploadAvatar,
    initUserState,
    checkPermission,
    checkRole,
    checkPermissions,
    checkAnyPermission
  }
})