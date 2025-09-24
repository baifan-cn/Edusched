<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      label-position="right"
    >
      <el-form-item label="学科名称" prop="name">
        <el-input
          v-model="formData.name"
          placeholder="请输入学科名称"
          maxlength="50"
          show-word-limit
          clearable
        />
      </el-form-item>

      <el-form-item label="学科代码" prop="code">
        <el-input
          v-model="formData.code"
          placeholder="请输入学科代码"
          maxlength="20"
          show-word-limit
          clearable
          @blur="handleCodeBlur"
        />
        <div v-if="codeChecking" class="checking-hint">
          <el-icon class="is-loading"><Loading /></el-icon>
          正在检查代码重复...
        </div>
        <div v-if="codeError" class="error-hint">
          {{ codeError }}
        </div>
      </el-form-item>

      <el-form-item label="学科描述" prop="description">
        <el-input
          v-model="formData.description"
          type="textarea"
          placeholder="请输入学科描述"
          :rows="4"
          maxlength="500"
          show-word-limit
          resize="none"
        />
      </el-form-item>

      <el-form-item label="状态" prop="is_active">
        <el-radio-group v-model="formData.is_active">
          <el-radio :label="true">激活</el-radio>
          <el-radio :label="false">停用</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { useSubjectsStore } from '@/stores/subjects'
import type { Subject, CreateSubjectRequest, UpdateSubjectRequest } from '@/types'

interface Props {
  modelValue: boolean
  subject?: Subject | null
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const subjectsStore = useSubjectsStore()

// 响应式数据
const formRef = ref<FormInstance>()
const submitting = ref(false)
const codeChecking = ref(false)
const codeError = ref<string>('')

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isEdit = computed(() => !!props.subject)

const title = computed(() => isEdit.value ? '编辑学科' : '新增学科')

// 表单数据
const formData = reactive<CreateSubjectRequest>({
  name: '',
  code: '',
  description: '',
  is_active: true
})

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入学科名称', trigger: 'blur' },
    { min: 2, max: 50, message: '学科名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入学科代码', trigger: 'blur' },
    { min: 2, max: 20, message: '学科代码长度在 2 到 20 个字符', trigger: 'blur' },
    { pattern: /^[A-Z0-9_-]+$/i, message: '学科代码只能包含字母、数字、下划线和连字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '学科描述最多 500 个字符', trigger: 'blur' }
  ],
  is_active: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 监听subject变化，填充表单
watch(
  () => props.subject,
  (newSubject) => {
    if (newSubject) {
      Object.assign(formData, {
        name: newSubject.name,
        code: newSubject.code,
        description: newSubject.description || '',
        is_active: newSubject.is_active
      })
    } else {
      resetForm()
    }
  },
  { immediate: true }
)

// 监听对话框显示状态
watch(
  visible,
  (newValue) => {
    if (newValue && !isEdit.value) {
      resetForm()
    }
  }
)

// 方法
const resetForm = () => {
  Object.assign(formData, {
    name: '',
    code: '',
    description: '',
    is_active: true
  })
  codeError.value = ''
  formRef.value?.clearValidate()
}

const handleClose = () => {
  visible.value = false
  emit('cancel')
}

const handleCodeBlur = async () => {
  if (!formData.code || formData.code.length < 2) {
    codeError.value = ''
    return
  }

  try {
    codeChecking.value = true
    codeError.value = ''

    const result = await subjectsStore.checkSubjectCode(
      formData.code,
      isEdit.value ? props.subject?.id : undefined
    )

    if (!result.is_available) {
      codeError.value = result.message
    }
  } catch (error) {
    console.error('检查学科代码失败:', error)
  } finally {
    codeChecking.value = false
  }
}

const validateForm = async (): Promise<boolean> => {
  if (!formRef.value) return false

  try {
    await formRef.value.validate()
    return true
  } catch (error) {
    return false
  }
}

const handleSubmit = async () => {
  if (codeError.value) {
    ElMessage.error('请先解决学科代码问题')
    return
  }

  const isValid = await validateForm()
  if (!isValid) return

  try {
    submitting.value = true

    if (isEdit.value) {
      await subjectsStore.updateSubject(props.subject!.id, formData as UpdateSubjectRequest)
    } else {
      await subjectsStore.createSubject(formData)
    }

    ElMessage.success(isEdit.value ? '学科更新成功' : '学科创建成功')
    emit('success')
    handleClose()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.checking-hint {
  margin-top: 4px;
  color: #909399;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.error-hint {
  margin-top: 4px;
  color: #f56c6c;
  font-size: 12px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}
</style>