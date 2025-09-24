import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import { apiClient } from '@/api'

// 模拟 axios
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Request Configuration', () => {
    it('should have correct base URL', () => {
      expect(apiClient.defaults.baseURL).toBe('/api/v1')
    })

    it('should have default timeout', () => {
      expect(apiClient.defaults.timeout).toBe(30000)
    })

    it('should have default headers', () => {
      expect(apiClient.defaults.headers['Content-Type']).toBe('application/json')
    })
  })

  describe('Request Interceptor', () => {
    it('should add authorization header if token exists', async () => {
      // 设置 token
      localStorage.setItem('token', 'test-token')

      // 模拟成功的请求
      mockedAxios.create.mockReturnValue({
        ...apiClient,
        request: vi.fn().mockResolvedValue({ data: 'success' }),
        interceptors: {
          request: { use: vi.fn((config) => config) },
          response: { use: vi.fn() }
        }
      })

      const client = axios.create({
        baseURL: '/api/v1',
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json'
        }
      })

      // 添加请求拦截器
      client.interceptors.request.use((config) => {
        const token = localStorage.getItem('token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      })

      const config = {
        method: 'get',
        url: '/test'
      }

      const interceptedConfig = client.interceptors.request.use.handlers[0].fulfilled(config)
      expect(interceptedConfig.headers.Authorization).toBe('Bearer test-token')

      // 清理
      localStorage.removeItem('token')
    })

    it('should not add authorization header if no token', async () => {
      localStorage.removeItem('token')

      const config = {
        method: 'get',
        url: '/test'
      }

      // 模拟拦截器逻辑
      const token = localStorage.getItem('token')
      if (token) {
        config.headers = config.headers || {}
        config.headers.Authorization = `Bearer ${token}`
      }

      expect(config.headers).toBeUndefined()
    })
  })

  describe('Response Interceptor', () => {
    it('should handle successful response', async () => {
      const responseData = { data: 'success' }

      const mockClient = {
        ...apiClient,
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn((response) => response) }
        }
      }

      const response = {
        data: responseData,
        status: 200,
        statusText: 'OK'
      }

      const result = mockClient.interceptors.response.use.handlers[0].fulfilled(response)
      expect(result).toEqual(responseData)
    })

    it('should handle error response', async () => {
      const error = {
        response: {
          status: 404,
          data: { message: 'Not Found' }
        }
      }

      const mockClient = {
        ...apiClient,
        interceptors: {
          request: { use: vi.fn() },
          response: {
            use: vi.fn((response) => response),
            eject: vi.fn()
          }
        }
      }

      // 添加错误拦截器
      mockClient.interceptors.response.use(
        (response) => response,
        (error) => {
          if (error.response) {
            throw new Error(error.response.data.message || '请求失败')
          }
          throw error
        }
      )

      expect(() => {
        mockClient.interceptors.response.use.handlers[1].rejected(error)
      }).toThrow('Not Found')
    })

    it('should handle network error', async () => {
      const error = new Error('Network Error')

      const mockClient = {
        ...apiClient,
        interceptors: {
          request: { use: vi.fn() },
          response: {
            use: vi.fn((response) => response),
            eject: vi.fn()
          }
        }
      }

      // 添加错误拦截器
      mockClient.interceptors.response.use(
        (response) => response,
        (error) => {
          if (!error.response) {
            throw new Error('网络连接失败')
          }
          throw error
        }
      )

      expect(() => {
        mockClient.interceptors.response.use.handlers[1].rejected(error)
      }).toThrow('网络连接失败')
    })
  })

  describe('HTTP Methods', () => {
    beforeEach(() => {
      // 重置模拟
      mockedAxios.create.mockReturnValue({
        get: vi.fn(),
        post: vi.fn(),
        put: vi.fn(),
        delete: vi.fn(),
        patch: vi.fn(),
        defaults: {
          baseURL: '/api/v1',
          timeout: 30000,
          headers: { 'Content-Type': 'application/json' }
        },
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() }
        }
      })
    })

    it('should make GET request', async () => {
      const mockClient = mockedAxios.create()
      await mockClient.get('/test', { params: { page: 1 } })

      expect(mockClient.get).toHaveBeenCalledWith('/test', { params: { page: 1 } })
    })

    it('should make POST request', async () => {
      const mockClient = mockedAxios.create()
      const data = { name: 'test' }
      await mockClient.post('/test', data)

      expect(mockClient.post).toHaveBeenCalledWith('/test', data)
    })

    it('should make PUT request', async () => {
      const mockClient = mockedAxios.create()
      const data = { name: 'updated' }
      await mockClient.put('/test/1', data)

      expect(mockClient.put).toHaveBeenCalledWith('/test/1', data)
    })

    it('should make DELETE request', async () => {
      const mockClient = mockedAxios.create()
      await mockClient.delete('/test/1')

      expect(mockClient.delete).toHaveBeenCalledWith('/test/1')
    })
  })

  describe('Error Handling', () => {
    it('should handle 401 Unauthorized', async () => {
      const error = {
        response: {
          status: 401,
          data: { message: 'Token expired' }
        }
      }

      const mockClient = {
        ...apiClient,
        interceptors: {
          request: { use: vi.fn() },
          response: {
            use: vi.fn((response) => response),
            eject: vi.fn()
          }
        }
      }

      // 模拟跳转到登录页
      const mockRouter = { push: vi.fn() }
      global.window = Object.create(window)
      Object.defineProperty(window, 'location', {
        value: {
          href: 'http://localhost:3000/dashboard',
          replace: vi.fn()
        },
        writable: true
      })

      // 添加401处理逻辑
      mockClient.interceptors.response.use(
        (response) => response,
        (error) => {
          if (error.response?.status === 401) {
            localStorage.removeItem('token')
            window.location.replace('/login')
          }
          throw error
        }
      )

      expect(() => {
        mockClient.interceptors.response.use.handlers[1].rejected(error)
      }).toThrow('Token expired')

      expect(localStorage.getItem('token')).toBeNull()
    })

    it('should handle 403 Forbidden', async () => {
      const error = {
        response: {
          status: 403,
          data: { message: 'Insufficient permissions' }
        }
      }

      const mockClient = {
        ...apiClient,
        interceptors: {
          request: { use: vi.fn() },
          response: {
            use: vi.fn((response) => response),
            eject: vi.fn()
          }
        }
      }

      expect(() => {
        mockClient.interceptors.response.use.handlers[1].rejected(error)
      }).toThrow('Insufficient permissions')
    })

    it('should handle 500 Server Error', async () => {
      const error = {
        response: {
          status: 500,
          data: { message: 'Internal server error' }
        }
      }

      const mockClient = {
        ...apiClient,
        interceptors: {
          request: { use: vi.fn() },
          response: {
            use: vi.fn((response) => response),
            eject: vi.fn()
          }
        }
      }

      expect(() => {
        mockClient.interceptors.response.use.handlers[1].rejected(error)
      }).toThrow('Internal server error')
    })
  })

  describe('Request Cancellation', () => {
    it('should support request cancellation', () => {
      const CancelToken = axios.CancelToken
      const source = CancelToken.source()

      expect(typeof source.cancel).toBe('function')
      expect(typeof source.token).toBe('object')
    })
  })
})