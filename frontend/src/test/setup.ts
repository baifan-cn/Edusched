import { vi, beforeEach, afterEach } from 'vitest'
import { config } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'

// 全局模拟
vi.mock('axios', () => ({
  default: {
    create: () => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      }
    })
  }
}))

// 全局测试配置
config.global.stubs = {
  'el-button': true,
  'el-input': true,
  'el-form': true,
  'el-form-item': true,
  'el-table': true,
  'el-table-column': true,
  'el-dialog': true,
  'el-select': true,
  'el-option': true,
  'el-date-picker': true,
  'el-time-picker': true,
  'el-switch': true,
  'el-checkbox': true,
  'el-checkbox-group': true,
  'el-radio': true,
  'el-radio-group': true,
  'el-upload': true,
  'el-card': true,
  'el-row': true,
  'el-col': true,
  'el-icon': true,
  'el-menu': true,
  'el-menu-item': true,
  'el-sub-menu': true,
  'el-tabs': true,
  'el-tab-pane': true,
  'el-pagination': true,
  'el-divider': true,
  'el-tag': true,
  'el-badge': true,
  'el-alert': true,
  'el-progress': true,
  'el-tooltip': true,
  'el-popover': true,
  'el-dropdown': true,
  'el-dropdown-menu': true,
  'el-dropdown-item': true,
  'el-steps': true,
  'el-step': true,
  'el-timeline': true,
  'el-timeline-item': true,
  'el-calendar': true,
  'el-statistic': true,
  'el-empty': true,
  'el-result': true,
}

// 模拟 Pinia store
config.global.plugins = [createTestingPinia({ createSpy: vi.fn })]

// 模拟 Vue Router
const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  go: vi.fn(),
  back: vi.fn(),
  forward: vi.fn()
}

config.global.mocks = {
  $router: mockRouter,
  $route: { params: {}, query: {} }
}

// 模拟 Element Plus 消息
global.ElMessage = {
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn(),
  info: vi.fn()
}

global.ElMessageBox = {
  confirm: vi.fn(),
  alert: vi.fn(),
  prompt: vi.fn()
}

global.ElNotification = {
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn(),
  info: vi.fn()
}

global.ElLoading = {
  service: vi.fn()
}

// 模拟 window 对象
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// 模拟 ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// 模拟 IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// 测试配置
beforeEach(() => {
  // 清理所有mock
  vi.clearAllMocks()
})

afterEach(() => {
  // 清理所有mock
  vi.clearAllMocks()
})

// 导出测试工具
export const createMockStore = (state = {}) => ({
  state: { ...state },
  getters: {},
  actions: {},
})

export const createMockRouter = () => ({
  push: vi.fn(),
  replace: vi.fn(),
  go: vi.fn(),
  back: vi.fn(),
  forward: vi.fn(),
})

export const createMockRoute = (path = '/', params = {}, query = {}) => ({
  path,
  params,
  query,
  hash: '',
  name: '',
  fullPath: path,
  matched: [],
  meta: {},
})

export const waitForNextTick = () => new Promise(resolve => setTimeout(resolve, 0))

export const flushPromises = () => new Promise(resolve => setImmediate(resolve))

export const createMockAxios = () => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
  patch: vi.fn(),
})

export const createMockResponse = (data: any, status = 200) => ({
  data,
  status,
  statusText: 'OK',
  headers: {},
  config: {},
})

export const createMockErrorResponse = (error: any, status = 400) => ({
  response: {
    data: error,
    status,
    statusText: 'Error',
    headers: {},
    config: {},
  },
})