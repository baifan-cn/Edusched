<template>
  <div class="subjects-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">学科管理</h1>
          <p class="page-description">管理系统中的学科信息，包括学科名称、代码、类型和相关课程设置</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增学科
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
                <el-icon><Collection /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.total }}</div>
                <div class="stats-label">总学科数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon required">
                <el-icon><Star /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.required }}</div>
                <div class="stats-label">必修学科</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon elective">
                <el-icon><Check /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.elective }}</div>
                <div class="stats-label">选修学科</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon courses">
                <el-icon><Reading /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.totalCourses }}</div>
                <div class="stats-label">相关课程</div>
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
        <el-form-item label="学科名称">
          <el-input
            v-model="filterForm.name"
            placeholder="请输入学科名称"
            clearable
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="学科代码">
          <el-input
            v-model="filterForm.code"
            placeholder="请输入学科代码"
            clearable
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="学科类型">
          <el-select
            v-model="filterForm.type"
            placeholder="请选择类型"
            clearable
            style="width: 120px"
          >
            <el-option label="必修" value="required" />
            <el-option label="选修" value="elective" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="filterForm.is_active"
            placeholder="请选择状态"
            clearable
            style="width: 100px"
          >
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
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

    <!-- 学科列表 -->
    <el-card class="table-card">
      <CommonTable
        ref="tableRef"
        :data="subjects"
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
        <template #school="{ row }">
          <el-tag size="small">{{ getSchoolName(row.school_id) }}</el-tag>
        </template>

        <template #type="{ row }">
          <el-tag :type="row.type === 'required' ? 'primary' : 'success'" size="small">
            {{ row.type === 'required' ? '必修' : '选修' }}
          </el-tag>
        </template>

        <template #credits="{ row }">
          <div class="credits-info">
            <el-tag size="small" type="info">{{ row.credits }}学分</el-tag>
            <span class="hours-text">{{ row.hours }}课时</span>
          </div>
        </template>

        <template #status="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '启用' : '禁用' }}
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
            @click="handleCourses(row)"
          >
            <el-icon><Reading /></el-icon>
            课程
          </el-button>
          <el-button
            :type="row.is_active ? 'warning' : 'success'"
            link
            @click="handleToggleStatus(row)"
          >
            <el-icon><Switch /></el-icon>
            {{ row.is_active ? '禁用' : '启用' }}
          </el-button>
        </template>
      </CommonTable>
    </el-card>

    <!-- 学科表单对话框 -->
    <SubjectForm
      v-model="formVisible"
      :subject="currentSubject"
      @success="handleFormSuccess"
      @cancel="handleFormCancel"
    />

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="学科详情"
      width="800px"
      @close="detailVisible = false"
    >
      <div v-if="currentSubject" class="subject-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="学科名称">{{ currentSubject.name }}</el-descriptions-item>
          <el-descriptions-item label="学科代码">{{ currentSubject.code }}</el-descriptions-item>
          <el-descriptions-item label="所属学校">{{ getSchoolName(currentSubject.school_id) }}</el-descriptions-item>
          <el-descriptions-item label="学科类型">
            <el-tag :type="currentSubject.type === 'required' ? 'primary' : 'success'">
              {{ currentSubject.type === 'required' ? '必修' : '选修' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="学分">{{ currentSubject.credits }}学分</el-descriptions-item>
          <el-descriptions-item label="课时">{{ currentSubject.hours }}课时</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentSubject.is_active ? 'success' : 'danger'">
              {{ currentSubject.is_active ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(currentSubject.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDateTime(currentSubject.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="学科描述" :span="2">{{ currentSubject.description || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 课程关联对话框 -->
    <el-dialog
      v-model="coursesVisible"
      title="关联课程"
      width="900px"
      @close="coursesVisible = false"
    >
      <div v-if="currentSubject" class="courses-content">
        <div class="subject-info">
          <h3>{{ currentSubject.name }} ({{ currentSubject.code }})</h3>
          <p>{{ currentSubject.type === 'required' ? '必修' : '选修' }} | {{ currentSubject.credits }}学分 | {{ currentSubject.hours }}课时</p>
        </div>

        <div class="courses-actions">
          <el-button type="primary" @click="handleAddCourse">
            <el-icon><Plus /></el-icon>
            添加课程
          </el-button>
        </div>

        <el-table :data="relatedCourses" style="width: 100%">
          <el-table-column prop="name" label="课程名称" min-width="150" />
          <el-table-column prop="code" label="课程代码" width="120" />
          <el-table-column prop="credits" label="学分" width="80" />
          <el-table-column prop="hours" label="课时" width="80" />
          <el-table-column prop="level" label="年级" width="80" />
          <el-table-column prop="is_active" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
                {{ row.is_active ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="handleEditCourse(row)">
                编辑
              </el-button>
              <el-button type="danger" link size="small" @click="handleRemoveCourse(row)">
                移除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="coursesVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Refresh, Search, RefreshLeft, Collection, Star, Check, Reading,
  View, Switch, Download
} from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/date'
import { useSchoolsStore } from '@/stores/schools'
import { useSubjectsStore } from '@/stores/subjects'
import type { Subject } from '@/types'
import CommonTable from '@/components/Common/Table.vue'
import SubjectForm from '@/components/Forms/SubjectForm.vue'

// 状态管理
const schoolsStore = useSchoolsStore()
const subjectsStore = useSubjectsStore()

// 响应式数据
const tableRef = ref()
const formVisible = ref(false)
const detailVisible = ref(false)
const coursesVisible = ref(false)
const currentSubject = ref<Subject | null>(null)
const selectedSubjects = ref<Subject[]>([])
const relatedCourses = ref([])

// 筛选表单
const filterForm = reactive({
  school_id: '',
  name: '',
  code: '',
  type: '',
  is_active: undefined as boolean | undefined
})

// 分页参数
const currentPage = ref(1)
const pageSize = ref(20)

// 计算属性
const schools = computed(() => schoolsStore.schoolOptions)
const subjects = computed(() => subjectsStore.subjects)
const loading = computed(() => subjectsStore.loading)
const total = computed(() => subjectsStore.total)

// 统计数据
const stats = computed(() => ({
  total: subjects.value.length,
  required: subjects.value.filter(s => s.type === 'required').length,
  elective: subjects.value.filter(s => s.type === 'elective').length,
  totalCourses: subjects.value.reduce((sum, s) => sum + (s.course_count || 0), 0)
}))

// 表格列定义
const tableColumns = [
  { prop: 'name', label: '学科名称', minWidth: 150 },
  { prop: 'code', label: '学科代码', width: 120 },
  { prop: 'school', label: '所属学校', width: 120 },
  { prop: 'type', label: '学科类型', width: 80 },
  { prop: 'credits', label: '学分', width: 100 },
  { prop: 'hours', label: '课时', width: 80 },
  { prop: 'description', label: '描述', minWidth: 200 },
  { prop: 'status', label: '状态', width: 80, align: 'center' },
  { prop: 'created_at', label: '创建时间', width: 160, type: 'datetime' },
  { prop: 'actions', label: '操作', width: 200, fixed: 'right' }
]

// 方法
const getSchoolName = (schoolId: string): string => {
  const school = schools.value.find(s => s.value === schoolId)
  return school?.label || '未知'
}

const loadSchools = async () => {
  try {
    await schoolsStore.fetchSchools()
  } catch (error) {
    ElMessage.error('加载学校列表失败')
  }
}

const loadSubjects = async () => {
  try {
    await subjectsStore.fetchSubjects({
      school_id: filterForm.school_id || undefined,
      name: filterForm.name || undefined,
      code: filterForm.code || undefined,
      type: filterForm.type || undefined,
      is_active: filterForm.is_active
    })
  } catch (error) {
    ElMessage.error('加载学科列表失败')
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadSubjects()
}

const handleReset = () => {
  Object.assign(filterForm, {
    school_id: '',
    name: '',
    code: '',
    type: '',
    is_active: undefined
  })
  currentPage.value = 1
  loadSubjects()
}

const handleTableSearch = (query: string) => {
  filterForm.name = query
  currentPage.value = 1
  loadSubjects()
}

const handleRefresh = () => {
  loadSubjects()
}

const handleAdd = () => {
  currentSubject.value = null
  formVisible.value = true
}

const handleEdit = (subject: Subject) => {
  currentSubject.value = subject
  formVisible.value = true
}

const handleView = (subject: Subject) => {
  currentSubject.value = subject
  detailVisible.value = true
}

const handleCourses = async (subject: Subject) => {
  currentSubject.value = subject
  try {
    relatedCourses.value = await subjectsStore.fetchSubjectCourses(subject.id)
    coursesVisible.value = true
  } catch (error) {
    ElMessage.error('加载关联课程失败')
  }
}

const handleAddCourse = () => {
  ElMessage.info('添加课程功能开发中...')
}

const handleEditCourse = (course: any) => {
  ElMessage.info('编辑课程功能开发中...')
}

const handleRemoveCourse = async (course: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要移除课程"${course.name}"吗？`,
      '确认移除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await subjectsStore.removeSubjectCourse(currentSubject.value!.id, course.id)
    ElMessage.success('移除成功')

    // 重新加载课程列表
    relatedCourses.value = await subjectsStore.fetchSubjectCourses(currentSubject.value!.id)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('移除失败')
    }
  }
}

const handleDelete = async (subject: Subject) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除学科"${subject.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await subjectsStore.deleteSubject(subject.id)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBulkDelete = async (subjects: Subject[]) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${subjects.length} 个学科吗？此操作不可恢复。`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const ids = subjects.map(s => s.id)
    await subjectsStore.bulkDeleteSubjects(ids)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleToggleStatus = async (subject: Subject) => {
  try {
    await subjectsStore.toggleSubjectStatus(subject.id, !subject.is_active)
  } catch (error) {
    ElMessage.error('状态切换失败')
  }
}

const handleExport = async () => {
  try {
    await subjectsStore.exportSubjects({
      school_id: filterForm.school_id || undefined,
      name: filterForm.name || undefined,
      code: filterForm.code || undefined,
      type: filterForm.type || undefined,
      is_active: filterForm.is_active
    })
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const handleSelectionChange = (selection: Subject[]) => {
  selectedSubjects.value = selection
}

const handleFormSuccess = () => {
  formVisible.value = false
  loadSubjects()
}

const handleFormCancel = () => {
  formVisible.value = false
}

// 生命周期
onMounted(() => {
  loadSchools()
  loadSubjects()
})
</script>

<style scoped>
.subjects-page {
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

.stats-icon.required {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stats-icon.elective {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stats-icon.courses {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
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

.credits-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.hours-text {
  font-size: 12px;
  color: #909399;
}

.subject-detail {
  padding: 16px 0;
}

.courses-content {
  padding: 16px 0;
}

.subject-info {
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.subject-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.subject-info p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.courses-actions {
  margin-bottom: 16px;
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