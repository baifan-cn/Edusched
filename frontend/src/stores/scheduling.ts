import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  schedulingApi,
  type SchedulingJob,
  type SchedulingConfig,
  type SchedulingResult,
  type ProgressUpdate,
  type ValidateRequest,
  type ValidateResponse,
  type SchedulingJobQueryParams,
  type CreateSchedulingJobRequest,
  type Constraint,
  type TimeSlot,
  type AlgorithmParams
} from '@/api/scheduling'
import type { PaginatedResponse } from '@/types'

export const useSchedulingStore = defineStore('scheduling', () => {
  // 状态
  const jobs = ref<SchedulingJob[]>([])
  const currentJob = ref<SchedulingJob | null>(null)
  const jobResult = ref<SchedulingResult | null>(null)
  const jobProgress = ref<ProgressUpdate | null>(null)
  const loading = ref(false)
  const validating = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const queryParams = ref<SchedulingJobQueryParams>({})
  const configTemplates = ref<SchedulingConfig[]>([])
  const constraintTemplates = ref<Constraint[]>([])
  const algorithmPresets = ref<any[]>([])
  const stats = ref<any>(null)

  // WebSocket连接状态
  const websocketConnected = ref(false)
  const progressUpdates = ref<ProgressUpdate[]>([])

  // 计算属性
  const hasJobs = computed(() => jobs.value.length > 0)
  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))
  const isJobRunning = computed(() =>
    currentJob.value?.status === 'running' ||
    jobs.value.some(job => job.status === 'running')
  )
  const jobStats = computed(() => ({
    total: jobs.value.length,
    pending: jobs.value.filter(job => job.status === 'pending').length,
    running: jobs.value.filter(job => job.status === 'running').length,
    completed: jobs.value.filter(job => job.status === 'completed').length,
    failed: jobs.value.filter(job => job.status === 'failed').length,
    cancelled: jobs.value.filter(job => job.status === 'cancelled').length,
    averageExecutionTime: jobs.value
      .filter(job => job.completed_at && job.started_at)
      .reduce((acc, job) => {
        const duration = new Date(job.completed_at!).getTime() - new Date(job.started_at!).getTime()
        return acc + duration
      }, 0) / jobs.value.filter(job => job.completed_at && job.started_at).length || 0
  }))

  // 获取最近的任务
  const recentJobs = computed(() =>
    jobs.value
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 10)
  )

  // 按状态分组的任务
  const jobsByStatus = computed(() => {
    const grouped: Record<string, SchedulingJob[]> = {}
    jobs.value.forEach(job => {
      if (!grouped[job.status]) {
        grouped[job.status] = []
      }
      grouped[job.status].push(job)
    })
    return grouped
  })

  // 动作
  const setJobs = (newJobs: SchedulingJob[]) => {
    jobs.value = newJobs
  }

  const setCurrentJob = (job: SchedulingJob | null) => {
    currentJob.value = job
  }

  const setJobResult = (result: SchedulingResult | null) => {
    jobResult.value = result
  }

  const setJobProgress = (progress: ProgressUpdate | null) => {
    jobProgress.value = progress
  }

  const setLoading = (status: boolean) => {
    loading.value = status
  }

  const setValidating = (status: boolean) => {
    validating.value = status
  }

  const setPagination = (page: number, size: number) => {
    currentPage.value = page
    pageSize.value = size
  }

  const setQueryParams = (params: SchedulingJobQueryParams) => {
    queryParams.value = { ...params }
  }

  const setWebsocketConnected = (connected: boolean) => {
    websocketConnected.value = connected
  }

  const addProgressUpdate = (update: ProgressUpdate) => {
    progressUpdates.value.push(update)
    // 保留最近的100条更新
    if (progressUpdates.value.length > 100) {
      progressUpdates.value = progressUpdates.value.slice(-100)
    }
  }

  const clearProgressUpdates = () => {
    progressUpdates.value = []
  }

  // 获取调度任务列表
  const fetchJobs = async (params?: SchedulingJobQueryParams) => {
    try {
      setLoading(true)
      const mergedParams = { ...queryParams.value, ...params }
      const response = await schedulingApi.getJobs(mergedParams)

      setJobs(response.items)
      total.value = response.total
      currentPage.value = response.page
      pageSize.value = response.size

      return response
    } catch (error) {
      ElMessage.error('获取调度任务列表失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取单个任务详情
  const fetchJob = async (jobId: string) => {
    try {
      setLoading(true)
      const job = await schedulingApi.getJob(jobId)
      setCurrentJob(job)
      return job
    } catch (error) {
      ElMessage.error('获取任务详情失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 创建调度任务
  const createJob = async (data: CreateSchedulingJobRequest) => {
    try {
      setLoading(true)
      const newJob = await schedulingApi.startJob(data)

      // 更新列表
      await fetchJobs()
      setCurrentJob(newJob)

      ElMessage.success('调度任务创建成功')
      return newJob
    } catch (error) {
      ElMessage.error('创建调度任务失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 取消任务
  const cancelJob = async (jobId: string, reason?: string) => {
    try {
      setLoading(true)
      await schedulingApi.cancelJob(jobId, reason)

      // 更新本地状态
      const job = jobs.value.find(j => j.id === jobId)
      if (job) {
        job.status = 'cancelled'
        job.cancelled_at = new Date().toISOString()
      }

      if (currentJob.value?.id === jobId) {
        currentJob.value.status = 'cancelled'
        currentJob.value.cancelled_at = new Date().toISOString()
      }

      ElMessage.success('任务已取消')
    } catch (error) {
      ElMessage.error('取消任务失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取任务进度
  const fetchJobProgress = async (jobId: string) => {
    try {
      const progress = await schedulingApi.getJobProgress(jobId)
      setJobProgress(progress)
      addProgressUpdate(progress)
      return progress
    } catch (error) {
      console.error('获取任务进度失败:', error)
      throw error
    }
  }

  // 获取任务结果
  const fetchJobResult = async (jobId: string) => {
    try {
      setLoading(true)
      const result = await schedulingApi.getJobResult(jobId)
      setJobResult(result)
      return result
    } catch (error) {
      ElMessage.error('获取任务结果失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 验证调度配置
  const validateConfig = async (data: ValidateRequest) => {
    try {
      setValidating(true)
      const result = await schedulingApi.validateConfig(data)
      return result
    } catch (error) {
      ElMessage.error('验证配置失败')
      throw error
    } finally {
      setValidating(false)
    }
  }

  // 重启任务
  const restartJob = async (jobId: string) => {
    try {
      setLoading(true)
      const restartedJob = await schedulingApi.restartJob(jobId)

      // 更新本地状态
      const index = jobs.value.findIndex(j => j.id === jobId)
      if (index !== -1) {
        jobs.value[index] = restartedJob
      }

      if (currentJob.value?.id === jobId) {
        setCurrentJob(restartedJob)
      }

      ElMessage.success('任务重启成功')
      return restartedJob
    } catch (error) {
      ElMessage.error('重启任务失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 删除任务
  const deleteJob = async (jobId: string) => {
    try {
      setLoading(true)
      await schedulingApi.deleteJob(jobId)

      // 从列表中移除
      jobs.value = jobs.value.filter(job => job.id !== jobId)

      // 如果删除的是当前任务，清除选中
      if (currentJob.value?.id === jobId) {
        setCurrentJob(null)
        setJobResult(null)
        setJobProgress(null)
      }

      // 更新总数
      total.value = Math.max(0, total.value - 1)

      ElMessage.success('任务删除成功')
    } catch (error) {
      ElMessage.error('删除任务失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 批量删除任务
  const bulkDeleteJobs = async (jobIds: string[]) => {
    try {
      setLoading(true)
      await schedulingApi.bulkDeleteJobs(jobIds)

      // 从列表中移除
      jobs.value = jobs.value.filter(job => !jobIds.includes(job.id))

      // 如果删除的任务包含当前任务，清除选中
      if (currentJob.value && jobIds.includes(currentJob.value.id)) {
        setCurrentJob(null)
        setJobResult(null)
        setJobProgress(null)
      }

      // 更新总数
      total.value = Math.max(0, total.value - jobIds.length)

      ElMessage.success(`成功删除 ${jobIds.length} 个任务`)
    } catch (error) {
      ElMessage.error('批量删除任务失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取调度统计信息
  const fetchSchedulingStats = async (params?: any) => {
    try {
      setLoading(true)
      const response = await schedulingApi.getSchedulingStats(params)
      stats.value = response
      return response
    } catch (error) {
      ElMessage.error('获取统计信息失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 获取约束模板
  const fetchConstraintTemplates = async () => {
    try {
      const templates = await schedulingApi.getConstraintTemplates()
      constraintTemplates.value = templates
      return templates
    } catch (error) {
      ElMessage.error('获取约束模板失败')
      throw error
    }
  }

  // 获取算法预设
  const fetchAlgorithmPresets = async () => {
    try {
      const presets = await schedulingApi.getAlgorithmPresets()
      algorithmPresets.value = presets
      return presets
    } catch (error) {
      ElMessage.error('获取算法预设失败')
      throw error
    }
  }

  // 导出结果
  const exportResult = async (jobId: string, format: 'json' | 'csv' | 'excel' | 'pdf') => {
    try {
      setLoading(true)
      const blob = await schedulingApi.exportResult(jobId, format)

      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `scheduling-result-${jobId}.${format}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      ElMessage.success('结果导出成功')
    } catch (error) {
      ElMessage.error('导出结果失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 导入配置
  const importConfig = async (file: File) => {
    try {
      setLoading(true)
      const config = await schedulingApi.importConfig(file)
      ElMessage.success('配置导入成功')
      return config
    } catch (error) {
      ElMessage.error('导入配置失败')
      throw error
    } finally {
      setLoading(false)
    }
  }

  // 初始化WebSocket连接
  const initWebSocket = (jobId?: string) => {
    if (websocketConnected.value) return

    try {
      const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/ws/scheduling`
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        setWebsocketConnected(true)
        console.log('WebSocket连接已建立')

        // 如果指定了jobId，订阅该任务的进度更新
        if (jobId) {
          ws.send(JSON.stringify({ action: 'subscribe', job_id: jobId }))
        }
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          if (data.type === 'progress_update') {
            const update: ProgressUpdate = data.payload
            setJobProgress(update)
            addProgressUpdate(update)

            // 更新当前任务的进度
            if (currentJob.value?.id === update.job_id) {
              currentJob.value.progress = update.progress
              currentJob.value.current_step = update.current_step
            }

            // 更新任务列表中的进度
            const job = jobs.value.find(j => j.id === update.job_id)
            if (job) {
              job.progress = update.progress
              job.current_step = update.current_step
            }
          } else if (data.type === 'job_completed') {
            // 任务完成，刷新任务信息
            if (currentJob.value?.id === data.payload.job_id) {
              fetchJob(data.payload.job_id)
            }
          }
        } catch (error) {
          console.error('处理WebSocket消息失败:', error)
        }
      }

      ws.onclose = () => {
        setWebsocketConnected(false)
        console.log('WebSocket连接已关闭')

        // 3秒后尝试重连
        setTimeout(() => {
          if (!websocketConnected.value) {
            initWebSocket(jobId)
          }
        }, 3000)
      }

      ws.onerror = (error) => {
        console.error('WebSocket错误:', error)
        setWebsocketConnected(false)
      }

      // 保存WebSocket实例以便后续使用
      ;(window as any).schedulingWebSocket = ws
    } catch (error) {
      console.error('初始化WebSocket失败:', error)
    }
  }

  // 关闭WebSocket连接
  const closeWebSocket = () => {
    const ws = (window as any).schedulingWebSocket
    if (ws) {
      ws.close()
      setWebsocketConnected(false)
    }
  }

  // 刷新任务列表
  const refreshJobs = async () => {
    await fetchJobs()
  }

  // 搜索任务
  const searchJobs = async (searchTerm: string) => {
    const params = { ...queryParams.value, search: searchTerm, page: 1 }
    await fetchJobs(params)
  }

  // 重置查询参数
  const resetQueryParams = () => {
    setQueryParams({})
    setPagination(1, 20)
    return fetchJobs()
  }

  // 清理资源
  const cleanup = () => {
    closeWebSocket()
    clearProgressUpdates()
    setCurrentJob(null)
    setJobResult(null)
    setJobProgress(null)
  }

  // 初始化
  const init = async () => {
    await fetchJobs()
    await fetchSchedulingStats()
    await fetchConstraintTemplates()
    await fetchAlgorithmPresets()
    initWebSocket()
  }

  return {
    // 状态
    jobs,
    currentJob,
    jobResult,
    jobProgress,
    loading,
    validating,
    total,
    currentPage,
    pageSize,
    queryParams,
    configTemplates,
    constraintTemplates,
    algorithmPresets,
    stats,
    websocketConnected,
    progressUpdates,

    // 计算属性
    hasJobs,
    totalPages,
    isJobRunning,
    jobStats,
    recentJobs,
    jobsByStatus,

    // 动作
    setJobs,
    setCurrentJob,
    setJobResult,
    setJobProgress,
    setLoading,
    setValidating,
    setPagination,
    setQueryParams,
    setWebsocketConnected,
    addProgressUpdate,
    clearProgressUpdates,
    fetchJobs,
    fetchJob,
    createJob,
    cancelJob,
    fetchJobProgress,
    fetchJobResult,
    validateConfig,
    restartJob,
    deleteJob,
    bulkDeleteJobs,
    fetchSchedulingStats,
    fetchConstraintTemplates,
    fetchAlgorithmPresets,
    exportResult,
    importConfig,
    initWebSocket,
    closeWebSocket,
    refreshJobs,
    searchJobs,
    resetQueryParams,
    cleanup,
    init
  }
})