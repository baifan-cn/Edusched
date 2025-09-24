<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑课程' : '新增课程'"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="100px"
      label-position="right"
    >
      <!-- 基本信息 -->
      <div class="form-section">
        <h4 class="section-title">基本信息</h4>

        <el-form-item label="课程名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入课程名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="课程代码" prop="code">
          <el-input
            v-model="formData.code"
            placeholder="请输入课程代码"
            maxlength="20"
            show-word-limit
          >
            <template #prefix>
              <el-icon><Key /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="所属学科" prop="subject_id">
          <el-select
            v-model="formData.subject_id"
            placeholder="请选择所属学科"
            style="width: 100%"
            filterable
            clearable
          >
            <el-option
              v-for="subject in subjectOptions"
              :key="subject.value"
              :label="subject.label"
              :value="subject.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="课程描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            placeholder="请输入课程描述"
            maxlength="500"
            show-word-limit
            :rows="3"
          />
        </el-form-item>
      </div>

      <!-- 学时信息 -->
      <div class="form-section">
        <h4 class="section-title">学时信息</h4>

        <el-form-item label="学分" prop="credits">
          <el-input-number
            v-model="formData.credits"
            :min="0.5"
            :max="10"
            :step="0.5"
            :precision="1"
            style="width: 200px"
          />
          <span class="unit-text">学分</span>
        </el-form-item>

        <el-form-item label="周学时" prop="hours_per_week">
          <el-input-number
            v-model="formData.hours_per_week"
            :min="1"
            :max="40"
            :step="1"
            style="width: 200px"
          />
          <span class="unit-text">小时/周</span>
        </el-form-item>

        <el-form-item label="总学时" prop="total_hours">
          <el-input-number
            v-model="formData.total_hours"
            :min="1"
            :max="200"
            :step="1"
            style="width: 200px"
          />
          <span class="unit-text">小时</span>
        </el-form-item>
      </div>

      <!-- 状态设置 -->
      <div class="form-section">
        <h4 class="section-title">状态设置</h4>

        <el-form-item label="启用状态" prop="is_active">
          <el-switch
            v-model="formData.is_active"
            :active-text="formData.is_active ? '启用' : '禁用'"
            inline-prompt
          />
        </el-form-item>
      </div>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="handleSubmit"
        >
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage, type FormInstance } from 'element-plus'
import { Key } from '@element-plus/icons-vue'
import { useFormSubmit } from '@/hooks/useAPI'
import { FormValidator } from '@/utils/validation'
import { useCoursesStore } from '@/stores/courses'
import type { Course, CreateCourseRequest, UpdateCourseRequest } from '@/types'

// 组件属性
interface Props {
  modelValue: boolean
  course?: Course | null
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  course: null
})

// 组件事件
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': [course: Course]
  'cancel': []
}>()

// 响应式数据
const formRef = ref<FormInstance>()
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isEdit = computed(() => !!props.course?.id)

// 状态管理
const coursesStore = useCoursesStore()

// 计算属性
const subjectOptions = computed(() => coursesStore.subjectOptions)

// 表单数据
const formData = reactive<CreateCourseRequest>({
  subject_id: '',
  name: '',
  code: '',
  description: '',
  credits: 2,
  hours_per_week: 2,
  total_hours: 36
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '课程名称不能为空', trigger: 'blur' },
    { min: 2, max: 100, message: '课程名称长度为2-100个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '课程代码不能为空', trigger: 'blur' },
    { min: 2, max: 20, message: '课程代码长度为2-20个字符', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9_-]+$/, message: '课程代码只能包含字母、数字、下划线和连字符', trigger: 'blur' }
  ],
  subject_id: [
    { required: true, message: '请选择所属学科', trigger: 'change' }
  ],
  credits: [
    { required: true, message: '学分不能为空', trigger: 'blur' },
    { type: 'number', min: 0.5, max: 10, message: '学分范围为0.5-10', trigger: 'blur' }
  ],
  hours_per_week: [
    { required: true, message: '周学时不能为空', trigger: 'blur' },
    { type: 'number', min: 1, max: 40, message: '周学时范围为1-40小时', trigger: 'blur' }
  ],
  total_hours: [
    { required: true, message: '总学时不能为空', trigger: 'blur' },
    { type: 'number', min: 1, max: 200, message: '总学时范围为1-200小时', trigger: 'blur' }
  ]
}

// 表单提交
const { submitting, submit: submitForm } = useFormSubmit(
  async (data: CreateCourseRequest | UpdateCourseRequest) => {
    const result = isEdit.value
      ? await coursesStore.updateCourse(props.course!.id, data as UpdateCourseRequest)
      : await coursesStore.createCourse(data as CreateCourseRequest)

    emit('success', result)
    visible.value = false
    ElMessage.success(isEdit.value ? '课程信息更新成功' : '课程创建成功')
  }
)

// 方法
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    // 提交表单
    const submitData = isEdit.value
      ? { ...formData, id: props.course!.id } as UpdateCourseRequest
      : { ...formData } as CreateCourseRequest

    await submitForm(submitData)
  } catch (error) {
    console.error('Form validation failed:', error)
  }
}

const handleClose = () => {
  visible.value = false
  emit('cancel')
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }

  // 重置表单数据
  Object.assign(formData, {
    subject_id: '',
    name: '',
    code: '',
    description: '',
    credits: 2,
    hours_per_week: 2,
    total_hours: 36
  })
}

// 监听对话框显示/隐藏
watch(visible, (newValue) => {
  if (newValue && props.course) {
    // 编辑模式，填充表单数据
    Object.assign(formData, {
      subject_id: props.course.subject_id,
      name: props.course.name,
      code: props.course.code,
      description: props.course.description || '',
      credits: props.course.credits,
      hours_per_week: props.course.hours_per_week,
      total_hours: props.course.total_hours
    })
  } else if (!newValue) {
    // 关闭对话框，重置表单
    resetForm()
  }
})

// 组件挂载时获取学科列表
onMounted(async () => {
  if (coursesStore.subjects.length === 0) {
    await coursesStore.fetchSubjects({ is_active: true })
  }
})

// 暴露方法供父组件调用
defineExpose({
  resetForm
})
</script>

<style scoped>
.form-section {
  margin-bottom: 24px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.unit-text {
  margin-left: 8px;
  color: #909399;
  font-size: 14px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-input__prefix) {
  color: #909399;
}

:deep(.el-input-number) {
  width: 100%;
}
</style>