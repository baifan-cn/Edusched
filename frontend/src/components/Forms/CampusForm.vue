<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑校区' : '新增校区'"
    width="600px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      label-position="left"
    >
      <el-form-item label="校区名称" prop="name">
        <el-input
          v-model="form.name"
          placeholder="请输入校区名称"
          maxlength="50"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="校区代码" prop="code">
        <el-input
          v-model="form.code"
          placeholder="请输入校区代码"
          maxlength="20"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="所属学校" prop="school_id">
        <el-select
          v-model="form.school_id"
          placeholder="请选择所属学校"
          style="width: 100%"
        >
          <el-option
            v-for="school in schools"
            :key="school.id"
            :label="school.name"
            :value="school.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="校区地址" prop="address">
        <el-input
          v-model="form.address"
          type="textarea"
          placeholder="请输入校区地址"
          maxlength="200"
          show-word-limit
          :rows="3"
        />
      </el-form-item>

      <el-form-item label="联系电话" prop="phone">
        <el-input
          v-model="form.phone"
          placeholder="请输入联系电话"
          maxlength="20"
        />
      </el-form-item>

      <el-form-item label="邮箱地址" prop="email">
        <el-input
          v-model="form.email"
          placeholder="请输入邮箱地址"
          maxlength="50"
        />
      </el-form-item>

      <el-form-item label="状态" prop="is_active">
        <el-switch
          v-model="form.is_active"
          :active-text="form.is_active ? '启用' : '禁用'"
        />
      </el-form-item>

      <el-form-item label="备注" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          placeholder="请输入备注信息"
          maxlength="500"
          show-word-limit
          :rows="3"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          确定
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useCampusesStore } from '@/stores/campuses'
import { useSchoolsStore } from '@/stores/schools'

interface Props {
  modelValue: boolean
  campus?: any
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  campus: null
})

const emit = defineEmits<Emits>()

const campusesStore = useCampusesStore()
const schoolsStore = useSchoolsStore()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isEdit = computed(() => !!props.campus)

// 学校列表
const schools = computed(() => schoolsStore.schools)

// 表单数据
const form = reactive({
  name: '',
  code: '',
  school_id: '',
  address: '',
  phone: '',
  email: '',
  is_active: true,
  description: ''
})

// 表单验证规则
const rules: FormRules = {
  name: [
    { required: true, message: '请输入校区名称', trigger: 'blur' },
    { min: 2, max: 50, message: '校区名称长度为 2-50 个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入校区代码', trigger: 'blur' },
    { min: 2, max: 20, message: '校区代码长度为 2-20 个字符', trigger: 'blur' }
  ],
  school_id: [
    { required: true, message: '请选择所属学校', trigger: 'change' }
  ],
  address: [
    { required: true, message: '请输入校区地址', trigger: 'blur' },
    { max: 200, message: '校区地址最多 200 个字符', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

// 监听校区数据变化
watch(() => props.campus, (newCampus) => {
  if (newCampus) {
    Object.assign(form, newCampus)
  } else {
    resetForm()
  }
}, { immediate: true })

// 方法
const resetForm = () => {
  Object.assign(form, {
    name: '',
    code: '',
    school_id: '',
    address: '',
    phone: '',
    email: '',
    is_active: true,
    description: ''
  })
  formRef.value?.clearValidate()
}

const handleClose = () => {
  visible.value = false
  resetForm()
  emit('cancel')
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    loading.value = true

    if (isEdit.value) {
      await campusesStore.updateCampus(props.campus.id, form)
      ElMessage.success('校区更新成功')
    } else {
      await campusesStore.createCampus(form)
      ElMessage.success('校区创建成功')
    }

    emit('success')
    handleClose()
  } catch (error: any) {
    console.error('校区保存失败:', error)
    ElMessage.error(error.message || '保存失败')
  } finally {
    loading.value = false
  }
}

// 初始化学校列表
const initSchools = async () => {
  try {
    await schoolsStore.fetchSchools()
  } catch (error) {
    console.error('获取学校列表失败:', error)
  }
}

// 组件挂载时初始化
initSchools()
</script>

<style scoped>
.dialog-footer {
  text-align: right;
}
</style>