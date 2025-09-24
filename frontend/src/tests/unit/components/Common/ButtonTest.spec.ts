import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ButtonTest from './ButtonTest.vue'
import { MockUtils, ComponentUtils, AssertionUtils } from '@/test/utils'

describe('ButtonTest', () => {
  let wrapper: any

  beforeEach(() => {
    wrapper = ComponentUtils.mountComponent(ButtonTest)
  })

  afterEach(() => {
    wrapper.unmount()
  })

  it('renders correctly with default props', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toBe('Button')
    expect(wrapper.find('el-button').exists()).toBe(true)
  })

  it('displays custom text when provided', () => {
    wrapper = ComponentUtils.mountComponent(ButtonTest, {
      props: { text: 'Custom Button' }
    })

    expect(wrapper.text()).toBe('Custom Button')
  })

  it('applies correct type prop', () => {
    wrapper = ComponentUtils.mountComponent(ButtonTest, {
      props: { type: 'success' }
    })

    expect(wrapper.find('el-button').attributes('type')).toBe('success')
  })

  it('applies correct size prop', () => {
    wrapper = ComponentUtils.mountComponent(ButtonTest, {
      props: { size: 'large' }
    })

    expect(wrapper.find('el-button').attributes('size')).toBe('large')
  })

  it('disables button when disabled prop is true', () => {
    wrapper = ComponentUtils.mountComponent(ButtonTest, {
      props: { disabled: true }
    })

    expect(wrapper.find('el-button').attributes('disabled')).toBe('')
  })

  it('shows loading state when loading prop is true', () => {
    wrapper = ComponentUtils.mountComponent(ButtonTest, {
      props: { loading: true }
    })

    expect(wrapper.find('el-button').attributes('loading')).toBe('')
  })

  it('emits click event when clicked', async () => {
    await wrapper.find('el-button').trigger('click')

    expect(wrapper.emitted('click')).toBeTruthy()
    expect(wrapper.emitted('click')).toHaveLength(1)
  })

  it('does not emit click event when disabled', async () => {
    wrapper = ComponentUtils.mountComponent(ButtonTest, {
      props: { disabled: true }
    })

    await wrapper.find('el-button').trigger('click')

    expect(wrapper.emitted('click')).toBeFalsy()
  })

  it('renders slot content when provided', () => {
    wrapper = ComponentUtils.mountComponent(ButtonTest, {
      slots: {
        default: '<span class="custom-content">Custom Slot Content</span>'
      }
    })

    expect(wrapper.find('.custom-content').exists()).toBe(true)
    expect(wrapper.find('.custom-content').text()).toBe('Custom Slot Content')
  })

  it('matches snapshot', () => {
    expect(wrapper.html()).toMatchSnapshot()
  })

  it('has correct CSS classes', () => {
    expect(wrapper.find('.button-test').exists()).toBe(true)
  })

  it('updates text when prop changes', async () => {
    await wrapper.setProps({ text: 'Updated Text' })

    expect(wrapper.text()).toBe('Updated Text')
  })

  it('updates type when prop changes', async () => {
    await wrapper.setProps({ type: 'danger' })

    expect(wrapper.find('el-button').attributes('type')).toBe('danger')
  })

  it('handles multiple clicks', async () => {
    await wrapper.find('el-button').trigger('click')
    await wrapper.find('el-button').trigger('click')
    await wrapper.find('el-button').trigger('click')

    expect(wrapper.emitted('click')).toHaveLength(3)
  })

  it('passes accessibility requirements', () => {
    const button = wrapper.find('el-button')
    expect(button.exists()).toBe(true)

    // Button should be focusable
    expect(button.element.tabIndex).toBeGreaterThanOrEqual(0)
  })

  it('computes reactive properties correctly', async () => {
    const clickSpy = vi.fn()
    wrapper.vm.$on('click', clickSpy)

    await wrapper.find('el-button').trigger('click')

    expect(clickSpy).toHaveBeenCalled()
  })

  it('handles edge cases', async () => {
    // Test with empty text
    await wrapper.setProps({ text: '' })
    expect(wrapper.text()).toBe('')

    // Test with very long text
    const longText = 'a'.repeat(1000)
    await wrapper.setProps({ text: longText })
    expect(wrapper.text()).toBe(longText)
  })

  it('maintains reactive behavior with computed properties', () => {
    // Test that component responds to prop changes
    expect(wrapper.vm.type).toBe('primary')

    wrapper.setData({ internalState: 'test' })
    expect(wrapper.vm.internalState).toBe('test')
  })
})