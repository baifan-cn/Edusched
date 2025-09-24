import { ref, unref, type Ref } from 'vue'
import { ElMessage } from 'element-plus'

// API请求状态
interface RequestState<T> {
  data: T | null
  loading: boolean
  error: Error | null
}

// API请求选项
interface RequestOptions {
  immediate?: boolean
  showLoading?: boolean
  showError?: boolean
  showSuccess?: boolean
  successMessage?: string
  onSuccess?: (data: any) => void
  onError?: (error: Error) => void
}

// 分页请求选项
interface PaginationOptions {
  page: number
  size: number
  sort?: string
  order?: 'asc' | 'desc'
}

// 分页响应
interface PaginatedData<T> {
  items: T[]
  total: number
  page: number
  size: number
  total_pages: number
}

/**
 * 通用的API请求Hook
 */
export function useAPI<T = any>(
  requestFn: (...args: any[]) => Promise<T>,
  options: RequestOptions = {}
) {
  const {
    immediate = false,
    showLoading = true,
    showError = true,
    showSuccess = false,
    successMessage,
    onSuccess,
    onError
  } = options

  const state = ref<RequestState<T>>({
    data: null,
    loading: false,
    error: null
  })

  const execute = async (...args: any[]): Promise<T> => {
    try {
      state.value.loading = showLoading
      state.value.error = null

      const result = await requestFn(...args)
      state.value.data = result

      if (showSuccess) {
        ElMessage.success(successMessage || '操作成功')
      }

      onSuccess?.(result)
      return result
    } catch (error) {
      state.value.error = error as Error

      if (showError) {
        ElMessage.error((error as Error).message || '请求失败')
      }

      onError?.(error as Error)
      throw error
    } finally {
      state.value.loading = false
    }
  }

  if (immediate) {
    execute()
  }

  return {
    state,
    execute,
    data: state.value.data,
    loading: state.value.loading,
    error: state.value.error
  }
}

/**
 * 分页数据请求Hook
 */
export function usePaginatedAPI<T = any>(
  requestFn: (params: PaginationOptions & Record<string, any>) => Promise<PaginatedData<T>>,
  defaultParams: PaginationOptions & Record<string, any> = { page: 1, size: 20 },
  options: RequestOptions = {}
) {
  const {
    immediate = false,
    showLoading = true,
    showError = true,
    onSuccess,
    onError
  } = options

  const state = ref<RequestState<PaginatedData<T>>>({
    data: null,
    loading: false,
    error: null
  })

  const params = ref(defaultParams)

  const execute = async (customParams?: Partial<typeof defaultParams>) => {
    try {
      state.value.loading = showLoading
      state.value.error = null

      const mergedParams = { ...unref(params), ...customParams }
      const result = await requestFn(mergedParams)

      state.value.data = result
      params.value = mergedParams

      onSuccess?.(result)
      return result
    } catch (error) {
      state.value.error = error as Error

      if (showError) {
        ElMessage.error((error as Error).message || '请求失败')
      }

      onError?.(error as Error)
      throw error
    } finally {
      state.value.loading = false
    }
  }

  const refresh = () => execute()
  const nextPage = () => {
    if (state.value.data && state.value.data.page < state.value.data.total_pages) {
      execute({ page: (state.value.data?.page || 0) + 1 })
    }
  }
  const prevPage = () => {
    if (state.value.data && state.value.data.page > 1) {
      execute({ page: (state.value.data?.page || 0) - 1 })
    }
  }
  const goToPage = (page: number) => execute({ page })
  const changePageSize = (size: number) => execute({ page: 1, size })

  if (immediate) {
    execute()
  }

  return {
    state,
    params,
    execute,
    refresh,
    nextPage,
    prevPage,
    goToPage,
    changePageSize,
    data: state.value.data,
    loading: state.value.loading,
    error: state.value.error
  }
}

/**
 * 表单提交Hook
 */
export function useFormSubmit<T = any>(
  submitFn: (data: T) => Promise<any>,
  options: RequestOptions = {}
) {
  const {
    showLoading = true,
    showError = true,
    showSuccess = true,
    successMessage = '提交成功',
    onSuccess,
    onError
  } = options

  const submitting = ref(false)
  const error = ref<Error | null>(null)

  const submit = async (data: T): Promise<any> => {
    try {
      submitting.value = true
      error.value = null

      const result = await submitFn(data)

      if (showSuccess) {
        ElMessage.success(successMessage)
      }

      onSuccess?.(result)
      return result
    } catch (err) {
      error.value = err as Error

      if (showError) {
        ElMessage.error((err as Error).message || '提交失败')
      }

      onError?.(err as Error)
      throw err
    } finally {
      submitting.value = false
    }
  }

  const reset = () => {
    error.value = null
    submitting.value = false
  }

  return {
    submitting,
    error,
    submit,
    reset
  }
}

/**
 * 文件上传Hook
 */
export function useFileUpload(
  uploadFn: (file: File) => Promise<{ url: string }>,
  options: RequestOptions = {}
) {
  const {
    showLoading = true,
    showError = true,
    showSuccess = true,
    successMessage = '上传成功',
    onSuccess,
    onError
  } = options

  const uploading = ref(false)
  const progress = ref(0)
  const error = ref<Error | null>(null)

  const upload = async (file: File): Promise<{ url: string }> => {
    try {
      uploading.value = true
      progress.value = 0
      error.value = null

      // 模拟上传进度
      const progressInterval = setInterval(() => {
        progress.value = Math.min(90, progress.value + 10)
      }, 100)

      const result = await uploadFn(file)

      clearInterval(progressInterval)
      progress.value = 100

      if (showSuccess) {
        ElMessage.success(successMessage)
      }

      onSuccess?.(result)
      return result
    } catch (err) {
      error.value = err as Error

      if (showError) {
        ElMessage.error((err as Error).message || '上传失败')
      }

      onError?.(err as Error)
      throw err
    } finally {
      uploading.value = false
      setTimeout(() => {
        progress.value = 0
      }, 1000)
    }
  }

  const reset = () => {
    uploading.value = false
    progress.value = 0
    error.value = null
  }

  return {
    uploading,
    progress,
    error,
    upload,
    reset
  }
}

/**
 * 防抖Hook
 */
export function useDebounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout

  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

/**
 * 节流Hook
 */
export function useThrottle<T extends (...args: any[]) => any>(
  fn: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      fn(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}