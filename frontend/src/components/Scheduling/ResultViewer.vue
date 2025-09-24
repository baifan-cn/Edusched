<template>
  <el-dialog
    v-model="visible"
    title="调度结果"
    width="90%"
    :before-close="handleClose"
    @close="handleClose"
  >
    <div class="result-viewer" v-if="result">
      <!-- 结果概览 -->
      <div class="result-overview">
        <el-row :gutter="16">
          <el-col :span="6">
            <el-card class="overview-card">
              <div class="overview-content">
                <div class="overview-icon" :class="{ success: result.success, error: !result.success }">
                  <el-icon><component :is="result.success ? 'CircleCheck' : 'CircleClose'" /></el-icon>
                </div>
                <div class="overview-info">
                  <div class="overview-value">{{ result.success ? '成功' : '失败' }}</div>
                  <div class="overview-label">调度状态</div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="overview-card">
              <div class="overview-content">
                <div class="overview-icon total">
                  <el-icon><Grid /></el-icon>
                </div>
                <div class="overview-info">
                  <div class="overview-value">{{ result.total_assignments }}</div>
                  <div class="overview-label">总分配数</div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="overview-card">
              <div class="overview-content">
                <div class="overview-icon" :class="{ warning: result.conflict_count > 0 }">
                  <el-icon><WarningFilled /></el-icon>
                </div>
                <div class="overview-info">
                  <div class="overview-value">{{ result.conflict_count }}</div>
                  <div class="overview-label">冲突数量</div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="overview-card">
              <div class="overview-content">
                <div class="overview-icon" :class="{ success: result.score > 0.8, warning: result.score > 0.5, error: result.score <= 0.5 }">
                  <el-icon><Trophy /></el-icon>
                </div>
                <div class="overview-info">
                  <div class="overview-value">{{ (result.score * 100).toFixed(1) }}%</div>
                  <div class="overview-label">综合得分</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 性能指标 -->
      <div class="performance-metrics">
        <h3 class="section-title">性能指标</h3>
        <el-row :gutter="16">
          <el-col :span="8">
            <div class="metric-item">
              <div class="metric-header">
                <span>执行时间</span>
                <el-tag type="info" size="small">{{ formatDuration(result.execution_time_ms) }}</el-tag>
              </div>
              <div class="metric-value">{{ result.execution_time_ms }}ms</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="metric-item">
              <div class="metric-header">
                <span>迭代次数</span>
                <el-tag type="info" size="small">{{ result.iterations }}</el-tag>
              </div>
              <div class="metric-value">{{ result.iterations }}</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="metric-item">
              <div class="metric-header">
                <span>平均速度</span>
                <el-tag type="info" size="small">{{ (result.iterations / (result.execution_time_ms / 1000)).toFixed(1) }}/s</el-tag>
              </div>
              <div class="metric-value">{{ (result.iterations / (result.execution_time_ms / 1000)).toFixed(1) }} 次/秒</div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 统计信息 -->
      <div class="statistics-section">
        <h3 class="section-title">统计信息</h3>
        <el-row :gutter="16">
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-content">
                <div class="stat-value">{{ (result.statistics.teacher_utilization * 100).toFixed(1) }}%</div>
                <div class="stat-label">教师利用率</div>
                <el-progress
                  :percentage="result.statistics.teacher_utilization * 100"
                  :stroke-width="8"
                  :show-text="false"
                />
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-content">
                <div class="stat-value">{{ (result.statistics.room_utilization * 100).toFixed(1) }}%</div>
                <div class="stat-label">教室利用率</div>
                <el-progress
                  :percentage="result.statistics.room_utilization * 100"
                  :stroke-width="8"
                  :show-text="false"
                />
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-content">
                <div class="stat-value">{{ (result.statistics.class_coverage * 100).toFixed(1) }}%</div>
                <div class="stat-label">班级覆盖率</div>
                <el-progress
                  :percentage="result.statistics.class_coverage * 100"
                  :stroke-width="8"
                  :show-text="false"
                />
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-content">
                <div class="stat-value">{{ (result.statistics.constraint_satisfaction * 100).toFixed(1) }}%</div>
                <div class="stat-label">约束满足度</div>
                <el-progress
                  :percentage="result.statistics.constraint_satisfaction * 100"
                  :stroke-width="8"
                  :show-text="false"
                />
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 主要内容区域 -->
      <div class="main-content">
        <el-tabs v-model="activeTab" @tab-click="handleTabChange">
          <el-tab-pane label="分配结果" name="assignments">
            <div class="assignments-section">
              <div class="section-header">
                <div class="header-left">
                  <span>分配结果 ({{ result.assignments.length }})</span>
                  <el-input
                    v-model="searchKeyword"
                    placeholder="搜索分配..."
                    style="width: 200px"
                    clearable
                  >
                    <template #prefix>
                      <el-icon><Search /></el-icon>
                    </template>
                  </el-input>
                </div>
                <div class="header-right">
                  <el-button size="small" @click="exportAssignments">
                    <el-icon><Download /></el-icon>
                    导出
                  </el-button>
                </div>
              </div>

              <el-table
                :data="filteredAssignments"
                style="width: 100%"
                max-height="400"
                stripe
              >
                <el-table-column prop="course_id" label="课程ID" width="120" />
                <el-table-column prop="teacher_id" label="教师ID" width="120" />
                <el-table-column prop="class_id" label="班级ID" width="120" />
                <el-table-column prop="room_id" label="教室ID" width="120" />
                <el-table-column prop="time_slot_id" label="时间槽" width="120" />
                <el-table-column prop="day_of_week" label="星期" width="80">
                  <template #default="{ row }">
                    {{ getDayName(row.day_of_week) }}
                  </template>
                </el-table-column>
                <el-table-column prop="week_number" label="周次" width="80" />
                <el-table-column prop="score" label="得分" width="80">
                  <template #default="{ row }">
                    <el-tag :type="getScoreType(row.score)" size="small">
                      {{ (row.score * 100).toFixed(0) }}%
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="冲突" width="100">
                  <template #default="{ row }">
                    <el-tag
                      v-if="row.conflicts.length > 0"
                      type="danger"
                      size="small"
                    >
                      {{ row.conflicts.length }} 个
                    </el-tag>
                    <el-tag v-else type="success" size="small">
                      无
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>

              <div class="pagination-wrapper" v-if="filteredAssignments.length > 50">
                <el-pagination
                  v-model:current-page="currentPage"
                  v-model:page-size="pageSize"
                  :page-sizes="[20, 50, 100]"
                  :total="filteredAssignments.length"
                  layout="total, sizes, prev, pager, next"
                  @size-change="handleSizeChange"
                  @current-change="handleCurrentChange"
                />
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="冲突分析" name="conflicts">
            <div class="conflicts-section">
              <div class="section-header">
                <span>冲突分析 ({{ result.conflicts.length }})</span>
                <div class="conflict-filters">
                  <el-select v-model="conflictFilter" placeholder="按类型筛选" clearable>
                    <el-option label="教师冲突" value="teacher" />
                    <el-option label="教室冲突" value="room" />
                    <el-option label="班级冲突" value="class" />
                    <el-option label="时间冲突" value="time" />
                  </el-select>
                </div>
              </div>

              <div class="conflicts-list">
                <div
                  v-for="conflict in filteredConflicts"
                  :key="conflict.id"
                  class="conflict-item"
                  :class="conflict.severity"
                >
                  <div class="conflict-header">
                    <div class="conflict-type">
                      <el-icon><Warning /></el-icon>
                      {{ conflict.type }}
                    </div>
                    <div class="conflict-severity">
                      <el-tag :type="getSeverityType(conflict.severity)" size="small">
                        {{ getSeverityText(conflict.severity) }}
                      </el-tag>
                    </div>
                  </div>
                  <div class="conflict-message">{{ conflict.message }}</div>
                  <div class="conflict-details" v-if="Object.keys(conflict.details).length > 0">
                    <div
                      v-for="(value, key) in conflict.details"
                      :key="key"
                      class="detail-item"
                    >
                      <span class="detail-key">{{ formatDetailKey(key) }}:</span>
                      <span class="detail-value">{{ formatDetailValue(value) }}</span>
                    </div>
                  </div>
                  <div class="affected-resources" v-if="conflict.affected_resources.length > 0">
                    <span class="resources-label">影响资源:</span>
                    <el-tag
                      v-for="resource in conflict.affected_resources"
                      :key="resource"
                      size="small"
                      style="margin-right: 4px"
                    >
                      {{ resource }}
                    </el-tag>
                  </div>
                </div>
                <div v-if="filteredConflicts.length === 0" class="no-conflicts">
                  <el-empty description="暂无冲突" />
                </div>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="警告信息" name="warnings">
            <div class="warnings-section">
              <div class="section-header">
                <span>警告信息 ({{ result.warnings.length }})</span>
              </div>

              <div class="warnings-list">
                <div
                  v-for="warning in result.warnings"
                  :key="warning.id"
                  class="warning-item"
                >
                  <div class="warning-header">
                    <div class="warning-type">
                      <el-icon><InfoFilled /></el-icon>
                      {{ warning.type }}
                    </div>
                  </div>
                  <div class="warning-message">{{ warning.message }}</div>
                  <div class="warning-details" v-if="Object.keys(warning.details).length > 0">
                    <div
                      v-for="(value, key) in warning.details"
                      :key="key"
                      class="detail-item"
                    >
                      <span class="detail-key">{{ formatDetailKey(key) }}:</span>
                      <span class="detail-value">{{ formatDetailValue(value) }}</span>
                    </div>
                  </div>
                  <div class="warning-suggestions" v-if="warning.suggestions.length > 0">
                    <span class="suggestions-label">建议:</span>
                    <ul class="suggestions-list">
                      <li v-for="suggestion in warning.suggestions" :key="suggestion">
                        {{ suggestion }}
                      </li>
                    </ul>
                  </div>
                </div>
                <div v-if="result.warnings.length === 0" class="no-warnings">
                  <el-empty description="暂无警告" />
                </div>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="执行日志" name="logs">
            <div class="logs-section">
              <div class="section-header">
                <span>执行日志 ({{ result.logs.length }})</span>
                <div class="log-filters">
                  <el-select v-model="logLevelFilter" placeholder="按级别筛选" clearable>
                    <el-option label="调试" value="debug" />
                    <el-option label="信息" value="info" />
                    <el-option label="警告" value="warn" />
                    <el-option label="错误" value="error" />
                  </el-select>
                  <el-button size="small" @click="exportLogs">
                    <el-icon><Download /></el-icon>
                    导出日志
                  </el-button>
                </div>
              </div>

              <div class="logs-container">
                <div
                  v-for="log in filteredLogs"
                  :key="log.timestamp"
                  class="log-item"
                  :class="`log-level-${log.level}`"
                >
                  <div class="log-time">{{ formatDateTime(log.timestamp) }}</div>
                  <div class="log-level">{{ log.level.toUpperCase() }}</div>
                  <div class="log-message">{{ log.message }}</div>
                  <div class="log-details" v-if="log.details && Object.keys(log.details).length > 0">
                    <el-collapse>
                      <el-collapse-item title="详细信息">
                        <pre>{{ JSON.stringify(log.details, null, 2) }}</pre>
                      </el-collapse-item>
                    </el-collapse>
                  </div>
                </div>
                <div v-if="filteredLogs.length === 0" class="no-logs">
                  <el-empty description="暂无日志" />
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <!-- 对话框底部 -->
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button type="primary" @click="handleExport">导出结果</el-button>
        <el-button type="success" @click="handleSaveReport">保存报告</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  CircleCheck, CircleClose, Grid, WarningFilled, Trophy,
  Search, Download, Warning, InfoFilled
} from '@element-plus/icons-vue'
import { formatDateTime, formatDuration } from '@/utils/date'
import type { SchedulingJob, SchedulingResult } from '@/api/scheduling'

interface Props {
  modelValue: boolean
  job: SchedulingJob | null
  result: SchedulingResult | null
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'export', format: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 响应式数据
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})
const activeTab = ref('assignments')
const searchKeyword = ref('')
const conflictFilter = ref('')
const logLevelFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// 计算属性
const filteredAssignments = computed(() => {
  if (!props.result) return []

  let assignments = props.result.assignments

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    assignments = assignments.filter(assignment =>
      Object.values(assignment).some(value =>
        String(value).toLowerCase().includes(keyword)
      )
    )
  }

  return assignments
})

const filteredConflicts = computed(() => {
  if (!props.result) return []

  let conflicts = props.result.conflicts

  if (conflictFilter.value) {
    conflicts = conflicts.filter(conflict =>
      conflict.type.toLowerCase().includes(conflictFilter.value.toLowerCase())
    )
  }

  return conflicts
})

const filteredLogs = computed(() => {
  if (!props.result) return []

  let logs = props.result.logs

  if (logLevelFilter.value) {
    logs = logs.filter(log => log.level === logLevelFilter.value)
  }

  return logs
})

// 方法
const handleTabChange = () => {
  // 标签切换时的处理
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

const getDayName = (dayOfWeek: number) => {
  const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return days[dayOfWeek] || '未知'
}

const getScoreType = (score: number) => {
  if (score >= 0.8) return 'success'
  if (score >= 0.6) return 'warning'
  return 'danger'
}

const getSeverityType = (severity: string) => {
  const types: Record<string, string> = {
    error: 'danger',
    warning: 'warning',
    info: 'info'
  }
  return types[severity] || 'info'
}

const getSeverityText = (severity: string) => {
  const texts: Record<string, string> = {
    error: '错误',
    warning: '警告',
    info: '信息'
  }
  return texts[severity] || '未知'
}

const formatDetailKey = (key: string) => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatDetailValue = (value: any) => {
  if (typeof value === 'boolean') {
    return value ? '是' : '否'
  }
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  return String(value)
}

const exportAssignments = () => {
  emit('export', 'excel')
}

const exportLogs = () => {
  emit('export', 'json')
}

const handleExport = () => {
  emit('export', 'excel')
}

const handleSaveReport = () => {
  ElMessage.success('报告保存成功')
}

const handleClose = () => {
  visible.value = false
}
</script>

<style scoped>
.result-viewer {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-overview {
  margin-bottom: 20px;
}

.overview-card {
  border-radius: 8px;
  border: none;
}

.overview-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.overview-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.overview-icon.success {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
}

.overview-icon.error {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.overview-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.overview-icon.warning {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.overview-info {
  flex: 1;
}

.overview-value {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.overview-label {
  font-size: 14px;
  color: #909399;
}

.performance-metrics,
.statistics-section {
  margin-bottom: 20px;
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.metric-item {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #ebeef5;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.stat-card {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #ebeef5;
}

.stat-content {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.main-content {
  flex: 1;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-right {
  display: flex;
  gap: 8px;
}

.assignments-section,
.conflicts-section,
.warnings-section,
.logs-section {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.conflicts-list,
.warnings-list,
.logs-container {
  max-height: 400px;
  overflow-y: auto;
}

.conflict-item {
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
}

.conflict-item.error {
  border-left: 4px solid #f56c6c;
  background-color: #fef2f2;
}

.conflict-item.warning {
  border-left: 4px solid #e6a23c;
  background-color: #fdf6ec;
}

.conflict-item.info {
  border-left: 4px solid #409eff;
  background-color: #f0f9ff;
}

.conflict-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.conflict-type {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #303133;
}

.conflict-message {
  color: #606266;
  margin-bottom: 8px;
}

.conflict-details,
.warning-details {
  margin-bottom: 8px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  margin-bottom: 4px;
}

.detail-key {
  color: #909399;
  font-weight: 500;
}

.detail-value {
  color: #606266;
}

.affected-resources {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.resources-label {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.warning-item {
  border: 1px solid #e6a23c;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
  background-color: #fdf6ec;
}

.warning-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 500;
  color: #303133;
}

.warning-message {
  color: #606266;
  margin-bottom: 8px;
}

.warning-suggestions {
  margin-top: 8px;
}

.suggestions-label {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
  margin-bottom: 4px;
}

.suggestions-list {
  margin: 0;
  padding-left: 20px;
  color: #606266;
  font-size: 12px;
}

.suggestions-list li {
  margin-bottom: 4px;
}

.log-item {
  border-left: 3px solid #e9ecef;
  padding: 8px 12px;
  margin-bottom: 8px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.log-level-debug {
  border-left-color: #909399;
  background-color: #f8f9fa;
}

.log-level-info {
  border-left-color: #409eff;
  background-color: #e6f7ff;
}

.log-level-warn {
  border-left-color: #e6a23c;
  background-color: #fdf6ec;
}

.log-level-error {
  border-left-color: #f56c6c;
  background-color: #fef2f2;
}

.log-time {
  color: #909399;
  margin-right: 12px;
}

.log-level {
  color: #303133;
  font-weight: 500;
  margin-right: 12px;
  min-width: 60px;
}

.log-message {
  color: #606266;
  flex: 1;
}

.no-conflicts,
.no-warnings,
.no-logs {
  text-align: center;
  padding: 40px;
}

.conflict-filters,
.log-filters {
  display: flex;
  gap: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-card__body) {
  padding: 16px;
}

:deep(.el-collapse-item__content) {
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 4px;
  margin-top: 8px;
}

:deep(.el-collapse-item__header) {
  font-size: 12px;
  color: #909399;
}

:deep(.el-table__row) {
  font-size: 12px;
}

:deep(.el-table__header th) {
  font-size: 12px;
  font-weight: 500;
}
</style>