<template>
  <div class="scheduling-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">调度引擎</h1>
          <p class="page-description">智能课程表调度系统，使用先进的约束满足和优化算法生成最优课程表</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="handleCreateJob">
            <el-icon><Plus /></el-icon>
            新建调度任务
          </el-button>
          <el-button @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon total">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ jobStats.total }}</div>
                <div class="stats-label">总任务数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon running">
                <el-icon><Loading /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ jobStats.running }}</div>
                <div class="stats-label">运行中</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon completed">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ jobStats.completed }}</div>
                <div class="stats-label">已完成</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon failed">
                <el-icon><CircleClose /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ jobStats.failed }}</div>
                <div class="stats-label">失败</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <el-row :gutter="16">
        <!-- 左侧：任务列表 -->
        <el-col :span="16">
          <el-card class="jobs-card">
            <template #header>
              <div class="card-header">
                <span>调度任务</span>
                <div class="header-actions">
                  <el-input
                    v-model="searchKeyword"
                    placeholder="搜索任务..."
                    style="width: 200px"
                    clearable
                    @input="handleSearch"
                  >
                    <template #prefix>
                      <el-icon><Search /></el-icon>
                    </template>
                  </el-input>
                  <el-select
                    v-model="statusFilter"
                    placeholder="状态筛选"
                    clearable
                    style="width: 120px"
                    @change="handleStatusFilter"
                  >
                    <el-option label="待处理" value="pending" />
                    <el-option label="运行中" value="running" />
                    <el-option label="已完成" value="completed" />
                    <el-option label="失败" value="failed" />
                    <el-option label="已取消" value="cancelled" />
                  </el-select>
                </div>
              </div>
            </template>

            <JobList
              :jobs="jobs"
              :loading="loading"
              :current-job="currentJob"
              @select="handleSelectJob"
              @cancel="handleCancelJob"
              @restart="handleRestartJob"
              @delete="handleDeleteJob"
              @view-result="handleViewResult"
            />
          </el-card>
        </el-col>

        <!-- 右侧：任务详情和进度 -->
        <el-col :span="8">
          <el-card class="detail-card" v-if="currentJob">
            <template #header>
              <div class="card-header">
                <span>任务详情</span>
                <el-tag :type="getJobStatusType(currentJob.status)">
                  {{ getJobStatusText(currentJob.status) }}
                </el-tag>
              </div>
            </template>

            <div class="job-info">
              <div class="info-item">
                <label>任务名称:</label>
                <span>{{ currentJob.name }}</span>
              </div>
              <div class="info-item">
                <label>优先级:</label>
                <el-tag :type="getPriorityType(currentJob.priority)" size="small">
                  {{ getPriorityText(currentJob.priority) }}
                </el-tag>
              </div>
              <div class="info-item">
                <label>创建时间:</label>
                <span>{{ formatDateTime(currentJob.created_at) }}</span>
              </div>
              <div class="info-item" v-if="currentJob.started_at">
                <label>开始时间:</label>
                <span>{{ formatDateTime(currentJob.started_at) }}</span>
              </div>
              <div class="info-item" v-if="currentJob.completed_at">
                <label>完成时间:</label>
                <span>{{ formatDateTime(currentJob.completed_at) }}</span>
              </div>
              <div class="info-item" v-if="currentJob.error_message">
                <label>错误信息:</label>
                <span class="error-message">{{ currentJob.error_message }}</span>
              </div>
            </div>

            <!-- 进度显示 -->
            <div class="progress-section" v-if="currentJob.status === 'running'">
              <div class="progress-header">
                <span>任务进度</span>
                <span class="progress-text">{{ currentJob.progress }}%</span>
              </div>
              <el-progress
                :percentage="currentJob.progress"
                :status="currentJob.progress === 100 ? 'success' : undefined"
                :stroke-width="8"
              />
              <div class="progress-steps">
                <span>步骤: {{ currentJob.current_step }} / {{ currentJob.total_steps }}</span>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="job-actions">
              <el-button
                v-if="currentJob.status === 'running'"
                type="warning"
                size="small"
                @click="handleCancelJob(currentJob)"
              >
                <el-icon><Close /></el-icon>
                取消任务
              </el-button>
              <el-button
                v-if="currentJob.status === 'failed'"
                type="primary"
                size="small"
                @click="handleRestartJob(currentJob)"
              >
                <el-icon><RefreshRight /></el-icon>
                重启任务
              </el-button>
              <el-button
                v-if="currentJob.status === 'completed'"
                type="success"
                size="small"
                @click="handleViewResult(currentJob)"
              >
                <el-icon><View /></el-icon>
                查看结果
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="handleDeleteJob(currentJob)"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </el-card>

          <!-- 实时进度监控 -->
          <el-card class="progress-card" v-if="currentJob && currentJob.status === 'running'">
            <template #header>
              <div class="card-header">
                <span>实时进度</span>
                <el-tag :type="websocketConnected ? 'success' : 'danger'" size="small">
                  {{ websocketConnected ? '已连接' : '已断开' }}
                </el-tag>
              </div>
            </template>

            <JobProgress
              :job="currentJob"
              :progress="jobProgress"
              :progress-updates="progressUpdates"
            />
          </el-card>

          <!-- 快速操作 -->
          <el-card class="quick-actions-card" v-if="!currentJob">
            <template #header>
              <span>快速操作</span>
            </template>
            <div class="quick-actions">
              <el-button type="primary" block @click="handleCreateJob">
                <el-icon><Plus /></el-icon>
                新建调度任务
              </el-button>
              <el-button block @click="handleImportConfig">
                <el-icon><Upload /></el-icon>
                导入配置
              </el-button>
              <el-button block @click="handleViewStats">
                <el-icon><TrendCharts /></el-icon>
                查看统计
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 新建任务对话框 -->
    <SchedulingForm
      v-model="formVisible"
      :schools="schoolOptions"
      @success="handleFormSuccess"
      @cancel="handleFormCancel"
    />

    <!-- 结果查看对话框 -->
    <ResultViewer
      v-model="resultVisible"
      :job="currentJob"
      :result="jobResult"
      @export="handleExportResult"
    />

    <!-- 统计对话框 -->
    <el-dialog
      v-model="statsVisible"
      title="调度统计"
      width="80%"
      @close="statsVisible = false"
    >
      <div v-if="stats" class="stats-content">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-card>
              <div class="stat-item">
                <div class="stat-value">{{ stats.success_rate }}%</div>
                <div class="stat-label">成功率</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <div class="stat-item">
                <div class="stat-value">{{ formatDuration(stats.average_execution_time) }}</div>
                <div class="stat-label">平均执行时间</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <div class="stat-item">
                <div class="stat-value">{{ stats.total_jobs }}</div>
                <div class="stat-label">总任务数</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Refresh, Search, DataAnalysis, Loading, CircleCheck, CircleClose,
  Close, RefreshRight, View, Delete, Upload, TrendCharts
} from '@element-plus/icons-vue'
import { formatDateTime, formatDuration } from '@/utils/date'
import { useSchedulingStore } from '@/stores/scheduling'
import { useSchoolsStore } from '@/stores/schools'
import type { SchedulingJob, SchedulingJobStatus, SchedulingJobPriority } from '@/api/scheduling'
import JobList from '@/components/Scheduling/JobList.vue'
import JobProgress from '@/components/Scheduling/JobProgress.vue'
import SchedulingForm from '@/components/Scheduling/SchedulingForm.vue'
import ResultViewer from '@/components/Scheduling/ResultViewer.vue'

// 状态管理
const schedulingStore = useSchedulingStore()
const schoolsStore = useSchoolsStore()

// 响应式数据
const formVisible = ref(false)
const resultVisible = ref(false)
const statsVisible = ref(false)
const searchKeyword = ref('')
const statusFilter = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

// 计算属性
const loading = computed(() => schedulingStore.loading)
const jobs = computed(() => schedulingStore.jobs)
const currentJob = computed(() => schedulingStore.currentJob)
const jobResult = computed(() => schedulingStore.jobResult)
const jobProgress = computed(() => schedulingStore.jobProgress)
const jobStats = computed(() => schedulingStore.jobStats)
const stats = computed(() => schedulingStore.stats)
const websocketConnected = computed(() => schedulingStore.websocketConnected)
const progressUpdates = computed(() => schedulingStore.progressUpdates)
const schoolOptions = computed(() => schoolsStore.schoolOptions)

// 方法
const loadJobs = async () => {
  try {
    await schedulingStore.fetchJobs()
  } catch (error) {
    ElMessage.error('加载任务列表失败')
  }
}

const handleCreateJob = () => {
  formVisible.value = true
}

const handleRefresh = () => {
  loadJobs()
}

const handleSearch = () => {
  schedulingStore.searchJobs(searchKeyword.value)
}

const handleStatusFilter = () => {
  const params = statusFilter.value ? { status: statusFilter.value as any } : {}
  schedulingStore.fetchJobs(params)
}

const handleSelectJob = async (job: SchedulingJob) => {
  await schedulingStore.fetchJob(job.id)
  schedulingStore.initWebSocket(job.id)
}

const handleCancelJob = async (job: SchedulingJob) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消任务"${job.name}"吗？`,
      '确认取消',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await schedulingStore.cancelJob(job.id)
    ElMessage.success('任务已取消')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消任务失败')
    }
  }
}

const handleRestartJob = async (job: SchedulingJob) => {
  try {
    await ElMessageBox.confirm(
      `确定要重启任务"${job.name}"吗？`,
      '确认重启',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await schedulingStore.restartJob(job.id)
    ElMessage.success('任务重启成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重启任务失败')
    }
  }
}

const handleDeleteJob = async (job: SchedulingJob) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除任务"${job.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await schedulingStore.deleteJob(job.id)
    ElMessage.success('任务删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除任务失败')
    }
  }
}

const handleViewResult = async (job: SchedulingJob) => {
  try {
    await schedulingStore.fetchJobResult(job.id)
    resultVisible.value = true
  } catch (error) {
    ElMessage.error('获取任务结果失败')
  }
}

const handleExportResult = (format: 'json' | 'csv' | 'excel' | 'pdf') => {
  if (currentJob.value) {
    schedulingStore.exportResult(currentJob.value.id, format)
  }
}

const handleImportConfig = () => {
  fileInput.value?.click()
}

const handleFileChange = async (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (file) {
    try {
      await schedulingStore.importConfig(file)
      ElMessage.success('配置导入成功')
    } catch (error) {
      ElMessage.error('配置导入失败')
    }
  }
}

const handleViewStats = async () => {
  await schedulingStore.fetchSchedulingStats()
  statsVisible.value = true
}

const handleFormSuccess = () => {
  formVisible.value = false
  loadJobs()
}

const handleFormCancel = () => {
  formVisible.value = false
}

// 工具函数
const getJobStatusType = (status: SchedulingJobStatus) => {
  const types: Record<SchedulingJobStatus, string> = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return types[status] || 'info'
}

const getJobStatusText = (status: SchedulingJobStatus) => {
  const texts: Record<SchedulingJobStatus, string> = {
    pending: '待处理',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return texts[status] || '未知'
}

const getPriorityType = (priority: SchedulingJobPriority) => {
  const types: Record<SchedulingJobPriority, string> = {
    low: 'info',
    normal: 'primary',
    high: 'warning',
    urgent: 'danger'
  }
  return types[priority] || 'info'
}

const getPriorityText = (priority: SchedulingJobPriority) => {
  const texts: Record<SchedulingJobPriority, string> = {
    low: '低',
    normal: '普通',
    high: '高',
    urgent: '紧急'
  }
  return texts[priority] || '普通'
}

// 生命周期
onMounted(async () => {
  await schedulingStore.init()
  await schoolsStore.fetchSchools()
})

onUnmounted(() => {
  schedulingStore.cleanup()
})
</script>

<style scoped>
.scheduling-page {
  padding: 16px;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-info h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.header-info p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-section {
  margin-bottom: 24px;
}

.stats-card {
  border-radius: 8px;
}

.stats-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stats-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stats-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stats-icon.running {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stats-icon.completed {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stats-icon.failed {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stats-info {
  flex: 1;
}

.stats-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

.main-content {
  margin-top: 24px;
}

.jobs-card,
.detail-card,
.progress-card,
.quick-actions-card {
  border-radius: 8px;
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.job-info {
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
}

.info-item label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
}

.info-item span {
  color: #303133;
}

.error-message {
  color: #f56c6c;
  font-size: 12px;
}

.progress-section {
  margin-bottom: 16px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.progress-text {
  font-weight: 500;
  color: #409eff;
}

.progress-steps {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.job-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stats-content {
  padding: 16px 0;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

:deep(.el-card__header) {
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-card__body) {
  padding: 16px;
}

:deep(.el-progress-bar__inner) {
  transition: width 0.3s ease;
}
</style>