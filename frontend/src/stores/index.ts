import { createPinia } from 'pinia'
import type { App } from 'vue'

// 创建Pinia实例
const pinia = createPinia()

// 定义store的类型
export interface State {
  // 全局状态
  app: {
    loading: boolean
    sidebar: {
      opened: boolean
      withoutAnimation: boolean
    }
    device: 'desktop' | 'mobile'
    size: 'large' | 'default' | 'small'
    theme: 'light' | 'dark'
  }

  // 用户状态
  user: {
    token: string
    userInfo: {
      id: string
      username: string
      email: string
      first_name: string
      last_name: string
      role: string
      avatar?: string
      permissions: string[]
    } | null
    tenantId: string
  }

  // 系统配置
  config: {
    appName: string
    appVersion: string
    apiVersion: string
    maintenance: boolean
    features: Record<string, boolean>
  }
}

// 插件：持久化存储
export const createPersistedState = () => {
  return ({ store }: { store: any }) => {
    // 从localStorage恢复状态
    const savedState = localStorage.getItem(`store_${store.$id}`)
    if (savedState) {
      try {
        store.$patch(JSON.parse(savedState))
      } catch (error) {
        console.error(`Failed to restore store ${store.$id}:`, error)
      }
    }

    // 订阅状态变化并保存到localStorage
    store.$subscribe(
      (mutation: any, state: any) => {
        try {
          localStorage.setItem(`store_${store.$id}`, JSON.stringify(state))
        } catch (error) {
          console.error(`Failed to persist store ${store.$id}:`, error)
        }
      },
      { detached: true }
    )
  }
}

// 插件：错误处理
export const createErrorHandler = () => {
  return ({ store }: { store: any }) => {
    store.$onAction(
      ({
        name,
        after,
        onError
      }: {
        name: string
        after: (callback: () => void) => void
        onError: (callback: (error: Error) => void) => void
      }) => {
        after((result: any) => {
          console.log(`✅ [${store.$id}] Action "${name}" completed`, result)
        })

        onError((error: Error) => {
          console.error(`❌ [${store.$id}] Action "${name}" failed:`, error)
          // 可以在这里添加错误上报逻辑
        })
      }
    )
  }
}

// 安装Pinia到Vue应用
export const setupPinia = (app: App) => {
  app.use(pinia)

  // 注册插件
  pinia.use(createPersistedState())
  pinia.use(createErrorHandler())

  return pinia
}

export default pinia