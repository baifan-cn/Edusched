import { vi } from 'vitest'
import type { Mock } from 'vitest'

// Mock 工具类
export class MockUtils {
  // 创建模拟 axios 实例
  static createMockAxios() {
    return {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      patch: vi.fn(),
      request: vi.fn(),
      interceptors: {
        request: { use: vi.fn(), eject: vi.fn() },
        response: { use: vi.fn(), eject: vi.fn() }
      },
      defaults: {
        headers: {
          common: {},
          post: {},
          get: {},
          put: {},
          delete: {},
          patch: {}
        }
      }
    }
  }

  // 创建模拟响应
  static createMockResponse<T>(data: T, status = 200, headers = {}) {
    return {
      data,
      status,
      statusText: 'OK',
      headers,
      config: {},
      request: {}
    }
  }

  // 创建模拟错误响应
  static createMockErrorResponse(message: string, status = 400, data?: any) {
    const error = new Error(message) as any
    error.response = {
      data: data || { message },
      status,
      statusText: 'Error',
      headers: {},
      config: {}
    }
    error.isAxiosError = true
    return error
  }

  // 创建模拟 Pinia store
  static createMockStore<T extends Record<string, any>>(state: T, actions: Record<string, Mock> = {}) {
    return {
      $id: 'test-store',
      $state: state,
      $patch: vi.fn(),
      $reset: vi.fn(),
      $onAction: vi.fn(),
      $dispose: vi.fn(),
      ...actions
    }
  }

  // 创建模拟路由
  static createMockRouter() {
    return {
      push: vi.fn(),
      replace: vi.fn(),
      go: vi.fn(),
      back: vi.fn(),
      forward: vi.fn(),
      addRoute: vi.fn(),
      removeRoute: vi.fn(),
      hasRoute: vi.fn(),
      getRoutes: vi.fn(),
      resolve: vi.fn(),
      beforeEach: vi.fn(),
      afterEach: vi.fn(),
      beforeResolve: vi.fn(),
      onError: vi.fn()
    }
  }

  // 创建模拟路由信息
  static createMockRoute(path = '/', params = {}, query = {}, hash = '') {
    return {
      path,
      params,
      query,
      hash,
      name: '',
      fullPath: path + (Object.keys(query).length ? '?' + new URLSearchParams(query).toString() : '') + hash,
      matched: [],
      meta: {}
    }
  }

  // 创建模拟 Element Plus 消息
  static createMockElMessage() {
    return {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn(),
      info: vi.fn()
    }
  }

  // 创建模拟 Element Plus 消息框
  static createMockElMessageBox() {
    return {
      confirm: vi.fn(),
      alert: vi.fn(),
      prompt: vi.fn()
    }
  }

  // 创建模拟 Element Plus 通知
  static createMockElNotification() {
    return {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn(),
      info: vi.fn()
    }
  }

  // 创建模拟 Element Plus 加载
  static createMockElLoading() {
    return {
      service: vi.fn(() => ({
        close: vi.fn()
      }))
    }
  }

  // 创建模拟本地存储
  static createMockLocalStorage() {
    const store: Record<string, string> = {}
    return {
      getItem: vi.fn((key: string) => store[key]),
      setItem: vi.fn((key: string, value: string) => {
        store[key] = value
      }),
      removeItem: vi.fn((key: string) => {
        delete store[key]
      }),
      clear: vi.fn(() => {
        Object.keys(store).forEach(key => delete store[key])
      }),
      key: vi.fn((index: number) => Object.keys(store)[index]),
      length: Object.keys(store).length
    }
  }

  // 创建模拟会话存储
  static createMockSessionStorage() {
    return this.createMockLocalStorage()
  }

  // 创建模拟文件
  static createMockFile(name: string, type: string, size: number = 1024) {
    const blob = new Blob(['test content'], { type })
    return new File([blob], name, { type })
  }

  // 创建模拟文件列表
  static createMockFileList(files: File[]) {
    const fileList = {
      length: files.length,
      item: (index: number) => files[index],
      [Symbol.iterator]: function* () {
        for (let i = 0; i < files.length; i++) {
          yield files[i]
        }
      }
    }
    return fileList as any
  }

  // 创建模拟拖拽事件
  static createMockDragEvent(type: string, dataTransfer?: DataTransfer) {
    return new Event(type, {
      bubbles: true,
      cancelable: true,
      ...dataTransfer && { dataTransfer }
    })
  }

  // 创建模拟键盘事件
  static createMockKeyboardEvent(type: string, key: string, options: KeyboardEventInit = {}) {
    return new KeyboardEvent(type, {
      key,
      bubbles: true,
      cancelable: true,
      ...options
    })
  }

  // 创建模拟鼠标事件
  static createMockMouseEvent(type: string, options: MouseEventInit = {}) {
    return new MouseEvent(type, {
      bubbles: true,
      cancelable: true,
      ...options
    })
  }

  // 创建模拟表单事件
  static createMockFormEvent(type: string, target: HTMLFormElement) {
    return new Event(type, {
      bubbles: true,
      cancelable: true,
      target
    })
  }

  // 创建模拟自定义事件
  static createMockCustomEvent(type: string, detail?: any) {
    return new CustomEvent(type, {
      bubbles: true,
      cancelable: true,
      detail
    })
  }

  // 创建模拟 ResizeObserver
  static createMockResizeObserver() {
    return vi.fn().mockImplementation(() => ({
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn()
    }))
  }

  // 创建模拟 IntersectionObserver
  static createMockIntersectionObserver() {
    return vi.fn().mockImplementation(() => ({
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn()
    }))
  }

  // 创建模拟 MutationObserver
  static createMockMutationObserver() {
    return vi.fn().mockImplementation(() => ({
      observe: vi.fn(),
      disconnect: vi.fn(),
      takeRecords: vi.fn(() => [])
    }))
  }

  // 创建模拟 PerformanceObserver
  static createMockPerformanceObserver() {
    return vi.fn().mockImplementation(() => ({
      observe: vi.fn(),
      disconnect: vi.fn()
    }))
  }

  // 创建模拟 MediaRecorder
  static createMockMediaRecorder() {
    return vi.fn().mockImplementation(() => ({
      start: vi.fn(),
      stop: vi.fn(),
      pause: vi.fn(),
      resume: vi.fn(),
      requestData: vi.fn(),
      ondataavailable: null,
      onerror: null,
      onpause: null,
      onresume: vi.fn(),
      onstart: vi.fn(),
      onstop: vi.fn()
    }))
  }

  // 创建模拟地理位置
  static createMockGeolocation() {
    return {
      getCurrentPosition: vi.fn(),
      watchPosition: vi.fn(),
      clearWatch: vi.fn()
    }
  }

  // 创建模拟通知
  static createMockNotification() {
    return {
      requestPermission: vi.fn(),
      permission: 'granted'
    }
  }

  // 创建模拟 Web Worker
  static createMockWorker() {
    return {
      postMessage: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      terminate: vi.fn(),
      onmessage: null,
      onerror: null
    }
  }

  // 创建模拟 WebSocket
  static createMockWebSocket() {
    return {
      send: vi.fn(),
      close: vi.fn(),
      onopen: null,
      onmessage: null,
      onerror: null,
      onclose: null,
      readyState: 1,
      bufferedAmount: 0,
      extensions: '',
      protocol: '',
      url: ''
    }
  }

  // 设置模拟响应延迟
  static createDelayedMock<T>(mockFn: Mock, delay: number, result: T) {
    return mockFn.mockImplementation(async () => {
      await new Promise(resolve => setTimeout(resolve, delay))
      return result
    })
  }

  // 设置模拟响应错误
  static createErrorMock<T>(mockFn: Mock, error: Error) {
    return mockFn.mockImplementation(async () => {
      throw error
    })
  }

  // 创建模拟进度事件
  static createMockProgressEvent(type: string, options: ProgressEventInit = {}) {
    return new ProgressEvent(type, {
      lengthComputable: true,
      loaded: 50,
      total: 100,
      ...options
    })
  }

  // 创建模拟定时器
  static createMockTimers() {
    return {
      setTimeout: vi.fn(),
      setInterval: vi.fn(),
      clearTimeout: vi.fn(),
      clearInterval: vi.fn(),
      setImmediate: vi.fn(),
      clearImmediate: vi.fn()
    }
  }

  // 创建模拟动画帧
  static createMockAnimationFrame() {
    return {
      requestAnimationFrame: vi.fn(),
      cancelAnimationFrame: vi.fn()
    }
  }

  // 创建模拟媒体查询
  static createMockMediaQueryList(matches: boolean = false) {
    return {
      matches,
      media: '',
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      onchange: null
    }
  }
}