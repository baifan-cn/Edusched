<template>
  <div class="teachers-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">教师管理</h1>
          <p class="page-description">管理系统中的教师信息，包括基本信息、工作设置和偏好配置</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增教师
          </el-button>
          <el-button @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          <el-button @click="handleExport">
            <el-icon><Download /></el-icon>
            导出
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
                <el-icon><User /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.total }}</div>
                <div class="stats-label">总教师数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon active">
                <el-icon><Check /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.active }}</div>
                <div class="stats-label">在职教师</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon departments">
                <el-icon><School /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.departments }}</div>
                <div class="stats-label">部门数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon workload">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.avgWorkload }}h</div>
                <div class="stats-label">平均周课时</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :model="filterForm" inline>
        <el-form-item label="学校">
          <el-select
            v-model="filterForm.school_id"
            placeholder="请选择学校"
            clearable
            style="width: 180px"
            filterable
          >
            <el-option
              v-for="school in schools"
              :key="school.id"
              :label="school.name"
              :value="school.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="姓名">
          <el-input
            v-model="filterForm.name"
            placeholder="请输入教师姓名"
            clearable
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="工号">
          <el-input
            v-model="filterForm.employee_id"
            placeholder="请输入工号"
            clearable
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="部门">
          <el-input
            v-model="filterForm.department"
            placeholder="请输入部门"
            clearable
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="filterForm.is_active"
            placeholder="请选择状态"
            clearable
            style="width: 100px"
          >
            <el-option label="在职" :value="true" />
            <el-option label="离职" :value="false" />
          </el-select>
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

    <!-- 教师列表 -->
    <el-card class="table-card">
      <CommonTable
        ref="tableRef"
        :data="teachers"
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
        <template #name="{ row }">
          <div class="teacher-name">
            <el-avatar :size="32" :src="row.avatar">
              {{ row.first_name?.charAt(0) }}{{ row.last_name?.charAt(0) }}
            </el-avatar>
            <div class="name-info">
              <div class="full-name">{{ row.first_name }} {{ row.last_name }}</div>
              <div class="employee-id">{{ row.employee_id }}</div>
            </div>
          </div>
        </template>

        <template #school="{ row }">
          <el-tag size="small">{{ getSchoolName(row.school_id) }}</el-tag>
        </template>

        <template #specialization="{ row }">
          <div class="specialization-tags">
            <el-tag
              v-for="spec in (row.specialization || []).slice(0, 2)"
              :key="spec"
              size="small"
              class="spec-tag"
            >
              {{ spec }}
            </el-tag>
            <el-tag
              v-if="(row.specialization || []).length > 2"
              size="small"
              type="info"
            >
              +{{ (row.specialization || []).length - 2 }}
            </el-tag>
          </div>
        </template>

        <template #workload="{ row }">
          <div class="workload-info">
            <div class="workload-progress">
              <el-progress
                :percentage="getWorkloadPercentage(row)"
                :color="getWorkloadColor(row)"
                :stroke-width="6"
                :show-text="false"
              />
            </div>
            <div class="workload-text">
              {{ row.assigned_hours || 0 }}/{{ row.max_hours_per_week || 20 }}h
            </div>
          </div>
        </template>

        <template #status="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '在职' : '离职' }}
          </el-tag>
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
            @click="handleSchedule(row)"
          >
            <el-icon><Calendar /></el-icon>
            课表
          </el-button>
          <el-button
            :type="row.is_active ? 'warning' : 'success'"
            link
            @click="handleToggleStatus(row)"
          >
            <el-icon><Switch /></el-icon>
            {{ row.is_active ? '离职' : '复职' }}
          </el-button>
        </template>
      </CommonTable>
    </el-card>

    <!-- 教师表单对话框 -->
    <TeacherForm
      v-model="formVisible"
      :teacher="currentTeacher"
      @success="handleFormSuccess"
      @cancel="handleFormCancel"
    />

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="教师详情"
      width="900px"
      @close="detailVisible = false"
    >
      <div v-if="currentTeacher" class="teacher-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="姓名">{{ currentTeacher.first_name }} {{ currentTeacher.last_name }}</el-descriptions-item>
          <el-descriptions-item label="工号">{{ currentTeacher.employee_id }}</el-descriptions-item>
          <el-descriptions-item label="所属学校">{{ getSchoolName(currentTeacher.school_id) }}</el-descriptions-item>
          <el-descriptions-item label="所属部门">{{ currentTeacher.department || '-' }}</el-descriptions-item>
          <el-descriptions-item label="职称">{{ currentTeacher.title || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentTeacher.is_active ? 'success' : 'danger'">
              {{ currentTeacher.is_active ? '在职' : '离职' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ currentTeacher.email }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ currentTeacher.phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="最大周课时">{{ currentTeacher.max_hours_per_week || 20 }}小时</el-descriptions-item>
          <el-descriptions-item label="已安排课时">{{ currentTeacher.assigned_hours || 0 }}小时</el-descriptions-item>
          <el-descriptions-item label="专业方向" :span="2">
            <div class="specialization-list">
              <el-tag
                v-for="spec in (currentTeacher.specialization || [])"
                :key="spec"
                size="small"
                class="spec-tag"
              >
                {{ spec }}
              </el-tag>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="偏好时间段" :span="2">
            {{ formatPreferredTime(currentTeacher.preferred_time_slots) }}
          </el-descriptions-item>
          <el-descriptions-item label="不可用时间" :span="2">
            {{ formatUnavailableTime(currentTeacher.unavailable_time_slots) }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(currentTeacher.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDateTime(currentTeacher.updated_at) }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog
      v-model="importVisible"
      title="导入教师数据"
      width="500px"
      @close="importVisible = false"
    >
      <div class="import-content">
        <el-alert
          title="导入说明"
          type="info"
          description="请下载模板文件，按照格式填写数据后上传。支持Excel格式（.xlsx, .xls）"
          show-icon
          :closable="false"
          class="import-alert"
        />

        <div class="upload-section">
          <el-upload
            ref="uploadRef"
            class="upload-demo"
            drag
            :auto-upload="false"
            :limit="1"
            accept=".xlsx,.xls"
            :on-change="handleFileChange"
            :on-exceed="handleExceed"
          >
            <el-icon class="el-icon--upload"><Upload /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                只能上传xlsx/xls文件，且不超过10MB
              </div>
            </template>
          </el-upload>
        </div>

        <div class="download-template">
          <el-button type="primary" @click="downloadTemplate">
            <el-icon><Download /></el-icon>
            下载模板
          </el-button>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="importVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="importing"
            @click="handleImport"
          >
            开始导入
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Refresh, Search, RefreshLeft, User, Check, School, Clock,
  View, Calendar, Switch, Download, Upload
} from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/date'
import { useSchoolsStore } from '@/stores/schools'
import { useTeachersStore } from '@/stores/teachers'
import type { Teacher } from '@/types'
import CommonTable from '@/components/Common/Table.vue'
import TeacherForm from '@/components/Forms/TeacherForm.vue'

// 状态管理
const schoolsStore = useSchoolsStore()
const teachersStore = useTeachersStore()

// 响应式数据
const tableRef = ref()
const formVisible = ref(false)
const detailVisible = ref(false)
const importVisible = ref(false)
const currentTeacher = ref<Teacher | null>(null)
const selectedTeachers = ref<Teacher[]>([])
const uploadRef = ref()
const uploadingFile = ref<File | null>(null)

// 筛选表单
const filterForm = reactive({
  school_id: '',
  name: '',
  employee_id: '',
  department: '',
  is_active: undefined as boolean | undefined
})

// 分页参数使用store中的状态

// 状态管理 - 使用store中的状态
const importing = ref(false)

// 计算属性
const schools = computed(() => schoolsStore.schoolOptions)

// 从store获取响应式数据
const teachers = computed(() => teachersStore.teachers)
const loading = computed(() => teachersStore.loading)
const total = computed(() => teachersStore.total)
const currentPage = computed({
  get: () => teachersStore.currentPage,
  set: (value) => teachersStore.currentPage = value
})
const pageSize = computed({
  get: () => teachersStore.pageSize,
  set: (value) => teachersStore.pageSize = value
})

// 统计数据
const stats = computed(() => ({
  total: teachers.value.length,
  active: teachersStore.activeTeachers.length,
  departments: Object.keys(teachersStore.teachersByDepartment).length,
  avgWorkload: Math.round(
    teachers.value.reduce((sum, t) => sum + (t.assigned_hours || 0), 0) / teachers.value.length || 0
  )
}))

// 表格列定义
const tableColumns = [
  { prop: 'name', label: '姓名', minWidth: 150 },
  { prop: 'school', label: '所属学校', width: 120 },
  { prop: 'department', label: '部门', width: 120 },
  { prop: 'title', label: '职称', width: 100 },
  { prop: 'specialization', label: '专业方向', minWidth: 180 },
  { prop: 'workload', label: '工作负载', width: 150 },
  { prop: 'email', label: '邮箱', minWidth: 180 },
  { prop: 'phone', label: '手机号', width: 120 },
  { prop: 'status', label: '状态', width: 80, align: 'center' },
  { prop: 'created_at', label: '创建时间', width: 160, type: 'datetime' },
  { prop: 'actions', label: '操作', width: 200, fixed: 'right' }
]

// 方法
const getSchoolName = (schoolId: string): string => {
  const school = schools.value.find(s => s.value === schoolId)
  return school?.label || '未知'
}

const getWorkloadPercentage = (teacher: Teacher): number => {
  const max = teacher.max_hours_per_week || 20
  const assigned = teacher.assigned_hours || 0
  return Math.round((assigned / max) * 100)
}

const getWorkloadColor = (teacher: Teacher): string => {
  const percentage = getWorkloadPercentage(teacher)
  if (percentage >= 90) return '#f56c6c'
  if (percentage >= 70) return '#e6a23c'
  return '#67c23a'
}

const formatPreferredTime = (slots: string[]): string => {
  if (!slots || slots.length < 2) return '未设置'
  return `${slots[0]} - ${slots[1]}`
}

const formatUnavailableTime = (slots: string[]): string => {
  if (!slots || slots.length === 0) return '无限制'

  const timeMap: Record<string, string> = {
    'monday-morning': '周一上午',
    'monday-afternoon': '周一下午',
    'tuesday-morning': '周二上午',
    'tuesday-afternoon': '周二下午',
    'wednesday-morning': '周三上午',
    'wednesday-afternoon': '周三下午',
    'thursday-morning': '周四上午',
    'thursday-afternoon': '周四下午',
    'friday-morning': '周五上午',
    'friday-afternoon': '周五下午'
  }

  return slots.map(slot => timeMap[slot] || slot).join(', ')
}

const loadSchools = async () => {
  try {
    await schoolsStore.fetchSchools()
  } catch (error) {
    ElMessage.error('加载学校列表失败')
  }
}

const loadTeachers = async () => {
  try {
    await teachersStore.fetchTeachers({
      school_id: filterForm.school_id || undefined,
      name: filterForm.name || undefined,
      department: filterForm.department || undefined,
      is_active: filterForm.is_active
    })
  } catch (error) {
    ElMessage.error('加载教师列表失败')
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadTeachers()
}

const handleReset = () => {
  Object.assign(filterForm, {
    school_id: '',
    name: '',
    employee_id: '',
    department: '',
    is_active: undefined
  })
  currentPage.value = 1
  loadTeachers()
}

const handleTableSearch = (query: string) => {
  filterForm.name = query
  currentPage.value = 1
  loadTeachers()
}

const handleRefresh = () => {
  loadTeachers()
}

const handleAdd = () => {
  currentTeacher.value = null
  formVisible.value = true
}

const handleEdit = (teacher: Teacher) => {
  currentTeacher.value = teacher
  formVisible.value = true
}

const handleView = (teacher: Teacher) => {
  currentTeacher.value = teacher
  detailVisible.value = true
}

const handleSchedule = (teacher: Teacher) => {
  ElMessage.info('课表功能开发中...')
}

const handleDelete = async (teacher: Teacher) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除教师"${teacher.first_name} ${teacher.last_name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await teachersStore.deleteTeacher(teacher.id)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBulkDelete = async (selectedTeachers: Teacher[]) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedTeachers.length} 名教师吗？此操作不可恢复。`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const ids = selectedTeachers.map(t => t.id)
    await teachersStore.bulkDeleteTeachers(ids)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleToggleStatus = async (teacher: Teacher) => {
  try {
    await teachersStore.toggleTeacherStatus(teacher.id, !teacher.is_active)
  } catch (error) {
    ElMessage.error('状态切换失败')
  }
}

const handleExport = async () => {
  try {
    await teachersStore.exportTeachers({
      school_id: filterForm.school_id || undefined,
      name: filterForm.name || undefined,
      department: filterForm.department || undefined,
      is_active: filterForm.is_active
    })
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const handleFileChange = (file: any) => {
  uploadingFile.value = file.raw
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

const handleImport = async () => {
  if (!uploadingFile.value) {
    ElMessage.warning('请先选择要导入的文件')
    return
  }

  if (!filterForm.school_id) {
    ElMessage.warning('请先选择要导入数据的学校')
    return
  }

  try {
    importing.value = true
    await teachersStore.importTeachers(filterForm.school_id, uploadingFile.value)

    importVisible.value = false
    uploadingFile.value = null
    uploadRef.value?.clearFiles()
  } catch (error) {
    ElMessage.error('导入失败')
  } finally {
    importing.value = false
  }
}

const downloadTemplate = () => {
  ElMessage.info('模板下载功能开发中...')
}

const handleSelectionChange = (selection: Teacher[]) => {
  selectedTeachers.value = selection
}

const handleFormSuccess = () => {
  formVisible.value = false
  loadTeachers()
}

const handleFormCancel = () => {
  formVisible.value = false
}

// 生命周期
onMounted(() => {
  loadSchools()
  loadTeachers()
})
</script>

<style scoped>
.teachers-page {
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

.stats-icon.active {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
}

.stats-icon.departments {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stats-icon.workload {
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

.teacher-name {
  display: flex;
  align-items: center;
  gap: 12px;
}

.name-info {
  display: flex;
  flex-direction: column;
}

.full-name {
  font-weight: 500;
  color: #303133;
}

.employee-id {
  font-size: 12px;
  color: #909399;
}

.specialization-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.spec-tag {
  margin-right: 0;
}

.workload-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.workload-progress {
  width: 100px;
}

.workload-text {
  font-size: 12px;
  color: #606266;
}

.teacher-detail {
  padding: 16px 0;
}

.specialization-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.import-content {
  padding: 16px 0;
}

.import-alert {
  margin-bottom: 20px;
}

.upload-section {
  margin-bottom: 20px;
}

.download-template {
  text-align: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-descriptions__label) {
  font-weight: 500;
}
</style>