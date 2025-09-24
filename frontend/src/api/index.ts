import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'

// API响应接口
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  timestamp: number
}

// API错误接口
export interface ApiError {
  code: number
  message: string
  details?: any
}

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // 添加认证token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers = config.headers || {}
      config.headers['Authorization'] = `Bearer ${token}`
    }

    // 添加租户ID
    const tenantId = localStorage.getItem('tenant_id') || getCurrentTenantId()
    if (tenantId) {
      config.headers = config.headers || {}
      config.headers['X-Tenant-ID'] = tenantId
    }

    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const { data } = response

    // 检查业务状态码
    if (data.code !== 200) {
      return Promise.reject({
        code: data.code,
        message: data.message || 'Request failed',
        details: data
      } as ApiError)
    }

    return data
  },
  (error: AxiosError) => {
    let errorInfo: ApiError = {
      code: error.response?.status || 500,
      message: error.message || 'Network error'
    }

    // 处理不同的HTTP错误状态
    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 400:
          errorInfo.message = (data as any)?.message || 'Bad request'
          break
        case 401:
          errorInfo.message = 'Unauthorized, please login'
          // 清除token并跳转到登录页
          localStorage.removeItem('token')
          window.location.href = '/login'
          break
        case 403:
          errorInfo.message = 'Access denied'
          break
        case 404:
          errorInfo.message = 'Resource not found'
          break
        case 500:
          errorInfo.message = 'Internal server error'
          break
        default:
          errorInfo.message = `Request failed with status ${status}`
      }
    }

    return Promise.reject(errorInfo)
  }
)

// 获取当前租户ID的工具函数
function getCurrentTenantId(): string {
  // 可以从URL参数、用户信息或其他地方获取租户ID
  const urlParams = new URLSearchParams(window.location.search)
  return urlParams.get('tenant_id') || 'default'
}

// 通用API请求方法
export const apiRequest = {
  // GET请求
  get: async <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    const response = await api.get<ApiResponse<T>>(url, config)
    return response.data
  },

  // POST请求
  post: async <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    const response = await api.post<ApiResponse<T>>(url, data, config)
    return response.data
  },

  // PUT请求
  put: async <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    const response = await api.put<ApiResponse<T>>(url, data, config)
    return response.data
  },

  // DELETE请求
  delete: async <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    const response = await api.delete<ApiResponse<T>>(url, config)
    return response.data
  },

  // PATCH请求
  patch: async <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    const response = await api.patch<ApiResponse<T>>(url, data, config)
    return response.data
  }
}

// 分页请求参数接口
export interface PaginationParams {
  page?: number
  size?: number
  sort?: string
  order?: 'asc' | 'desc'
}

// 分页响应接口
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  total_pages: number
}

export default api