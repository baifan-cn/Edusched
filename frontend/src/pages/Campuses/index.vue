<template>
  <div class="campuses-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">校区管理</h1>
          <p class="page-description">管理系统中的校区信息，包括校区位置、建筑分布、交通和配套设施</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增校区
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
                <el-icon><Location /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.total }}</div>
                <div class="stats-label">总校区数</div>
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
                <div class="stats-label">启用校区</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon buildings">
                <el-icon><School /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.totalBuildings }}</div>
                <div class="stats-label">建筑物数量</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon rooms">
                <el-icon><House /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.totalRooms }}</div>
                <div class="stats-label">教室总数</div>
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
        <el-form-item label="校区名称">
          <el-input
            v-model="filterForm.name"
            placeholder="请输入校区名称"
            clearable
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="校区代码">
          <el-input
            v-model="filterForm.code"
            placeholder="请输入校区代码"
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

    <!-- 校区列表 -->
    <el-card class="table-card">
      <CommonTable
        ref="tableRef"
        :data="campuses"
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

        <template #status="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>

        <template #buildings="{ row }">
          <div class="buildings-info">
            <el-tag size="small" type="info">{{ row.building_count || 0 }}栋</el-tag>
            <span class="area-text">{{ row.total_area || 0 }}㎡</span>
          </div>
        </template>

        <template #contact="{ row }">
          <div class="contact-info">
            <div class="contact-person">{{ row.contact_person || '-' }}</div>
            <div class="contact-phone">{{ row.contact_phone || '-' }}</div>
          </div>
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
            @click="handleBuildings(row)"
          >
            <el-icon><School /></el-icon>
            建筑
          </el-button>
          <el-button
            type="info"
            link
            @click="handleMap(row)"
          >
            <el-icon><MapLocation /></el-icon>
            地图
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

    <!-- 校区表单对话框 -->
    <CampusForm
      v-model="formVisible"
      :campus="currentCampus"
      @success="handleFormSuccess"
      @cancel="handleFormCancel"
    />

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="校区详情"
      width="900px"
      @close="detailVisible = false"
    >
      <div v-if="currentCampus" class="campus-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="校区名称">{{ currentCampus.name }}</el-descriptions-item>
          <el-descriptions-item label="校区代码">{{ currentCampus.code }}</el-descriptions-item>
          <el-descriptions-item label="所属学校">{{ getSchoolName(currentCampus.school_id) }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentCampus.is_active ? 'success' : 'danger'">
              {{ currentCampus.is_active ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="详细地址">{{ currentCampus.address || '-' }}</el-descriptions-item>
          <el-descriptions-item label="邮政编码">{{ currentCampus.postal_code || '-' }}</el-descriptions-item>
          <el-descriptions-item label="联系人">{{ currentCampus.contact_person || '-' }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ currentCampus.contact_phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="占地面积">{{ currentCampus.area || '-' }}亩</el-descriptions-item>
          <el-descriptions-item label="建筑面积">{{ currentCampus.total_area || '-' }}㎡</el-descriptions-item>
          <el-descriptions-item label="建筑物数量">{{ currentCampus.building_count || 0 }}栋</el-descriptions-item>
          <el-descriptions-item label="教室数量">{{ currentCampus.room_count || 0 }}间</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(currentCampus.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDateTime(currentCampus.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="交通信息" :span="2">{{ currentCampus.transportation || '-' }}</el-descriptions-item>
          <el-descriptions-item label="配套设施" :span="2">{{ currentCampus.facilities || '-' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ currentCampus.description || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 建筑管理对话框 -->
    <el-dialog
      v-model="buildingsVisible"
      title="建筑管理"
      width="1000px"
      @close="buildingsVisible = false"
    >
      <div v-if="currentCampus" class="buildings-content">
        <div class="campus-info">
          <h3>{{ currentCampus.name }} ({{ currentCampus.code }})</h3>
          <p>{{ getSchoolName(currentCampus.school_id) }} | {{ currentCampus.address }}</p>
        </div>

        <div class="buildings-actions">
          <el-button type="primary" @click="handleAddBuilding">
            <el-icon><Plus /></el-icon>
            新增建筑
          </el-button>
          <el-button @click="handleRefreshBuildings">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>

        <el-table :data="buildings" style="width: 100%">
          <el-table-column prop="name" label="建筑名称" min-width="150" />
          <el-table-column prop="code" label="建筑代码" width="120" />
          <el-table-column prop="floors" label="楼层" width="80" />
          <el-table-column prop="area" label="面积(㎡)" width="100" />
          <el-table-column prop="room_count" label="教室数" width="80" />
          <el-table-column prop="built_year" label="建成年份" width="100" />
          <el-table-column prop="is_active" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
                {{ row.is_active ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="handleEditBuilding(row)">
                编辑
              </el-button>
              <el-button type="success" link size="small" @click="handleViewBuilding(row)">
                查看
              </el-button>
              <el-button type="danger" link size="small" @click="handleDeleteBuilding(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="buildingsVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 地图对话框 -->
    <el-dialog
      v-model="mapVisible"
      title="校区地图"
      width="800px"
      @close="mapVisible = false"
    >
      <div v-if="currentCampus" class="map-content">
        <div class="map-info">
          <h3>{{ currentCampus.name }} - 位置信息</h3>
          <p>{{ currentCampus.address }}</p>
        </div>

        <div class="map-placeholder">
          <el-empty description="地图功能开发中..." />
        </div>

        <div class="location-details">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="经度">{{ currentCampus.longitude || '-' }}</el-descriptions-item>
            <el-descriptions-item label="纬度">{{ currentCampus.latitude || '-' }}</el-descriptions-item>
            <el-descriptions-item label="交通信息" :span="2">{{ currentCampus.transportation || '-' }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="mapVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Refresh, Search, RefreshLeft, Location, Check, School, House,
  View, Switch, Download, MapLocation
} from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/date'
import { useSchoolsStore } from '@/stores/schools'
import { useCampusesStore } from '@/stores/campuses'
import type { Campus } from '@/types'
import CommonTable from '@/components/Common/Table.vue'
import CampusForm from '@/components/Forms/CampusForm.vue'

// 状态管理
const schoolsStore = useSchoolsStore()
const campusesStore = useCampusesStore()

// 响应式数据
const tableRef = ref()
const formVisible = ref(false)
const detailVisible = ref(false)
const buildingsVisible = ref(false)
const mapVisible = ref(false)
const currentCampus = ref<Campus | null>(null)
const selectedCampuses = ref<Campus[]>([])
const buildings = ref([])

// 筛选表单
const filterForm = reactive({
  school_id: '',
  name: '',
  code: '',
  is_active: undefined as boolean | undefined
})

// 分页参数
const currentPage = ref(1)
const pageSize = ref(20)

// 计算属性
const schools = computed(() => schoolsStore.schoolOptions)
const campuses = computed(() => campusesStore.campuses)
const loading = computed(() => campusesStore.loading)
const total = computed(() => campusesStore.total)

// 统计数据
const stats = computed(() => ({
  total: campuses.value.length,
  active: campuses.value.filter(c => c.is_active).length,
  totalBuildings: campuses.value.reduce((sum, c) => sum + (c.building_count || 0), 0),
  totalRooms: campuses.value.reduce((sum, c) => sum + (c.room_count || 0), 0)
}))

// 表格列定义
const tableColumns = [
  { prop: 'name', label: '校区名称', minWidth: 150 },
  { prop: 'code', label: '校区代码', width: 120 },
  { prop: 'school', label: '所属学校', width: 120 },
  { prop: 'address', label: '地址', minWidth: 200 },
  { prop: 'contact', label: '联系人', width: 120 },
  { prop: 'buildings', label: '建筑信息', width: 150 },
  { prop: 'status', label: '状态', width: 80, align: 'center' },
  { prop: 'created_at', label: '创建时间', width: 160, type: 'datetime' },
  { prop: 'actions', label: '操作', width: 240, fixed: 'right' }
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

const loadCampuses = async () => {
  try {
    await campusesStore.fetchCampuses({
      school_id: filterForm.school_id || undefined,
      name: filterForm.name || undefined,
      code: filterForm.code || undefined,
      is_active: filterForm.is_active
    })
  } catch (error) {
    ElMessage.error('加载校区列表失败')
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadCampuses()
}

const handleReset = () => {
  Object.assign(filterForm, {
    school_id: '',
    name: '',
    code: '',
    is_active: undefined
  })
  currentPage.value = 1
  loadCampuses()
}

const handleTableSearch = (query: string) => {
  filterForm.name = query
  currentPage.value = 1
  loadCampuses()
}

const handleRefresh = () => {
  loadCampuses()
}

const handleAdd = () => {
  currentCampus.value = null
  formVisible.value = true
}

const handleEdit = (campus: Campus) => {
  currentCampus.value = campus
  formVisible.value = true
}

const handleView = (campus: Campus) => {
  currentCampus.value = campus
  detailVisible.value = true
}

const handleBuildings = async (campus: Campus) => {
  currentCampus.value = campus
  try {
    buildings.value = await campusesStore.fetchCampusBuildings(campus.id)
    buildingsVisible.value = true
  } catch (error) {
    ElMessage.error('加载建筑列表失败')
  }
}

const handleMap = (campus: Campus) => {
  currentCampus.value = campus
  mapVisible.value = true
}

const handleAddBuilding = () => {
  ElMessage.info('新增建筑功能开发中...')
}

const handleEditBuilding = (building: any) => {
  ElMessage.info('编辑建筑功能开发中...')
}

const handleViewBuilding = (building: any) => {
  ElMessage.info('查看建筑详情功能开发中...')
}

const handleDeleteBuilding = async (building: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除建筑"${building.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await campusesStore.deleteCampusBuilding(currentCampus.value!.id, building.id)
    ElMessage.success('删除成功')

    // 重新加载建筑列表
    buildings.value = await campusesStore.fetchCampusBuildings(currentCampus.value!.id)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleRefreshBuildings = async () => {
  try {
    buildings.value = await campusesStore.fetchCampusBuildings(currentCampus.value!.id)
  } catch (error) {
    ElMessage.error('刷新建筑列表失败')
  }
}

const handleDelete = async (campus: Campus) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除校区"${campus.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await campusesStore.deleteCampus(campus.id)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBulkDelete = async (campuses: Campus[]) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${campuses.length} 个校区吗？此操作不可恢复。`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const ids = campuses.map(c => c.id)
    await campusesStore.bulkDeleteCampuses(ids)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleToggleStatus = async (campus: Campus) => {
  try {
    await campusesStore.toggleCampusStatus(campus.id, !campus.is_active)
  } catch (error) {
    ElMessage.error('状态切换失败')
  }
}

const handleExport = async () => {
  try {
    await campusesStore.exportCampuses({
      school_id: filterForm.school_id || undefined,
      name: filterForm.name || undefined,
      code: filterForm.code || undefined,
      is_active: filterForm.is_active
    })
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const handleSelectionChange = (selection: Campus[]) => {
  selectedCampuses.value = selection
}

const handleFormSuccess = () => {
  formVisible.value = false
  loadCampuses()
}

const handleFormCancel = () => {
  formVisible.value = false
}

// 生命周期
onMounted(() => {
  loadSchools()
  loadCampuses()
})
</script>

<style scoped>
.campuses-page {
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

.stats-icon.buildings {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stats-icon.rooms {
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

.buildings-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.area-text {
  font-size: 12px;
  color: #909399;
}

.contact-info {
  display: flex;
  flex-direction: column;
}

.contact-person {
  font-weight: 500;
  color: #303133;
  font-size: 13px;
}

.contact-phone {
  font-size: 12px;
  color: #909399;
}

.campus-detail {
  padding: 16px 0;
}

.buildings-content {
  padding: 16px 0;
}

.campus-info {
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.campus-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.campus-info p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.buildings-actions {
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
}

.map-content {
  padding: 16px 0;
}

.map-info {
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.map-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.map-info p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.map-placeholder {
  margin: 20px 0;
  text-align: center;
  padding: 40px;
  background: #fafafa;
  border-radius: 8px;
}

.location-details {
  margin-top: 20px;
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