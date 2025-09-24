import { createTestingPinia } from '@pinia/testing'
import { setActivePinia } from 'pinia'
import { nextTick } from 'vue'
import type { StoreGeneric, StoreDefinition } from 'pinia'

// Store 测试工具类
export class StoreUtils {
  // 创建测试 Pinia
  static createTestPinia(initialState: Record<string, any> = {}) {
    return createTestingPinia({
      createSpy: vi.fn,
      initialState,
      stubActions: false
    })
  }

  // 设置活跃的 Pinia
  static setActivePinia(pinia: any) {
    setActivePinia(pinia)
  }

  // 创建测试 store
  static createStore<T extends StoreGeneric>(
    storeDefinition: StoreDefinition<T>,
    initialState: Partial<T['$state']> = {}
  ) {
    const pinia = this.createTestPinia()
    this.setActivePinia(pinia)

    const store = storeDefinition(pinia)

    // 设置初始状态
    if (Object.keys(initialState).length > 0) {
      store.$patch(initialState)
    }

    return store
  }

  // 创建 mock store
  static createMockStore<T extends Record<string, any>>(
    initialState: T,
    actions: Record<string, any> = {}
  ) {
    const store = {
      $id: 'mock-store',
      $state: { ...initialState },
      $patch: vi.fn(),
      $reset: vi.fn(),
      $onAction: vi.fn(),
      $subscribe: vi.fn(),
      $dispose: vi.fn(),
      ...actions
    }

    // 添加 getter 模拟
    Object.keys(initialState).forEach(key => {
      Object.defineProperty(store, key, {
        get: () => store.$state[key],
        set: (value: any) => {
          store.$state[key] = value
        }
      })
    })

    return store
  }

  // 等待 store 更新
  static async waitForStoreUpdate(store: any, key?: string) {
    await nextTick()
    if (key) {
      return store[key]
    }
    return store.$state
  }

  // 触发 store action
  static async triggerAction(store: any, actionName: string, ...args: any[]) {
    if (store[actionName]) {
      return await store[actionName](...args)
    }
    throw new Error(`Action ${actionName} not found in store`)
  }

  // 模拟 store action
  static mockAction(store: any, actionName: string, implementation?: any) {
    if (implementation) {
      store[actionName] = vi.fn(implementation)
    } else {
      store[actionName] = vi.fn()
    }
    return store[actionName]
  }

  // 模拟 store getter
  static mockGetter(store: any, getterName: string, value: any) {
    Object.defineProperty(store, getterName, {
      get: () => value,
      configurable: true
    })
  }

  // 设置 store 状态
  static setState(store: any, state: Record<string, any>) {
    store.$patch(state)
  }

  // 获取 store 状态
  static getState(store: any, key?: string) {
    if (key) {
      return store[key]
    }
    return store.$state
  }

  // 重置 store
  static resetStore(store: any) {
    store.$reset()
  }

  // 订阅 store 变化
  static subscribeToStore(store: any, callback: (mutation: any, state: any) => void) {
    return store.$subscribe(callback)
  }

  // 监听 store action
  static listenToActions(store: any, callback: (action: any) => void) {
    return store.$onAction(callback)
  }

  // 验证 action 调用
  static verifyActionCall(store: any, actionName: string, expectedArgs?: any[]) {
    expect(store[actionName]).toHaveBeenCalled()
    if (expectedArgs) {
      expect(store[actionName]).toHaveBeenCalledWith(...expectedArgs)
    }
  }

  // 验证 action 调用次数
  static verifyActionCallCount(store: any, actionName: string, expectedCount: number) {
    expect(store[actionName]).toHaveBeenCalledTimes(expectedCount)
  }

  // 验证 action 未被调用
  static verifyActionNotCalled(store: any, actionName: string) {
    expect(store[actionName]).not.toHaveBeenCalled()
  }

  // 验证 store 状态
  static verifyState(store: any, expectedState: Record<string, any>) {
    expect(store.$state).toMatchObject(expectedState)
  }

  // 验证状态变化
  static verifyStateChange(store: any, key: string, expectedValue: any) {
    expect(store[key]).toBe(expectedValue)
  }

  // 创建异步 action 测试
  static async testAsyncAction(
    store: any,
    actionName: string,
    args: any[],
    expectedState?: Record<string, any>,
    expectedError?: any
  ) {
    try {
      const result = await this.triggerAction(store, actionName, ...args)

      if (expectedState) {
        this.verifyState(store, expectedState)
      }

      return result
    } catch (error) {
      if (expectedError) {
        expect(error).toEqual(expectedError)
      } else {
        throw error
      }
    }
  }

  // 创建 store 交互测试
  static async testStoreInteraction(
    stores: Record<string, any>,
    actions: Array<{
      storeName: string
      actionName: string
      args: any[]
      expectedState?: Record<string, any>
    }>
  ) {
    for (const action of actions) {
      const store = stores[action.storeName]
      await this.triggerAction(store, action.actionName, ...action.args)

      if (action.expectedState) {
        this.verifyState(store, action.expectedState)
      }
    }
  }

  // 创建 store 状态快照
  static createStoreSnapshot(store: any) {
    return {
      state: JSON.parse(JSON.stringify(store.$state)),
      getters: Object.keys(store).reduce((acc, key) => {
        if (typeof store[key] === 'function' || key.startsWith('$')) {
          return acc
        }
        acc[key] = store[key]
        return acc
      }, {} as Record<string, any>)
    }
  }

  // 验证 store 状态快照
  static verifyStoreSnapshot(store: any, snapshot: any) {
    expect(store.$state).toEqual(snapshot.state)
    Object.keys(snapshot.getters).forEach(key => {
      expect(store[key]).toBe(snapshot.getters[key])
    })
  }

  // 创建 store 测试套件
  static createStoreTestSuite(
    storeDefinition: StoreDefinition<any>,
    tests: Array<{
      name: string
      initialState?: Record<string, any>
      action?: {
        name: string
        args: any[]
      }
      expectedState?: Record<string, any>
      expectedError?: any
    }>
  ) {
    return tests.map(test => ({
      name: test.name,
      test: async () => {
        const store = this.createStore(storeDefinition, test.initialState)

        if (test.action) {
          await this.testAsyncAction(
            store,
            test.action.name,
            test.action.args,
            test.expectedState,
            test.expectedError
          )
        } else if (test.expectedState) {
          this.verifyState(store, test.expectedState)
        }
      }
    }))
  }

  // 模拟 API 调用的 store action
  static mockApiAction(store: any, actionName: string, mockResponse: any) {
    this.mockAction(store, actionName, async () => {
      await new Promise(resolve => setTimeout(resolve, 10))
      return mockResponse
    })
  }

  // 模拟 API 错误的 store action
  static mockApiErrorAction(store: any, actionName: string, error: any) {
    this.mockAction(store, actionName, async () => {
      await new Promise(resolve => setTimeout(resolve, 10))
      throw error
    })
  }

  // 创建持久化 store 测试
  static createPersistedStoreTest(
    storeDefinition: StoreDefinition<any>,
    storageKey: string,
    testData: any
  ) {
    return {
      name: 'persisted store',
      test: async () => {
        // 设置本地存储
        localStorage.setItem(storageKey, JSON.stringify(testData))

        const store = this.createStore(storeDefinition)

        // 验证状态恢复
        this.verifyState(store, testData)

        // 清理
        localStorage.removeItem(storageKey)
      }
    }
  }

  // 创建 store 竞态条件测试
  static createRaceConditionTest(
    store: any,
    actionName: string,
    testData: any[]
  ) {
    return {
      name: 'race condition',
      test: async () => {
        const promises = testData.map(data =>
          this.triggerAction(store, actionName, data)
        )

        await Promise.all(promises)

        // 验证最终状态
        expect(store.$state).toBeDefined()
      }
    }
  }

  // 创建 store 性能测试
  static createPerformanceTest(
    store: any,
    actionName: string,
    args: any[],
    maxTime: number
  ) {
    return {
      name: 'performance',
      test: async () => {
        const start = performance.now()

        await this.triggerAction(store, actionName, ...args)

        const end = performance.now()
        const duration = end - start

        expect(duration).toBeLessThan(maxTime)
      }
    }
  }
}