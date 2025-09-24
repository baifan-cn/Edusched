<template>
  <el-dialog
    v-model="visible"
    title="新建调度任务"
    width="90%"
    :before-close="handleClose"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      label-position="right"
    >
      <!-- 基本信息 -->
      <div class="form-section">
        <h3 class="section-title">基本信息</h3>
        <el-form-item label="任务名称" prop="name">
          <el-input
            v-model="form.name"
            placeholder="请输入任务名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="任务描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入任务描述（可选）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-radio-group v-model="form.priority">
            <el-radio label="low">低</el-radio>
            <el-radio label="normal">普通</el-radio>
            <el-radio label="high">高</el-radio>
            <el-radio label="urgent">紧急</el-radio>
          </el-radio-group>
        </el-form-item>
      </div>

      <!-- 调度配置 -->
      <div class="form-section">
        <h3 class="section-title">调度配置</h3>
        <el-form-item label="学校" prop="config.school_id">
          <el-select
            v-model="form.config.school_id"
            placeholder="请选择学校"
            style="width: 300px"
          >
            <el-option
              v-for="school in schools"
              :key="school.value"
              :label="school.label"
              :value="school.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="学年" prop="config.academic_year">
          <el-input
            v-model="form.config.academic_year"
            placeholder="如：2024-2025"
            maxlength="20"
          />
        </el-form-item>
        <el-form-item label="学期" prop="config.semester">
          <el-select
            v-model="form.config.semester"
            placeholder="请选择学期"
            style="width: 200px"
          >
            <el-option label="第一学期" value="1" />
            <el-option label="第二学期" value="2" />
            <el-option label="夏季学期" value="3" />
          </el-select>
        </el-form-item>
      </div>

      <!-- 时间槽配置 -->
      <div class="form-section">
        <h3 class="section-title">时间槽配置</h3>
        <div class="time-slots-header">
          <span>时间槽列表</span>
          <el-button type="primary" size="small" @click="addTimeSlot">
            <el-icon><Plus /></el-icon>
            添加时间槽
          </el-button>
        </div>
        <div class="time-slots-list">
          <div
            v-for="(slot, index) in form.config.time_slots"
            :key="index"
            class="time-slot-item"
          >
            <el-form-item
              :label="`时间槽 ${index + 1}`"
              :prop="`config.time_slots.${index}`"
              :rules="{ required: true, message: '请完善时间槽信息', trigger: 'blur' }"
            >
              <div class="time-slot-content">
                <el-input
                  v-model="slot.name"
                  placeholder="名称"
                  style="width: 120px"
                />
                <el-time-picker
                  v-model="slot.start_time"
                  placeholder="开始时间"
                  format="HH:mm"
                  value-format="HH:mm"
                  style="width: 120px"
                />
                <span>至</span>
                <el-time-picker
                  v-model="slot.end_time"
                  placeholder="结束时间"
                  format="HH:mm"
                  value-format="HH:mm"
                  style="width: 120px"
                />
                <el-checkbox v-model="slot.is_break">休息时间</el-checkbox>
                <el-input-number
                  v-model="slot.weight"
                  :min="0"
                  :max="10"
                  :step="0.1"
                  placeholder="权重"
                  style="width: 100px"
                />
                <el-button
                  type="danger"
                  size="small"
                  circle
                  @click="removeTimeSlot(index)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </el-form-item>
          </div>
        </div>
      </div>

      <!-- 约束配置 -->
      <div class="form-section">
        <h3 class="section-title">约束配置</h3>
        <div class="constraints-header">
          <span>约束条件</span>
          <el-button type="primary" size="small" @click="showConstraintEditor = true">
            <el-icon><Setting /></el-icon>
            配置约束
          </el-button>
        </div>
        <div class="constraints-summary">
          <el-tag
            v-for="constraint in form.config.constraints"
            :key="constraint.id"
            :type="constraint.type === 'hard' ? 'danger' : 'warning'"
            size="small"
            style="margin-right: 8px; margin-bottom: 8px"
          >
            {{ constraint.name }}
            <el-icon
              class="constraint-remove"
              @click="removeConstraint(constraint.id)"
            >
              <Close />
            </el-icon>
          </el-tag>
          <span v-if="form.config.constraints.length === 0" class="no-constraints">
            暂无约束条件
          </span>
        </div>
      </div>

      <!-- 算法参数 -->
      <div class="form-section">
        <h3 class="section-title">算法参数</h3>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="最大迭代次数" prop="config.algorithm_params.max_iterations">
              <el-input-number
                v-model="form.config.algorithm_params.max_iterations"
                :min="100"
                :max="1000000"
                :step="100"
                style="width: 200px"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="时间限制(秒)" prop="config.algorithm_params.time_limit_seconds">
              <el-input-number
                v-model="form.config.algorithm_params.time_limit_seconds"
                :min="10"
                :max="3600"
                :step="10"
                style="width: 200px"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="搜索策略" prop="config.algorithm_params.search_strategy">
              <el-select
                v-model="form.config.algorithm_params.search_strategy"
                style="width: 200px"
              >
                <el-option label="深度优先" value="depth_first" />
                <el-option label="广度优先" value="breadth_first" />
                <el-option label="最佳优先" value="best_first" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="并行计算" prop="config.algorithm_params.enable_parallel">
              <el-switch v-model="form.config.algorithm_params.enable_parallel" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16" v-if="form.config.algorithm_params.enable_parallel">
          <el-col :span="12">
            <el-form-item label="并行工作数" prop="config.algorithm_params.parallel_workers">
              <el-input-number
                v-model="form.config.algorithm_params.parallel_workers"
                :min="1"
                :max="16"
                :step="1"
                style="width: 200px"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="随机种子" prop="config.algorithm_params.random_seed">
              <el-input-number
                v-model="form.config.algorithm_params.random_seed"
                :min="0"
                :max="2147483647"
                style="width: 200px"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="启用日志" prop="config.algorithm_params.enable_logging">
              <el-switch v-model="form.config.algorithm_params.enable_logging" />
            </el-form-item>
          </el-col>
          <el-col :span="12" v-if="form.config.algorithm_params.enable_logging">
            <el-form-item label="日志级别" prop="config.algorithm_params.log_level">
              <el-select
                v-model="form.config.algorithm_params.log_level"
                style="width: 200px"
              >
                <el-option label="调试" value="debug" />
                <el-option label="信息" value="info" />
                <el-option label="警告" value="warn" />
                <el-option label="错误" value="error" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <!-- 优化目标 -->
      <div class="form-section">
        <h3 class="section-title">优化目标</h3>
        <div class="optimization-targets">
          <div
            v-for="(target, index) in form.config.optimization_targets"
            :key="index"
            class="target-item"
          >
            <el-form-item
              :label="`目标 ${index + 1}`"
              :prop="`config.optimization_targets.${index}`"
              :rules="{ required: true, message: '请完善优化目标', trigger: 'blur' }"
            >
              <div class="target-content">
                <el-select
                  v-model="target.metric"
                  placeholder="选择指标"
                  style="width: 150px"
                >
                  <el-option label="教师利用率" value="teacher_utilization" />
                  <el-option label="教室利用率" value="room_utilization" />
                  <el-option label="课程覆盖率" value="course_coverage" />
                  <el-option label="约束满足度" value="constraint_satisfaction" />
                  <el-option label="时间均匀性" value="time_uniformity" />
                </el-select>
                <el-select
                  v-model="target.direction"
                  placeholder="优化方向"
                  style="width: 120px"
                >
                  <el-option label="最小化" value="minimize" />
                  <el-option label="最大化" value="maximize" />
                </el-select>
                <el-input-number
                  v-model="target.weight"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  placeholder="权重"
                  style="width: 100px"
                />
                <el-input-number
                  v-model="target.target_value"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  placeholder="目标值"
                  style="width: 100px"
                />
                <el-button
                  type="danger"
                  size="small"
                  circle
                  @click="removeOptimizationTarget(index)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </el-form-item>
          </div>
        </div>
        <el-button type="primary" size="small" @click="addOptimizationTarget">
          <el-icon><Plus /></el-icon>
          添加优化目标
        </el-button>
      </div>
    </el-form>

    <!-- 约束编辑器对话框 -->
    <ConstraintEditor
      v-model="showConstraintEditor"
      :constraints="form.config.constraints"
      :templates="constraintTemplates"
      @update="updateConstraints"
    />

    <!-- 对话框底部 -->
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleValidate" :loading="validating">
          验证配置
        </el-button>
        <el-button type="success" @click="handleSubmit" :loading="submitting">
          创建任务
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Setting, Close } from '@element-plus/icons-vue'
import { useSchedulingStore } from '@/stores/scheduling'
import type {
  SchedulingConfig,
  Constraint,
  TimeSlot,
  AlgorithmParams,
  OptimizationTarget
} from '@/api/scheduling'
import ConstraintEditor from './ConstraintEditor.vue'

interface Props {
  modelValue: boolean
  schools: Array<{ label: string; value: string; code?: string }>
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 状态管理
const schedulingStore = useSchedulingStore()

// 响应式数据
const formRef = ref()
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})
const showConstraintEditor = ref(false)
const submitting = ref(false)
const validating = ref(false)

// 约束模板
const constraintTemplates = computed(() => schedulingStore.constraintTemplates)

// 表单数据
const form = reactive({
  name: '',
  description: '',
  priority: 'normal' as 'low' | 'normal' | 'high' | 'urgent',
  config: {
    school_id: '',
    academic_year: '',
    semester: '1',
    week_days: [1, 2, 3, 4, 5],
    time_slots: [] as TimeSlot[],
    constraints: [] as Constraint[],
    algorithm_params: {
      max_iterations: 10000,
      time_limit_seconds: 300,
      search_strategy: 'best_first' as 'depth_first' | 'breadth_first' | 'best_first',
      enable_parallel: true,
      parallel_workers: 4,
      random_seed: undefined as number | undefined,
      enable_logging: true,
      log_level: 'info' as 'debug' | 'info' | 'warn' | 'error'
    } as AlgorithmParams,
    optimization_targets: [] as OptimizationTarget[]
  } as SchedulingConfig
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' },
    { min: 2, max: 100, message: '任务名称长度应在2-100个字符之间', trigger: 'blur' }
  ],
  'config.school_id': [
    { required: true, message: '请选择学校', trigger: 'change' }
  ],
  'config.academic_year': [
    { required: true, message: '请输入学年', trigger: 'blur' }
  ],
  'config.semester': [
    { required: true, message: '请选择学期', trigger: 'change' }
  ],
  'config.algorithm_params.max_iterations': [
    { required: true, message: '请输入最大迭代次数', trigger: 'blur' }
  ],
  'config.algorithm_params.time_limit_seconds': [
    { required: true, message: '请输入时间限制', trigger: 'blur' }
  ]
}

// 方法
const addTimeSlot = () => {
  form.config.time_slots.push({
    id: Date.now().toString(),
    name: '',
    start_time: '',
    end_time: '',
    is_break: false,
    weight: 1.0
  })
}

const removeTimeSlot = (index: number) => {
  form.config.time_slots.splice(index, 1)
}

const addOptimizationTarget = () => {
  form.config.optimization_targets.push({
    metric: '',
    weight: 1.0,
    direction: 'maximize' as 'minimize' | 'maximize'
  })
}

const removeOptimizationTarget = (index: number) => {
  form.config.optimization_targets.splice(index, 1)
}

const updateConstraints = (constraints: Constraint[]) => {
  form.config.constraints = constraints
}

const removeConstraint = (constraintId: string) => {
  form.config.constraints = form.config.constraints.filter(c => c.id !== constraintId)
}

const handleValidate = async () => {
  try {
    await formRef.value.validate()
    validating.value = true

    const result = await schedulingStore.validateConfig({
      config: form.config,
      check_data_integrity: true,
      check_constraints: true,
      check_resource_availability: true
    })

    if (result.valid) {
      ElMessage.success('配置验证通过')
    } else {
      ElMessage.warning('配置验证失败，请检查配置')
      // 显示验证错误
      const errorMessages = result.errors.map(e => e.message).join('\n')
      ElMessageBox.alert(errorMessages, '配置验证失败', {
        type: 'warning',
        confirmButtonText: '确定'
      })
    }
  } catch (error) {
    ElMessage.error('验证配置失败')
  } finally {
    validating.value = false
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    await schedulingStore.createJob({
      name: form.name,
      description: form.description,
      priority: form.priority as any,
      config: form.config
    })

    ElMessage.success('调度任务创建成功')
    emit('success')
    resetForm()
  } catch (error) {
    ElMessage.error('创建调度任务失败')
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  if (!submitting.value && !validating.value) {
    emit('cancel')
    resetForm()
  }
}

const resetForm = () => {
  formRef.value?.resetFields()
  Object.assign(form, {
    name: '',
    description: '',
    priority: 'normal',
    config: {
      school_id: '',
      academic_year: '',
      semester: '1',
      week_days: [1, 2, 3, 4, 5],
      time_slots: [],
      constraints: [],
      algorithm_params: {
        max_iterations: 10000,
        time_limit_seconds: 300,
        search_strategy: 'best_first',
        enable_parallel: true,
        parallel_workers: 4,
        random_seed: undefined,
        enable_logging: true,
        log_level: 'info'
      },
      optimization_targets: []
    }
  })
}

// 监听对话框显示状态
watch(visible, (newValue) => {
  if (newValue) {
    // 加载约束模板
    schedulingStore.fetchConstraintTemplates()

    // 设置默认时间槽
    if (form.config.time_slots.length === 0) {
      form.config.time_slots = [
        { id: '1', name: '第1节', start_time: '08:00', end_time: '08:45', is_break: false, weight: 1.0 },
        { id: '2', name: '第2节', start_time: '08:55', end_time: '09:40', is_break: false, weight: 1.0 },
        { id: '3', name: '第3节', start_time: '10:00', end_time: '10:45', is_break: false, weight: 1.0 },
        { id: '4', name: '第4节', start_time: '10:55', end_time: '11:40', is_break: false, weight: 1.0 },
        { id: '5', name: '午休', start_time: '11:40', end_time: '14:00', is_break: true, weight: 0.0 },
        { id: '6', name: '第5节', start_time: '14:00', end_time: '14:45', is_break: false, weight: 1.0 },
        { id: '7', name: '第6节', start_time: '14:55', end_time: '15:40', is_break: false, weight: 1.0 },
        { id: '8', name: '第7节', start_time: '15:50', end_time: '16:35', is_break: false, weight: 1.0 },
        { id: '9', name: '第8节', start_time: '16:45', end_time: '17:30', is_break: false, weight: 1.0 }
      ]
    }

    // 设置默认优化目标
    if (form.config.optimization_targets.length === 0) {
      form.config.optimization_targets = [
        { metric: 'constraint_satisfaction', weight: 1.0, direction: 'maximize' },
        { metric: 'teacher_utilization', weight: 0.8, direction: 'maximize' },
        { metric: 'room_utilization', weight: 0.6, direction: 'maximize' }
      ]
    }
  }
})
</script>

<style scoped>
.form-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #ebeef5;
}

.form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.time-slots-header,
.constraints-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.time-slots-list {
  max-height: 300px;
  overflow-y: auto;
}

.time-slot-item {
  margin-bottom: 16px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.time-slot-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.constraints-summary {
  min-height: 40px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border: 1px dashed #dcdfe6;
}

.constraint-remove {
  margin-left: 4px;
  cursor: pointer;
  font-size: 12px;
}

.constraint-remove:hover {
  color: #f56c6c;
}

.no-constraints {
  color: #909399;
  font-size: 14px;
}

.optimization-targets {
  margin-bottom: 16px;
}

.target-item {
  margin-bottom: 16px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.target-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-input-number) {
  width: 100%;
}

:deep(.el-time-picker) {
  width: 100%;
}

:deep(.el-select) {
  width: 100%;
}
</style>