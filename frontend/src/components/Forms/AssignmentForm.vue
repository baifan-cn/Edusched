<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑课程安排' : '新增课程安排'"
    width="500px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      label-position="left"
    >
      <!-- 基本信息 -->
      <el-form-item label="教学段" prop="section_id">
        <el-select
          v-model="form.section_id"
          placeholder="请选择教学段"
          style="width: 100%"
          filterable
          clearable
          @change="handleSectionChange"
        >
          <el-option
            v-for="section in sectionOptions"
            :key="section.value"
            :label="section.label"
            :value="section.value"
          >
            <div class="section-option">
              <span class="section-name">{{ section.label }}</span>
              <span class="section-info">{{ section.teacher }} - {{ section.course }}</span>
            </div>
          </el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="时间段" prop="timeslot_id">
        <el-select
          v-model="form.timeslot_id"
          placeholder="请选择时间段"
          style="width: 100%"
          filterable
          clearable
          :disabled="!!defaultTimeslot"
        >
          <el-option
            v-for="timeslot in timeslotOptions"
            :key="timeslot.value"
            :label="timeslot.label"
            :value="timeslot.value"
          >
            <div class="timeslot-option">
              <span class="timeslot-time">{{ timeslot.label }}</span>
              <span class="timeslot-day">{{ timeslot.day }}</span>
            </div>
          </el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="教室" prop="room_id">
        <el-select
          v-model="form.room_id"
          placeholder="请选择教室"
          style="width: 100%"
          filterable
          clearable
        >
          <el-option
            v-for="room in roomOptions"
            :key="room.value"
            :label="room.label"
            :value="room.value"
          >
            <div class="room-option">
              <span class="room-name">{{ room.label }}</span>
              <span class="room-info">{{ room.capacity }}人 | {{ room.type }}</span>
            </div>
          </el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="周模式" prop="week_pattern_id">
        <el-select
          v-model="form.week_pattern_id"
          placeholder="请选择周模式（可选）"
          style="width: 100%"
          clearable
        >
          <el-option
            v-for="pattern in weekPatternOptions"
            :key="pattern.value"
            :label="pattern.label"
            :value="pattern.value"
          />
        </el-select>
      </el-form-item>

      <!-- 高级选项 -->
      <div class="advanced-options">
        <el-collapse v-model="activeCollapse">
          <el-collapse-item title="高级选项" name="advanced">
            <el-form-item label="锁定状态">
              <el-switch
                v-model="form.is_locked"
                active-text="锁定"
                inactive-text="解锁"
              />
              <div class="option-hint">
                <el-icon><InfoFilled /></el-icon>
                <span>锁定后的安排不会被自动调整</span>
              </div>
            </el-form-item>

            <el-form-item label="备注">
              <el-input
                v-model="form.notes"
                type="textarea"
                :rows="2"
                placeholder="请输入备注信息"
                maxlength="200"
                show-word-limit
              />
            </el-form-item>
          </el-collapse-item>
        </el-collapse>
      </div>

      <!-- 冲突提示 -->
      <div v-if="conflicts.length" class="conflict-warning">
        <el-alert
          title="存在冲突"
          type="warning"
          :description="conflicts.join('；')"
          show-icon
          :closable="false"
        />
      </div>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import { useTimetablesStore } from '@/stores/timetables'
import { useSectionsStore } from '@/stores/sections'
import { useRoomsStore } from '@/stores/rooms'
import { useTimeslotsStore } from '@/stores/timeslots'
import type {
  Assignment,
  CreateAssignmentRequest,
  UpdateAssignmentRequest,
  Timeslot,
  Section
} from '@/types/timetables'

// Props
interface Props {
  modelValue: boolean
  assignment?: Assignment | null
  timetableId: string
  defaultTimeslot?: Timeslot | null
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success', assignment: Assignment): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  assignment: null,
  defaultTimeslot: null
})

const emit = defineEmits<Emits>()

// Store
const timetablesStore = useTimetablesStore()
const sectionsStore = useSectionsStore()
const roomsStore = useRoomsStore()
const timeslotsStore = useTimeslotsStore()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)
const activeCollapse = ref<string[]>([])
const conflicts = ref<string[]>([])

// 表单数据
const form = reactive({
  section_id: '',
  timeslot_id: '',
  room_id: '',
  week_pattern_id: '',
  is_locked: false,
  notes: ''
})

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isEdit = computed(() => !!props.assignment)

const currentAssignment = computed(() => props.assignment)

const sectionOptions = computed(() => {
  // 这里应该从sections store获取，暂时使用模拟数据
  return [
    {
      label: '数学-高一1班',
      value: 'section-1',
      teacher: '张老师',
      course: '数学'
    },
    {
      label: '语文-高一1班',
      value: 'section-2',
      teacher: '李老师',
      course: '语文'
    }
  ]
})

const timeslotOptions = computed(() => {
  // 这里应该从timeslots store获取，暂时使用模拟数据
  return [
    { label: '08:00-08:45', value: 'timeslot-1', day: '周一' },
    { label: '08:55-09:40', value: 'timeslot-2', day: '周一' },
    { label: '10:00-10:45', value: 'timeslot-3', day: '周一' },
    { label: '10:55-11:40', value: 'timeslot-4', day: '周一' },
    { label: '14:00-14:45', value: 'timeslot-5', day: '周一' },
    { label: '14:55-15:40', value: 'timeslot-6', day: '周一' },
    { label: '16:00-16:45', value: 'timeslot-7', day: '周一' },
    { label: '16:55-17:40', value: 'timeslot-8', day: '周一' }
  ]
})

const roomOptions = computed(() => {
  // 这里应该从rooms store获取，暂时使用模拟数据
  return [
    { label: '101教室', value: 'room-1', capacity: 50, type: '普通教室' },
    { label: '102教室', value: 'room-2', capacity: 45, type: '普通教室' },
    { label: '201实验室', value: 'room-3', capacity: 30, type: '实验室' },
    { label: '301多媒体教室', value: 'room-4', capacity: 60, type: '多媒体教室' }
  ]
})

const weekPatternOptions = computed(() => {
  // 这里应该从week patterns store获取，暂时使用模拟数据
  return [
    { label: '每周', value: 'pattern-1' },
    { label: '单周', value: 'pattern-2' },
    { label: '双周', value: 'pattern-3' },
    { label: '第1-4周', value: 'pattern-4' },
    { label: '第5-8周', value: 'pattern-5' }
  ]
})

// 表单验证规则
const rules: FormRules = {
  section_id: [
    { required: true, message: '请选择教学段', trigger: 'change' }
  ],
  timeslot_id: [
    { required: true, message: '请选择时间段', trigger: 'change' }
  ],
  room_id: [
    { required: true, message: '请选择教室', trigger: 'change' }
  ]
}

// 方法
const initForm = () => {
  if (props.assignment) {
    // 编辑模式
    form.section_id = props.assignment.section_id
    form.timeslot_id = props.assignment.timeslot_id
    form.room_id = props.assignment.room_id
    form.week_pattern_id = props.assignment.week_pattern_id || ''
    form.is_locked = props.assignment.is_locked
    form.notes = props.assignment.notes || ''
  } else {
    // 新增模式
    form.section_id = ''
    form.timeslot_id = props.defaultTimeslot?.id || ''
    form.room_id = ''
    form.week_pattern_id = ''
    form.is_locked = false
    form.notes = ''
  }
}

const handleSectionChange = (sectionId: string) => {
  // 根据教学段更新可用选项
  checkConflicts()
}

const checkConflicts = async () => {
  conflicts.value = []

  if (!form.section_id || !form.timeslot_id || !form.room_id) {
    return
  }

  try {
    // 这里应该调用API检查冲突
    // const result = await timetablesApi.checkAssignmentConflicts({
    //   timetable_id: props.timetableId,
    //   section_id: form.section_id,
    //   timeslot_id: form.timeslot_id,
    //   room_id: form.room_id,
    //   exclude_assignment_id: props.assignment?.id
    // })

    // 暂时使用模拟冲突检查
    if (form.section_id === 'section-1' && form.timeslot_id === 'timeslot-1') {
      conflicts.value.push('该教学段在此时间段已有安排')
    }
    if (form.room_id === 'room-1' && form.timeslot_id === 'timeslot-1') {
      conflicts.value.push('该教室在此时间段已被占用')
    }
  } catch (error) {
    console.error('检查冲突失败:', error)
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()

    if (conflicts.value.length > 0) {
      ElMessage.warning('存在冲突，请先解决')
      return
    }

    loading.value = true

    const data = {
      section_id: form.section_id,
      timeslot_id: form.timeslot_id,
      room_id: form.room_id,
      week_pattern_id: form.week_pattern_id || undefined,
      is_locked: form.is_locked,
      notes: form.notes || undefined
    }

    let result: Assignment
    if (isEdit.value) {
      result = await timetablesStore.updateAssignment(
        props.timetableId,
        props.assignment!.id,
        {
          ...data,
          id: props.assignment!.id
        }
      )
    } else {
      result = await timetablesStore.createAssignment(props.timetableId, data)
    }

    ElMessage.success(isEdit.value ? '课程安排更新成功' : '课程安排创建成功')
    emit('success', result)
    visible.value = false
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  visible.value = false
  emit('cancel')
}

// 监听
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    initForm()
    conflicts.value = []
  }
})

// 监听表单变化，检查冲突
watch([() => form.section_id, () => form.timeslot_id, () => form.room_id], () => {
  if (visible.value) {
    checkConflicts()
  }
})

// 初始化
initForm()
</script>

<style scoped>
.section-option,
.timeslot-option,
.room-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.section-name,
.timeslot-time,
.room-name {
  flex: 1;
  font-weight: 500;
}

.section-info,
.timeslot-day,
.room-info {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}

.advanced-options {
  margin-top: 16px;
}

.option-hint {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.conflict-warning {
  margin-top: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>