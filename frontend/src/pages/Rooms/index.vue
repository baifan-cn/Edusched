<template>
  <div class="rooms-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">教室管理</h1>
          <p class="page-description">管理系统中的教室信息，包括教室位置、容量、设备配置和使用状态</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增教室
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
                <el-icon><School /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.total }}</div>
                <div class="stats-label">总教室数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon available">
                <el-icon><Check /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.available }}</div>
                <div class="stats-label">可用教室</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon occupied">
                <el-icon><Timer /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.occupied }}</div>
                <div class="stats-label">已占用</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-icon capacity">
                <el-icon><User /></el-icon>
              </div>
              <div class="stats-info">
                <div class="stats-value">{{ stats.avgCapacity }}</div>
                <div class="stats-label">平均容量</div>
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
        <el-form-item label="校区">
          <el-select
            v-model="filterForm.campus_id"
            placeholder="请选择校区"
            clearable
            style="width: 150px"
            filterable
          >
            <el-option
              v-for="campus in campuses"
              :key="campus.id"
              :label="campus.name"
              :value="campus.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="教室名称">
          <el-input
            v-model="filterForm.name"
            placeholder="请输入教室名称"
            clearable
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="教室类型">
          <el-select
            v-model="filterForm.room_type"
            placeholder="请选择类型"
            clearable
            style="width: 120px"
          >
            <el-option label="普通教室" value="classroom" />
            <el-option label="实验室" value="lab" />
            <el-option label="多媒体教室" value="multimedia" />
            <el-option label="会议室" value="meeting" />
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

    <!-- 教室列表 -->
    <el-card class="table-card">
      <CommonTable
        ref="tableRef"
        :data="rooms"
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

        <template #campus="{ row }">
          <el-tag size="small" type="info">{{ getCampusName(row.campus_id) }}</el-tag>
        </template>

        <template #room_type="{ row }">
          <el-tag :type="getRoomTypeTagType(row.room_type)" size="small">
            {{ getRoomTypeName(row.room_type) }}
          </el-tag>
        </template>

        <template #capacity="{ row }">
          <div class="capacity-info">
            <el-progress
              :percentage="getUtilizationPercentage(row)"
              :color="getUtilizationColor(row)"
              :stroke-width="6"
              :show-text="false"
              style="width: 60px"
            />
            <span class="capacity-text">{{ row.capacity }}人</span>
          </div>
        </template>

        <template #facilities="{ row }">
          <div class="facilities-tags">
            <el-tag
              v-for="facility in (row.facilities || []).slice(0, 2)"
              :key="facility"
              size="small"
              class="facility-tag"
            >
              {{ getFacilityName(facility) }}
            </el-tag>
            <el-tag
              v-if="(row.facilities || []).length > 2"
              size="small"
              type="info"
            >
              +{{ (row.facilities || []).length - 2 }}
            </el-tag>
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
            @click="handleSchedule(row)"
          >
            <el-icon><Calendar /></el-icon>
            排课
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

    <!-- 教室表单对话框 -->
    <RoomForm
      v-model="formVisible"
      :room="currentRoom"
      @success="handleFormSuccess"
      @cancel="handleFormCancel"
    />

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="教室详情"
      width="900px"
      @close="detailVisible = false"
    >
      <div v-if="currentRoom" class="room-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="教室名称">{{ currentRoom.name }}</el-descriptions-item>
          <el-descriptions-item label="教室编号">{{ currentRoom.code }}</el-descriptions-item>
          <el-descriptions-item label="所属学校">{{ getSchoolName(currentRoom.school_id) }}</el-descriptions-item>
          <el-descriptions-item label="所属校区">{{ getCampusName(currentRoom.campus_id) }}</el-descriptions-item>
          <el-descriptions-item label="教室位置">{{ currentRoom.location || '-' }}</el-descriptions-item>
          <el-descriptions-item label="教室类型">
            <el-tag :type="getRoomTypeTagType(currentRoom.room_type)" size="small">
              {{ getRoomTypeName(currentRoom.room_type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="容量">{{ currentRoom.capacity }}人</el-descriptions-item>
          <el-descriptions-item label="面积">{{ currentRoom.area || '-' }}㎡</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentRoom.is_active ? 'success' : 'danger'">
              {{ currentRoom.is_active ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(currentRoom.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDateTime(currentRoom.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="设备设施" :span="2">
            <div class="facilities-list">
              <el-tag
                v-for="facility in (currentRoom.facilities || [])"
                :key="facility"
                size="small"
                class="facility-tag"
              >
                {{ getFacilityName(facility) }}
              </el-tag>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ currentRoom.description || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 教室排课对话框 -->
    <el-dialog
      v-model="scheduleVisible"
      title="教室排课情况"
      width="1000px"
      @close="scheduleVisible = false"
    >
      <div v-if="currentRoom" class="schedule-content">
        <div class="room-info">
          <h3>{{ currentRoom.name }} ({{ currentRoom.code }})</h3>
          <p>{{ getCampusName(currentRoom.campus_id) }} | {{ currentRoom.location }} | {{ currentRoom.capacity }}人</p>
        </div>

        <div class="schedule-tabs">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="本周排课" name="week">
              <div class="week-schedule">
                <el-table :data="weekSchedule" style="width: 100%">
                  <el-table-column prop="day" label="星期" width="100" />
                  <el-table-column prop="time" label="时间" width="120" />
                  <el-table-column prop="course" label="课程" min-width="150" />
                  <el-table-column prop="teacher" label="教师" width="120" />
                  <el-table-column prop="class" label="班级" width="120" />
                  <el-table-column prop="duration" label="时长" width="80" />
                </el-table>
              </div>
            </el-tab-pane>
            <el-tab-pane label="利用率统计" name="utilization">
              <div class="utilization-stats">
                <el-row :gutter="16">
                  <el-col :span="8">
                    <el-card>
                      <div class="stat-item">
                        <div class="stat-value">{{ utilizationRate }}%</div>
                        <div class="stat-label">本周利用率</div>
                      </div>
                    </el-card>
                  </el-col>
                  <el-col :span="8">
                    <el-card>
                      <div class="stat-item">
                        <div class="stat-value">{{ totalHours }}</div>
                        <div class="stat-label">总课时</div>
                      </div>
                    </el-card>
                  </el-col>
                  <el-col :span="8">
                    <el-card>
                      <div class="stat-item">
                        <div class="stat-value">{{ availableHours }}</div>
                        <div class="stat-label">可用课时</div>
                      </div>
                    </el-card>
                  </el-col>
                </el-row>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="scheduleVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Refresh, Search, RefreshLeft, School, Check, Timer, User,
  View, Switch, Download, Calendar
} from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/date'
import { useSchoolsStore } from '@/stores/schools'
import { useCampusesStore } from '@/stores/campuses'
import { useRoomsStore } from '@/stores/rooms'
import type { Room } from '@/types'
import CommonTable from '@/components/Common/Table.vue'
import RoomForm from '@/components/Forms/RoomForm.vue'

// 状态管理
const schoolsStore = useSchoolsStore()
const campusesStore = useCampusesStore()
const roomsStore = useRoomsStore()

// 响应式数据
const tableRef = ref()
const formVisible = ref(false)
const detailVisible = ref(false)
const scheduleVisible = ref(false)
const currentRoom = ref<Room | null>(null)
const selectedRooms = ref<Room[]>([])
const activeTab = ref('week')
const weekSchedule = ref([])

// 筛选表单
const filterForm = reactive({
  school_id: '',
  campus_id: '',
  name: '',
  room_type: '',
  is_active: undefined as boolean | undefined
})

// 分页参数
const currentPage = ref(1)
const pageSize = ref(20)

// 计算属性
const schools = computed(() => schoolsStore.schoolOptions)
const campuses = computed(() => campusesStore.campusOptions)
const rooms = computed(() => roomsStore.rooms)
const loading = computed(() => roomsStore.loading)
const total = computed(() => roomsStore.total)

// 统计数据
const stats = computed(() => ({
  total: rooms.value.length,
  available: rooms.value.filter(r => r.is_active).length,
  occupied: rooms.value.filter(r => r.is_occupied).length,
  avgCapacity: Math.round(rooms.value.reduce((sum, r) => sum + r.capacity, 0) / rooms.value.length || 0)
}))

// 利用率数据
const utilizationRate = ref(0)
const totalHours = ref(0)
const availableHours = ref(0)

// 表格列定义
const tableColumns = [
  { prop: 'name', label: '教室名称', minWidth: 120 },
  { prop: 'code', label: '教室编号', width: 120 },
  { prop: 'school', label: '所属学校', width: 120 },
  { prop: 'campus', label: '所属校区', width: 120 },
  { prop: 'location', label: '位置', width: 150 },
  { prop: 'room_type', label: '教室类型', width: 100 },
  { prop: 'capacity', label: '容量', width: 100 },
  { prop: 'facilities', label: '设备设施', minWidth: 150 },
  { prop: 'status', label: '状态', width: 80, align: 'center' },
  { prop: 'created_at', label: '创建时间', width: 160, type: 'datetime' },
  { prop: 'actions', label: '操作', width: 200, fixed: 'right' }
]

// 方法
const getSchoolName = (schoolId: string): string => {
  const school = schools.value.find(s => s.value === schoolId)
  return school?.label || '未知'
}

const getCampusName = (campusId: string): string => {
  const campus = campuses.value.find(c => c.value === campusId)
  return campus?.label || '未知'
}

const getRoomTypeName = (type: string): string => {
  const typeMap: Record<string, string> = {
    'classroom': '普通教室',
    'lab': '实验室',
    'multimedia': '多媒体教室',
    'meeting': '会议室'
  }
  return typeMap[type] || type
}

const getRoomTypeTagType = (type: string): string => {
  const typeMap: Record<string, string> = {
    'classroom': 'primary',
    'lab': 'warning',
    'multimedia': 'success',
    'meeting': 'info'
  }
  return typeMap[type] || 'info'
}

const getFacilityName = (facility: string): string => {
  const facilityMap: Record<string, string> = {
    'projector': '投影仪',
    'computer': '电脑',
    'whiteboard': '白板',
    'air_conditioner': '空调',
    'wifi': 'WiFi',
    'speaker': '音响',
    'microphone': '麦克风',
    'camera': '摄像头'
  }
  return facilityMap[facility] || facility
}

const getUtilizationPercentage = (room: Room): number => {
  // 假设的利用率计算，实际应该从API获取
  return Math.min(100, Math.round((room.occupied_hours || 0) / 40 * 100))
}

const getUtilizationColor = (room: Room): string => {
  const percentage = getUtilizationPercentage(room)
  if (percentage >= 90) return '#f56c6c'
  if (percentage >= 70) return '#e6a23c'
  return '#67c23a'
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
    await campusesStore.fetchCampuses()
  } catch (error) {
    ElMessage.error('加载校区列表失败')
  }
}

const loadRooms = async () => {
  try {
    await roomsStore.fetchRooms({
      school_id: filterForm.school_id || undefined,
      campus_id: filterForm.campus_id || undefined,
      name: filterForm.name || undefined,
      room_type: filterForm.room_type || undefined,
      is_active: filterForm.is_active
    })
  } catch (error) {
    ElMessage.error('加载教室列表失败')
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadRooms()
}

const handleReset = () => {
  Object.assign(filterForm, {
    school_id: '',
    campus_id: '',
    name: '',
    room_type: '',
    is_active: undefined
  })
  currentPage.value = 1
  loadRooms()
}

const handleTableSearch = (query: string) => {
  filterForm.name = query
  currentPage.value = 1
  loadRooms()
}

const handleRefresh = () => {
  loadRooms()
}

const handleAdd = () => {
  currentRoom.value = null
  formVisible.value = true
}

const handleEdit = (room: Room) => {
  currentRoom.value = room
  formVisible.value = true
}

const handleView = (room: Room) => {
  currentRoom.value = room
  detailVisible.value = true
}

const handleSchedule = async (room: Room) => {
  currentRoom.value = room
  try {
    weekSchedule.value = await roomsStore.fetchRoomSchedule(room.id)
    utilizationRate.value = roomsStore.getRoomUtilization(room.id)
    totalHours.value = 40 // 假设每周40个课时
    availableHours.value = Math.round(totalHours.value * (100 - utilizationRate.value) / 100)
    scheduleVisible.value = true
  } catch (error) {
    ElMessage.error('加载排课情况失败')
  }
}

const handleDelete = async (room: Room) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除教室"${room.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await roomsStore.deleteRoom(room.id)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBulkDelete = async (rooms: Room[]) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${rooms.length} 个教室吗？此操作不可恢复。`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const ids = rooms.map(r => r.id)
    await roomsStore.bulkDeleteRooms(ids)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleToggleStatus = async (room: Room) => {
  try {
    await roomsStore.toggleRoomStatus(room.id, !room.is_active)
  } catch (error) {
    ElMessage.error('状态切换失败')
  }
}

const handleExport = async () => {
  try {
    await roomsStore.exportRooms({
      school_id: filterForm.school_id || undefined,
      campus_id: filterForm.campus_id || undefined,
      name: filterForm.name || undefined,
      room_type: filterForm.room_type || undefined,
      is_active: filterForm.is_active
    })
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const handleSelectionChange = (selection: Room[]) => {
  selectedRooms.value = selection
}

const handleFormSuccess = () => {
  formVisible.value = false
  loadRooms()
}

const handleFormCancel = () => {
  formVisible.value = false
}

// 生命周期
onMounted(() => {
  loadSchools()
  loadCampuses()
  loadRooms()
})
</script>

<style scoped>
.rooms-page {
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

.stats-icon.available {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
}

.stats-icon.occupied {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stats-icon.capacity {
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

.capacity-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.capacity-text {
  font-size: 12px;
  color: #606266;
}

.facilities-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.facility-tag {
  margin-right: 0;
}

.room-detail {
  padding: 16px 0;
}

.facilities-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.schedule-content {
  padding: 16px 0;
}

.room-info {
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.room-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.room-info p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.schedule-tabs {
  margin-top: 20px;
}

.week-schedule {
  margin-top: 16px;
}

.utilization-stats {
  margin-top: 16px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
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