import { apiRequest } from './index'
import type { User, LoginRequest } from '@/types'

// 登录响应
export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

// 刷新token响应
export interface RefreshTokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

// 修改密码请求
export interface ChangePasswordRequest {
  old_password: string
  new_password: string
  confirm_password: string
}

// 认证API服务
export const authApi = {
  // 登录
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    return apiRequest.post('/auth/login', data)
  },

  // 登出
  logout: async (): Promise<void> => {
    return apiRequest.post('/auth/logout')
  },

  // 获取用户信息
  getUserInfo: async (): Promise<User> => {
    return apiRequest.get('/auth/me')
  },

  // 刷新token
  refreshToken: async (): Promise<RefreshTokenResponse> => {
    return apiRequest.post('/auth/refresh')
  },

  // 修改密码
  changePassword: async (data: ChangePasswordRequest): Promise<void> => {
    return apiRequest.post('/auth/change-password', data)
  },

  // 更新用户信息
  updateUserInfo: async (data: Partial<User>): Promise<User> => {
    return apiRequest.put('/auth/user', data)
  },

  // 上传头像
  uploadAvatar: async (file: File): Promise<{ avatar_url: string }> => {
    const formData = new FormData()
    formData.append('file', file)

    return apiRequest.post('/auth/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 发送验证码
  sendVerificationCode: async (email: string): Promise<void> => {
    return apiRequest.post('/auth/send-code', { email })
  },

  // 验证邮箱
  verifyEmail: async (email: string, code: string): Promise<void> => {
    return apiRequest.post('/auth/verify-email', { email, code })
  },

  // 重置密码请求
  resetPasswordRequest: async (email: string): Promise<void> => {
    return apiRequest.post('/auth/reset-password-request', { email })
  },

  // 重置密码
  resetPassword: async (data: {
    email: string
    code: string
    new_password: string
    confirm_password: string
  }): Promise<void> => {
    return apiRequest.post('/auth/reset-password', data)
  },

  // 检查用户权限
  checkPermission: async (permission: string): Promise<boolean> => {
    return apiRequest.get('/auth/check-permission', { params: { permission } })
  },

  // 获取用户权限列表
  getUserPermissions: async (): Promise<string[]> => {
    return apiRequest.get('/auth/permissions')
  }
}