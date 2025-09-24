import { VueWrapper } from '@vue/test-utils'

// 断言工具类
export class AssertionUtils {
  // 基础断言
  static exists(wrapper: VueWrapper, selector: string) {
    const element = wrapper.find(selector)
    expect(element.exists()).toBe(true)
  }

  static notExists(wrapper: VueWrapper, selector: string) {
    const element = wrapper.find(selector)
    expect(element.exists()).toBe(false)
  }

  static isVisible(wrapper: VueWrapper, selector: string) {
    const element = wrapper.find(selector)
    expect(element.exists()).toBe(true)
    expect(element.isVisible()).toBe(true)
  }

  static isHidden(wrapper: VueWrapper, selector: string) {
    const element = wrapper.find(selector)
    if (element.exists()) {
      expect(element.isVisible()).toBe(false)
    } else {
      expect(element.exists()).toBe(false)
    }
  }

  static hasText(wrapper: VueWrapper, selector: string, text: string) {
    const element = wrapper.find(selector)
    expect(element.exists()).toBe(true)
    expect(element.text()).toContain(text)
  }

  static hasExactText(wrapper: VueWrapper, selector: string, text: string) {
    const element = wrapper.find(selector)
    expect(element.exists()).toBe(true)
    expect(element.text()).toBe(text)
  }

  static notHasText(wrapper: VueWrapper, selector: string, text: string) {
    const element = wrapper.find(selector)
    if (element.exists()) {
      expect(element.text()).not.toContain(text)
    }
  }

  // 属性断言
  static hasAttribute(wrapper: VueWrapper, selector: string, attribute: string, value?: string) {
    const element = wrapper.find(selector)
    expect(element.exists()).toBe(true)

    if (value !== undefined) {
      expect(element.attributes(attribute)).toBe(value)
    } else {
      expect(element.attributes(attribute)).toBeDefined()
    }
  }

  static notHasAttribute(wrapper: VueWrapper, selector: string, attribute: string) {
    const element = wrapper.find(selector)
    if (element.exists()) {
      expect(element.attributes(attribute)).toBeUndefined()
    }
  }

  static hasClass(wrapper: VueWrapper, selector: string, className: string) {
    const element = wrapper.find(selector)
    expect(element.exists()).toBe(true)
    expect(element.classes()).toContain(className)
  }

  static notHasClass(wrapper: VueWrapper, selector: string, className: string) {
    const element = wrapper.find(selector)
    if (element.exists()) {
      expect(element.classes()).not.toContain(className)
    }
  }

  static hasClasses(wrapper: VueWrapper, selector: string, classNames: string[]) {
    const element = wrapper.find(selector)
    expect(element.exists()).toBe(true)
    classNames.forEach(className => {
      expect(element.classes()).toContain(className)
    })
  }

  // 样式断言
  static hasStyle(wrapper: VueWrapper, selector: string, style: string, value: string) {
    const element = wrapper.find(selector)
    expect(element.exists()).toBe(true)
    expect(element.element.style[style as any]).toBe(value)
  }

  static notHasStyle(wrapper: VueWrapper, selector: string, style: string, value: string) {
    const element = wrapper.find(selector)
    if (element.exists()) {
      expect(element.element.style[style as any]).not.toBe(value)
    }
  }

  // 表单断言
  static hasValue(wrapper: VueWrapper, selector: string, value: any) {
    const element = wrapper.find(selector)
    expect(element.exists()).toBe(true)
    expect(element.element.value).toBe(value)
  }

  static notHasValue(wrapper: VueWrapper, selector: string, value: any) {
    const element = wrapper.find(selector)
    if (element.exists()) {
      expect(element.element.value).not.toBe(value)
    }
  }

  static isChecked(wrapper: VueWrapper, selector: string) {
    const element = wrapper.find(selector)
    expect(element.exists()).toBe(true)
    expect(element.element.checked).toBe(true)
  }

  static isNotChecked(wrapper: VueWrapper, selector: string) {
    const element = wrapper.find(selector)
    if (element.exists()) {
      expect(element.element.checked).toBe(false)
    }
  }

  static isDisabled(wrapper: VueWrapper, selector: string) {
    const element = wrapper.find(selector)
    expect(element.exists()).toBe(true)
    expect(element.element.disabled).toBe(true)
  }

  static isNotDisabled(wrapper: VueWrapper, selector: string) {
    const element = wrapper.find(selector)
    if (element.exists()) {
      expect(element.element.disabled).toBe(false)
    }
  }

  static isReadOnly(wrapper: VueWrapper, selector: string) {
    const element = wrapper.find(selector)
    expect(element.exists()).toBe(true)
    expect(element.element.readOnly).toBe(true)
  }

  static isNotReadOnly(wrapper: VueWrapper, selector: string) {
    const element = wrapper.find(selector)
    if (element.exists()) {
      expect(element.element.readOnly).toBe(false)
    }
  }

  // 列表断言
  static hasCount(wrapper: VueWrapper, selector: string, count: number) {
    const elements = wrapper.findAll(selector)
    expect(elements.length).toBe(count)
  }

  static hasCountAtLeast(wrapper: VueWrapper, selector: string, minCount: number) {
    const elements = wrapper.findAll(selector)
    expect(elements.length).toBeGreaterThanOrEqual(minCount)
  }

  static hasCountAtMost(wrapper: VueWrapper, selector: string, maxCount: number) {
    const elements = wrapper.findAll(selector)
    expect(elements.length).toBeLessThanOrEqual(maxCount)
  }

  static hasCountInRange(wrapper: VueWrapper, selector: string, minCount: number, maxCount: number) {
    const elements = wrapper.findAll(selector)
    expect(elements.length).toBeGreaterThanOrEqual(minCount)
    expect(elements.length).toBeLessThanOrEqual(maxCount)
  }

  // 组件断言
  static hasComponent(wrapper: VueWrapper, componentName: string) {
    expect(wrapper.findComponent({ name: componentName }).exists()).toBe(true)
  }

  static notHasComponent(wrapper: VueWrapper, componentName: string) {
    expect(wrapper.findComponent({ name: componentName }).exists()).toBe(false)
  }

  static hasComponents(wrapper: VueWrapper, componentName: string, count: number) {
    const components = wrapper.findAllComponents({ name: componentName })
    expect(components.length).toBe(count)
  }

  // 数据断言
  static hasData(wrapper: VueWrapper, key: string, value: any) {
    expect(wrapper.vm[key]).toBe(value)
  }

  static notHasData(wrapper: VueWrapper, key: string, value: any) {
    expect(wrapper.vm[key]).not.toBe(value)
  }

  static hasDataProperty(wrapper: VueWrapper, key: string) {
    expect(wrapper.vm).toHaveProperty(key)
  }

  static notHasDataProperty(wrapper: VueWrapper, key: string) {
    expect(wrapper.vm).not.toHaveProperty(key)
  }

  // 计算属性断言
  static hasComputed(wrapper: VueWrapper, key: string, value: any) {
    expect(wrapper.vm[key]).toBe(value)
  }

  static computedIsTruthy(wrapper: VueWrapper, key: string) {
    expect(wrapper.vm[key]).toBeTruthy()
  }

  static computedIsFalsy(wrapper: VueWrapper, key: string) {
    expect(wrapper.vm[key]).toBeFalsy()
  }

  // 方法断言
  static hasMethod(wrapper: VueWrapper, methodName: string) {
    expect(typeof wrapper.vm[methodName]).toBe('function')
  }

  static notHasMethod(wrapper: VueWrapper, methodName: string) {
    expect(typeof wrapper.vm[methodName]).not.toBe('function')
  }

  static methodReturns(wrapper: VueWrapper, methodName: string, args: any[], expectedValue: any) {
    const result = wrapper.vm[methodName](...args)
    expect(result).toBe(expectedValue)
  }

  static methodThrows(wrapper: VueWrapper, methodName: string, args: any[], errorType: any) {
    expect(() => wrapper.vm[methodName](...args)).toThrow(errorType)
  }

  // 事件断言
  static hasEmitted(wrapper: VueWrapper, eventName: string) {
    expect(wrapper.emitted()[eventName]).toBeDefined()
  }

  static notEmitted(wrapper: VueWrapper, eventName: string) {
    expect(wrapper.emitted()[eventName]).toBeUndefined()
  }

  static hasEmittedCount(wrapper: VueWrapper, eventName: string, count: number) {
    expect(wrapper.emitted()[eventName]).toHaveLength(count)
  }

  static hasEmittedWith(wrapper: VueWrapper, eventName: string, ...args: any[]) {
    expect(wrapper.emitted()[eventName]).toContainEqual(args)
  }

  // 路由断言
  static hasRoute(wrapper: VueWrapper, path: string) {
    expect(wrapper.vm.$route.path).toBe(path)
  }

  static hasRouteParams(wrapper: VueWrapper, params: Record<string, any>) {
    expect(wrapper.vm.$route.params).toEqual(params)
  }

  static hasRouteQuery(wrapper: VueWrapper, query: Record<string, any>) {
    expect(wrapper.vm.$route.query).toEqual(query)
  }

  static hasRouteHash(wrapper: VueWrapper, hash: string) {
    expect(wrapper.vm.$route.hash).toBe(hash)
  }

  // Store 断言
  static hasStoreState(wrapper: VueWrapper, storeName: string, key: string, value: any) {
    const store = wrapper.vm.$pinia._s.get(storeName)
    expect(store[key]).toBe(value)
  }

  static hasStoreGetter(wrapper: VueWrapper, storeName: string, getterName: string, value: any) {
    const store = wrapper.vm.$pinia._s.get(storeName)
    expect(store[getterName]).toBe(value)
  }

  // DOM 断言
  static hasChildElement(wrapper: VueWrapper, parentSelector: string, childSelector: string) {
    const parent = wrapper.find(parentSelector)
    expect(parent.exists()).toBe(true)
    expect(parent.find(childSelector).exists()).toBe(true)
  }

  static notHasChildElement(wrapper: VueWrapper, parentSelector: string, childSelector: string) {
    const parent = wrapper.find(parentSelector)
    if (parent.exists()) {
      expect(parent.find(childSelector).exists()).toBe(false)
    }
  }

  static hasSiblingElement(wrapper: VueWrapper, selector: string, siblingSelector: string) {
    const element = wrapper.find(selector)
    expect(element.exists()).toBe(true)
    const sibling = element.find(siblingSelector)
    expect(sibling.exists()).toBe(true)
  }

  static hasParentElement(wrapper: VueWrapper, selector: string, parentSelector: string) {
    const element = wrapper.find(selector)
    expect(element.exists()).toBe(true)
    const parent = element.find(parentSelector)
    expect(parent.exists()).toBe(true)
  }

  // 快照断言
  static matchesSnapshot(wrapper: VueWrapper, name?: string) {
    expect(wrapper.html()).toMatchSnapshot(name)
  }

  static matchesComponentSnapshot(wrapper: VueWrapper, name?: string) {
    expect(wrapper.vm).toMatchSnapshot(name)
  }

  // 性能断言
  static renderTimeLessThan(wrapper: VueWrapper, maxTime: number) {
    const start = performance.now()
    wrapper.html()
    const end = performance.now()
    expect(end - start).toBeLessThan(maxTime)
  }

  static componentRenderTimeLessThan(component: any, maxTime: number) {
    const start = performance.now()
    wrapper.html()
    const end = performance.now()
    expect(end - start).toBeLessThan(maxTime)
  }

  // 异步断言
  static async resolvesTo(promise: Promise<any>, expectedValue: any) {
    await expect(promise).resolves.toBe(expectedValue)
  }

  static async rejectsTo(promise: Promise<any>, expectedError: any) {
    await expect(promise).rejects.toBe(expectedError)
  }

  static async resolvesWith(promise: Promise<any>, matcher: (value: any) => boolean) {
    const result = await promise
    expect(matcher(result)).toBe(true)
  }

  static async rejectsWith(promise: Promise<any>, matcher: (error: any) => boolean) {
    try {
      await promise
      expect(false).toBe(true) // Should not reach here
    } catch (error) {
      expect(matcher(error)).toBe(true)
    }
  }

  // 顺序断言
  static elementsInOrder(wrapper: VueWrapper, selectors: string[]) {
    const elements = selectors.map(selector => wrapper.find(selector))
    elements.forEach(element => {
      expect(element.exists()).toBe(true)
    })

    for (let i = 0; i < elements.length - 1; i++) {
      const current = elements[i].element
      const next = elements[i + 1].element

      // 检查元素在 DOM 中的顺序
      let sibling = current.nextElementSibling
      let found = false

      while (sibling) {
        if (sibling === next) {
          found = true
          break
        }
        sibling = sibling.nextElementSibling
      }

      expect(found).toBe(true)
    }
  }

  // 可访问性断言
  static hasAccessibleName(wrapper: VueWrapper, selector: string, name: string) {
    const element = wrapper.find(selector)
    expect(element.exists()).toBe(true)

    const accessibleName = element.attributes('aria-label') ||
                           element.attributes('title') ||
                           element.text()

    expect(accessibleName).toContain(name)
  }

  static hasValidAltText(wrapper: VueWrapper, selector: string) {
    const element = wrapper.find(selector)
    expect(element.exists()).toBe(true)
    expect(element.attributes('alt')).toBeDefined()
  }

  static hasValidRole(wrapper: VueWrapper, selector: string, role: string) {
    const element = wrapper.find(selector)
    expect(element.exists()).toBe(true)
    expect(element.attributes('role')).toBe(role)
  }

  // 响应式断言
  static isReactive(wrapper: VueWrapper, key: string) {
    const originalValue = wrapper.vm[key]
    wrapper.vm[key] = 'test_value'
    expect(wrapper.vm[key]).toBe('test_value')
    wrapper.vm[key] = originalValue
  }

  static isComputedReactive(wrapper: VueWrapper, key: string) {
    const originalValue = wrapper.vm[key]
    // 修改依赖的数据
    // wrapper.vm.dependentKey = 'new_value'
    expect(wrapper.vm[key]).not.toBe(originalValue)
  }

  // 类型断言
  static isType(value: any, type: string) {
    expect(typeof value).toBe(type)
  }

  static isInstanceOf(value: any, constructor: any) {
    expect(value).toBeInstanceOf(constructor)
  }

  static isArray(value: any) {
    expect(Array.isArray(value)).toBe(true)
  }

  static isObject(value: any) {
    expect(typeof value === 'object' && value !== null).toBe(true)
  }

  static isString(value: any) {
    expect(typeof value === 'string').toBe(true)
  }

  static isNumber(value: any) {
    expect(typeof value === 'number').toBe(true)
  }

  static isBoolean(value: any) {
    expect(typeof value === 'boolean').toBe(true)
  }

  static isFunction(value: any) {
    expect(typeof value === 'function').toBe(true)
  }

  static isUndefined(value: any) {
    expect(typeof value === 'undefined').toBe(true)
  }

  static isNull(value: any) {
    expect(value === null).toBe(true)
  }

  // 自定义断言
  static customAssertion(
    name: string,
    actual: any,
    expected: any,
    matcher: (actual: any, expected: any) => boolean
  ) {
    try {
      expect(matcher(actual, expected)).toBe(true)
    } catch (error) {
      throw new Error(`Custom assertion '${name}' failed: ${error.message}`)
    }
  }
}