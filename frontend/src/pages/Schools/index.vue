<template>
  <div class="schools-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">学校管理</h1>
          <p class="page-description">管理系统中的学校信息，包括基本信息、联系方式和状态设置</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增学校
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
                <el-icon><School /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.total }}</div>
                <div class="stats-label">总学校数</div>
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
                <div class="stats-label">启用学校</div>
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
                <div class="stats-label">禁用学校</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon teachers">
                <el-icon><User /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.totalTeachers }}</div>
                <div class="stats-label">总教师数</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :model="filterForm" inline>
        <el-form-item label="学校名称">
          <el-input
            v-model="filterForm.name"
            placeholder="请输入学校名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="学校代码">
          <el-input
            v-model="filterForm.code"
            placeholder="请输入学校代码"
            clearable
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="filterForm.is_active"
            placeholder="请选择状态"
            clearable
            style="width: 120px"
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

    <!-- 学校列表 -->
    <el-card class="table-card">
      <CommonTable
        ref="tableRef"
        :data="schools"
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
        <template #logo_url="{ row }">
          <el-image
            v-if="row.logo_url"
            :src="row.logo_url"
            :preview-src-list="[row.logo_url]"
            style="width: 40px; height: 40px; border-radius: 4px"
            fit="cover"
          />
          <el-avatar v-else :size="40">
            <el-icon><School /></el-icon>
          </el-avatar>
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

    <!-- 学校表单对话框 -->
    <SchoolForm
      v-model="formVisible"
      :school="currentSchool"
      @success="handleFormSuccess"
      @cancel="handleFormCancel"
    />

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="学校详情"
      width="800px"
      @close="detailVisible = false"
    >
      <div v-if="currentSchool" class="school-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="学校名称">{{ currentSchool.name }}</el-descriptions-item>
          <el-descriptions-item label="学校代码">{{ currentSchool.code }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ currentSchool.phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="邮箱地址">{{ currentSchool.email || '-' }}</el-descriptions-item>
          <el-descriptions-item label="官方网站">
            <el-link
              v-if="currentSchool.website"
              :href="currentSchool.website"
              target="_blank"
            >
              {{ currentSchool.website }}
            </el-link>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentSchool.is_active ? 'success' : 'danger'">
              {{ currentSchool.is_active ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(currentSchool.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDateTime(currentSchool.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="学校地址" :span="2">{{ currentSchool.address || '-' }}</el-descriptions-item>
          <el-descriptions-item label="学校简介" :span="2">{{ currentSchool.description || '-' }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="currentSchool.logo_url" class="logo-section">
          <h4>学校Logo</h4>
          <el-image
            :src="currentSchool.logo_url"
            style="max-width: 200px; max-height: 200px; border-radius: 8px"
            fit="contain"
          />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Refresh, Search, RefreshLeft, School, Check, Close, User,
  View, Switch
} from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/date'
import { useSchoolsStore } from '@/stores/schools'
import CommonTable from '@/components/Common/Table.vue'
import SchoolForm from '@/components/Forms/SchoolForm.vue'

// 状态管理
const schoolsStore = useSchoolsStore()

// 响应式数据
const tableRef = ref()
const formVisible = ref(false)
const detailVisible = ref(false)
const currentSchool = ref<School | null>(null)
const selectedSchools = ref<School[]>([])

// 筛选表单
const filterForm = reactive({
  name: '',
  code: '',
  is_active: undefined as boolean | undefined
})

// 分页参数
const currentPage = ref(1)
const pageSize = ref(20)

// 统计数据
const stats = computed(() => ({
  total: schoolsStore.total,
  active: schoolsStore.schools.filter(s => s.is_active).length,
  inactive: schoolsStore.schools.filter(s => !s.is_active).length,
  totalTeachers: 0 // 这里可以从API获取
}))

// 表格列定义
const tableColumns = [
  { prop: 'logo_url', label: 'Logo', width: 80, align: 'center' },
  { prop: 'name', label: '学校名称', minWidth: 150 },
  { prop: 'code', label: '学校代码', width: 120 },
  { prop: 'phone', label: '联系电话', width: 120 },
  { prop: 'email', label: '邮箱地址', minWidth: 180 },
  { prop: 'status', label: '状态', width: 80, align: 'center' },
  { prop: 'created_at', label: '创建时间', width: 160, type: 'datetime' },
  { prop: 'actions', label: '操作', width: 200, fixed: 'right' }
]

// 计算属性
const loading = computed(() => schoolsStore.loading)
const schools = computed(() => schoolsStore.schools)
const total = computed(() => schoolsStore.total)

// 方法
const loadSchools = async () => {
  try {
    await schoolsStore.fetchSchools({
      ...filterForm,
      page: currentPage.value,
      size: pageSize.value
    })
  } catch (error) {
    ElMessage.error('加载学校列表失败')
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadSchools()
}

const handleReset = () => {
  Object.assign(filterForm, {
    name: '',
    code: '',
    is_active: undefined
  })
  currentPage.value = 1
  loadSchools()
}

const handleTableSearch = (query: string) => {
  filterForm.name = query
  currentPage.value = 1
  loadSchools()
}

const handleRefresh = () => {
  loadSchools()
}

const handleAdd = () => {
  currentSchool.value = null
  formVisible.value = true
}

const handleEdit = (school: School) => {
  currentSchool.value = school
  formVisible.value = true
}

const handleView = (school: School) => {
  currentSchool.value = school
  detailVisible.value = true
}

const handleDelete = async (school: School) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除学校"${school.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await schoolsStore.deleteSchool(school.id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBulkDelete = async (schools: School[]) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${schools.length} 个学校吗？此操作不可恢复。`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const ids = schools.map(s => s.id)
    await schoolsStore.bulkDeleteSchools(ids)
    ElMessage.success('批量删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleToggleStatus = async (school: School) => {
  try {
    await schoolsStore.toggleSchoolStatus(school.id, !school.is_active)
  } catch (error) {
    ElMessage.error('状态切换失败')
  }
}

const handleSelectionChange = (selection: School[]) => {
  selectedSchools.value = selection
}

const handleFormSuccess = () => {
  formVisible.value = false
  loadSchools()
}

const handleFormCancel = () => {
  formVisible.value = false
}

// 生命周期
onMounted(() => {
  loadSchools()
})
</script>

<style scoped>
.schools-page {
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

.stats-icon.teachers {
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

.school-detail {
  padding: 16px 0;
}

.logo-section {
  margin-top: 24px;
  text-align: center;
}

.logo-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

:deep(.el-descriptions__label) {
  font-weight: 500;
}
</style>