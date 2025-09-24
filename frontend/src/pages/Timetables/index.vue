<template>
  <div class="timetables-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">时间表管理</h1>
          <p class="page-description">管理系统中的时间表，包括创建、编辑、优化和发布时间表</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增时间表
          </el-button>
          <el-button @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          <el-dropdown @command="handleBulkAction" :disabled="!selectedTimetables.length">
            <el-button :disabled="!selectedTimetables.length">
              批量操作
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="publish">
                  <el-icon><Upload /></el-icon>
                  批量发布
                </el-dropdown-item>
                <el-dropdown-item command="unpublish">
                  <el-icon><Download /></el-icon>
                  批量取消发布
                </el-dropdown-item>
                <el-dropdown-item command="delete" divided class="danger-item">
                  <el-icon><Delete /></el-icon>
                  批量删除
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
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
                <el-icon><Calendar /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.total }}</div>
                <div class="stats-label">总时间表</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon published">
                <el-icon><Check /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.published }}</div>
                <div class="stats-label">已发布</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon draft">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.draft }}</div>
                <div class="stats-label">草稿</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon optimized">
                <el-icon><MagicStick /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.optimized }}</div>
                <div class="stats-label">已优化</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :model="filterForm" inline>
        <el-form-item label="时间表名称">
          <el-input
            v-model="filterForm.name"
            placeholder="请输入时间表名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="filterForm.status"
            placeholder="请选择状态"
            clearable
            style="width: 120px"
          >
            <el-option label="草稿" value="draft" />
            <el-option label="运行中" value="running" />
            <el-option label="可行" value="feasible" />
            <el-option label="已优化" value="optimized" />
            <el-option label="已发布" value="published" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属日历">
          <el-select
            v-model="filterForm.calendar_id"
            placeholder="请选择日历"
            clearable
            style="width: 160px"
          >
            <el-option
              v-for="calendar in calendarOptions"
              :key="calendar.value"
              :label="calendar.label"
              :value="calendar.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-date-picker
            v-model="filterForm.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 240px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 时间表列表 -->
    <el-card class="table-card">
      <CommonTable
        ref="tableRef"
        :data="timetables"
        :loading="loading"
        :columns="tableColumns"
        :total="total"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        @selection-change="handleSelectionChange"
        @search="handleTableSearch"
        @refresh="handleRefresh"
        @add="handleAdd"
        @edit="handleEdit"
        @delete="handleDelete"
        @bulk-delete="handleBulkDelete"
      >
        <template #status="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>

        <template #calendar_id="{ row }">
          <span>{{ getCalendarName(row.calendar_id) }}</span>
        </template>

        <template #assignments_count="{ row }">
          <el-badge :value="row.assignments_count" :max="99" class="assignment-badge">
            <el-icon><Calendar /></el-icon>
          </el-badge>
        </template>

        <template #created_at="{ row }">
          {{ formatDate(row.created_at) }}
        </template>

        <template #row-actions="{ row }">
          <el-button
            type="primary"
            link
            @click="handleView(row)"
          >
            <el-icon><View /></el-icon>
            查看
          </el-button>
          <el-button
            type="success"
            link
            v-if="row.status !== 'published'"
            @click="handlePublish(row)"
          >
            <el-icon><Upload /></el-icon>
            发布
          </el-button>
          <el-button
            type="warning"
            link
            v-if="row.status === 'published'"
            @click="handleUnpublish(row)"
          >
            <el-icon><Download /></el-icon>
            取消发布
          </el-button>
          <el-button
            link
            @click="handleDuplicate(row)"
          >
            <el-icon><CopyDocument /></el-icon>
            复制
          </el-button>
          <el-button
            link
            @click="handleOptimize(row)"
            v-if="row.status !== 'published'"
          >
            <el-icon><MagicStick /></el-icon>
            优化
          </el-button>
        </template>
      </CommonTable>
    </el-card>

    <!-- 时间表表单对话框 -->
    <TimetableForm
      v-model="formVisible"
      :timetable="currentTimetable"
      @success="handleFormSuccess"
      @cancel="handleFormCancel"
    />

    <!-- 时间表查看对话框 -->
    <el-dialog
      v-model="viewVisible"
      :title="currentTimetable?.name"
      width="90%"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <TimetableView
        v-if="currentTimetable"
        :timetable-id="currentTimetable.id"
        :timetable="currentTimetable"
        @edit="handleEditFromView"
        @delete="handleDeleteFromView"
        @refresh="handleRefresh"
      />
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog
      v-model="importVisible"
      title="导入时间表"
      width="500px"
      :close-on-click-modal="false"
    >
      <div class="import-content">
        <el-upload
          class="upload-area"
          drag
          :auto-upload="false"
          :limit="1"
          accept=".xlsx,.xls,.csv"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处或 <em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 .xlsx、.xls、.csv 格式文件
            </div>
          </template>
        </el-upload>

        <el-form-item label="所属日历" style="margin-top: 16px;">
          <el-select
            v-model="importForm.calendar_id"
            placeholder="请选择所属日历"
            style="width: 100%"
          >
            <el-option
              v-for="calendar in calendarOptions"
              :key="calendar.value"
              :label="calendar.label"
              :value="calendar.value"
            />
          </el-select>
        </el-form-item>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="importVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="importLoading"
            :disabled="!importFile || !importForm.calendar_id"
            @click="handleImport"
          >
            导入
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Refresh,
  ArrowDown,
  Search,
  RefreshLeft,
  Calendar,
  Check,
  Document,
  MagicStick,
  View,
  Upload,
  Download,
  CopyDocument,
  UploadFilled
} from '@element-plus/icons-vue'
import { useTimetablesStore } from '@/stores/timetables'
import { formatDate } from '@/utils/date'
import type { Timetable, TimetableStatus } from '@/types/timetables'
import CommonTable from '@/components/Common/Table.vue'
import TimetableForm from '@/components/Forms/TimetableForm.vue'
import TimetableView from '@/components/Timetables/TimetableView.vue'

// Store
const timetablesStore = useTimetablesStore()

// 响应式数据
const tableRef = ref()
const formVisible = ref(false)
const viewVisible = ref(false)
const importVisible = ref(false)
const importLoading = ref(false)
const currentTimetable = ref<Timetable | null>(null)
const selectedTimetables = ref<Timetable[]>([])
const importFile = ref<File | null>(null)

// 筛选表单
const filterForm = reactive({
  name: '',
  status: '',
  calendar_id: '',
  date_range: null as [Date, Date] | null
})

// 导入表单
const importForm = reactive({
  calendar_id: ''
})

// 分页参数
const currentPage = ref(1)
const pageSize = ref(20)

// 统计数据
const stats = computed(() => ({
  total: timetablesStore.total,
  published: timetablesStore.timetables.filter(t => t.status === 'published').length,
  draft: timetablesStore.timetables.filter(t => t.status === 'draft').length,
  optimized: timetablesStore.timetables.filter(t => t.status === 'optimized').length
}))

// 日历选项（模拟数据）
const calendarOptions = computed(() => [
  { label: '2024学年第一学期', value: 'calendar-1' },
  { label: '2024学年第二学期', value: 'calendar-2' }
])

// 表格列定义
const tableColumns = [
  { prop: 'name', label: '时间表名称', minWidth: 150 },
  { prop: 'calendar_id', label: '所属日历', width: 140 },
  { prop: 'status', label: '状态', width: 100, align: 'center' },
  { prop: 'assignments_count', label: '安排数', width: 100, align: 'center' },
  { prop: 'description', label: '描述', minWidth: 200, showOverflowTooltip: true },
  { prop: 'created_at', label: '创建时间', width: 160, type: 'datetime' },
  { prop: 'actions', label: '操作', width: 280, fixed: 'right' }
]

// 计算属性
const loading = computed(() => timetablesStore.loading)
const timetables = computed(() => timetablesStore.timetables)
const total = computed(() => timetablesStore.total)

// 方法
const getStatusType = (status: TimetableStatus) => {
  const statusMap: Record<TimetableStatus, string> = {
    draft: '',
    running: 'warning',
    feasible: 'info',
    optimized: 'success',
    published: 'success',
    failed: 'danger'
  }
  return statusMap[status]
}

const getStatusText = (status: TimetableStatus) => {
  const statusMap: Record<TimetableStatus, string> = {
    draft: '草稿',
    running: '运行中',
    feasible: '可行',
    optimized: '已优化',
    published: '已发布',
    failed: '失败'
  }
  return statusMap[status]
}

const getCalendarName = (calendarId: string) => {
  const calendar = calendarOptions.value.find(c => c.value === calendarId)
  return calendar?.label || calendarId
}

const loadTimetables = async () => {
  try {
    const params = {
      ...filterForm,
      page: currentPage.value,
      size: pageSize.value
    }

    // 处理日期范围
    if (filterForm.date_range) {
      params.start_date = filterForm.date_range[0].toISOString()
      params.end_date = filterForm.date_range[1].toISOString()
    }

    await timetablesStore.fetchTimetables(params)
  } catch (error) {
    ElMessage.error('加载时间表列表失败')
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadTimetables()
}

const handleReset = () => {
  Object.assign(filterForm, {
    name: '',
    status: '',
    calendar_id: '',
    date_range: null
  })
  currentPage.value = 1
  loadTimetables()
}

const handleTableSearch = (query: string) => {
  filterForm.name = query
  currentPage.value = 1
  loadTimetables()
}

const handleRefresh = () => {
  loadTimetables()
}

const handleAdd = () => {
  currentTimetable.value = null
  formVisible.value = true
}

const handleEdit = (timetable: Timetable) => {
  currentTimetable.value = timetable
  formVisible.value = true
}

const handleView = (timetable: Timetable) => {
  currentTimetable.value = timetable
  viewVisible.value = true
}

const handleDelete = async (timetable: Timetable) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除时间表"${timetable.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await timetablesStore.deleteTimetable(timetable.id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBulkDelete = async (timetables: Timetable[]) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${timetables.length} 个时间表吗？此操作不可恢复。`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const ids = timetables.map(t => t.id)
    await timetablesStore.bulkDeleteTimetables(ids)
    ElMessage.success('批量删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const handlePublish = async (timetable: Timetable) => {
  try {
    await ElMessageBox.confirm('确定要发布此时间表吗？发布后将不可编辑。', '确认发布', {
      type: 'warning'
    })

    await timetablesStore.publishTimetable(timetable.id)
    ElMessage.success('发布成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('发布失败')
    }
  }
}

const handleUnpublish = async (timetable: Timetable) => {
  try {
    await ElMessageBox.confirm('确定要取消发布此时间表吗？', '确认取消发布', {
      type: 'warning'
    })

    await timetablesStore.unpublishTimetable(timetable.id)
    ElMessage.success('取消发布成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消发布失败')
    }
  }
}

const handleDuplicate = async (timetable: Timetable) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入新时间表名称', '复制时间表', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPlaceholder: '新时间表名称'
    })

    await timetablesStore.duplicateTimetable({
      source_timetable_id: timetable.id,
      new_name: value,
      copy_assignments: true,
      copy_constraints: true
    })

    ElMessage.success('复制成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('复制失败')
    }
  }
}

const handleOptimize = async (timetable: Timetable) => {
  try {
    await ElMessageBox.confirm('确定要优化此时间表吗？此操作可能需要一些时间。', '确认优化', {
      type: 'info'
    })

    // 这里应该调用优化API
    ElMessage.info('优化功能开发中')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('优化失败')
    }
  }
}

const handleBulkAction = async (command: string) => {
  if (!selectedTimetables.value.length) return

  try {
    const ids = selectedTimetables.value.map(t => t.id)

    switch (command) {
      case 'publish':
        await ElMessageBox.confirm(
          `确定要发布选中的 ${selectedTimetables.value.length} 个时间表吗？`,
          '确认批量发布',
          { type: 'warning' }
        )
        await timetablesStore.bulkActionTimetables({
          action: 'publish',
          timetable_ids: ids
        })
        ElMessage.success('批量发布成功')
        break

      case 'unpublish':
        await ElMessageBox.confirm(
          `确定要取消发布选中的 ${selectedTimetables.value.length} 个时间表吗？`,
          '确认批量取消发布',
          { type: 'warning' }
        )
        await timetablesStore.bulkActionTimetables({
          action: 'unpublish',
          timetable_ids: ids
        })
        ElMessage.success('批量取消发布成功')
        break

      case 'delete':
        await handleBulkDelete(selectedTimetables.value)
        break
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量操作失败')
    }
  }
}

const handleSelectionChange = (selection: Timetable[]) => {
  selectedTimetables.value = selection
}

const handleFormSuccess = () => {
  formVisible.value = false
  loadTimetables()
}

const handleFormCancel = () => {
  formVisible.value = false
}

const handleEditFromView = (timetable: Timetable) => {
  viewVisible.value = false
  handleEdit(timetable)
}

const handleDeleteFromView = (timetable: Timetable) => {
  viewVisible.value = false
  handleDelete(timetable)
}

const handleFileChange = (file: any) => {
  importFile.value = file.raw
}

const handleFileRemove = () => {
  importFile.value = null
}

const handleImport = async () => {
  if (!importFile.value || !importForm.calendar_id) {
    ElMessage.warning('请选择文件和所属日历')
    return
  }

  try {
    importLoading.value = true
    await timetablesStore.importTimetable(importFile.value, importForm.calendar_id)

    ElMessage.success('导入成功')
    importVisible.value = false
    importFile.value = null
    importForm.calendar_id = ''

    loadTimetables()
  } catch (error) {
    ElMessage.error('导入失败')
  } finally {
    importLoading.value = false
  }
}

// 生命周期
onMounted(() => {
  loadTimetables()
})
</script>

<style scoped>
.timetables-page {
  padding: 16px;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.stats-icon.published {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
}

.stats-icon.draft {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stats-icon.optimized {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
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

.filter-card {
  margin-bottom: 16px;
}

.table-card {
  border-radius: 8px;
}

.assignment-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.import-content {
  padding: 16px 0;
}

.upload-area {
  text-align: center;
}

:deep(.el-upload-dragger) {
  width: 100%;
}

.danger-item {
  color: #f56c6c;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>