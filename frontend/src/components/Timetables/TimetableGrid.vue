<template>
  <div class="timetable-grid">
    <!-- 工具栏 -->
    <div class="grid-toolbar">
      <div class="toolbar-left">
        <el-button-group>
          <el-button
            :type="viewMode === 'week' ? 'primary' : 'default'"
            size="small"
            @click="viewMode = 'week'"
          >
            <el-icon><Calendar /></el-icon>
            周视图
          </el-button>
          <el-button
            :type="viewMode === 'day' ? 'primary' : 'default'"
            size="small"
            @click="viewMode = 'day'"
          >
            <el-icon><Calendar /></el-icon>
            日视图
          </el-button>
        </el-button-group>

        <el-select
          v-model="selectedWeek"
          placeholder="选择周"
          size="small"
          style="width: 120px; margin-left: 12px"
        >
          <el-option
            v-for="week in weekOptions"
            :key="week.value"
            :label="week.label"
            :value="week.value"
          />
        </el-select>
      </div>

      <div class="toolbar-right">
        <el-button size="small" @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button size="small" type="primary" @click="handleOptimize">
          <el-icon><MagicStick /></el-icon>
          优化
        </el-button>
        <el-button size="small" @click="handleExport">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
        <el-button size="small" @click="handlePrint">
          <el-icon><Printer /></el-icon>
          打印
        </el-button>
      </div>
    </div>

    <!-- 网格容器 -->
    <div class="grid-container" :class="{ 'loading': loading }">
      <!-- 时间轴 -->
      <div class="time-axis">
        <div class="corner-cell"></div>
        <div
          v-for="day in weekDays"
          :key="day.value"
          class="day-header"
          :class="{ 'today': isToday(day.value) }"
        >
          <div class="day-name">{{ day.label }}</div>
          <div class="day-date">{{ getDayDate(day.value) }}</div>
        </div>
      </div>

      <!-- 时间网格 -->
      <div class="time-grid" ref="gridRef">
        <!-- 时间标签 -->
        <div class="time-labels">
          <div
            v-for="timeslot in timeslots"
            :key="timeslot.id"
            class="time-label"
            :style="{ height: `${timeslotHeight}px` }"
          >
            <div class="time-text">{{ formatTime(timeslot.start_time) }}</div>
            <div class="period-text">第{{ timeslot.period_number }}节</div>
          </div>
        </div>

        <!-- 网格单元格 -->
        <div class="grid-cells" @mousedown="handleMouseDown" @mousemove="handleMouseMove" @mouseup="handleMouseUp">
          <div
            v-for="day in weekDays"
            :key="day.value"
            class="day-column"
            :data-day="day.value"
          >
            <div
              v-for="timeslot in timeslots"
              :key="`${day.value}-${timeslot.id}`"
              class="grid-cell"
              :class="getCellClass(day.value, timeslot)"
              :data-day="day.value"
              :data-timeslot="timeslot.id"
              :style="{ height: `${timeslotHeight}px` }"
              @click="handleCellClick(day.value, timeslot)"
              @contextmenu.prevent="handleCellRightClick(day.value, timeslot, $event)"
            >
              <!-- 单元格内容 -->
              <div v-if="getCellAssignment(day.value, timeslot)" class="cell-content">
                <div class="assignment-info">
                  <div class="course-name">{{ getCellAssignment(day.value, timeslot)?.section?.name }}</div>
                  <div class="teacher-name">{{ getCellAssignment(day.value, timeslot)?.section?.teacher_id }}</div>
                  <div class="room-name">{{ getCellAssignment(day.value, timeslot)?.room?.name }}</div>
                </div>
                <div class="assignment-actions">
                  <el-button
                    size="small"
                    link
                    @click.stop="handleEditAssignment(getCellAssignment(day.value, timeslot)!)"
                  >
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button
                    size="small"
                    link
                    type="danger"
                    @click.stop="handleDeleteAssignment(getCellAssignment(day.value, timeslot)!)"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>

              <!-- 冲突标记 -->
              <div v-if="hasConflict(day.value, timeslot)" class="conflict-marker">
                <el-tooltip content="存在冲突" placement="top">
                  <el-icon class="conflict-icon"><WarningFilled /></el-icon>
                </el-tooltip>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 拖拽选择框 -->
    <div
      v-if="selectionBox.visible"
      class="selection-box"
      :style="{
        left: `${selectionBox.x}px`,
        top: `${selectionBox.y}px`,
        width: `${selectionBox.width}px`,
        height: `${selectionBox.height}px`
      }"
    ></div>

    <!-- 统计信息 -->
    <div class="grid-stats">
      <div class="stat-item">
        <span class="stat-label">总课时:</span>
        <span class="stat-value">{{ stats.total_assignments }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">已安排:</span>
        <span class="stat-value">{{ stats.completed_assignments }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">利用率:</span>
        <span class="stat-value">{{ (stats.utilization_rate * 100).toFixed(1) }}%</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">冲突:</span>
        <span class="stat-value conflict">{{ stats.conflict_count }}</span>
      </div>
    </div>

    <!-- 右键菜单 -->
    <el-menu
      v-if="contextMenu.visible"
      class="context-menu"
      :style="{
        left: `${contextMenu.x}px`,
        top: `${contextMenu.y}px`
      }"
      @select="handleContextMenuSelect"
    >
      <el-menu-item index="add-assignment">
        <el-icon><Plus /></el-icon>
        添加安排
      </el-menu-item>
      <el-menu-item index="view-details">
        <el-icon><View /></el-icon>
        查看详情
      </el-menu-item>
      <el-menu-item index="edit-cell">
        <el-icon><Edit /></el-icon>
        编辑单元格
      </el-menu-item>
      <el-menu-item divided index="clear-cell">
        <el-icon><Delete /></el-icon>
        清空单元格
      </el-menu-item>
    </el-menu>

    <!-- 分配表单对话框 -->
    <AssignmentForm
      v-model="assignmentFormVisible"
      :assignment="currentAssignment"
      :timetable-id="timetableId"
      :default-timeslot="selectedTimeslot"
      @success="handleAssignmentSuccess"
      @cancel="assignmentFormVisible = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Calendar,
  Refresh,
  MagicStick,
  Download,
  Printer,
  Edit,
  Delete,
  WarningFilled,
  Plus,
  View
} from '@element-plus/icons-vue'
import { useTimetablesStore } from '@/stores/timetables'
import type {
  TimetableGridData,
  TimetableGridCell,
  Assignment,
  Timeslot,
  WeekDay
} from '@/types/timetables'

// Props
interface Props {
  timetableId: string
  gridData?: TimetableGridData
  loading?: boolean
}

interface Emits {
  (e: 'refresh'): void
  (e: 'optimize'): void
  (e: 'export'): void
  (e: 'print'): void
  (e: 'cell-click', day: WeekDay, timeslot: Timeslot): void
  (e: 'assignment-edit', assignment: Assignment): void
  (e: 'assignment-delete', assignment: Assignment): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const emit = defineEmits<Emits>()

// Store
const timetablesStore = useTimetablesStore()

// 响应式数据
const gridRef = ref<HTMLElement>()
const viewMode = ref<'week' | 'day'>('week')
const selectedWeek = ref(1)
const timeslotHeight = ref(60)
const assignmentFormVisible = ref(false)
const currentAssignment = ref<Assignment | null>(null)
const selectedTimeslot = ref<Timeslot | null>(null)

// 选择框
const selectionBox = reactive({
  visible: false,
  x: 0,
  y: 0,
  width: 0,
  height: 0,
  startCell: null as { day: WeekDay; timeslot: Timeslot } | null,
  endCell: null as { day: WeekDay; timeslot: Timeslot } | null
})

// 右键菜单
const contextMenu = reactive({
  visible: false,
  x: 0,
  y: 0,
  cell: null as { day: WeekDay; timeslot: Timeslot } | null
})

// 拖拽状态
const isDragging = ref(false)
const dragStartCell = ref<{ day: WeekDay; timeslot: Timeslot } | null>(null)

// 计算属性
const gridData = computed(() => props.gridData || timetablesStore.timetableGrid)

const weekDays = computed(() => [
  { value: WeekDay.MONDAY, label: '周一' },
  { value: WeekDay.TUESDAY, label: '周二' },
  { value: WeekDay.WEDNESDAY, label: '周三' },
  { value: WeekDay.THURSDAY, label: '周四' },
  { value: WeekDay.FRIDAY, label: '周五' },
  { value: WeekDay.SATURDAY, label: '周六' },
  { value: WeekDay.SUNDAY, label: '周日' }
])

const timeslots = computed(() => gridData.value?.timeslots || [])

const stats = computed(() => gridData.value?.statistics || {
  total_assignments: 0,
  completed_assignments: 0,
  conflict_count: 0,
  utilization_rate: 0
})

const weekOptions = computed(() => {
  const options = []
  for (let i = 1; i <= 20; i++) {
    options.push({ label: `第${i}周`, value: i })
  }
  return options
})

// 方法
const formatTime = (time: string) => {
  return time.slice(0, 5) // 只显示时:分
}

const getDayDate = (day: WeekDay) => {
  // 这里应该根据选中的周计算具体日期
  const dayMap: Record<WeekDay, number> = {
    [WeekDay.MONDAY]: 1,
    [WeekDay.TUESDAY]: 2,
    [WeekDay.WEDNESDAY]: 3,
    [WeekDay.THURSDAY]: 4,
    [WeekDay.FRIDAY]: 5,
    [WeekDay.SATURDAY]: 6,
    [WeekDay.SUNDAY]: 7
  }
  return `${dayMap[day]}日`
}

const isToday = (day: WeekDay) => {
  // 检查是否为今天
  const today = new Date().getDay()
  const dayMap: Record<WeekDay, number> = {
    [WeekDay.MONDAY]: 1,
    [WeekDay.TUESDAY]: 2,
    [WeekDay.WEDNESDAY]: 3,
    [WeekDay.THURSDAY]: 4,
    [WeekDay.FRIDAY]: 5,
    [WeekDay.SATURDAY]: 6,
    [WeekDay.SUNDAY]: 0
  }
  return dayMap[day] === today
}

const getCellAssignment = (day: WeekDay, timeslot: Timeslot) => {
  const cell = gridData.value?.cells.find(
    c => c.week_day === day && c.timeslot_id === timeslot.id
  )
  return cell?.assignment
}

const getCellClass = (day: WeekDay, timeslot: Timeslot) => {
  const cell = gridData.value?.cells.find(
    c => c.week_day === day && c.timeslot_id === timeslot.id
  )
  const classes = []

  if (cell?.assignment) {
    classes.push('has-assignment')
  }
  if (cell?.conflicts?.length) {
    classes.push('has-conflict')
  }
  if (cell?.is_highlighted) {
    classes.push('highlighted')
  }
  if (timeslot.is_break) {
    classes.push('break-time')
  }
  if (isToday(day)) {
    classes.push('today')
  }

  return classes
}

const hasConflict = (day: WeekDay, timeslot: Timeslot) => {
  const cell = gridData.value?.cells.find(
    c => c.week_day === day && c.timeslot_id === timeslot.id
  )
  return cell?.conflicts?.length > 0
}

const handleCellClick = (day: WeekDay, timeslot: Timeslot) => {
  emit('cell-click', day, timeslot)
}

const handleCellRightClick = (day: WeekDay, timeslot: Timeslot, event: MouseEvent) => {
  event.preventDefault()
  contextMenu.visible = true
  contextMenu.x = event.clientX
  contextMenu.y = event.clientY
  contextMenu.cell = { day, timeslot }
}

const handleContextMenuSelect = async (index: string) => {
  if (!contextMenu.cell) return

  const { day, timeslot } = contextMenu.cell

  switch (index) {
    case 'add-assignment':
      selectedTimeslot.value = timeslot
      currentAssignment.value = null
      assignmentFormVisible.value = true
      break
    case 'view-details':
      // 实现查看详情逻辑
      break
    case 'edit-cell':
      // 实现编辑单元格逻辑
      break
    case 'clear-cell':
      try {
        await ElMessageBox.confirm('确定要清空此单元格吗？', '确认', {
          type: 'warning'
        })
        const assignment = getCellAssignment(day, timeslot)
        if (assignment) {
          emit('assignment-delete', assignment)
        }
      } catch (error) {
        // 用户取消
      }
      break
  }

  contextMenu.visible = false
}

const handleEditAssignment = (assignment: Assignment) => {
  currentAssignment.value = assignment
  assignmentFormVisible.value = true
}

const handleDeleteAssignment = async (assignment: Assignment) => {
  try {
    await ElMessageBox.confirm('确定要删除此安排吗？', '确认删除', {
      type: 'warning'
    })
    emit('assignment-delete', assignment)
  } catch (error) {
    // 用户取消
  }
}

const handleAssignmentSuccess = () => {
  assignmentFormVisible.value = false
  currentAssignment.value = null
  selectedTimeslot.value = null
  emit('refresh')
}

const handleMouseDown = (event: MouseEvent) => {
  if (event.button !== 0) return // 只响应左键

  const target = event.target as HTMLElement
  const cell = target.closest('.grid-cell') as HTMLElement
  if (!cell) return

  const day = cell.dataset.day as WeekDay
  const timeslotId = cell.dataset.timeslot
  const timeslot = timeslots.value.find(t => t.id === timeslotId)

  if (!day || !timeslot) return

  isDragging.value = true
  dragStartCell.value = { day, timeslot }

  // 初始化选择框
  const rect = cell.getBoundingClientRect()
  const gridRect = gridRef.value?.getBoundingClientRect()
  if (!gridRect) return

  selectionBox.visible = true
  selectionBox.x = rect.left - gridRect.left
  selectionBox.y = rect.top - gridRect.top
  selectionBox.width = rect.width
  selectionBox.height = rect.height
  selectionBox.startCell = { day, timeslot }
  selectionBox.endCell = { day, timeslot }
}

const handleMouseMove = (event: MouseEvent) => {
  if (!isDragging.value || !dragStartCell.value) return

  const target = event.target as HTMLElement
  const cell = target.closest('.grid-cell') as HTMLElement
  if (!cell) return

  const day = cell.dataset.day as WeekDay
  const timeslotId = cell.dataset.timeslot
  const timeslot = timeslots.value.find(t => t.id === timeslotId)

  if (!day || !timeslot) return

  // 更新选择框
  const gridRect = gridRef.value?.getBoundingClientRect()
  if (!gridRect) return

  const startRect = document.querySelector(`.grid-cell[data-day="${dragStartCell.value.day}"][data-timeslot="${dragStartCell.value.timeslot.id}"]`)?.getBoundingClientRect()
  const endRect = cell.getBoundingClientRect()

  if (!startRect || !endRect) return

  selectionBox.x = Math.min(startRect.left, endRect.left) - gridRect.left
  selectionBox.y = Math.min(startRect.top, endRect.top) - gridRect.top
  selectionBox.width = Math.abs(endRect.left - startRect.left) + endRect.width
  selectionBox.height = Math.abs(endRect.top - startRect.top) + endRect.height
  selectionBox.endCell = { day, timeslot }
}

const handleMouseUp = () => {
  if (!isDragging.value) return

  isDragging.value = false
  selectionBox.visible = false

  // 处理选择结果
  if (selectionBox.startCell && selectionBox.endCell) {
    // 这里可以实现批量操作逻辑
    console.log('选择范围:', selectionBox.startCell, '到', selectionBox.endCell)
  }

  dragStartCell.value = null
  selectionBox.startCell = null
  selectionBox.endCell = null
}

const handleRefresh = () => {
  emit('refresh')
}

const handleOptimize = () => {
  emit('optimize')
}

const handleExport = () => {
  emit('export')
}

const handlePrint = () => {
  emit('print')
}

// 生命周期
onMounted(() => {
  // 添加全局事件监听
  document.addEventListener('mouseup', handleMouseUp)
  document.addEventListener('click', () => {
    contextMenu.visible = false
  })
})
</script>

<style scoped>
.timetable-grid {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.grid-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
  background-color: #fafafa;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.grid-container {
  flex: 1;
  overflow: auto;
  position: relative;
}

.grid-container.loading {
  opacity: 0.6;
  pointer-events: none;
}

.time-axis {
  display: flex;
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: #fff;
  border-bottom: 1px solid #ebeef5;
}

.corner-cell {
  width: 80px;
  min-width: 80px;
  height: 60px;
  border-right: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
}

.day-header {
  flex: 1;
  min-width: 120px;
  height: 60px;
  padding: 8px;
  text-align: center;
  border-right: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
  background-color: #fafafa;
}

.day-header.today {
  background-color: #e6f7ff;
}

.day-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.day-date {
  font-size: 12px;
  color: #909399;
}

.time-grid {
  display: flex;
  position: relative;
}

.time-labels {
  width: 80px;
  min-width: 80px;
  position: sticky;
  left: 0;
  z-index: 5;
  background-color: #fff;
  border-right: 1px solid #ebeef5;
}

.time-label {
  padding: 8px;
  border-bottom: 1px solid #ebeef5;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  font-size: 12px;
  color: #606266;
}

.time-text {
  font-weight: 500;
  margin-bottom: 2px;
}

.period-text {
  color: #909399;
}

.grid-cells {
  flex: 1;
  display: flex;
  position: relative;
}

.day-column {
  flex: 1;
  min-width: 120px;
  border-right: 1px solid #ebeef5;
}

.grid-cell {
  border-bottom: 1px solid #ebeef5;
  padding: 4px;
  cursor: pointer;
  position: relative;
  transition: background-color 0.2s;
}

.grid-cell:hover {
  background-color: #f5f7fa;
}

.grid-cell.has-assignment {
  background-color: #f0f9ff;
}

.grid-cell.has-conflict {
  background-color: #fef2f2;
}

.grid-cell.highlighted {
  background-color: #fff7ed;
}

.grid-cell.break-time {
  background-color: #f9fafb;
  color: #9ca3af;
}

.grid-cell.today {
  background-color: #eff6ff;
}

.cell-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.assignment-info {
  flex: 1;
  overflow: hidden;
}

.course-name {
  font-weight: 500;
  color: #303133;
  font-size: 12px;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.teacher-name,
.room-name {
  font-size: 11px;
  color: #606266;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.assignment-actions {
  display: flex;
  justify-content: flex-end;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.grid-cell:hover .assignment-actions {
  opacity: 1;
}

.conflict-marker {
  position: absolute;
  top: 2px;
  right: 2px;
}

.conflict-icon {
  color: #ef4444;
  font-size: 14px;
}

.selection-box {
  position: absolute;
  border: 2px solid #409eff;
  background-color: rgba(64, 158, 255, 0.1);
  pointer-events: none;
  z-index: 20;
}

.grid-stats {
  display: flex;
  justify-content: space-around;
  padding: 16px;
  border-top: 1px solid #ebeef5;
  background-color: #fafafa;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.stat-value {
  font-weight: 600;
  color: #303133;
}

.stat-value.conflict {
  color: #ef4444;
}

.context-menu {
  position: fixed;
  z-index: 1000;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
</style>