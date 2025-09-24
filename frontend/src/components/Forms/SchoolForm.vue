<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑学校' : '新增学校'"
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

        <el-form-item label="学校名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入学校名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="学校代码" prop="code">
          <el-input
            v-model="formData.code"
            placeholder="请输入学校代码"
            maxlength="20"
            show-word-limit
          >
            <template #prefix>
              <el-icon><Key /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="学校地址" prop="address">
          <el-input
            v-model="formData.address"
            type="textarea"
            placeholder="请输入学校地址"
            maxlength="200"
            show-word-limit
            :rows="2"
          />
        </el-form-item>

        <el-form-item label="联系电话" prop="phone">
          <el-input
            v-model="formData.phone"
            placeholder="请输入联系电话"
            maxlength="20"
          >
            <template #prefix>
              <el-icon><Phone /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="邮箱地址" prop="email">
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

        <el-form-item label="官方网站" prop="website">
          <el-input
            v-model="formData.website"
            placeholder="请输入官方网站"
            maxlength="200"
          >
            <template #prefix>
              <el-icon><Link /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="学校简介" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            placeholder="请输入学校简介"
            maxlength="500"
            show-word-limit
            :rows="3"
          />
        </el-form-item>
      </div>

      <!-- Logo上传 -->
      <div class="form-section">
        <h4 class="section-title">学校Logo</h4>

        <el-form-item label="Logo图片" prop="logo_url">
          <el-upload
            class="logo-uploader"
            :show-file-list="false"
            :before-upload="beforeLogoUpload"
            :http-request="handleLogoUpload"
            accept="image/*"
          >
            <img
              v-if="formData.logo_url"
              :src="formData.logo_url"
              class="logo-image"
              alt="学校Logo"
            />
            <el-icon v-else class="logo-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">
            支持 JPG、PNG 格式，大小不超过 2MB，建议尺寸 200x200px
          </div>
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
import { ElMessage, type FormInstance, type UploadRequestOptions } from 'element-plus'
import { Key, Phone, Message, Link, Plus } from '@element-plus/icons-vue'
import { useFormSubmit } from '@/hooks/useAPI'
import { FormValidator } from '@/utils/validation'
import type { School, CreateSchoolRequest, UpdateSchoolRequest } from '@/types'

// 组件属性
interface Props {
  modelValue: boolean
  school?: School | null
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  school: null
})

// 组件事件
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': [school: School]
  'cancel': []
}>()

// 响应式数据
const formRef = ref<FormInstance>()
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isEdit = computed(() => !!props.school?.id)

// 表单数据
const formData = reactive<CreateSchoolRequest>({
  name: '',
  code: '',
  address: '',
  phone: '',
  email: '',
  website: '',
  description: '',
  logo_url: '',
  is_active: true
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '学校名称不能为空', trigger: 'blur' },
    { min: 2, max: 100, message: '学校名称长度为2-100个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '学校代码不能为空', trigger: 'blur' },
    { min: 2, max: 20, message: '学校代码长度为2-20个字符', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9_-]+$/, message: '学校代码只能包含字母、数字、下划线和连字符', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  website: [
    { type: 'url', message: '网址格式不正确', trigger: 'blur' }
  ]
}

// 表单提交
const { submitting, submit: submitForm } = useFormSubmit(
  async (data: CreateSchoolRequest | UpdateSchoolRequest) => {
    // 在实际应用中，这里应该调用API
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    const result = {
      ...data,
      id: props.school?.id || `school_${Date.now()}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    } as School

    emit('success', result)
    visible.value = false
    ElMessage.success(isEdit.value ? '学校信息更新成功' : '学校创建成功')
  }
)

// 方法
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    // 检查邮箱和电话号码的唯一性（在编辑模式下排除自己）
    if (formData.email || formData.phone) {
      // 这里可以添加唯一性检查
    }

    // 提交表单
    const submitData = isEdit.value
      ? { ...formData, id: props.school!.id } as UpdateSchoolRequest
      : { ...formData } as CreateSchoolRequest

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
    name: '',
    code: '',
    address: '',
    phone: '',
    email: '',
    website: '',
    description: '',
    logo_url: '',
    is_active: true
  })
}

// Logo上传相关
const beforeLogoUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件！')
    return false
  }

  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB！')
    return false
  }

  return true
}

const handleLogoUpload = async (options: UploadRequestOptions) => {
  try {
    // 模拟上传
    await new Promise(resolve => setTimeout(resolve, 1000))

    // 生成预览URL
    const reader = new FileReader()
    reader.onload = (e) => {
      formData.logo_url = e.target?.result as string
    }
    reader.readAsDataURL(options.file)
  } catch (error) {
    ElMessage.error('Logo上传失败')
  }
}

// 监听对话框显示/隐藏
watch(visible, (newValue) => {
  if (newValue && props.school) {
    // 编辑模式，填充表单数据
    Object.assign(formData, {
      name: props.school.name,
      code: props.school.code,
      address: props.school.address || '',
      phone: props.school.phone || '',
      email: props.school.email || '',
      website: props.school.website || '',
      description: props.school.description || '',
      logo_url: props.school.logo_url || '',
      is_active: props.school.is_active
    })
  } else if (!newValue) {
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

.logo-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.3s;
}

.logo-uploader:hover {
  border-color: #409eff;
}

.logo-uploader-icon {
  font-size: 28px;
  color: #8c939d;
}

.logo-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
  line-height: 1.4;
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
</style>