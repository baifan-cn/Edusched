<template>
  <div class="job-progress">
    <!-- 总进度 -->
    <div class="progress-overview">
      <div class="progress-header">
        <span class="progress-title">总进度</span>
        <span class="progress-percentage">{{ job.progress }}%</span>
      </div>
      <el-progress
        :percentage="job.progress"
        :status="getProgressStatus(job.progress)"
        :stroke-width="12"
        :show-text="false"
      />
      <div class="progress-details">
        <span class="step-info">步骤: {{ job.current_step }} / {{ job.total_steps }}</span>
        <span class="status-info">状态: {{ getJobStatusText(job.status) }}</span>
      </div>
    </div>

    <!-- 当前步骤信息 -->
    <div v-if="progress" class="current-step">
      <div class="step-header">
        <el-icon class="step-icon"><Loading /></el-icon>
        <div class="step-info">
          <div class="step-name">{{ progress.step_name }}</div>
          <div class="step-message">{{ progress.message || '正在处理...' }}</div>
        </div>
      </div>
    </div>

    <!-- 进度更新历史 -->
    <div class="progress-history">
      <div class="history-header">
        <span>进度更新历史</span>
        <el-button size="small" @click="clearHistory">
          <el-icon><Delete /></el-icon>
          清空
        </el-button>
      </div>
      <div class="history-list" ref="historyListRef">
        <div
          v-for="(update, index) in progressUpdates"
          :key="index"
          class="history-item"
          :class="{ 'history-item-latest': index === progressUpdates.length - 1 }"
        >
          <div class="history-time">
            {{ formatDateTime(update.timestamp) }}
          </div>
          <div class="history-content">
            <div class="history-progress">{{ update.progress }}%</div>
            <div class="history-step">{{ update.step_name }}</div>
            <div v-if="update.message" class="history-message">
              {{ update.message }}
            </div>
          </div>
        </div>
        <div v-if="progressUpdates.length === 0" class="no-history">
          暂无进度更新
        </div>
      </div>
    </div>

    <!-- 性能指标 -->
    <div v-if="job.started_at" class="performance-metrics">
      <div class="metrics-header">
        <span>性能指标</span>
      </div>
      <div class="metrics-grid">
        <div class="metric-item">
          <div class="metric-label">已运行时间</div>
          <div class="metric-value">{{ getRunningTime() }}</div>
        </div>
        <div class="metric-item">
          <div class="metric-label">预计剩余时间</div>
          <div class="metric-value">{{ getEstimatedTimeRemaining() }}</div>
        </div>
        <div class="metric-item">
          <div class="metric-label">平均速度</div>
          <div class="metric-value">{{ getAverageSpeed() }}</div>
        </div>
        <div class="metric-item">
          <div class="metric-label">完成率</div>
          <div class="metric-value">{{ job.progress }}%</div>
        </div>
      </div>
    </div>

    <!-- 实时日志 -->
    <div class="real-time-logs">
      <div class="logs-header">
        <span>实时日志</span>
        <el-button size="small" @click="toggleAutoScroll">
          <el-icon><Refresh /></el-icon>
          {{ autoScroll ? '停止滚动' : '自动滚动' }}
        </el-button>
      </div>
      <div class="logs-container" ref="logsContainerRef">
        <div
          v-for="(log, index) in recentLogs"
          :key="index"
          class="log-item"
          :class="`log-level-${log.level}`"
        >
          <div class="log-time">{{ formatDateTime(log.timestamp) }}</div>
          <div class="log-level">{{ log.level.toUpperCase() }}</div>
          <div class="log-message">{{ log.message }}</div>
        </div>
        <div v-if="recentLogs.length === 0" class="no-logs">
          暂无日志
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { Loading, Delete, Refresh } from '@element-plus/icons-vue'
import { formatDateTime, formatDuration } from '@/utils/date'
import type { SchedulingJob, ProgressUpdate } from '@/api/scheduling'

interface Props {
  job: SchedulingJob
  progress: ProgressUpdate | null
  progressUpdates: ProgressUpdate[]
}

interface LogEntry {
  timestamp: string
  level: 'debug' | 'info' | 'warn' | 'error'
  message: string
}

const props = defineProps<Props>()

// 响应式数据
const historyListRef = ref<HTMLElement | null>(null)
const logsContainerRef = ref<HTMLElement | null>(null)
const autoScroll = ref(true)
const recentLogs = ref<LogEntry[]>([])

// 计算属性
const getProgressStatus = (progress: number) => {
  if (progress === 100) return 'success'
  if (progress >= 80) return 'warning'
  return undefined
}

const getJobStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待处理',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return statusMap[status] || '未知'
}

const getRunningTime = () => {
  if (!props.job.started_at) return '-'

  const startTime = new Date(props.job.started_at).getTime()
  const endTime = props.job.completed_at ? new Date(props.job.completed_at).getTime() : Date.now()
  const duration = endTime - startTime

  return formatDuration(duration)
}

const getEstimatedTimeRemaining = () => {
  if (!props.job.started_at || props.job.progress === 0) return '-'

  const startTime = new Date(props.job.started_at).getTime()
  const currentTime = Date.now()
  const elapsed = currentTime - startTime
  const progress = props.job.progress / 100

  if (progress === 0) return '-'

  const estimatedTotal = elapsed / progress
  const estimatedRemaining = estimatedTotal - elapsed

  return formatDuration(estimatedRemaining)
}

const getAverageSpeed = () => {
  if (!props.job.started_at || props.job.progress === 0) return '-'

  const startTime = new Date(props.job.started_at).getTime()
  const currentTime = Date.now()
  const elapsed = currentTime - startTime
  const elapsedMinutes = elapsed / (1000 * 60)

  if (elapsedMinutes === 0) return '-'

  const speed = props.job.progress / elapsedMinutes
  return `${speed.toFixed(1)}%/分钟`
}

// 方法
const clearHistory = () => {
  // 这里应该通过store或props来清除历史
  recentLogs.value = []
}

const toggleAutoScroll = () => {
  autoScroll.value = !autoScroll.value
}

const scrollToBottom = async () => {
  if (!autoScroll.value) return

  await nextTick()

  if (historyListRef.value) {
    historyListRef.value.scrollTop = historyListRef.value.scrollHeight
  }

  if (logsContainerRef.value) {
    logsContainerRef.value.scrollTop = logsContainerRef.value.scrollHeight
  }
}

const generateMockLogs = () => {
  const levels: Array<'debug' | 'info' | 'warn' | 'error'> = ['debug', 'info', 'warn', 'error']
  const messages = [
    '开始加载数据...',
    '验证约束条件...',
    '初始化求解器...',
    '开始搜索解空间...',
    '找到可行解...',
    '优化解的质量...',
    '验证最终结果...',
    '生成报告...'
  ]

  // 模拟日志生成
  const log: LogEntry = {
    timestamp: new Date().toISOString(),
    level: levels[Math.floor(Math.random() * levels.length)],
    message: messages[Math.floor(Math.random() * messages.length)]
  }

  recentLogs.value.push(log)

  // 保留最近的50条日志
  if (recentLogs.value.length > 50) {
    recentLogs.value = recentLogs.value.slice(-50)
  }

  scrollToBottom()
}

// 监听进度更新
const watchProgressUpdates = () => {
  let logInterval: NodeJS.Timeout | null = null

  if (props.job.status === 'running') {
    // 启动日志生成定时器
    logInterval = setInterval(generateMockLogs, 2000)
  }

  return () => {
    if (logInterval) {
      clearInterval(logInterval)
    }
  }
}

// 生命周期
onMounted(() => {
  const cleanup = watchProgressUpdates()

  // 监听进度更新，自动滚动到底部
  const unwatch = props.progressUpdates.length
  scrollToBottom()

  onUnmounted(() => {
    cleanup()
    if (unwatch) {
      unwatch()
    }
  })
})
</script>

<style scoped>
.job-progress {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.progress-overview {
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-title {
  font-weight: 600;
  color: #303133;
}

.progress-percentage {
  font-size: 18px;
  font-weight: 600;
  color: #409eff;
}

.progress-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.current-step {
  padding: 16px;
  background-color: #e6f7ff;
  border-radius: 8px;
  border: 1px solid #91d5ff;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-icon {
  color: #1890ff;
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.step-info {
  flex: 1;
}

.step-name {
  font-weight: 500;
  color: #1890ff;
  margin-bottom: 4px;
}

.step-message {
  font-size: 12px;
  color: #666;
}

.progress-history {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #ebeef5;
  border-radius: 8px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
  background-color: #fafafa;
  border-radius: 8px 8px 0 0;
}

.history-list {
  flex: 1;
  max-height: 200px;
  overflow-y: auto;
  padding: 8px;
}

.history-item {
  padding: 8px;
  margin-bottom: 8px;
  border-left: 3px solid #e9ecef;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.history-item-latest {
  border-left-color: #409eff;
  background-color: #e6f7ff;
}

.history-time {
  font-size: 11px;
  color: #909399;
  margin-bottom: 4px;
}

.history-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.history-progress {
  font-weight: 600;
  color: #409eff;
  min-width: 45px;
}

.history-step {
  font-size: 12px;
  color: #303133;
}

.history-message {
  font-size: 11px;
  color: #666;
  flex: 1;
}

.no-history {
  text-align: center;
  padding: 20px;
  color: #909399;
  font-size: 14px;
}

.performance-metrics {
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.metrics-header {
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.metric-item {
  text-align: center;
  padding: 8px;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}

.metric-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.real-time-logs {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  max-height: 250px;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
  background-color: #fafafa;
  border-radius: 8px 8px 0 0;
}

.logs-container {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.log-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 4px;
  padding: 4px;
  border-radius: 2px;
}

.log-level-debug {
  background-color: #f0f0f0;
}

.log-level-info {
  background-color: #e6f7ff;
}

.log-level-warn {
  background-color: #fff7e6;
}

.log-level-error {
  background-color: #fff2f0;
}

.log-time {
  color: #909399;
  min-width: 80px;
}

.log-level {
  font-weight: 600;
  min-width: 50px;
}

.log-level-debug .log-level { color: #909399; }
.log-level-info .log-level { color: #1890ff; }
.log-level-warn .log-level { color: #fa8c16; }
.log-level-error .log-level { color: #f5222d; }

.log-message {
  flex: 1;
  color: #303133;
}

.no-logs {
  text-align: center;
  padding: 20px;
  color: #909399;
  font-size: 14px;
}

/* 滚动条样式 */
:deep(.history-list::-webkit-scrollbar),
:deep(.logs-container::-webkit-scrollbar) {
  width: 6px;
}

:deep(.history-list::-webkit-scrollbar-track),
:deep(.logs-container::-webkit-scrollbar-track) {
  background: #f1f1f1;
  border-radius: 3px;
}

:deep(.history-list::-webkit-scrollbar-thumb),
:deep(.logs-container::-webkit-scrollbar-thumb) {
  background: #c1c1c1;
  border-radius: 3px;
}

:deep(.history-list::-webkit-scrollbar-thumb:hover),
:deep(.logs-container::-webkit-scrollbar-thumb:hover) {
  background: #a8a8a8;
}
</style>