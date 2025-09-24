<template>
  <div class="common-table">
    <!-- 搜索和工具栏 -->
    <div v-if="showToolbar" class="table-toolbar">
      <div class="toolbar-left">
        <slot name="toolbar-left">
          <el-input
            v-model="searchQuery"
            placeholder="搜索..."
            :style="{ width: '300px' }"
            clearable
            @clear="handleSearchClear"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </slot>
      </div>

      <div class="toolbar-right">
        <slot name="toolbar-right">
          <el-button type="primary" @click="$emit('add')">
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
          <el-button
            type="danger"
            :disabled="!selectedRows.length"
            @click="$emit('bulk-delete', selectedRows)"
          >
            <el-icon><Delete /></el-icon>
            批量删除 ({{ selectedRows.length }})
          </el-button>
          <el-button @click="$emit('refresh')">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </slot>
      </div>
    </div>

    <!-- 表格主体 -->
    <el-table
      v-loading="loading"
      :data="data"
      :stripe="stripe"
      :border="border"
      :height="height"
      :max-height="maxHeight"
      :row-key="rowKey"
      @selection-change="handleSelectionChange"
      @sort-change="handleSortChange"
    >
      <!-- 选择列 -->
      <el-table-column
        v-if="showSelection"
        type="selection"
        width="55"
        align="center"
      />

      <!-- 序号列 -->
      <el-table-column
        v-if="showIndex"
        type="index"
        width="60"
        label="序号"
        align="center"
        :index="indexMethod"
      />

      <!-- 动态列 -->
      <el-table-column
        v-for="column in columns"
        :key="column.prop"
        :prop="column.prop"
        :label="column.label"
        :width="column.width"
        :min-width="column.minWidth"
        :sortable="column.sortable"
        :align="column.align || 'left'"
        :show-overflow-tooltip="column.showOverflowTooltip !== false"
      >
        <template #default="scope">
          <slot :name="column.prop" :row="scope.row" :column="column" :index="scope.$index">
            <!-- 状态列 -->
            <el-tag
              v-if="column.prop === 'status'"
              :type="getStatusType(scope.row[column.prop])"
            >
              {{ getStatusText(scope.row[column.prop]) }}
            </el-tag>

            <!-- 时间列 -->
            <span v-else-if="column.type === 'datetime'">
              {{ formatDateTime(scope.row[column.prop]) }}
            </span>

            <!-- 日期列 -->
            <span v-else-if="column.type === 'date'">
              {{ formatDate(scope.row[column.prop]) }}
            </span>

            <!-- 图片列 -->
            <el-image
              v-else-if="column.type === 'image'"
              :src="scope.row[column.prop]"
              :preview-src-list="[scope.row[column.prop]]"
              :style="{ width: '40px', height: '40px', borderRadius: '4px' }"
              fit="cover"
            />

            <!-- 操作列 -->
            <div v-else-if="column.prop === 'actions'">
              <el-button-group size="small">
                <el-button
                  type="primary"
                  link
                  @click="$emit('edit', scope.row)"
                >
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button
                  type="danger"
                  link
                  @click="$emit('delete', scope.row)"
                >
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
                <slot name="row-actions" :row="scope.row" />
              </el-button-group>
            </div>

            <!-- 默认显示 -->
            <span v-else>
              {{ scope.row[column.prop] }}
            </span>
          </slot>
        </template>
      </el-table-column>

      <!-- 空状态 -->
      <template #empty>
        <el-empty description="暂无数据" />
      </template>
    </el-table>

    <!-- 分页 -->
    <div v-if="showPagination" class="table-pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search, Plus, Delete, Refresh, Edit } from '@element-plus/icons-vue'
import { formatDate, formatDateTime } from '@/utils/date'

// 组件属性
interface Props {
  data: any[]
  loading?: boolean
  columns: Array<{
    prop: string
    label: string
    width?: number | string
    minWidth?: number | string
    sortable?: boolean | 'custom'
    align?: 'left' | 'center' | 'right'
    showOverflowTooltip?: boolean
    type?: 'text' | 'datetime' | 'date' | 'image' | 'status'
  }>
  stripe?: boolean
  border?: boolean
  height?: string | number
  maxHeight?: string | number
  rowKey?: string | ((row: any) => string)
  showSelection?: boolean
  showIndex?: boolean
  showPagination?: boolean
  showToolbar?: boolean
  total?: number
  currentPage?: number
  pageSize?: number
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  stripe: true,
  border: true,
  showSelection: true,
  showIndex: true,
  showPagination: true,
  showToolbar: true,
  data: () => [],
  columns: () => [],
  total: 0,
  currentPage: 1,
  pageSize: 20
})

// 组件事件
const emit = defineEmits<{
  'update:currentPage': [value: number]
  'update:pageSize': [value: number]
  'selection-change': [selection: any[]]
  'sort-change': [sort: any]
  'search': [query: string]
  'refresh': []
  'add': []
  'edit': [row: any]
  'delete': [row: any]
  'bulk-delete': [rows: any[]]
}>()

// 响应式数据
const searchQuery = ref('')
const selectedRows = ref<any[]>([])

// 计算属性
const internalCurrentPage = computed({
  get: () => props.currentPage,
  set: (value) => emit('update:currentPage', value)
})

const internalPageSize = computed({
  get: () => props.pageSize,
  set: (value) => emit('update:pageSize', value)
})

// 方法
const handleSelectionChange = (selection: any[]) => {
  selectedRows.value = selection
  emit('selection-change', selection)
}

const handleSortChange = (sort: any) => {
  emit('sort-change', sort)
}

const handleSizeChange = (size: number) => {
  internalPageSize.value = size
}

const handleCurrentChange = (page: number) => {
  internalCurrentPage.value = page
}

const handleSearch = () => {
  emit('search', searchQuery.value)
}

const handleSearchClear = () => {
  searchQuery.value = ''
  emit('search', '')
}

const indexMethod = (index: number) => {
  return (props.currentPage - 1) * props.pageSize + index + 1
}

const getStatusType = (status: boolean | string) => {
  if (typeof status === 'boolean') {
    return status ? 'success' : 'danger'
  }
  switch (status) {
    case 'active':
    case 'enabled':
    case 'published':
      return 'success'
    case 'inactive':
    case 'disabled':
    case 'draft':
      return 'warning'
    case 'pending':
      return 'info'
    case 'failed':
    case 'error':
      return 'danger'
    default:
      return ''
  }
}

const getStatusText = (status: boolean | string) => {
  if (typeof status === 'boolean') {
    return status ? '启用' : '禁用'
  }
  switch (status) {
    case 'active':
    case 'enabled':
      return '启用'
    case 'inactive':
    case 'disabled':
      return '禁用'
    case 'published':
      return '已发布'
    case 'draft':
      return '草稿'
    case 'pending':
      return '待处理'
    case 'failed':
      return '失败'
    case 'error':
      return '错误'
    default:
      return status
  }
}

// 暴露方法供父组件调用
defineExpose({
  searchQuery,
  selectedRows,
  clearSelection: () => {
    selectedRows.value = []
  },
  resetSearch: () => {
    searchQuery.value = ''
    handleSearchClear()
  }
})
</script>

<style scoped>
.common-table {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.table-pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-table) {
  --el-table-border-color: #ebeef5;
  --el-table-header-bg-color: #f5f7fa;
}

:deep(.el-table th) {
  font-weight: 600;
}

:deep(.el-table .cell) {
  padding: 12px 0;
}
</style>