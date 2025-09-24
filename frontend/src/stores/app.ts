import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 设备类型
type DeviceType = 'desktop' | 'mobile' | 'tablet'

// 主题类型
type ThemeType = 'light' | 'dark' | 'auto'

// 尺寸类型
type SizeType = 'large' | 'default' | 'small'

export const useAppStore = defineStore('app', () => {
  // 状态
  const loading = ref(false)
  const sidebar = ref({
    opened: true,
    withoutAnimation: false
  })
  const device = ref<DeviceType>('desktop')
  const size = ref<SizeType>('default')
  const theme = ref<ThemeType>('light')
  const cachedViews = ref<string[]>([])
  const visitedViews = ref<Array<{ path: string; name: string; title: string }>>([])

  // 计算属性
  const isMobile = computed(() => device.value === 'mobile')
  const isDesktop = computed(() => device.value === 'desktop')
  const sidebarOpened = computed(() => sidebar.value.opened)
  const currentTheme = computed(() => theme.value)

  // 动作
  const setLoading = (status: boolean) => {
    loading.value = status
  }

  const toggleSidebar = (withoutAnimation?: boolean) => {
    sidebar.value.opened = !sidebar.value.opened
    sidebar.value.withoutAnimation = withoutAnimation || false
  }

  const closeSidebar = (withoutAnimation?: boolean) => {
    sidebar.value.opened = false
    sidebar.value.withoutAnimation = withoutAnimation || false
  }

  const openSidebar = (withoutAnimation?: boolean) => {
    sidebar.value.opened = true
    sidebar.value.withoutAnimation = withoutAnimation || false
  }

  const toggleDevice = (deviceType: DeviceType) => {
    device.value = deviceType
  }

  const setSize = (sizeType: SizeType) => {
    size.value = sizeType
  }

  const setTheme = (themeType: ThemeType) => {
    theme.value = themeType
    // 应用主题到DOM
    if (themeType === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  const addCachedView = (view: string) => {
    if (!cachedViews.value.includes(view)) {
      cachedViews.value.push(view)
    }
  }

  const removeCachedView = (view: string) => {
    const index = cachedViews.value.indexOf(view)
    if (index > -1) {
      cachedViews.value.splice(index, 1)
    }
  }

  const addVisitedView = (view: { path: string; name: string; title: string }) => {
    const exists = visitedViews.value.find(v => v.path === view.path)
    if (!exists) {
      visitedViews.value.push(view)
    }
  }

  const removeVisitedView = (path: string) => {
    visitedViews.value = visitedViews.value.filter(v => v.path !== path)
  }

  const clearCachedViews = () => {
    cachedViews.value = []
  }

  const clearVisitedViews = () => {
    visitedViews.value = []
  }

  // 监听系统主题变化
  const watchSystemTheme = () => {
    if (theme.value === 'auto') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      const handleChange = (e: MediaQueryListEvent) => {
        if (e.matches) {
          document.documentElement.classList.add('dark')
        } else {
          document.documentElement.classList.remove('dark')
        }
      }

      // 初始设置
      if (mediaQuery.matches) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }

      // 监听变化
      mediaQuery.addEventListener('change', handleChange)

      // 返回清理函数
      return () => {
        mediaQuery.removeEventListener('change', handleChange)
      }
    }
  }

  // 初始化
  const init = () => {
    // 从localStorage恢复主题
    const savedTheme = localStorage.getItem('theme') as ThemeType
    if (savedTheme) {
      setTheme(savedTheme)
    }

    // 检测设备类型
    const checkDevice = () => {
      const width = window.innerWidth
      if (width < 768) {
        toggleDevice('mobile')
      } else if (width < 1024) {
        toggleDevice('tablet')
      } else {
        toggleDevice('desktop')
      }
    }

    checkDevice()
    window.addEventListener('resize', checkDevice)

    // 监听系统主题
    const cleanupTheme = watchSystemTheme()

    // 返回清理函数
    return () => {
      window.removeEventListener('resize', checkDevice)
      cleanupTheme?.()
    }
  }

  return {
    // 状态
    loading,
    sidebar,
    device,
    size,
    theme,
    cachedViews,
    visitedViews,

    // 计算属性
    isMobile,
    isDesktop,
    sidebarOpened,
    currentTheme,

    // 动作
    setLoading,
    toggleSidebar,
    closeSidebar,
    openSidebar,
    toggleDevice,
    setSize,
    setTheme,
    addCachedView,
    removeCachedView,
    addVisitedView,
    removeVisitedView,
    clearCachedViews,
    clearVisitedViews,
    init
  }
})