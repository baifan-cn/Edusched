<template>
  <div class="timetable-view">
    <!-- 头部信息 -->
    <div class="view-header">
      <div class="header-info">
        <h2 class="timetable-name">{{ currentTimetable?.name }}</h2>
        <p class="timetable-description">{{ currentTimetable?.description || '暂无描述' }}</p>
        <div class="timetable-meta">
          <el-tag :type="getStatusType(currentTimetable?.status)">
            {{ getStatusText(currentTimetable?.status) }}
          </el-tag>
          <span class="meta-item">
            <el-icon><Calendar /></el-icon>
            创建时间: {{ formatDate(currentTimetable?.created_at) }}
          </span>
          <span v-if="currentTimetable?.published_at" class="meta-item">
            <el-icon><Check /></el-icon>
            发布时间: {{ formatDate(currentTimetable?.published_at) }}
          </span>
        </div>
      </div>
      <div class="header-actions">
        <el-button-group>
          <el-button
            :type="viewMode === 'grid' ? 'primary' : 'default'"
            size="small"
            @click="viewMode = 'grid'"
          >
            <el-icon><Grid /></el-icon>
            网格视图
          </el-button>
          <el-button
            :type="viewMode === 'list' ? 'primary' : 'default'"
            size="small"
            @click="viewMode = 'list'"
          >
            <el-icon><List /></el-icon>
            列表视图
          </el-button>
          <el-button
            :type="viewMode === 'stats' ? 'primary' : 'default'"
            size="small"
            @click="viewMode = 'stats'"
          >
            <el-icon><PieChart /></el-icon>
            统计视图
          </el-button>
        </el-button-group>

        <el-dropdown @command="handleAction">
          <el-button type="primary" size="small">
            操作
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="edit" :disabled="!canEdit">
                <el-icon><Edit /></el-icon>
                编辑
              </el-dropdown-item>
              <el-dropdown-item command="duplicate">
                <el-icon><CopyDocument /></el-icon>
                复制
              </el-dropdown-item>
              <el-dropdown-item v-if="!isPublished" command="publish" divided>
                <el-icon><Upload /></el-icon>
                发布
              </el-dropdown-item>
              <el-dropdown-item v-if="isPublished" command="unpublish">
                <el-icon><Download /></el-icon>
                取消发布
              </el-dropdown-item>
              <el-dropdown-item command="optimize">
                <el-icon><MagicStick /></el-icon>
                优化
              </el-dropdown-item>
              <el-dropdown-item divided command="export">
                <el-icon><Document /></el-icon>
                导出
              </el-dropdown-item>
              <el-dropdown-item command="print">
                <el-icon><Printer /></el-icon>
                打印
              </el-dropdown-item>
              <el-dropdown-item v-if="canDelete" command="delete" divided class="danger-item">
                <el-icon><Delete /></el-icon>
                删除
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 标签页 -->
    <el-tabs v-model="activeTab" class="view-tabs">
      <el-tab-pane label="时间表网格" name="grid">
        <TimetableGrid
          :timetable-id="timetableId"
          :grid-data="timetableGrid"
          :loading="loading"
          @refresh="loadTimetableData"
          @optimize="handleOptimize"
          @export="handleExport"
          @print="handlePrint"
          @cell-click="handleCellClick"
          @assignment-edit="handleAssignmentEdit"
          @assignment-delete="handleAssignmentDelete"
        />
      </el-tab-pane>

      <el-tab-pane label="课程安排" name="assignments">
        <div class="assignments-section">
          <div class="section-toolbar">
            <el-input
              v-model="searchQuery"
              placeholder="搜索课程安排..."
              style="width: 300px"
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="handleAddAssignment">
              <el-icon><Plus /></el-icon>
              新增安排
            </el-button>
          </div>

          <el-table
            v-loading="assignmentsLoading"
            :data="filteredAssignments"
            stripe
            border
            style="width: 100%"
          >
            <el-table-column prop="section.name" label="教学段" min-width="120" />
            <el-table-column prop="section.teacher_id" label="教师" width="100" />
            <el-table-column prop="section.class_group_id" label="班级" width="100" />
            <el-table-column prop="timeslot.week_day" label="星期" width="80">
              <template #default="scope">
                {{ getWeekDayText(scope.row.timeslot?.week_day) }}
              </template>
            </el-table-column>
            <el-table-column label="时间段" width="120">
              <template #default="scope">
                {{ formatTime(scope.row.timeslot?.start_time) }}-{{ formatTime(scope.row.timeslot?.end_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="room.name" label="教室" width="100" />
            <el-table-column prop="is_locked" label="状态" width="80" align="center">
              <template #default="scope">
                <el-tag :type="scope.row.is_locked ? 'warning' : 'success'" size="small">
                  {{ scope.row.is_locked ? '锁定' : '正常' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="notes" label="备注" min-width="150" show-overflow-tooltip />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="scope">
                <el-button
                  size="small"
                  link
                  @click="handleAssignmentEdit(scope.row)"
                >
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button
                  size="small"
                  link
                  type="danger"
                  @click="handleAssignmentDelete(scope.row)"
                >
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="统计信息" name="stats">
        <div class="stats-section">
          <!-- 统计卡片 -->
          <el-row :gutter="16" class="stats-cards">
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon total">
                    <el-icon><Calendar /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ timetableStats?.total_sections || 0 }}</div>
                    <div class="stat-label">总教学段</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon assigned">
                    <el-icon><Check /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ timetableStats?.assigned_sections || 0 }}</div>
                    <div class="stat-label">已安排</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon teachers">
                    <el-icon><User /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ timetableStats?.total_teachers || 0 }}</div>
                    <div class="stat-label">教师数</div>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon utilization">
                    <el-icon><TrendCharts /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ ((timetableStats?.room_utilization_rate || 0) * 100).toFixed(1) }}%</div>
                    <div class="stat-label">教室利用率</div>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 冲突信息 -->
          <div v-if="hasConflicts" class="conflicts-section">
            <h3 class="section-title">
              <el-icon><WarningFilled /></el-icon>
              冲突信息 ({{ conflictCount }})
            </h3>
            <el-table
              :data="timetableConflicts"
              stripe
              style="width: 100%"
            >
              <el-table-column prop="type" label="类型" width="100">
                <template #default="scope">
                  <el-tag :type="getConflictType(scope.row.type)" size="small">
                    {{ getConflictTypeText(scope.row.type) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="severity" label="严重程度" width="100">
                <template #default="scope">
                  <el-tag :type="getSeverityType(scope.row.severity)" size="small">
                    {{ getSeverityText(scope.row.severity) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="message" label="描述" min-width="200" />
              <el-table-column label="建议" min-width="200">
                <template #default="scope">
                  <div class="suggestions">
                    <div
                      v-for="(suggestion, index) in scope.row.suggestions"
                      :key="index"
                      class="suggestion-item"
                    >
                      {{ suggestion }}
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100">
                <template #default="scope">
                  <el-button
                    size="small"
                    link
                    @click="handleResolveConflict(scope.row)"
                  >
                    解决
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 详细统计 -->
          <div class="detailed-stats">
            <h3 class="section-title">详细统计</h3>
            <el-row :gutter="16">
              <el-col :span="8">
                <el-card>
                  <template #header>
                    <div class="card-header">
                      <span>教师统计</span>
                    </div>
                  </template>
                  <div class="stats-list">
                    <div class="stats-item">
                      <span class="label">平均课时/教师:</span>
                      <span class="value">{{ timetableStats?.average_hours_per_teacher || 0 }}小时</span>
                    </div>
                    <div class="stats-item">
                      <span class="label">最大课时/教师:</span>
                      <span class="value">--</span>
                    </div>
                    <div class="stats-item">
                      <span class="label">最小课时/教师:</span>
                      <span class="value">--</span>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card>
                  <template #header>
                    <div class="card-header">
                      <span>教室统计</span>
                    </div>
                  </template>
                  <div class="stats-list">
                    <div class="stats-item">
                      <span class="label">总教室数:</span>
                      <span class="value">{{ timetableStats?.total_rooms || 0 }}</span>
                    </div>
                    <div class="stats-item">
                      <span class="label">使用率:</span>
                      <span class="value">{{ ((timetableStats?.room_utilization_rate || 0) * 100).toFixed(1) }}%</span>
                    </div>
                    <div class="stats-item">
                      <span class="label">平均容量:</span>
                      <span class="value">--</span>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card>
                  <template #header>
                    <div class="card-header">
                      <span>质量指标</span>
                    </div>
                  </template>
                  <div class="stats-list">
                    <div class="stats-item">
                      <span class="label">约束违反:</span>
                      <span class="value">{{ timetableStats?.constraint_violations || 0 }}</span>
                    </div>
                    <div class="stats-item">
                      <span class="label">冲突数量:</span>
                      <span class="value">{{ timetableStats?.conflict_count || 0 }}</span>
                    </div>
                    <div class="stats-item">
                      <span class="label">完成度:</span>
                      <span class="value">{{ getCompletionPercentage() }}%</span>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="历史记录" name="history">
        <div class="history-section">
          <el-timeline>
            <el-timeline-item
              v-for="record in historyRecords"
              :key="record.id"
              :timestamp="formatDateTime(record.timestamp)"
              :type="getRecordType(record.type)"
            >
              <div class="record-content">
                <div class="record-title">{{ record.title }}</div>
                <div class="record-description">{{ record.description }}</div>
                <div class="record-user">操作人: {{ record.user }}</div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 课程安排表单 -->
    <AssignmentForm
      v-model="assignmentFormVisible"
      :assignment="currentAssignment"
      :timetable-id="timetableId"
      @success="handleAssignmentSuccess"
      @cancel="assignmentFormVisible = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Grid,
  List,
  PieChart,
  Edit,
  CopyDocument,
  Upload,
  Download,
  MagicStick,
  Document,
  Printer,
  Delete,
  ArrowDown,
  Search,
  Plus,
  Check,
  Calendar,
  User,
  TrendCharts,
  WarningFilled
} from '@element-plus/icons-vue'
import { useTimetablesStore } from '@/stores/timetables'
import TimetableGrid from './TimetableGrid.vue'
import AssignmentForm from '../Forms/AssignmentForm.vue'
import type {
  Timetable,
  Assignment,
  TimetableGridData,
  TimetableStats,
  TimetableConflict,
  WeekDay
} from '@/types/timetables'
import { formatDate, formatDateTime, formatTime } from '@/utils/date'

// Props
interface Props {
  timetableId: string
  timetable?: Timetable | null
}

interface Emits {
  (e: 'edit', timetable: Timetable): void
  (e: 'delete', timetable: Timetable): void
  (e: 'refresh'): void
}

const props = withDefaults(defineProps<Props>(), {})

const emit = defineEmits<Emits>()

// Store
const timetablesStore = useTimetablesStore()

// 响应式数据
const viewMode = ref<'grid' | 'list' | 'stats'>('grid')
const activeTab = ref('grid')
const loading = ref(false)
const assignmentsLoading = ref(false)
const assignmentFormVisible = ref(false)
const currentAssignment = ref<Assignment | null>(null)
const searchQuery = ref('')

// 历史记录（模拟数据）
const historyRecords = ref([
  {
    id: '1',
    type: 'created',
    title: '创建时间表',
    description: '时间表创建成功',
    user: '系统',
    timestamp: new Date().toISOString()
  }
])

// 计算属性
const currentTimetable = computed(() => props.timetable || timetablesStore.currentTimetable)

const timetableGrid = computed(() => timetablesStore.timetableGrid)

const timetableStats = computed(() => timetablesStore.timetableStats)

const timetableConflicts = computed(() => timetablesStore.timetableConflicts)

const assignments = computed(() => timetablesStore.assignments)

const filteredAssignments = computed(() => {
  if (!searchQuery.value) return assignments.value

  const query = searchQuery.value.toLowerCase()
  return assignments.value.filter(assignment =>
    assignment.section.name.toLowerCase().includes(query) ||
    assignment.section.teacher_id.toLowerCase().includes(query) ||
    assignment.room.name.toLowerCase().includes(query)
  )
})

const hasConflicts = computed(() => timetablesStore.hasConflicts)

const conflictCount = computed(() => timetablesStore.conflictCount)

const isPublished = computed(() => currentTimetable.value?.status === 'published')

const canEdit = computed(() => currentTimetable.value?.status !== 'published')

const canDelete = computed(() => currentTimetable.value?.status !== 'published')

// 方法
const getStatusType = (status?: string) => {
  const statusMap: Record<string, string> = {
    draft: '',
    running: 'warning',
    feasible: 'info',
    optimized: 'success',
    published: 'success',
    failed: 'danger'
  }
  return statusMap[status || 'draft'] || ''
}

const getStatusText = (status?: string) => {
  const statusMap: Record<string, string> = {
    draft: '草稿',
    running: '运行中',
    feasible: '可行',
    optimized: '已优化',
    published: '已发布',
    failed: '失败'
  }
  return statusMap[status || 'draft'] || '未知'
}

const getWeekDayText = (day?: WeekDay) => {
  const dayMap: Record<WeekDay, string> = {
    [WeekDay.MONDAY]: '周一',
    [WeekDay.TUESDAY]: '周二',
    [WeekDay.WEDNESDAY]: '周三',
    [WeekDay.THURSDAY]: '周四',
    [WeekDay.FRIDAY]: '周五',
    [WeekDay.SATURDAY]: '周六',
    [WeekDay.SUNDAY]: '周日'
  }
  return dayMap[day || WeekDay.MONDAY]
}

const getConflictType = (type: string) => {
  const typeMap: Record<string, string> = {
    teacher: 'warning',
    room: 'warning',
    class: 'warning',
    constraint: 'info'
  }
  return typeMap[type] || 'info'
}

const getConflictTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    teacher: '教师',
    room: '教室',
    class: '班级',
    constraint: '约束'
  }
  return typeMap[type] || '未知'
}

const getSeverityType = (severity: string) => {
  const severityMap: Record<string, string> = {
    error: 'danger',
    warning: 'warning',
    info: 'info'
  }
  return severityMap[severity] || 'info'
}

const getSeverityText = (severity: string) => {
  const severityMap: Record<string, string> = {
    error: '错误',
    warning: '警告',
    info: '信息'
  }
  return severityMap[severity] || '未知'
}

const getRecordType = (type: string) => {
  const typeMap: Record<string, string> = {
    created: 'primary',
    updated: 'warning',
    published: 'success',
    deleted: 'danger'
  }
  return typeMap[type] || 'info'
}

const getCompletionPercentage = () => {
  if (!timetableStats.value) return 0
  const { total_sections, assigned_sections } = timetableStats.value
  return total_sections > 0 ? Math.round((assigned_sections / total_sections) * 100) : 0
}

const loadTimetableData = async () => {
  if (!props.timetableId) return

  try {
    loading.value = true

    // 并行加载数据
    const [gridData, statsData, conflictsData, assignmentsData] = await Promise.all([
      timetablesStore.fetchTimetableGrid(props.timetableId),
      timetablesStore.fetchTimetableStats(props.timetableId),
      timetablesStore.fetchTimetableConflicts(props.timetableId),
      timetablesStore.fetchTimetableAssignments(props.timetableId)
    ])

    console.log('时间表数据加载完成:', { gridData, statsData, conflictsData, assignmentsData })
  } catch (error) {
    ElMessage.error('加载时间表数据失败')
  } finally {
    loading.value = false
  }
}

const handleAction = async (command: string) => {
  if (!currentTimetable.value) return

  switch (command) {
    case 'edit':
      emit('edit', currentTimetable.value)
      break
    case 'duplicate':
      handleDuplicate()
      break
    case 'publish':
      handlePublish()
      break
    case 'unpublish':
      handleUnpublish()
      break
    case 'optimize':
      handleOptimize()
      break
    case 'export':
      handleExport()
      break
    case 'print':
      handlePrint()
      break
    case 'delete':
      handleDelete()
      break
  }
}

const handleDuplicate = async () => {
  try {
    const { value } = await ElMessageBox.prompt('请输入新时间表名称', '复制时间表', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPlaceholder: '新时间表名称'
    })

    await timetablesStore.duplicateTimetable({
      source_timetable_id: currentTimetable.value!.id,
      new_name: value,
      copy_assignments: true,
      copy_constraints: true
    })

    ElMessage.success('时间表复制成功')
    emit('refresh')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('复制时间表失败')
    }
  }
}

const handlePublish = async () => {
  try {
    await ElMessageBox.confirm('确定要发布此时间表吗？发布后将不可编辑。', '确认发布', {
      type: 'warning'
    })

    await timetablesStore.publishTimetable(currentTimetable.value!.id)
    ElMessage.success('时间表发布成功')
    emit('refresh')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('发布时间表失败')
    }
  }
}

const handleUnpublish = async () => {
  try {
    await ElMessageBox.confirm('确定要取消发布此时间表吗？', '确认取消发布', {
      type: 'warning'
    })

    await timetablesStore.unpublishTimetable(currentTimetable.value!.id)
    ElMessage.success('时间表取消发布成功')
    emit('refresh')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消发布时间表失败')
    }
  }
}

const handleOptimize = async () => {
  try {
    await ElMessageBox.confirm('确定要优化此时间表吗？此操作可能需要一些时间。', '确认优化', {
      type: 'info'
    })

    loading.value = true
    // 这里应该调用优化API
    await new Promise(resolve => setTimeout(resolve, 2000)) // 模拟优化过程

    ElMessage.success('时间表优化完成')
    await loadTimetableData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('优化时间表失败')
    }
  } finally {
    loading.value = false
  }
}

const handleExport = () => {
  // 这里应该调用导出功能
  ElMessage.info('导出功能开发中')
}

const handlePrint = () => {
  // 这里应该调用打印功能
  ElMessage.info('打印功能开发中')
}

const handleDelete = async () => {
  try {
    await ElMessageBox.confirm('确定要删除此时间表吗？此操作不可恢复。', '确认删除', {
      type: 'error',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })

    emit('delete', currentTimetable.value!)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除时间表失败')
    }
  }
}

const handleAddAssignment = () => {
  currentAssignment.value = null
  assignmentFormVisible.value = true
}

const handleAssignmentEdit = (assignment: Assignment) => {
  currentAssignment.value = assignment
  assignmentFormVisible.value = true
}

const handleAssignmentDelete = async (assignment: Assignment) => {
  try {
    await ElMessageBox.confirm('确定要删除此课程安排吗？', '确认删除', {
      type: 'warning'
    })

    await timetablesStore.deleteAssignment(props.timetableId, assignment.id)
    ElMessage.success('课程安排删除成功')
    await loadTimetableData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除课程安排失败')
    }
  }
}

const handleAssignmentSuccess = () => {
  assignmentFormVisible.value = false
  currentAssignment.value = null
  loadTimetableData()
}

const handleCellClick = (day: WeekDay, timeslot: any) => {
  console.log('单元格点击:', day, timeslot)
}

const handleResolveConflict = async (conflict: TimetableConflict) => {
  try {
    await ElMessageBox.confirm('确定要解决此冲突吗？', '确认解决', {
      type: 'info'
    })

    // 这里应该调用解决冲突API
    ElMessage.success('冲突已解决')
    await loadTimetableData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('解决冲突失败')
    }
  }
}

const handleSearch = () => {
  // 搜索逻辑已通过计算属性实现
}

// 生命周期
onMounted(() => {
  loadTimetableData()
})
</script>

<style scoped>
.timetable-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px;
  border-bottom: 1px solid #ebeef5;
  background-color: #fafafa;
}

.header-info {
  flex: 1;
}

.timetable-name {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.timetable-description {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 14px;
}

.timetable-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.view-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.view-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: auto;
}

.view-tabs :deep(.el-tab-pane) {
  height: 100%;
  padding: 16px;
}

.assignments-section {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.section-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.stats-section {
  height: 100%;
  overflow: auto;
}

.stats-cards {
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 8px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.assigned {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
}

.stat-icon.teachers {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.stat-icon.utilization {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

.stat-info {
  flex: 1;
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

.conflicts-section {
  margin-bottom: 24px;
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.suggestions {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.suggestion-item {
  font-size: 12px;
  color: #606266;
  padding: 2px 0;
}

.detailed-stats {
  margin-bottom: 24px;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stats-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-item .label {
  font-size: 14px;
  color: #606266;
}

.stats-item .value {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.history-section {
  height: 100%;
  overflow: auto;
  padding: 16px 0;
}

.record-content {
  padding: 8px 0;
}

.record-title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.record-description {
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
}

.record-user {
  font-size: 12px;
  color: #909399;
}

.danger-item {
  color: #f56c6c;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>