import axios from 'axios'
import { vi } from 'vitest'
import type { Mock } from 'vitest'

// API 测试工具类
export class ApiUtils {
  // 创建测试 axios 实例
  static createTestAxios(baseURL?: string) {
    return axios.create({
      baseURL: baseURL || '/api',
      timeout: 5000,
      headers: {
        'Content-Type': 'application/json'
      }
    })
  }

  // 模拟 API 响应
  static mockApiResponse(mockAxios: any, method: string, url: string, response: any, status = 200) {
    mockAxios[method](url).mockResolvedValue({
      data: response,
      status,
      statusText: 'OK',
      headers: {},
      config: {}
    })
  }

  // 模拟 API 错误
  static mockApiError(mockAxios: any, method: string, url: string, error: any, status = 400) {
    mockAxios[method](url).mockRejectedValue({
      response: {
        data: error,
        status,
        statusText: 'Error',
        headers: {},
        config: {}
      },
      isAxiosError: true
    })
  }

  // 模拟网络错误
  static mockNetworkError(mockAxios: any, method: string, url: string) {
    mockAxios[method](url).mockRejectedValue(new Error('Network Error'))
  }

  // 模拟超时错误
  static mockTimeoutError(mockAxios: any, method: string, url: string) {
    mockAxios[method](url).mockRejectedValue(new Error('Timeout Error'))
  }

  // 创建请求拦截器测试
  static testRequestInterceptor(axiosInstance: any, interceptor: (config: any) => any) {
    axiosInstance.interceptors.request.use(interceptor)
  }

  // 创建响应拦截器测试
  static testResponseInterceptor(axiosInstance: any, interceptor: (response: any) => any) {
    axiosInstance.interceptors.response.use(interceptor)
  }

  // 创建错误处理拦截器测试
  static testErrorInterceptor(axiosInstance: any, interceptor: (error: any) => any) {
    axiosInstance.interceptors.response.use(
      response => response,
      interceptor
    )
  }

  // 创建 API 测试用例
  static createApiTestCases(
    mockAxios: any,
    tests: Array<{
      name: string
      method: string
      url: string
      data?: any
      mockResponse: any
      mockStatus?: number
      expectedResponse?: any
      expectedError?: any
    }>
  ) {
    return tests.map(test => ({
      name: test.name,
      test: async () => {
        // 设置模拟响应
        if (test.expectedError) {
          this.mockApiError(mockAxios, test.method, test.url, test.expectedError, test.mockStatus)
        } else {
          this.mockApiResponse(mockAxios, test.method, test.url, test.mockResponse, test.mockStatus)
        }

        // 执行请求
        try {
          const response = await mockAxios[test.method](test.url, test.data)

          if (test.expectedResponse) {
            expect(response.data).toEqual(test.expectedResponse)
          } else {
            expect(response.data).toEqual(test.mockResponse)
          }
        } catch (error) {
          if (test.expectedError) {
            expect(error.response.data).toEqual(test.expectedError)
          } else {
            throw error
          }
        }
      }
    }))
  }

  // 创建分页 API 测试
  static createPaginationApiTest(
    mockAxios: any,
    url: string,
    mockData: any[],
    page: number = 1,
    size: number = 10
  ) {
    return {
      name: 'pagination API',
      test: async () => {
        const paginatedData = {
          data: mockData.slice((page - 1) * size, page * size),
          pagination: {
            page,
            size,
            total: mockData.length,
            totalPages: Math.ceil(mockData.length / size)
          }
        }

        this.mockApiResponse(mockAxios, 'get', url, paginatedData)

        const response = await mockAxios.get(url, {
          params: { page, size }
        })

        expect(response.data).toEqual(paginatedData)
        expect(response.data.pagination.page).toBe(page)
        expect(response.data.pagination.size).toBe(size)
      }
    }
  }

  // 创建过滤 API 测试
  static createFilterApiTest(
    mockAxios: any,
    url: string,
    mockData: any[],
    filters: Record<string, any>
  ) {
    return {
      name: 'filter API',
      test: async () => {
        const filteredData = mockData.filter(item => {
          return Object.entries(filters).every(([key, value]) => {
            return item[key] === value
          })
        })

        this.mockApiResponse(mockAxios, 'get', url, filteredData)

        const response = await mockAxios.get(url, {
          params: filters
        })

        expect(response.data).toEqual(filteredData)
      }
    }
  }

  // 创建搜索 API 测试
  static createSearchApiTest(
    mockAxios: any,
    url: string,
    mockData: any[],
    searchTerm: string
  ) {
    return {
      name: 'search API',
      test: async () => {
        const searchData = mockData.filter(item => {
          return Object.values(item).some(value =>
            String(value).toLowerCase().includes(searchTerm.toLowerCase())
          )
        })

        this.mockApiResponse(mockAxios, 'get', url, searchData)

        const response = await mockAxios.get(url, {
          params: { search: searchTerm }
        })

        expect(response.data).toEqual(searchData)
      }
    }
  }

  // 创建排序 API 测试
  static createSortApiTest(
    mockAxios: any,
    url: string,
    mockData: any[],
    sortField: string,
    sortOrder: 'asc' | 'desc' = 'asc'
  ) {
    return {
      name: 'sort API',
      test: async () => {
        const sortedData = [...mockData].sort((a, b) => {
          if (sortOrder === 'asc') {
            return a[sortField] > b[sortField] ? 1 : -1
          } else {
            return a[sortField] < b[sortField] ? 1 : -1
          }
        })

        this.mockApiResponse(mockAxios, 'get', url, sortedData)

        const response = await mockAxios.get(url, {
          params: { sort: `${sortField}:${sortOrder}` }
        })

        expect(response.data).toEqual(sortedData)
      }
    }
  }

  // 创建批量操作 API 测试
  static createBatchApiTest(
    mockAxios: any,
    url: string,
    mockData: any[],
    operation: string
  ) {
    return {
      name: 'batch API',
      test: async () => {
        this.mockApiResponse(mockAxios, 'post', url, { success: true, count: mockData.length })

        const response = await mockAxios.post(url, {
          ids: mockData.map(item => item.id),
          operation
        })

        expect(response.data.success).toBe(true)
        expect(response.data.count).toBe(mockData.length)
      }
    }
  }

  // 创建文件上传 API 测试
  static createFileUploadApiTest(
    mockAxios: any,
    url: string,
    mockFile: File,
    mockResponse: any
  ) {
    return {
      name: 'file upload API',
      test: async () => {
        this.mockApiResponse(mockAxios, 'post', url, mockResponse)

        const formData = new FormData()
        formData.append('file', mockFile)

        const response = await mockAxios.post(url, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        expect(response.data).toEqual(mockResponse)
      }
    }
  }

  // 创建认证 API 测试
  static createAuthApiTest(
    mockAxios: any,
    loginUrl: string,
    logoutUrl: string,
    profileUrl: string,
    mockCredentials: any,
    mockUser: any
  ) {
    return [
      {
        name: 'login API',
        test: async () => {
          this.mockApiResponse(mockAxios, 'post', loginUrl, {
            user: mockUser,
            token: 'mock-token'
          })

          const response = await mockAxios.post(loginUrl, mockCredentials)

          expect(response.data.user).toEqual(mockUser)
          expect(response.data.token).toBe('mock-token')
        }
      },
      {
        name: 'logout API',
        test: async () => {
          this.mockApiResponse(mockAxios, 'post', logoutUrl, { success: true })

          const response = await mockAxios.post(logoutUrl)

          expect(response.data.success).toBe(true)
        }
      },
      {
        name: 'profile API',
        test: async () => {
          this.mockApiResponse(mockAxios, 'get', profileUrl, mockUser)

          const response = await mockAxios.get(profileUrl)

          expect(response.data).toEqual(mockUser)
        }
      }
    ]
  }

  // 创建 API 性能测试
  static createPerformanceApiTest(
    mockAxios: any,
    url: string,
    maxTime: number = 1000
  ) {
    return {
      name: 'API performance',
      test: async () => {
        this.mockApiResponse(mockAxios, 'get', url, { data: 'test' })

        const start = performance.now()
        await mockAxios.get(url)
        const end = performance.now()

        expect(end - start).toBeLessThan(maxTime)
      }
    }
  }

  // 创建 API 重试测试
  static createRetryApiTest(
    mockAxios: any,
    url: string,
    maxRetries: number = 3
  ) {
    return {
      name: 'API retry',
      test: async () => {
        let callCount = 0
        mockAxios.get.mockImplementation(() => {
          callCount++
          if (callCount < maxRetries) {
            return Promise.reject(new Error('Network Error'))
          }
          return Promise.resolve({ data: { success: true } })
        })

        const response = await mockAxios.get(url)

        expect(response.data.success).toBe(true)
        expect(callCount).toBe(maxRetries)
      }
    }
  }

  // 创建 API 缓存测试
  static createCacheApiTest(
    mockAxios: any,
    url: string,
    mockResponse: any
  ) {
    return {
      name: 'API cache',
      test: async () => {
        let callCount = 0
        mockAxios.get.mockImplementation(() => {
          callCount++
          return Promise.resolve({ data: mockResponse })
        })

        // 第一次调用
        const response1 = await mockAxios.get(url)
        expect(response1.data).toEqual(mockResponse)

        // 第二次调用（应该使用缓存）
        const response2 = await mockAxios.get(url)
        expect(response2.data).toEqual(mockResponse)

        // 验证只调用了一次 API
        expect(callCount).toBe(1)
      }
    }
  }

  // 创建 API 并发测试
  static createConcurrentApiTest(
    mockAxios: any,
    url: string,
    mockResponse: any,
    concurrentCount: number = 5
  ) {
    return {
      name: 'API concurrent',
      test: async () => {
        this.mockApiResponse(mockAxios, 'get', url, mockResponse)

        const promises = Array(concurrentCount).fill(0).map(() => mockAxios.get(url))
        const responses = await Promise.all(promises)

        expect(responses.length).toBe(concurrentCount)
        responses.forEach(response => {
          expect(response.data).toEqual(mockResponse)
        })
      }
    }
  }

  // 创建 API 限流测试
  static createRateLimitApiTest(
    mockAxios: any,
    url: string,
    rateLimit: number = 10,
    timeWindow: number = 1000
  ) {
    return {
      name: 'API rate limit',
      test: async () => {
        let callCount = 0
        mockAxios.get.mockImplementation(() => {
          callCount++
          if (callCount > rateLimit) {
            return Promise.reject({
              response: {
                status: 429,
                data: { error: 'Rate limit exceeded' }
              }
            })
          }
          return Promise.resolve({ data: { success: true } })
        })

        // 发送超出限流数量的请求
        const promises = Array(rateLimit + 1).fill(0).map(() =>
          mockAxios.get(url).catch(error => error)
        )

        const responses = await Promise.all(promises)

        // 验证限流错误
        const rateLimitErrors = responses.filter(response =>
          response.response && response.response.status === 429
        )
        expect(rateLimitErrors.length).toBeGreaterThan(0)
      }
    }
  }
}