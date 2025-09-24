import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { ElMessage, ElNotification } from 'element-plus'
import type { ApiResponse, ApiError } from '@/types'

// 扩展AxiosRequestConfig，支持自定义配置
interface CustomAxiosRequestConfig extends AxiosRequestConfig {
  loading?: boolean
  showError?: boolean
  showSuccess?: boolean
  successMessage?: string
}

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求计数器，用于控制loading状态
let requestCount = 0
let loadingInstance: any = null

// 显示loading
const showLoading = () => {
  if (requestCount === 0) {
    loadingInstance = ElLoading.service({
      lock: true,
      text: '加载中...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
  }
  requestCount++
}

// 隐藏loading
const hideLoading = () => {
  requestCount--
  if (requestCount <= 0 && loadingInstance) {
    loadingInstance.close()
    loadingInstance = null
    requestCount = 0
  }
}

// 请求拦截器
request.interceptors.request.use(
  (config: CustomAxiosRequestConfig) => {
    // 显示loading
    if (config.loading !== false) {
      showLoading()
    }

    // 添加认证token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers = config.headers || {}
      config.headers['Authorization'] = `Bearer ${token}`
    }

    // 添加租户ID
    const tenantId = localStorage.getItem('tenant_id')
    if (tenantId) {
      config.headers = config.headers || {}
      config.headers['X-Tenant-ID'] = tenantId
    }

    // 添加请求ID用于追踪
    config.headers['X-Request-ID'] = generateRequestId()

    return config
  },
  (error: AxiosError) => {
    hideLoading()
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    // 隐藏loading
    const config = response.config as CustomAxiosRequestConfig
    if (config.loading !== false) {
      hideLoading()
    }

    const { data } = response

    // 检查业务状态码
    if (data.code !== 200) {
      // 处理业务错误
      handleError({
        code: data.code,
        message: data.message || 'Request failed',
        details: data
      }, config)

      return Promise.reject({
        code: data.code,
        message: data.message || 'Request failed',
        details: data
      } as ApiError)
    }

    // 显示成功消息
    if (config.showSuccess) {
      const message = config.successMessage || data.message || '操作成功'
      ElMessage.success(message)
    }

    return response
  },
  (error: AxiosError) => {
    // 隐藏loading
    const config = error.config as CustomAxiosRequestConfig
    if (config?.loading !== false) {
      hideLoading()
    }

    // 处理HTTP错误
    handleError(error, config)
    return Promise.reject(error)
  }
)

// 错误处理函数
const handleError = (error: any, config?: CustomAxiosRequestConfig) => {
  if (!config || config.showError !== false) {
    let errorMessage = error.message || '网络错误'

    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 400:
          errorMessage = (data as any)?.message || '请求参数错误'
          break
        case 401:
          errorMessage = '未授权，请登录'
          // 清除token并跳转到登录页
          localStorage.removeItem('token')
          localStorage.removeItem('user_info')
          window.location.href = '/login'
          break
        case 403:
          errorMessage = '访问被拒绝'
          break
        case 404:
          errorMessage = '资源不存在'
          break
        case 422:
          errorMessage = '数据验证失败'
          break
        case 500:
          errorMessage = '服务器内部错误'
          break
        case 502:
          errorMessage = '网关错误'
          break
        case 503:
          errorMessage = '服务暂时不可用'
          break
        default:
          errorMessage = `请求失败 (${status})`
      }
    }

    // 根据错误类型选择显示方式
    if (error.code === 401) {
      ElNotification({
        title: '认证失败',
        message: errorMessage,
        type: 'warning',
        duration: 3000
      })
    } else {
      ElMessage.error(errorMessage)
    }
  }

  // 记录错误日志
  logError(error, config)
}

// 记录错误日志
const logError = (error: any, config?: CustomAxiosRequestConfig) => {
  const errorInfo = {
    url: config?.url,
    method: config?.method,
    params: config?.params,
    data: config?.data,
    error: {
      message: error.message,
      code: error.code,
      status: error.response?.status,
      data: error.response?.data
    },
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent
  }

  // 发送到错误日志服务
  if (import.meta.env.PROD) {
    // 在生产环境中发送错误日志
    console.error('API Error:', errorInfo)
  }
}

// 生成请求ID
const generateRequestId = () => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

// 导出请求方法
export const http = {
  get: <T = any>(url: string, config?: CustomAxiosRequestConfig) => {
    return request.get<ApiResponse<T>>(url, config).then(res => res.data.data)
  },

  post: <T = any>(url: string, data?: any, config?: CustomAxiosRequestConfig) => {
    return request.post<ApiResponse<T>>(url, data, config).then(res => res.data.data)
  },

  put: <T = any>(url: string, data?: any, config?: CustomAxiosRequestConfig) => {
    return request.put<ApiResponse<T>>(url, data, config).then(res => res.data.data)
  },

  patch: <T = any>(url: string, data?: any, config?: CustomAxiosRequestConfig) => {
    return request.patch<ApiResponse<T>>(url, data, config).then(res => res.data.data)
  },

  delete: <T = any>(url: string, config?: CustomAxiosRequestConfig) => {
    return request.delete<ApiResponse<T>>(url, config).then(res => res.data.data)
  },

  // 上传文件
  upload: (url: string, file: File, config?: CustomAxiosRequestConfig) => {
    const formData = new FormData()
    formData.append('file', file)

    return request.post<ApiResponse<{ url: string }>>(url, formData, {
      ...config,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }).then(res => res.data.data)
  },

  // 下载文件
  download: (url: string, filename?: string, config?: CustomAxiosRequestConfig) => {
    return request.get(url, {
      ...config,
      responseType: 'blob'
    }).then(response => {
      const blob = new Blob([response.data])
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename || 'download'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    })
  }
}

export default request