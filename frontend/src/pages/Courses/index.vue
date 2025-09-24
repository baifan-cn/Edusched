<template>
  <div class="courses-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">课程管理</h1>
          <p class="page-description">管理系统中的课程信息，包括基本信息、学时安排和状态设置</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增课程
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
                <el-icon><Reading /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.total }}</div>
                <div class="stats-label">总课程数</div>
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
                <div class="stats-label">启用课程</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon inactive">
                <el-icon><Close /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.inactive }}</div>
                <div class="stats-label">停用课程</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon credits">
                <el-icon><Trophy /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.totalCredits }}</div>
                <div class="stats-label">总学分</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :model="filterForm" inline>
        <el-form-item label="课程名称">
          <el-input
            v-model="filterForm.name"
            placeholder="请输入课程名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="课程代码">
          <el-input
            v-model="filterForm.code"
            placeholder="请输入课程代码"
            clearable
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item label="所属学科">
          <el-select
            v-model="filterForm.subject_id"
            placeholder="请选择学科"
            clearable
            style="width: 160px"
            filterable
          >
            <el-option
              v-for="subject in subjectOptions"
              :key="subject.value"
              :label="subject.label"
              :value="subject.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="filterForm.is_active"
            placeholder="请选择状态"
            clearable
            style="width: 120px"
          >
            <el-option label="启用" :value="true" />
            <el-option label="停用" :value="false" />
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

    <!-- 课程列表 -->
    <el-card class="table-card">
      <CommonTable
        ref="tableRef"
        :data="courses"
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
        <template #subject_id="{ row }">
          <el-tag type="info">{{ getSubjectName(row.subject_id) }}</el-tag>
        </template>

        <template #credits="{ row }">
          <span>{{ row.credits }} 学分</span>
        </template>

        <template #hours_per_week="{ row }">
          <span>{{ row.hours_per_week }} 小时/周</span>
        </template>

        <template #total_hours="{ row }">
          <span>{{ row.total_hours }} 小时</span>
        </template>

        <template #status="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '启用' : '停用' }}
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
            :type="row.is_active ? 'warning' : 'success'"
            link
            @click="handleToggleStatus(row)"
          >
            <el-icon><Switch /></el-icon>
            {{ row.is_active ? '停用' : '启用' }}
          </el-button>
        </template>
      </CommonTable>
    </el-card>

    <!-- 课程表单对话框 -->
    <CourseForm
      v-model="formVisible"
      :course="currentCourse"
      @success="handleFormSuccess"
      @cancel="handleFormCancel"
    />

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="课程详情"
      width="800px"
      @close="detailVisible = false"
    >
      <div v-if="currentCourse" class="course-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="课程名称">{{ currentCourse.name }}</el-descriptions-item>
          <el-descriptions-item label="课程代码">{{ currentCourse.code }}</el-descriptions-item>
          <el-descriptions-item label="所属学科">{{ getSubjectName(currentCourse.subject_id) }}</el-descriptions-item>
          <el-descriptions-item label="学分">{{ currentCourse.credits }} 学分</el-descriptions-item>
          <el-descriptions-item label="周学时">{{ currentCourse.hours_per_week }} 小时/周</el-descriptions-item>
          <el-descriptions-item label="总学时">{{ currentCourse.total_hours }} 小时</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentCourse.is_active ? 'success' : 'danger'">
              {{ currentCourse.is_active ? '启用' : '停用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(currentCourse.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDateTime(currentCourse.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="课程描述" :span="2">{{ currentCourse.description || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Refresh, Search, RefreshLeft, Reading, Check, Close, Trophy,
  View, Switch
} from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/date'
import { useCoursesStore } from '@/stores/courses'
import type { Course } from '@/types'
import CommonTable from '@/components/Common/Table.vue'
import CourseForm from '@/components/Forms/CourseForm.vue'

// 状态管理
const coursesStore = useCoursesStore()

// 响应式数据
const tableRef = ref()
const formVisible = ref(false)
const detailVisible = ref(false)
const currentCourse = ref<Course | null>(null)
const selectedCourses = ref<Course[]>([])

// 筛选表单
const filterForm = reactive({
  name: '',
  code: '',
  subject_id: '',
  is_active: undefined as boolean | undefined
})

// 分页参数
const currentPage = ref(1)
const pageSize = ref(20)

// 计算属性
const stats = computed(() => coursesStore.stats)
const loading = computed(() => coursesStore.loading)
const courses = computed(() => coursesStore.courses)
const total = computed(() => coursesStore.total)
const subjectOptions = computed(() => coursesStore.subjectOptions)

// 表格列定义
const tableColumns = [
  { prop: 'name', label: '课程名称', minWidth: 150 },
  { prop: 'code', label: '课程代码', width: 120 },
  { prop: 'subject_id', label: '所属学科', width: 120 },
  { prop: 'credits', label: '学分', width: 80, align: 'center' },
  { prop: 'hours_per_week', label: '周学时', width: 100, align: 'center' },
  { prop: 'total_hours', label: '总学时', width: 100, align: 'center' },
  { prop: 'status', label: '状态', width: 80, align: 'center' },
  { prop: 'created_at', label: '创建时间', width: 160, type: 'datetime' },
  { prop: 'actions', label: '操作', width: 200, fixed: 'right' }
]

// 方法
const getSubjectName = (subjectId: string) => {
  const subject = coursesStore.subjects.find(s => s.id === subjectId)
  return subject ? `${subject.name} (${subject.code})` : '未知学科'
}

const loadCourses = async () => {
  try {
    await coursesStore.fetchCourses({
      ...filterForm,
      page: currentPage.value,
      size: pageSize.value
    })
  } catch (error) {
    ElMessage.error('加载课程列表失败')
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadCourses()
}

const handleReset = () => {
  Object.assign(filterForm, {
    name: '',
    code: '',
    subject_id: '',
    is_active: undefined
  })
  currentPage.value = 1
  loadCourses()
}

const handleTableSearch = (query: string) => {
  filterForm.name = query
  currentPage.value = 1
  loadCourses()
}

const handleRefresh = () => {
  loadCourses()
}

const handleAdd = () => {
  currentCourse.value = null
  formVisible.value = true
}

const handleEdit = (course: Course) => {
  currentCourse.value = course
  formVisible.value = true
}

const handleView = (course: Course) => {
  currentCourse.value = course
  detailVisible.value = true
}

const handleDelete = async (course: Course) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除课程"${course.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await coursesStore.deleteCourse(course.id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBulkDelete = async (courses: Course[]) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${courses.length} 个课程吗？此操作不可恢复。`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const ids = courses.map(c => c.id)
    await coursesStore.bulkDeleteCourses(ids)
    ElMessage.success('批量删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleToggleStatus = async (course: Course) => {
  try {
    await coursesStore.toggleCourseStatus(course.id, !course.is_active)
  } catch (error) {
    ElMessage.error('状态切换失败')
  }
}

const handleSelectionChange = (selection: Course[]) => {
  selectedCourses.value = selection
}

const handleFormSuccess = () => {
  formVisible.value = false
  loadCourses()
}

const handleFormCancel = () => {
  formVisible.value = false
}

// 生命周期
onMounted(async () => {
  await coursesStore.init()
  loadCourses()
})
</script>

<style scoped>
.courses-page {
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

.stats-icon.inactive {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stats-icon.credits {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
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

.course-detail {
  padding: 16px 0;
}

:deep(.el-descriptions__label) {
  font-weight: 500;
}
</style>