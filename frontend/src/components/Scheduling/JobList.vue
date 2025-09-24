<template>
  <div class="job-list">
    <!-- 表格工具栏 -->
    <div class="table-toolbar">
      <div class="toolbar-left">
        <el-button
          type="danger"
          size="small"
          :disabled="selectedJobs.length === 0"
          @click="handleBulkDelete"
        >
          <el-icon><Delete /></el-icon>
          批量删除 ({{ selectedJobs.length }})
        </el-button>
        <el-button
          type="warning"
          size="small"
          :disabled="!hasRunningJobs"
          @click="handleBulkCancel"
        >
          <el-icon><Close /></el-icon>
          取消运行中
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-button size="small" @click="$emit('refresh')">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 任务表格 -->
    <el-table
      v-loading="loading"
      :data="jobs"
      style="width: 100%"
      @selection-change="handleSelectionChange"
      @row-click="handleRowClick"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="name" label="任务名称" min-width="200">
        <template #default="{ row }">
          <div class="job-name">
            <el-icon v-if="row.status === 'running'" class="running-icon">
              <Loading />
            </el-icon>
            {{ row.name }}
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="priority" label="优先级" width="80">
        <template #default="{ row }">
          <el-tag :type="getPriorityType(row.priority)" size="small">
            {{ getPriorityText(row.priority) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="progress" label="进度" width="120">
        <template #default="{ row }">
          <div class="progress-cell">
            <el-progress
              :percentage="row.progress"
              :status="getProgressStatus(row.progress, row.status)"
              :stroke-width="6"
              :show-text="false"
              style="width: 80px"
            />
            <span class="progress-text">{{ row.progress }}%</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160">
        <template #default="{ row }">
          {{ formatDateTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column prop="started_at" label="开始时间" width="160">
        <template #default="{ row }">
          {{ row.started_at ? formatDateTime(row.started_at) : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="duration" label="运行时长" width="100">
        <template #default="{ row }">
          {{ getDuration(row) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button
              v-if="row.status === 'running'"
              type="warning"
              link
              size="small"
              @click.stop="handleCancel(row)"
            >
              <el-icon><Close /></el-icon>
              取消
            </el-button>
            <el-button
              v-if="row.status === 'failed'"
              type="primary"
              link
              size="small"
              @click.stop="handleRestart(row)"
            >
              <el-icon><RefreshRight /></el-icon>
              重启
            </el-button>
            <el-button
              v-if="row.status === 'completed'"
              type="success"
              link
              size="small"
              @click.stop="handleViewResult(row)"
            >
              <el-icon><View /></el-icon>
              结果
            </el-button>
            <el-dropdown @command="(cmd) => handleDropdownCommand(cmd, row)">
              <el-button link size="small">
                <el-icon><More /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="detail">
                    <el-icon><InfoFilled /></el-icon>
                    详情
                  </el-dropdown-item>
                  <el-dropdown-item command="export" v-if="row.status === 'completed'">
                    <el-icon><Download /></el-icon>
                    导出
                  </el-dropdown-item>
                  <el-dropdown-item command="logs">
                    <el-icon><Document /></el-icon>
                    日志
                  </el-dropdown-item>
                  <el-dropdown-item divided command="delete">
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页器 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="任务详情"
      width="800px"
      @close="detailVisible = false"
    >
      <div v-if="selectedJobForDetail" class="job-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务名称">{{ selectedJobForDetail.name }}</el-descriptions-item>
          <el-descriptions-item label="任务描述">{{ selectedJobForDetail.description || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedJobForDetail.status)">
              {{ getStatusText(selectedJobForDetail.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityType(selectedJobForDetail.priority)">
              {{ getPriorityText(selectedJobForDetail.priority) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="进度">{{ selectedJobForDetail.progress }}%</el-descriptions-item>
          <el-descriptions-item label="步骤">{{ selectedJobForDetail.current_step }} / {{ selectedJobForDetail.total_steps }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(selectedJobForDetail.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ selectedJobForDetail.started_at ? formatDateTime(selectedJobForDetail.started_at) : '-' }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ selectedJobForDetail.completed_at ? formatDateTime(selectedJobForDetail.completed_at) : '-' }}</el-descriptions-item>
          <el-descriptions-item label="取消时间">{{ selectedJobForDetail.cancelled_at ? formatDateTime(selectedJobForDetail.cancelled_at) : '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建人">{{ selectedJobForDetail.created_by }}</el-descriptions-item>
          <el-descriptions-item label="租户ID">{{ selectedJobForDetail.tenant_id }}</el-descriptions-item>
          <el-descriptions-item v-if="selectedJobForDetail.error_message" label="错误信息" :span="2">
            <div class="error-message">{{ selectedJobForDetail.error_message }}</div>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 配置信息 -->
        <div class="config-section">
          <h4>调度配置</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="学校ID">{{ selectedJobForDetail.config.school_id }}</el-descriptions-item>
            <el-descriptions-item label="学年">{{ selectedJobForDetail.config.academic_year }}</el-descriptions-item>
            <el-descriptions-item label="学期">{{ selectedJobForDetail.config.semester }}</el-descriptions-item>
            <el-descriptions-item label="工作日">{{ selectedJobForDetail.config.week_days.join(', ') }}</el-descriptions-item>
            <el-descriptions-item label="时间槽数量">{{ selectedJobForDetail.config.time_slots.length }}</el-descriptions-item>
            <el-descriptions-item label="约束数量">{{ selectedJobForDetail.config.constraints.length }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 算法参数 -->
        <div class="algorithm-section">
          <h4>算法参数</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="最大迭代次数">{{ selectedJobForDetail.config.algorithm_params.max_iterations }}</el-descriptions-item>
            <el-descriptions-item label="时间限制">{{ selectedJobForDetail.config.algorithm_params.time_limit_seconds }}秒</el-descriptions-item>
            <el-descriptions-item label="搜索策略">{{ selectedJobForDetail.config.algorithm_params.search_strategy }}</el-descriptions-item>
            <el-descriptions-item label="并行计算">{{ selectedJobForDetail.config.algorithm_params.enable_parallel ? '是' : '否' }}</el-descriptions-item>
            <el-descriptions-item v-if="selectedJobForDetail.config.algorithm_params.enable_parallel" label="并行工作数">{{ selectedJobForDetail.config.algorithm_params.parallel_workers }}</el-descriptions-item>
            <el-descriptions-item label="启用日志">{{ selectedJobForDetail.config.algorithm_params.enable_logging ? '是' : '否' }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-dialog>

    <!-- 导出对话框 -->
    <el-dialog
      v-model="exportVisible"
      title="导出结果"
      width="400px"
      @close="exportVisible = false"
    >
      <div class="export-form">
        <el-form :model="exportForm" label-width="80px">
          <el-form-item label="导出格式">
            <el-select v-model="exportForm.format" style="width: 100%">
              <el-option label="JSON" value="json" />
              <el-option label="CSV" value="csv" />
              <el-option label="Excel" value="excel" />
              <el-option label="PDF" value="pdf" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="exportVisible = false">取消</el-button>
        <el-button type="primary" @click="handleExportConfirm">确认导出</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Loading, Refresh, Delete, Close, RefreshRight, View, More,
  InfoFilled, Download, Document
} from '@element-plus/icons-vue'
import { formatDateTime, formatDuration } from '@/utils/date'
import type { SchedulingJob, SchedulingJobStatus, SchedulingJobPriority } from '@/api/scheduling'

interface Props {
  jobs: SchedulingJob[]
  loading: boolean
  currentJob: SchedulingJob | null
  total: number
  currentPage: number
  pageSize: number
}

interface Emits {
  (e: 'select', job: SchedulingJob): void
  (e: 'cancel', job: SchedulingJob): void
  (e: 'restart', job: SchedulingJob): void
  (e: 'delete', job: SchedulingJob): void
  (e: 'view-result', job: SchedulingJob): void
  (e: 'refresh'): void
  (e: 'bulk-delete', jobs: SchedulingJob[]): void
  (e: 'bulk-cancel'): void
  (e: 'export', job: SchedulingJob, format: string): void
  (e: 'size-change', size: number): void
  (e: 'current-change', page: number): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 响应式数据
const selectedJobs = ref<SchedulingJob[]>([])
const detailVisible = ref(false)
const exportVisible = ref(false)
const selectedJobForDetail = ref<SchedulingJob | null>(null)
const selectedJobForExport = ref<SchedulingJob | null>(null)
const exportForm = ref({ format: 'json' })

// 计算属性
const hasRunningJobs = computed(() =>
  props.jobs.some(job => job.status === 'running')
)

// 方法
const handleSelectionChange = (selection: SchedulingJob[]) => {
  selectedJobs.value = selection
}

const handleRowClick = (row: SchedulingJob) => {
  emit('select', row)
}

const handleCancel = async (job: SchedulingJob) => {
  emit('cancel', job)
}

const handleRestart = async (job: SchedulingJob) => {
  emit('restart', job)
}

const handleDelete = async (job: SchedulingJob) => {
  emit('delete', job)
}

const handleViewResult = (job: SchedulingJob) => {
  emit('view-result', job)
}

const handleBulkDelete = async () => {
  if (selectedJobs.value.length === 0) return

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedJobs.value.length} 个任务吗？此操作不可恢复。`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    emit('bulk-delete', selectedJobs.value)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleBulkCancel = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要取消所有运行中的任务吗？',
      '确认批量取消',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    emit('bulk-cancel')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量取消失败')
    }
  }
}

const handleDropdownCommand = (command: string, job: SchedulingJob) => {
  switch (command) {
    case 'detail':
      selectedJobForDetail.value = job
      detailVisible.value = true
      break
    case 'export':
      selectedJobForExport.value = job
      exportVisible.value = true
      break
    case 'logs':
      // TODO: 实现查看日志功能
      ElMessage.info('日志功能开发中')
      break
    case 'delete':
      handleDelete(job)
      break
  }
}

const handleExportConfirm = () => {
  if (selectedJobForExport.value) {
    emit('export', selectedJobForExport.value, exportForm.value.format)
    exportVisible.value = false
  }
}

const handleSizeChange = (size: number) => {
  emit('size-change', size)
}

const handleCurrentChange = (page: number) => {
  emit('current-change', page)
}

const getStatusType = (status: SchedulingJobStatus) => {
  const types: Record<SchedulingJobStatus, string> = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status: SchedulingJobStatus) => {
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

const getProgressStatus = (progress: number, status: SchedulingJobStatus) => {
  if (status === 'failed') return 'exception'
  if (status === 'cancelled') return 'warning'
  if (progress === 100) return 'success'
  return undefined
}

const getDuration = (job: SchedulingJob) => {
  const startTime = job.started_at ? new Date(job.started_at).getTime() : null
  const endTime = job.completed_at || job.cancelled_at
    ? new Date(job.completed_at || job.cancelled_at!).getTime()
    : Date.now()

  if (!startTime) return '-'

  const duration = endTime - startTime
  return formatDuration(duration)
}
</script>

<style scoped>
.job-list {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 8px;
}

.job-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.running-icon {
  color: #409eff;
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-text {
  font-size: 12px;
  color: #606266;
  min-width: 35px;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.job-detail {
  max-height: 600px;
  overflow-y: auto;
}

.job-detail h4 {
  margin: 20px 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.config-section,
.algorithm-section {
  margin-top: 20px;
}

.error-message {
  color: #f56c6c;
  font-size: 12px;
  line-height: 1.4;
  max-height: 100px;
  overflow-y: auto;
  padding: 8px;
  background-color: #fef2f2;
  border-radius: 4px;
  border: 1px solid #fecaca;
}

.export-form {
  padding: 20px 0;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

:deep(.el-table__row.selected) {
  background-color: #e6f7ff;
}

:deep(.el-descriptions__label) {
  font-weight: 500;
}

:deep(.el-descriptions__content) {
  color: #606266;
}
</style>