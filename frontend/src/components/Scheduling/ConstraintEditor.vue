<template>
  <el-dialog
    v-model="visible"
    title="约束编辑器"
    width="80%"
    :before-close="handleClose"
    @close="handleClose"
  >
    <div class="constraint-editor">
      <!-- 约束分类标签 -->
      <div class="constraint-categories">
        <el-tabs v-model="activeCategory" @tab-click="handleCategoryChange">
          <el-tab-pane label="教师约束" name="teacher">
            <el-icon><User /></el-icon>
            教师约束
          </el-tab-pane>
          <el-tab-pane label="教室约束" name="room">
            <el-icon><House /></el-icon>
            教室约束
          </el-tab-pane>
          <el-tab-pane label="班级约束" name="class">
            <el-icon><Grid /></el-icon>
            班级约束
          </el-tab-pane>
          <el-tab-pane label="时间约束" name="time">
            <el-icon><Clock /></el-icon>
            时间约束
          </el-tab-pane>
          <el-tab-pane label="课程约束" name="course">
            <el-icon><Reading /></el-icon>
            课程约束
          </el-tab-pane>
          <el-tab-pane label="自定义约束" name="custom">
            <el-icon><Setting /></el-icon>
            自定义约束
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 约束列表 -->
      <div class="constraint-list">
        <div class="list-header">
          <span>{{ getCategoryTitle(activeCategory) }}</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索约束..."
              style="width: 200px"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="showConstraintForm = true">
              <el-icon><Plus /></el-icon>
              新建约束
            </el-button>
          </div>
        </div>

        <div class="constraints-grid">
          <!-- 模板约束 -->
          <div class="template-section">
            <h4>模板约束</h4>
            <div class="template-grid">
              <div
                v-for="template in filteredTemplates"
                :key="template.id"
                class="template-card"
                :class="{ 'selected': isConstraintSelected(template.id) }"
                @click="toggleTemplate(template)"
              >
                <div class="card-header">
                  <div class="template-info">
                    <div class="template-name">{{ template.name }}</div>
                    <div class="template-desc">{{ template.description }}</div>
                  </div>
                  <div class="template-type">
                    <el-tag :type="template.type === 'hard' ? 'danger' : 'warning'" size="small">
                      {{ template.type === 'hard' ? '硬约束' : '软约束' }}
                    </el-tag>
                  </div>
                </div>
                <div class="card-footer">
                  <div class="weight-control">
                    <span>权重:</span>
                    <el-input-number
                      v-model="template.weight"
                      :min="0"
                      :max="1"
                      :step="0.1"
                      size="small"
                      style="width: 80px"
                    />
                  </div>
                  <el-switch
                    v-model="template.enabled"
                    size="small"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- 自定义约束 -->
          <div class="custom-section">
            <h4>自定义约束</h4>
            <div class="custom-grid">
              <div
                v-for="constraint in filteredCustomConstraints"
                :key="constraint.id"
                class="constraint-card"
                :class="{ 'selected': isConstraintSelected(constraint.id) }"
              >
                <div class="card-header">
                  <div class="constraint-info">
                    <div class="constraint-name">
                      {{ constraint.name }}
                      <el-tag v-if="constraint.id.startsWith('custom_')" type="info" size="small">
                        自定义
                      </el-tag>
                    </div>
                    <div class="constraint-desc">{{ constraint.description }}</div>
                  </div>
                  <div class="constraint-actions">
                    <el-button
                      type="primary"
                      link
                      size="small"
                      @click="editConstraint(constraint)"
                    >
                      <el-icon><Edit /></el-icon>
                    </el-button>
                    <el-button
                      type="danger"
                      link
                      size="small"
                      @click="deleteConstraint(constraint)"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
                <div class="card-content">
                  <div class="constraint-params">
                    <div
                      v-for="(value, key) in constraint.params"
                      :key="key"
                      class="param-item"
                    >
                      <span class="param-key">{{ formatParamKey(key) }}:</span>
                      <span class="param-value">{{ formatParamValue(value) }}</span>
                    </div>
                  </div>
                </div>
                <div class="card-footer">
                  <div class="weight-control">
                    <span>权重:</span>
                    <el-input-number
                      v-model="constraint.weight"
                      :min="0"
                      :max="1"
                      :step="0.1"
                      size="small"
                      style="width: 80px"
                      @change="updateConstraintWeight(constraint.id, constraint.weight)"
                    />
                  </div>
                  <div class="type-control">
                    <el-radio-group
                      v-model="constraint.type"
                      size="small"
                      @change="updateConstraintType(constraint.id, constraint.type)"
                    >
                      <el-radio label="hard">硬约束</el-radio>
                      <el-radio label="soft">软约束</el-radio>
                    </el-radio-group>
                  </div>
                  <el-switch
                    v-model="constraint.enabled"
                    size="small"
                    @change="updateConstraintEnabled(constraint.id, constraint.enabled)"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 已选择的约束摘要 -->
      <div class="selected-constraints">
        <div class="selected-header">
          <span>已选择的约束 ({{ selectedConstraints.length }})</span>
          <el-button size="small" @click="clearSelectedConstraints">
            清空选择
          </el-button>
        </div>
        <div class="selected-list">
          <el-tag
            v-for="constraint in selectedConstraints"
            :key="constraint.id"
            :type="constraint.type === 'hard' ? 'danger' : 'warning'"
            size="small"
            style="margin-right: 8px; margin-bottom: 8px"
            closable
            @close="removeSelectedConstraint(constraint.id)"
          >
            {{ constraint.name }}
          </el-tag>
          <div v-if="selectedConstraints.length === 0" class="no-selection">
            暂未选择任何约束
          </div>
        </div>
      </div>
    </div>

    <!-- 约束表单对话框 -->
    <el-dialog
      v-model="showConstraintForm"
      :title="editingConstraint ? '编辑约束' : '新建约束'"
      width="600px"
      append-to-body
      @close="resetConstraintForm"
    >
      <el-form
        ref="constraintFormRef"
        :model="constraintForm"
        :rules="constraintRules"
        label-width="120px"
      >
        <el-form-item label="约束名称" prop="name">
          <el-input v-model="constraintForm.name" placeholder="请输入约束名称" />
        </el-form-item>
        <el-form-item label="约束类型" prop="type">
          <el-radio-group v-model="constraintForm.type">
            <el-radio label="hard">硬约束</el-radio>
            <el-radio label="soft">软约束</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="约束类别" prop="category">
          <el-select v-model="constraintForm.category" style="width: 100%">
            <el-option label="教师约束" value="teacher" />
            <el-option label="教室约束" value="room" />
            <el-option label="班级约束" value="class" />
            <el-option label="时间约束" value="time" />
            <el-option label="课程约束" value="course" />
            <el-option label="自定义约束" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="权重" prop="weight">
          <el-input-number
            v-model="constraintForm.weight"
            :min="0"
            :max="1"
            :step="0.1"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="constraintForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入约束描述"
          />
        </el-form-item>
        <el-form-item label="约束参数" prop="params">
          <div class="params-editor">
            <div
              v-for="(param, index) in constraintForm.params"
              :key="index"
              class="param-item"
            >
              <el-input
                v-model="param.key"
                placeholder="参数名"
                style="width: 150px"
              />
              <span>=</span>
              <el-input
                v-model="param.value"
                placeholder="参数值"
                style="width: 200px"
              />
              <el-button
                type="danger"
                size="small"
                circle
                @click="removeParam(index)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button type="primary" size="small" @click="addParam">
              <el-icon><Plus /></el-icon>
              添加参数
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showConstraintForm = false">取消</el-button>
        <el-button type="primary" @click="saveConstraint">保存</el-button>
      </template>
    </el-dialog>

    <!-- 对话框底部 -->
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSave">保存约束配置</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User, House, Grid, Clock, Reading, Setting, Plus, Search, Edit, Delete
} from '@element-plus/icons-vue'
import type { Constraint } from '@/api/scheduling'

interface Props {
  modelValue: boolean
  constraints: Constraint[]
  templates: Constraint[]
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'update', constraints: Constraint[]): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 响应式数据
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})
const activeCategory = ref('teacher')
const searchKeyword = ref('')
const showConstraintForm = ref(false)
const editingConstraint = ref<Constraint | null>(null)
const selectedConstraints = ref<Constraint[]>([])
const customConstraints = ref<Constraint[]>([])

// 表单数据
const constraintFormRef = ref()
const constraintForm = reactive({
  name: '',
  type: 'soft' as 'hard' | 'soft',
  category: 'teacher',
  weight: 1.0,
  description: '',
  params: [] as Array<{ key: string; value: string }>
})

const constraintRules = {
  name: [
    { required: true, message: '请输入约束名称', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择约束类型', trigger: 'change' }
  ],
  category: [
    { required: true, message: '请选择约束类别', trigger: 'change' }
  ],
  weight: [
    { required: true, message: '请输入权重', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入约束描述', trigger: 'blur' }
  ]
}

// 计算属性
const filteredTemplates = computed(() => {
  return props.templates
    .filter(template => template.category === activeCategory.value)
    .filter(template =>
      template.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      template.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
})

const filteredCustomConstraints = computed(() => {
  return customConstraints.value
    .filter(constraint => constraint.category === activeCategory.value)
    .filter(constraint =>
      constraint.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      constraint.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
})

// 方法
const getCategoryTitle = (category: string) => {
  const titles: Record<string, string> = {
    teacher: '教师相关约束',
    room: '教室相关约束',
    class: '班级相关约束',
    time: '时间相关约束',
    course: '课程相关约束',
    custom: '自定义约束'
  }
  return titles[category] || '约束'
}

const handleCategoryChange = () => {
  searchKeyword.value = ''
}

const isConstraintSelected = (constraintId: string) => {
  return selectedConstraints.value.some(c => c.id === constraintId)
}

const toggleTemplate = (template: Constraint) => {
  const index = selectedConstraints.value.findIndex(c => c.id === template.id)
  if (index === -1) {
    selectedConstraints.value.push({ ...template })
  } else {
    selectedConstraints.value.splice(index, 1)
  }
}

const editConstraint = (constraint: Constraint) => {
  editingConstraint.value = constraint
  constraintForm.name = constraint.name
  constraintForm.type = constraint.type
  constraintForm.category = constraint.category
  constraintForm.weight = constraint.weight
  constraintForm.description = constraint.description
  constraintForm.params = Object.entries(constraint.params).map(([key, value]) => ({
    key,
    value: String(value)
  }))
  showConstraintForm.value = true
}

const deleteConstraint = async (constraint: Constraint) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除约束"${constraint.name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const index = customConstraints.value.findIndex(c => c.id === constraint.id)
    if (index !== -1) {
      customConstraints.value.splice(index, 1)
    }

    // 同时从已选择中移除
    const selectedIndex = selectedConstraints.value.findIndex(c => c.id === constraint.id)
    if (selectedIndex !== -1) {
      selectedConstraints.value.splice(selectedIndex, 1)
    }

    ElMessage.success('约束删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除约束失败')
    }
  }
}

const updateConstraintWeight = (constraintId: string, weight: number) => {
  const constraint = customConstraints.value.find(c => c.id === constraintId)
  if (constraint) {
    constraint.weight = weight
  }
}

const updateConstraintType = (constraintId: string, type: 'hard' | 'soft') => {
  const constraint = customConstraints.value.find(c => c.id === constraintId)
  if (constraint) {
    constraint.type = type
  }
}

const updateConstraintEnabled = (constraintId: string, enabled: boolean) => {
  const constraint = customConstraints.value.find(c => c.id === constraintId)
  if (constraint) {
    constraint.enabled = enabled
  }
}

const removeSelectedConstraint = (constraintId: string) => {
  const index = selectedConstraints.value.findIndex(c => c.id === constraintId)
  if (index !== -1) {
    selectedConstraints.value.splice(index, 1)
  }
}

const clearSelectedConstraints = () => {
  selectedConstraints.value = []
}

const addParam = () => {
  constraintForm.params.push({ key: '', value: '' })
}

const removeParam = (index: number) => {
  constraintForm.params.splice(index, 1)
}

const saveConstraint = async () => {
  try {
    await constraintFormRef.value.validate()

    const params: Record<string, any> = {}
    constraintForm.params.forEach(param => {
      if (param.key && param.value) {
        params[param.key] = param.value
      }
    })

    const newConstraint: Constraint = {
      id: editingConstraint.value?.id || `custom_${Date.now()}`,
      name: constraintForm.name,
      type: constraintForm.type,
      category: constraintForm.category,
      description: constraintForm.description,
      weight: constraintForm.weight,
      enabled: true,
      params
    }

    if (editingConstraint.value) {
      // 更新现有约束
      const index = customConstraints.value.findIndex(c => c.id === editingConstraint.value!.id)
      if (index !== -1) {
        customConstraints.value[index] = newConstraint
      }
      ElMessage.success('约束更新成功')
    } else {
      // 创建新约束
      customConstraints.value.push(newConstraint)
      ElMessage.success('约束创建成功')
    }

    showConstraintForm.value = false
    resetConstraintForm()
  } catch (error) {
    ElMessage.error('保存约束失败')
  }
}

const resetConstraintForm = () => {
  constraintFormRef.value?.resetFields()
  constraintForm.params = []
  editingConstraint.value = null
}

const formatParamKey = (key: string) => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatParamValue = (value: any) => {
  if (typeof value === 'boolean') {
    return value ? '是' : '否'
  }
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  return String(value)
}

const handleClose = () => {
  visible.value = false
}

const handleSave = () => {
  // 合并模板约束和自定义约束
  const allConstraints = [
    ...selectedConstraints.value,
    ...customConstraints.value.filter(c => c.enabled)
  ]

  emit('update', allConstraints)
  ElMessage.success('约束配置保存成功')
  visible.value = false
}

// 监听对话框显示状态
watch(visible, (newValue) => {
  if (newValue) {
    // 初始化已选择的约束
    selectedConstraints.value = [...props.constraints]

    // 初始化自定义约束（从传入的约束中过滤出自定义的）
    customConstraints.value = props.constraints.filter(c => c.id.startsWith('custom_'))
  }
})
</script>

<style scoped>
.constraint-editor {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.constraint-categories {
  border-bottom: 1px solid #ebeef5;
}

.constraint-list {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.constraints-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.template-section,
.custom-section {
  margin-bottom: 20px;
}

.template-section h4,
.custom-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #606266;
}

.template-grid,
.custom-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 12px;
}

.template-card,
.constraint-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px;
  background-color: #fff;
  transition: all 0.3s ease;
  cursor: pointer;
}

.template-card:hover,
.constraint-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px 0 rgba(64, 158, 255, 0.1);
}

.template-card.selected,
.constraint-card.selected {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.template-info,
.constraint-info {
  flex: 1;
}

.template-name,
.constraint-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.template-desc,
.constraint-desc {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.template-type,
.constraint-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.card-content {
  margin-bottom: 12px;
}

.constraint-params {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.param-item {
  background-color: #f8f9fa;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.param-key {
  color: #606266;
  font-weight: 500;
}

.param-value {
  color: #303133;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.weight-control {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.type-control {
  display: flex;
  align-items: center;
}

.selected-constraints {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  background-color: #f8f9fa;
}

.selected-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: 500;
  color: #303133;
}

.selected-list {
  min-height: 40px;
}

.no-selection {
  color: #909399;
  font-size: 14px;
  text-align: center;
  padding: 12px;
}

.params-editor {
  border: 1px dashed #dcdfe6;
  border-radius: 6px;
  padding: 12px;
}

.params-editor .param-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.params-editor .param-item:last-child {
  margin-bottom: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-tabs__nav-wrap::after) {
  height: 1px;
}

:deep(.el-tabs__item) {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>