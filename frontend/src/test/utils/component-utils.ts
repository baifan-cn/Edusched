import { mount, VueWrapper } from '@vue/test-utils'
import { createRouter, createWebHistory, Router } from 'vue-router'
import { createPinia, Pinia } from 'pinia'
import { nextTick } from 'vue'
import type { ComponentOptions } from 'vue'

// 组件测试工具类
export class ComponentUtils {
  // 创建测试路由
  static createTestRouter(routes: any[] = []): Router {
    return createRouter({
      history: createWebHistory(),
      routes: [
        {
          path: '/',
          component: { template: '<div></div>' }
        },
        ...routes
      ]
    })
  }

  // 创建测试 Pinia
  static createTestPinia(): Pinia {
    return createPinia()
  }

  // 创建测试组件挂载配置
  static createMountConfig(component: ComponentOptions, options: {
    props?: Record<string, any>
    slots?: Record<string, string>
    global?: {
      plugins?: any[]
      stubs?: Record<string, any>
      mocks?: Record<string, any>
      provide?: Record<string, any>
    }
  } = {}) {
    const config: any = {
      props: options.props || {},
      slots: options.slots || {},
      global: {
        plugins: [],
        stubs: {},
        mocks: {},
        provide: {},
        ...options.global
      }
    }

    // 添加默认插件
    if (!config.global.plugins.includes(createPinia())) {
      config.global.plugins.push(createPinia())
    }

    return config
  }

  // 挂载组件
  static mountComponent(component: ComponentOptions, options = {}) {
    const config = this.createMountConfig(component, options)
    return mount(component, config)
  }

  // 异步挂载组件
  static async mountComponentAsync(component: ComponentOptions, options = {}) {
    const wrapper = this.mountComponent(component, options)
    await nextTick()
    return wrapper
  }

  // 挂载带路由的组件
  static mountComponentWithRouter(component: ComponentOptions, routes: any[] = [], options = {}) {
    const router = this.createTestRouter(routes)
    const config = this.createMountConfig(component, {
      global: {
        plugins: [router],
        ...options.global
      },
      ...options
    })
    return mount(component, config)
  }

  // 挂载带 Pinia 的组件
  static mountComponentWithPinia(component: ComponentOptions, initialState = {}, options = {}) {
    const pinia = this.createTestPinia()

    // 如果需要设置初始状态，需要在 Pinia 创建后设置
    // 这里需要根据具体 store 进行设置

    const config = this.createMountConfig(component, {
      global: {
        plugins: [pinia],
        ...options.global
      },
      ...options
    })
    return mount(component, config)
  }

  // 等待组件更新
  static async waitForUpdate(wrapper: VueWrapper) {
    await nextTick()
    await wrapper.vm.$nextTick()
  }

  // 等待条件满足
  static async waitForCondition(condition: () => boolean, timeout = 5000, interval = 100) {
    const start = Date.now()

    while (Date.now() - start < timeout) {
      if (condition()) {
        return
      }
      await new Promise(resolve => setTimeout(resolve, interval))
    }

    throw new Error(`Condition not met within ${timeout}ms`)
  }

  // 等待元素出现
  static async waitForElement(wrapper: VueWrapper, selector: string, timeout = 5000) {
    return this.waitForCondition(() => wrapper.find(selector).exists(), timeout)
  }

  // 等待元素消失
  static async waitForElementDisappear(wrapper: VueWrapper, selector: string, timeout = 5000) {
    return this.waitForCondition(() => !wrapper.find(selector).exists(), timeout)
  }

  // 等待文本出现
  static async waitForText(wrapper: VueWrapper, text: string, timeout = 5000) {
    return this.waitForCondition(() => wrapper.text().includes(text), timeout)
  }

  // 触发事件
  static async triggerEvent(wrapper: VueWrapper, selector: string, event: string, options = {}) {
    const element = wrapper.find(selector)
    if (element.exists()) {
      await element.trigger(event, options)
    }
  }

  // 触发点击事件
  static async click(wrapper: VueWrapper, selector: string) {
    await this.triggerEvent(wrapper, selector, 'click')
  }

  // 触发输入事件
  static async input(wrapper: VueWrapper, selector: string, value: string) {
    const element = wrapper.find(selector)
    if (element.exists()) {
      await element.setValue(value)
    }
  }

  // 触发键盘事件
  static async keyPress(wrapper: VueWrapper, selector: string, key: string, options = {}) {
    await this.triggerEvent(wrapper, selector, 'keydown', { key, ...options })
  }

  // 触发鼠标事件
  static async mouseEvent(wrapper: VueWrapper, selector: string, event: string, options = {}) {
    await this.triggerEvent(wrapper, selector, event, options)
  }

  // 触发表单提交
  static async submitForm(wrapper: VueWrapper, selector: string = 'form') {
    await this.triggerEvent(wrapper, selector, 'submit.prevent')
  }

  // 获取组件属性
  static getProps(wrapper: VueWrapper, prop?: string) {
    return wrapper.props(prop)
  }

  // 设置组件属性
  static async setProps(wrapper: VueWrapper, props: Record<string, any>) {
    await wrapper.setProps(props)
  }

  // 获取组件数据
  static getData(wrapper: VueWrapper, key?: string) {
    return wrapper.vm.$data
  }

  // 设置组件数据
  static async setData(wrapper: VueWrapper, data: Record<string, any>) {
    await wrapper.setData(data)
  }

  // 调用组件方法
  static callMethod(wrapper: VueWrapper, methodName: string, ...args: any[]) {
    if (wrapper.vm[methodName]) {
      return wrapper.vm[methodName](...args)
    }
    throw new Error(`Method ${methodName} not found`)
  }

  // 获取计算属性
  static getComputed(wrapper: VueWrapper, propName: string) {
    return wrapper.vm[propName]
  }

  // 检查元素是否存在
  static exists(wrapper: VueWrapper, selector: string) {
    return wrapper.find(selector).exists()
  }

  // 检查元素可见性
  static isVisible(wrapper: VueWrapper, selector: string) {
    const element = wrapper.find(selector)
    return element.exists() && element.isVisible()
  }

  // 检查元素是否禁用
  static isDisabled(wrapper: VueWrapper, selector: string) {
    const element = wrapper.find(selector)
    return element.exists() && element.attributes('disabled') !== undefined
  }

  // 检查元素是否选中
  static isChecked(wrapper: VueWrapper, selector: string) {
    const element = wrapper.find(selector)
    return element.exists() && element.element.checked
  }

  // 获取元素文本
  static getText(wrapper: VueWrapper, selector: string) {
    const element = wrapper.find(selector)
    return element.exists() ? element.text() : ''
  }

  // 获取元素属性
  static getAttribute(wrapper: VueWrapper, selector: string, attr: string) {
    const element = wrapper.find(selector)
    return element.exists() ? element.attributes(attr) : undefined
  }

  // 获取元素类名
  static getClasses(wrapper: VueWrapper, selector: string) {
    const element = wrapper.find(selector)
    return element.exists() ? element.classes() : []
  }

  // 检查元素是否包含类名
  static hasClass(wrapper: VueWrapper, selector: string, className: string) {
    const classes = this.getClasses(wrapper, selector)
    return classes.includes(className)
  }

  // 获取元素样式
  static getStyle(wrapper: VueWrapper, selector: string) {
    const element = wrapper.find(selector)
    return element.exists() ? element.attributes('style') : undefined
  }

  // 查找所有匹配的元素
  static findAll(wrapper: VueWrapper, selector: string) {
    return wrapper.findAll(selector)
  }

  // 获取元素数量
  static count(wrapper: VueWrapper, selector: string) {
    return wrapper.findAll(selector).length
  }

  // 检查表单验证状态
  static async checkFormValidation(wrapper: VueWrapper, formSelector: string = 'form') {
    const form = wrapper.find(formSelector)
    if (!form.exists()) {
      throw new Error('Form not found')
    }

    // 触发表单验证
    await form.trigger('submit.prevent')

    // 检查验证错误
    const errors = wrapper.findAll('.el-form-item__error')
    return {
      isValid: errors.length === 0,
      errors: errors.map(error => error.text())
    }
  }

  // 模拟文件上传
  static async simulateFileUpload(wrapper: VueWrapper, selector: string, files: File[]) {
    const input = wrapper.find(selector)
    if (input.exists()) {
      await input.setValue(files)
    }
  }

  // 模拟拖拽
  static async simulateDragAndDrop(wrapper: VueWrapper, dragSelector: string, dropSelector: string) {
    const dragElement = wrapper.find(dragSelector)
    const dropElement = wrapper.find(dropSelector)

    if (dragElement.exists() && dropElement.exists()) {
      await dragElement.trigger('dragstart')
      await dropElement.trigger('dragover')
      await dropElement.trigger('drop')
    }
  }

  // 模拟滚动
  static async simulateScroll(wrapper: VueWrapper, selector: string, scrollOptions: ScrollToOptions) {
    const element = wrapper.find(selector)
    if (element.exists()) {
      await element.element.scrollTo(scrollOptions)
      await element.trigger('scroll')
    }
  }

  // 模拟窗口大小变化
  static async simulateResize(width: number, height: number) {
    window.innerWidth = width
    window.innerHeight = height
    window.dispatchEvent(new Event('resize'))
    await nextTick()
  }

  // 清理组件
  static unmount(wrapper: VueWrapper) {
    wrapper.unmount()
  }

  // 批量测试用例
  static createTestCases(testCases: Array<{
    name: string
    selector: string
    expected: any
    action?: () => Promise<void>
  }>) {
    return testCases.map(testCase => ({
      ...testCase,
      test: async (wrapper: VueWrapper) => {
        if (testCase.action) {
          await testCase.action()
        }
        return testCase.expected
      }
    }))
  }

  // 创建快照测试
  static async createSnapshot(wrapper: VueWrapper, name?: string) {
    const html = wrapper.html()
    expect(html).toMatchSnapshot(name)
  }

  // 创建组件快照
  static async createComponentSnapshot(wrapper: VueWrapper, name?: string) {
    const snapshot = {
      props: wrapper.props(),
      data: wrapper.vm.$data,
      computed: Object.keys(wrapper.vm.$options.computed || {}).reduce((acc, key) => {
        acc[key] = wrapper.vm[key]
        return acc
      }, {} as any)
    }
    expect(snapshot).toMatchSnapshot(name)
  }
}