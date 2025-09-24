<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑时间表' : '新增时间表'"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      label-position="left"
    >
      <!-- 基本信息 -->
      <div class="form-section">
        <h4 class="section-title">基本信息</h4>

        <el-form-item label="时间表名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="请输入时间表名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="所属日历" prop="calendar_id">
          <el-select
            v-model="form.calendar_id"
            placeholder="请选择所属日历"
            style="width: 100%"
            filterable
            clearable
          >
            <el-option
              v-for="calendar in calendarOptions"
              :key="calendar.value"
              :label="calendar.label"
              :value="calendar.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入时间表描述"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </div>

      <!-- 高级设置 -->
      <div class="form-section">
        <h4 class="section-title">
          高级设置
          <el-tooltip content="高级配置选项，通常不需要修改" placement="top">
            <el-icon class="help-icon"><QuestionFilled /></el-icon>
          </el-tooltip>
        </h4>

        <el-form-item label="约束配置" prop="constraints">
          <el-select
            v-model="form.constraints"
            placeholder="选择约束条件"
            style="width: 100%"
            multiple
            filterable
            clearable
          >
            <el-option
              v-for="constraint in constraintOptions"
              :key="constraint.value"
              :label="constraint.label"
              :value="constraint.value"
            >
              <div class="constraint-option">
                <span class="constraint-name">{{ constraint.label }}</span>
                <span class="constraint-type">{{ constraint.type }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="优化参数" prop="optimization_params">
          <div class="optimization-params">
            <div class="param-item">
              <label>最大迭代次数:</label>
              <el-input-number
                v-model="form.optimization_params.max_iterations"
                :min="100"
                :max="10000"
                :step="100"
                size="small"
              />
            </div>
            <div class="param-item">
              <label>时间限制(秒):</label>
              <el-input-number
                v-model="form.optimization_params.time_limit"
                :min="10"
                :max="3600"
                :step="10"
                size="small"
              />
            </div>
            <div class="param-item">
              <label>收敛阈值:</label>
              <el-input-number
                v-model="form.optimization_params.convergence_threshold"
                :min="0.001"
                :max="0.1"
                :step="0.001"
                :precision="3"
                size="small"
              />
            </div>
          </div>
        </el-form-item>

        <el-form-item label="元数据" prop="metadata">
          <el-input
            v-model="metadataJson"
            type="textarea"
            :rows="3"
            placeholder="请输入JSON格式的元数据"
            @blur="handleMetadataBlur"
          />
          <div class="metadata-hint">
            <el-icon><InfoFilled /></el-icon>
            <span>请输入有效的JSON格式数据</span>
          </div>
        </el-form-item>
      </div>

      <!-- 预览信息 -->
      <div v-if="isEdit" class="form-section">
        <h4 class="section-title">预览信息</h4>
        <div class="preview-info">
          <div class="preview-item">
            <span class="label">创建时间:</span>
            <span class="value">{{ formatDate(currentTimetable?.created_at) }}</span>
          </div>
          <div class="preview-item">
            <span class="label">更新时间:</span>
            <span class="value">{{ formatDate(currentTimetable?.updated_at) }}</span>
          </div>
          <div class="preview-item">
            <span class="label">状态:</span>
            <el-tag :type="getStatusType(currentTimetable?.status)">
              {{ getStatusText(currentTimetable?.status) }}
            </el-tag>
          </div>
          <div class="preview-item">
            <span class="label">分配数量:</span>
            <span class="value">{{ currentTimetable?.assignments_count || 0 }}</span>
          </div>
        </div>
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
import { QuestionFilled, InfoFilled } from '@element-plus/icons-vue'
import { useTimetablesStore } from '@/stores/timetables'
import { useCalendarsStore } from '@/stores/calendars'
import { useConstraintsStore } from '@/stores/constraints'
import type {
  Timetable,
  CreateTimetableRequest,
  UpdateTimetableRequest
} from '@/types/timetables'
import { formatDate } from '@/utils/date'

// Props
interface Props {
  modelValue: boolean
  timetable?: Timetable | null
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success', timetable: Timetable): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  timetable: null
})

const emit = defineEmits<Emits>()

// Store
const timetablesStore = useTimetablesStore()
const calendarsStore = useCalendarsStore()
const constraintsStore = useConstraintsStore()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)
const metadataJson = ref('')

// 表单数据
const form = reactive({
  name: '',
  calendar_id: '',
  description: '',
  constraints: [] as string[],
  optimization_params: {
    max_iterations: 1000,
    time_limit: 300,
    convergence_threshold: 0.01
  },
  metadata: {} as Record<string, any>
})

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isEdit = computed(() => !!props.timetable)

const currentTimetable = computed(() => props.timetable)

const calendarOptions = computed(() => {
  // 这里应该从日历store获取，暂时使用模拟数据
  return [
    { label: '2024学年第一学期', value: 'calendar-1' },
    { label: '2024学年第二学期', value: 'calendar-2' }
  ]
})

const constraintOptions = computed(() => {
  // 这里应该从约束store获取，暂时使用模拟数据
  return [
    { label: '教师时间冲突约束', value: 'constraint-1', type: '硬约束' },
    { label: '教室容量约束', value: 'constraint-2', type: '硬约束' },
    { label: '教师偏好约束', value: 'constraint-3', type: '软约束' },
    { label: '课程分布约束', value: 'constraint-4', type: '软约束' }
  ]
})

// 表单验证规则
const rules: FormRules = {
  name: [
    { required: true, message: '请输入时间表名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  calendar_id: [
    { required: true, message: '请选择所属日历', trigger: 'change' }
  ],
  description: [
    { max: 500, message: '描述不能超过 500 个字符', trigger: 'blur' }
  ]
}

// 方法
const initForm = () => {
  if (props.timetable) {
    // 编辑模式
    form.name = props.timetable.name
    form.calendar_id = props.timetable.calendar_id
    form.description = props.timetable.description || ''
    form.constraints = props.timetable.constraints || []
    form.optimization_params = {
      max_iterations: props.timetable.metadata?.optimization_params?.max_iterations || 1000,
      time_limit: props.timetable.metadata?.optimization_params?.time_limit || 300,
      convergence_threshold: props.timetable.metadata?.optimization_params?.convergence_threshold || 0.01
    }
    form.metadata = props.timetable.metadata || {}
    metadataJson.value = JSON.stringify(form.metadata, null, 2)
  } else {
    // 新增模式
    form.name = ''
    form.calendar_id = ''
    form.description = ''
    form.constraints = []
    form.optimization_params = {
      max_iterations: 1000,
      time_limit: 300,
      convergence_threshold: 0.01
    }
    form.metadata = {}
    metadataJson.value = ''
  }
}

const handleMetadataBlur = () => {
  try {
    if (metadataJson.value.trim()) {
      form.metadata = JSON.parse(metadataJson.value)
    } else {
      form.metadata = {}
    }
  } catch (error) {
    ElMessage.error('元数据格式错误，请输入有效的JSON')
    metadataJson.value = JSON.stringify(form.metadata, null, 2)
  }
}

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

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    loading.value = true

    const data = {
      ...form,
      metadata: {
        ...form.metadata,
        optimization_params: form.optimization_params
      }
    }

    let result: Timetable
    if (isEdit.value) {
      result = await timetablesStore.updateTimetable(props.timetable!.id, {
        ...data,
        id: props.timetable!.id
      })
    } else {
      result = await timetablesStore.createTimetable(data)
    }

    ElMessage.success(isEdit.value ? '时间表更新成功' : '时间表创建成功')
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
  }
})

// 初始化
initForm()
</script>

<style scoped>
.form-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #ebeef5;
}

.form-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
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

.help-icon {
  color: #909399;
  cursor: help;
}

.constraint-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.constraint-name {
  flex: 1;
}

.constraint-type {
  font-size: 12px;
  color: #909399;
  padding: 2px 6px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.optimization-params {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.param-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.param-item label {
  min-width: 100px;
  font-size: 14px;
  color: #606266;
}

.metadata-hint {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.preview-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.preview-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.preview-item .label {
  font-size: 14px;
  color: #606266;
  min-width: 80px;
}

.preview-item .value {
  font-size: 14px;
  color: #303133;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>