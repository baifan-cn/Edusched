<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑教室' : '新增教室'"
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
      <el-form-item label="教室名称" prop="name">
        <el-input
          v-model="form.name"
          placeholder="请输入教室名称"
          maxlength="50"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="教室代码" prop="code">
        <el-input
          v-model="form.code"
          placeholder="请输入教室代码"
          maxlength="20"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="所属校区" prop="campus_id">
        <el-select
          v-model="form.campus_id"
          placeholder="请选择所属校区"
          style="width: 100%"
          @change="handleCampusChange"
        >
          <el-option
            v-for="campus in campuses"
            :key="campus.id"
            :label="campus.name"
            :value="campus.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="教室类型" prop="room_type">
        <el-select
          v-model="form.room_type"
          placeholder="请选择教室类型"
          style="width: 100%"
        >
          <el-option label="普通教室" value="classroom" />
          <el-option label="实验室" value="lab" />
          <el-option label="多媒体教室" value="multimedia" />
          <el-option label="计算机教室" value="computer" />
          <el-option label="会议室" value="meeting" />
          <el-option label="体育馆" value="gym" />
          <el-option label="音乐教室" value="music" />
          <el-option label="美术教室" value="art" />
          <el-option label="其他" value="other" />
        </el-select>
      </el-form-item>

      <el-form-item label="容量" prop="capacity">
        <el-input-number
          v-model="form.capacity"
          :min="1"
          :max="1000"
          placeholder="请输入教室容量"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="楼层" prop="floor">
        <el-input-number
          v-model="form.floor"
          :min="1"
          :max="100"
          placeholder="请输入楼层"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="座位数" prop="seat_count">
        <el-input-number
          v-model="form.seat_count"
          :min="1"
          :max="1000"
          placeholder="请输入座位数"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="设备设施" prop="facilities">
        <el-checkbox-group v-model="form.facilities">
          <el-checkbox label="projector">投影仪</el-checkbox>
          <el-checkbox label="computer">电脑</el-checkbox>
          <el-checkbox label="air_conditioner">空调</el-checkbox>
          <el-checkbox label="speaker">音响</el-checkbox>
          <el-checkbox label="microphone">麦克风</el-checkbox>
          <el-checkbox label="whiteboard">白板</el-checkbox>
          <el-checkbox label="smart_board">智能黑板</el-checkbox>
          <el-checkbox label="wifi">WiFi</el-checkbox>
        </el-checkbox-group>
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
import { useRoomsStore } from '@/stores/rooms'

interface Props {
  modelValue: boolean
  room?: any
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  room: null
})

const emit = defineEmits<Emits>()

const roomsStore = useRoomsStore()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isEdit = computed(() => !!props.room)

// 校区列表
const campuses = computed(() => roomsStore.campuses)

// 表单数据
const form = reactive({
  name: '',
  code: '',
  campus_id: '',
  room_type: 'classroom',
  capacity: 50,
  floor: 1,
  seat_count: 50,
  facilities: [],
  is_active: true,
  description: ''
})

// 表单验证规则
const rules: FormRules = {
  name: [
    { required: true, message: '请输入教室名称', trigger: 'blur' },
    { min: 2, max: 50, message: '教室名称长度为 2-50 个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入教室代码', trigger: 'blur' },
    { min: 2, max: 20, message: '教室代码长度为 2-20 个字符', trigger: 'blur' }
  ],
  campus_id: [
    { required: true, message: '请选择所属校区', trigger: 'change' }
  ],
  room_type: [
    { required: true, message: '请选择教室类型', trigger: 'change' }
  ],
  capacity: [
    { required: true, message: '请输入教室容量', trigger: 'blur' }
  ],
  floor: [
    { required: true, message: '请输入楼层', trigger: 'blur' }
  ],
  seat_count: [
    { required: true, message: '请输入座位数', trigger: 'blur' }
  ]
}

// 监听教室数据变化
watch(() => props.room, (newRoom) => {
  if (newRoom) {
    Object.assign(form, newRoom)
  } else {
    resetForm()
  }
}, { immediate: true })

// 方法
const resetForm = () => {
  Object.assign(form, {
    name: '',
    code: '',
    campus_id: '',
    room_type: 'classroom',
    capacity: 50,
    floor: 1,
    seat_count: 50,
    facilities: [],
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

const handleCampusChange = () => {
  formRef.value?.validateField('campus_id')
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    loading.value = true

    if (isEdit.value) {
      await roomsStore.updateRoom(props.room.id, form)
      ElMessage.success('教室更新成功')
    } else {
      await roomsStore.createRoom(form)
      ElMessage.success('教室创建成功')
    }

    emit('success')
    handleClose()
  } catch (error: any) {
    console.error('教室保存失败:', error)
    ElMessage.error(error.message || '保存失败')
  } finally {
    loading.value = false
  }
}

// 初始化校区列表
const initCampuses = async () => {
  try {
    await roomsStore.fetchCampuses()
  } catch (error) {
    console.error('获取校区列表失败:', error)
  }
}

// 组件挂载时初始化
initCampuses()
</script>

<style scoped>
.dialog-footer {
  text-align: right;
}
</style>