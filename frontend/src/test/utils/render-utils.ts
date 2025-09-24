import { render, RenderResult } from '@vue/test-utils'
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'

// 渲染工具类
export class RenderUtils {
  // 创建测试应用
  static createTestApp() {
    const app = createApp({})
    const pinia = createPinia()
    const router = createRouter({
      history: createWebHistory(),
      routes: [
        {
          path: '/',
          component: { template: '<div></div>' }
        }
      ]
    })

    app.use(pinia)
    app.use(router)
    app.use(ElementPlus)

    return { app, pinia, router }
  }

  // 渲染组件
  static renderComponent(component: any, options: any = {}) {
    const { app, pinia, router } = this.createTestApp()

    const defaultOptions = {
      global: {
        plugins: [pinia, router],
        stubs: this.getDefaultStubs(),
        mocks: this.getDefaultMocks(),
        provide: this.getDefaultProvide()
      }
    }

    const mergedOptions = this.mergeOptions(defaultOptions, options)

    return render(component, mergedOptions)
  }

  // 渲染带路由的组件
  static renderComponentWithRouter(component: any, routes: any[] = [], options: any = {}) {
    const router = createRouter({
      history: createWebHistory(),
      routes: [
        {
          path: '/',
          component: { template: '<div></div>' }
        },
        ...routes
      ]
    })

    const { app, pinia } = this.createTestApp()

    const defaultOptions = {
      global: {
        plugins: [pinia, router],
        stubs: this.getDefaultStubs(),
        mocks: this.getDefaultMocks(),
        provide: this.getDefaultProvide()
      }
    }

    const mergedOptions = this.mergeOptions(defaultOptions, options)

    return render(component, mergedOptions)
  }

  // 渲染完整页面
  static renderPage(component: any, options: any = {}) {
    const { app, pinia, router } = this.createTestApp()

    const defaultOptions = {
      global: {
        plugins: [pinia, router],
        stubs: this.getPageStubs(),
        mocks: this.getPageMocks(),
        provide: this.getPageProvide()
      }
    }

    const mergedOptions = this.mergeOptions(defaultOptions, options)

    return render(component, mergedOptions)
  }

  // 渲染弹窗组件
  static renderModal(component: any, options: any = {}) {
    const defaultOptions = {
      props: {
        modelValue: true
      },
      global: {
        stubs: this.getModalStubs(),
        mocks: this.getModalMocks(),
        provide: this.getModalProvide()
      }
    }

    const mergedOptions = this.mergeOptions(defaultOptions, options)

    return render(component, mergedOptions)
  }

  // 渲染表单组件
  static renderForm(component: any, formData: any = {}, options: any = {}) {
    const defaultOptions = {
      props: {
        modelValue: formData
      },
      global: {
        stubs: this.getFormStubs(),
        mocks: this.getFormMocks(),
        provide: this.getFormProvide()
      }
    }

    const mergedOptions = this.mergeOptions(defaultOptions, options)

    return render(component, mergedOptions)
  }

  // 渲染表格组件
  static renderTable(component: any, tableData: any[] = [], options: any = {}) {
    const defaultOptions = {
      props: {
        data: tableData
      },
      global: {
        stubs: this.getTableStubs(),
        mocks: this.getTableMocks(),
        provide: this.getTableProvide()
      }
    }

    const mergedOptions = this.mergeOptions(defaultOptions, options)

    return render(component, mergedOptions)
  }

  // 渲染图表组件
  static renderChart(component: any, chartData: any = {}, options: any = {}) {
    const defaultOptions = {
      props: {
        data: chartData
      },
      global: {
        stubs: this.getChartStubs(),
        mocks: this.getChartMocks(),
        provide: this.getChartProvide()
      }
    }

    const mergedOptions = this.mergeOptions(defaultOptions, options)

    return render(component, mergedOptions)
  }

  // 获取默认 stubs
  static getDefaultStubs() {
    return {
      'el-button': true,
      'el-input': true,
      'el-select': true,
      'el-option': true,
      'el-form': true,
      'el-form-item': true,
      'el-table': true,
      'el-table-column': true,
      'el-dialog': true,
      'el-drawer': true,
      'el-menu': true,
      'el-menu-item': true,
      'el-sub-menu': true,
      'el-tabs': true,
      'el-tab-pane': true,
      'el-pagination': true,
      'el-card': true,
      'el-row': true,
      'el-col': true,
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
      'el-result': true
    }
  }

  // 获取页面 stubs
  static getPageStubs() {
    return {
      ...this.getDefaultStubs(),
      'router-view': true,
      'router-link': true,
      'nuxt-link': true
    }
  }

  // 获取弹窗 stubs
  static getModalStubs() {
    return {
      'el-dialog': true,
      'el-drawer': true,
      'el-overlay': true,
      'el-message-box': true,
      'el-notification': true
    }
  }

  // 获取表单 stubs
  static getFormStubs() {
    return {
      'el-form': true,
      'el-form-item': true,
      'el-input': true,
      'el-input-number': true,
      'el-select': true,
      'el-option': true,
      'el-cascader': true,
      'el-switch': true,
      'el-checkbox': true,
      'el-checkbox-group': true,
      'el-radio': true,
      'el-radio-group': true,
      'el-date-picker': true,
      'el-time-picker': true,
      'el-color-picker': true,
      'el-slider': true,
      'el-rate': true,
      'el-upload': true,
      'el-transfer': true,
      'el-autocomplete': true
    }
  }

  // 获取表格 stubs
  static getTableStubs() {
    return {
      'el-table': true,
      'el-table-column': true,
      'el-pagination': true,
      'el-tag': true,
      'el-button': true,
      'el-input': true,
      'el-select': true,
      'el-option': true,
      'el-tooltip': true,
      'el-popover': true,
      'el-dropdown': true,
      'el-dropdown-menu': true,
      'el-dropdown-item': true,
      'el-progress': true
    }
  }

  // 获取图表 stubs
  static getChartStubs() {
    return {
      'v-chart': true,
      'echarts': true,
      'el-progress': true,
      'el-statistic': true,
      'el-calendar': true
    }
  }

  // 获取默认 mocks
  static getDefaultMocks() {
    return {
      $router: {
        push: vi.fn(),
        replace: vi.fn(),
        go: vi.fn(),
        back: vi.fn(),
        forward: vi.fn()
      },
      $route: {
        path: '/',
        params: {},
        query: {},
        hash: '',
        name: '',
        fullPath: '/',
        matched: [],
        meta: {}
      },
      $t: (key: string) => key,
      $i18n: {
        locale: 'zh-CN',
        availableLocales: ['zh-CN', 'en-US']
      }
    }
  }

  // 获取页面 mocks
  static getPageMocks() {
    return {
      ...this.getDefaultMocks(),
      $store: {},
      $auth: {
        user: null,
        token: null,
        isAuthenticated: false
      }
    }
  }

  // 获取弹窗 mocks
  static getModalMocks() {
    return {
      ...this.getDefaultMocks(),
      $message: {
        success: vi.fn(),
        error: vi.fn(),
        warning: vi.fn(),
        info: vi.fn()
      },
      $confirm: vi.fn(),
      $alert: vi.fn(),
      $prompt: vi.fn()
    }
  }

  // 获取表单 mocks
  static getFormMocks() {
    return {
      ...this.getDefaultMocks(),
      $refs: {},
      $form: {
        validate: vi.fn(),
        validateField: vi.fn(),
        resetFields: vi.fn(),
        clearValidate: vi.fn()
      }
    }
  }

  // 获取表格 mocks
  static getTableMocks() {
    return {
      ...this.getDefaultMocks(),
      $refs: {
        tableRef: {
          clearSelection: vi.fn(),
          toggleRowSelection: vi.fn(),
          toggleAllSelection: vi.fn(),
          toggleRowExpansion: vi.fn(),
          setCurrentRow: vi.fn(),
          clearSort: vi.fn(),
          clearFilter: vi.fn(),
          doLayout: vi.fn(),
          sort: vi.fn(),
          filter: vi.fn()
        }
      }
    }
  }

  // 获取图表 mocks
  static getChartMocks() {
    return {
      ...this.getDefaultMocks(),
      $echarts: {
        init: vi.fn(),
        setOption: vi.fn(),
        resize: vi.fn(),
        dispose: vi.fn()
      }
    }
  }

  // 获取默认 provide
  static getDefaultProvide() {
    return {
      app: createApp({}),
      router: createRouter({
        history: createWebHistory(),
        routes: []
      }),
      pinia: createPinia()
    }
  }

  // 获取页面 provide
  static getPageProvide() {
    return {
      ...this.getDefaultProvide(),
      auth: {
        user: null,
        token: null,
        login: vi.fn(),
        logout: vi.fn()
      }
    }
  }

  // 获取弹窗 provide
  static getModalProvide() {
    return {
      ...this.getDefaultProvide(),
      dialog: {
        open: vi.fn(),
        close: vi.fn()
      }
    }
  }

  // 获取表单 provide
  static getFormProvide() {
    return {
      ...this.getDefaultProvide(),
      form: {
        validate: vi.fn(),
        reset: vi.fn(),
        submit: vi.fn()
      }
    }
  }

  // 获取表格 provide
  static getTableProvide() {
    return {
      ...this.getDefaultProvide(),
      table: {
        refresh: vi.fn(),
        filter: vi.fn(),
        sort: vi.fn(),
        export: vi.fn()
      }
    }
  }

  // 获取图表 provide
  static getChartProvide() {
    return {
      ...this.getDefaultProvide(),
      chart: {
        update: vi.fn(),
        resize: vi.fn(),
        export: vi.fn()
      }
    }
  }

  // 合并选项
  static mergeOptions(defaultOptions: any, customOptions: any) {
    return {
      ...defaultOptions,
      ...customOptions,
      props: {
        ...defaultOptions.props,
        ...customOptions.props
      },
      global: {
        ...defaultOptions.global,
        ...customOptions.global,
        plugins: [
          ...(defaultOptions.global?.plugins || []),
          ...(customOptions.global?.plugins || [])
        ],
        stubs: {
          ...defaultOptions.global?.stubs,
          ...customOptions.global?.stubs
        },
        mocks: {
          ...defaultOptions.global?.mocks,
          ...customOptions.global?.mocks
        },
        provide: {
          ...defaultOptions.global?.provide,
          ...customOptions.global?.provide
        }
      }
    }
  }

  // 创建快照渲染器
  static createSnapshotRenderer(component: any, options: any = {}) {
    const { html } = this.renderComponent(component, options)
    return html
  }

  // 创建渲染测试
  static createRenderTest(component: any, options: any = {}) {
    return {
      name: 'render test',
      test: () => {
        const { html } = this.renderComponent(component, options)
        expect(html).toMatchSnapshot()
      }
    }
  }

  // 创建属性测试
  static createPropsTest(component: any, props: any, expectedBehavior: () => void) {
    return {
      name: 'props test',
      test: () => {
        const wrapper = this.renderComponent(component, { props })
        expectedBehavior()
      }
    }
  }

  // 创建事件测试
  static createEventTest(component: any, eventName: string, eventHandler: () => void) {
    return {
      name: 'event test',
      test: async () => {
        const wrapper = this.renderComponent(component)
        await wrapper.vm.$emit(eventName)
        expect(eventHandler).toHaveBeenCalled()
      }
    }
  }

  // 创建插槽测试
  static createSlotTest(component: any, slotName: string, slotContent: string) {
    return {
      name: 'slot test',
      test: () => {
        const wrapper = this.renderComponent(component, {
          slots: {
            [slotName]: slotContent
          }
        })
        expect(wrapper.html()).toContain(slotContent)
      }
    }
  }
}