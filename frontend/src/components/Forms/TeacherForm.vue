<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑教师' : '新增教师'"
    width="800px"
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

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="所属学校" prop="school_id">
              <el-select
                v-model="formData.school_id"
                placeholder="请选择所属学校"
                style="width: 100%"
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
          </el-col>
          <el-col :span="12">
            <el-form-item label="工号" prop="employee_id">
              <el-input
                v-model="formData.employee_id"
                placeholder="请输入工号"
                maxlength="20"
              >
                <template #prefix>
                  <el-icon><Key /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="姓" prop="first_name">
              <el-input
                v-model="formData.first_name"
                placeholder="请输入姓"
                maxlength="50"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="名" prop="last_name">
              <el-input
                v-model="formData.last_name"
                placeholder="请输入名"
                maxlength="50"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input
                v-model="formData.email"
                placeholder="请输入邮箱地址"
                maxlength="100"
              >
                <template #prefix>
                  <el-icon><Message /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-input
                v-model="formData.phone"
                placeholder="请输入手机号"
                maxlength="20"
              >
                <template #prefix>
                  <el-icon><Phone /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="所属部门" prop="department">
              <el-input
                v-model="formData.department"
                placeholder="请输入所属部门"
                maxlength="50"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职称" prop="title">
              <el-select
                v-model="formData.title"
                placeholder="请选择职称"
                style="width: 100%"
                clearable
              >
                <el-option label="教授" value="教授" />
                <el-option label="副教授" value="副教授" />
                <el-option label="讲师" value="讲师" />
                <el-option label="助教" value="助教" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="专业方向" prop="specialization">
          <el-select
            v-model="formData.specialization"
            placeholder="请选择专业方向"
            style="width: 100%"
            multiple
            filterable
            allow-create
            default-first-option
          >
            <el-option label="数学" value="数学" />
            <el-option label="语文" value="语文" />
            <el-option label="英语" value="英语" />
            <el-option label="物理" value="物理" />
            <el-option label="化学" value="化学" />
            <el-option label="生物" value="生物" />
            <el-option label="历史" value="历史" />
            <el-option label="地理" value="地理" />
            <el-option label="政治" value="政治" />
            <el-option label="体育" value="体育" />
            <el-option label="音乐" value="音乐" />
            <el-option label="美术" value="美术" />
            <el-option label="信息技术" value="信息技术" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
      </div>

      <!-- 工作设置 -->
      <div class="form-section">
        <h4 class="section-title">工作设置</h4>

        <el-form-item label="最大周课时" prop="max_hours_per_week">
          <el-input-number
            v-model="formData.max_hours_per_week"
            :min="1"
            :max="40"
            placeholder="请输入最大周课时"
            style="width: 200px"
          />
          <span class="form-help-text">设置教师每周最多可承担的课时数</span>
        </el-form-item>

        <el-form-item label="偏好时间段" prop="preferred_time_slots">
          <el-time-picker
            v-model="preferredTimeRange"
            is-range
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="HH:mm"
            value-format="HH:mm"
            style="width: 300px"
          />
          <span class="form-help-text">设置教师偏好的教学时间段</span>
        </el-form-item>

        <el-form-item label="不可用时间" prop="unavailable_time_slots">
          <el-checkbox-group v-model="formData.unavailable_time_slots">
            <el-checkbox label="monday-morning">周一上午</el-checkbox>
            <el-checkbox label="monday-afternoon">周一下午</el-checkbox>
            <el-checkbox label="tuesday-morning">周二上午</el-checkbox>
            <el-checkbox label="tuesday-afternoon">周二下午</el-checkbox>
            <el-checkbox label="wednesday-morning">周三上午</el-checkbox>
            <el-checkbox label="wednesday-afternoon">周三下午</el-checkbox>
            <el-checkbox label="thursday-morning">周四上午</el-checkbox>
            <el-checkbox label="thursday-afternoon">周四下午</el-checkbox>
            <el-checkbox label="friday-morning">周五上午</el-checkbox>
            <el-checkbox label="friday-afternoon">周五下午</el-checkbox>
          </el-checkbox-group>
          <span class="form-help-text">选择教师不能授课的时间段</span>
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
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, type FormInstance } from 'element-plus'
import { Key, Phone, Message } from '@element-plus/icons-vue'
import { useFormSubmit } from '@/hooks/useAPI'
import { FormValidator } from '@/utils/validation'
import { useSchoolsStore } from '@/stores/schools'
import type { Teacher, CreateTeacherRequest, UpdateTeacherRequest } from '@/types'

// 组件属性
interface Props {
  modelValue: boolean
  teacher?: Teacher | null
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  teacher: null
})

// 组件事件
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': [teacher: Teacher]
  'cancel': []
}>()

// 状态管理
const schoolsStore = useSchoolsStore()

// 响应式数据
const formRef = ref<FormInstance>()
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isEdit = computed(() => !!props.teacher?.id)

// 偏好时间段
const preferredTimeRange = ref<[string, string] | null>(null)

// 表单数据
const formData = reactive<CreateTeacherRequest>({
  school_id: '',
  employee_id: '',
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  department: '',
  title: '',
  specialization: [],
  max_hours_per_week: 20,
  preferred_time_slots: [],
  unavailable_time_slots: [],
  is_active: true
})

// 计算属性
const schools = computed(() => schoolsStore.schoolOptions)

// 表单验证规则
const rules = {
  school_id: [
    { required: true, message: '请选择所属学校', trigger: 'change' }
  ],
  employee_id: [
    { required: true, message: '工号不能为空', trigger: 'blur' },
    { min: 2, max: 20, message: '工号长度为2-20个字符', trigger: 'blur' }
  ],
  first_name: [
    { required: true, message: '姓不能为空', trigger: 'blur' },
    { min: 1, max: 50, message: '姓长度为1-50个字符', trigger: 'blur' }
  ],
  last_name: [
    { required: true, message: '名不能为空', trigger: 'blur' },
    { min: 1, max: 50, message: '名长度为1-50个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '邮箱不能为空', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '手机号不能为空', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  max_hours_per_week: [
    { required: true, message: '最大周课时不能为空', trigger: 'blur' },
    { type: 'number', min: 1, max: 40, message: '最大周课时为1-40小时', trigger: 'blur' }
  ]
}

// 表单提交
const { submitting, submit: submitForm } = useFormSubmit(
  async (data: CreateTeacherRequest | UpdateTeacherRequest) => {
    // 处理偏好时间段
    if (preferredTimeRange.value) {
      data.preferred_time_slots = [
        preferredTimeRange.value[0],
        preferredTimeRange.value[1]
      ]
    }

    // 在实际应用中，这里应该调用API
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    const result = {
      ...data,
      id: props.teacher?.id || `teacher_${Date.now()}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    } as Teacher

    emit('success', result)
    visible.value = false
    ElMessage.success(isEdit.value ? '教师信息更新成功' : '教师创建成功')
  }
)

// 方法
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    await submitForm(isEdit.value
      ? { ...formData, id: props.teacher!.id } as UpdateTeacherRequest
      : { ...formData } as CreateTeacherRequest
    )
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
    school_id: '',
    employee_id: '',
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    department: '',
    title: '',
    specialization: [],
    max_hours_per_week: 20,
    preferred_time_slots: [],
    unavailable_time_slots: [],
    is_active: true
  })

  // 重置偏好时间段
  preferredTimeRange.value = null
}

// 监听对话框显示/隐藏
watch(visible, async (newValue) => {
  if (newValue) {
    // 加载学校列表
    if (schoolsStore.schools.length === 0) {
      await schoolsStore.fetchSchools()
    }

    if (props.teacher) {
      // 编辑模式，填充表单数据
      Object.assign(formData, {
        school_id: props.teacher.school_id,
        employee_id: props.teacher.employee_id,
        first_name: props.teacher.first_name,
        last_name: props.teacher.last_name,
        email: props.teacher.email,
        phone: props.teacher.phone || '',
        department: props.teacher.department || '',
        title: props.teacher.title || '',
        specialization: props.teacher.specialization || [],
        max_hours_per_week: props.teacher.max_hours_per_week || 20,
        preferred_time_slots: props.teacher.preferred_time_slots || [],
        unavailable_time_slots: props.teacher.unavailable_time_slots || [],
        is_active: props.teacher.is_active
      })

      // 设置偏好时间段
      if (props.teacher.preferred_time_slots && props.teacher.preferred_time_slots.length >= 2) {
        preferredTimeRange.value = [
          props.teacher.preferred_time_slots[0],
          props.teacher.preferred_time_slots[1]
        ]
      }
    }
  } else {
    // 关闭对话框，重置表单
    resetForm()
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

.form-help-text {
  margin-left: 12px;
  font-size: 12px;
  color: #909399;
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

:deep(.el-checkbox-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

:deep(.el-checkbox) {
  margin-right: 0;
}
</style>