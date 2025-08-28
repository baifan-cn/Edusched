<template>
  <div class="dashboard">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>{{ $t('dashboard.title') }}</h1>
      <p>{{ $t('dashboard.subtitle') }}</p>
    </div>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6" v-for="stat in stats" :key="stat.key">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="40">
                <component :is="stat.icon" />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>时间表状态分布</span>
            </div>
          </template>
          <div class="chart-container">
            <div ref="pieChartRef" class="pie-chart"></div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>调度任务进度</span>
            </div>
          </template>
          <div class="chart-container">
            <div ref="barChartRef" class="bar-chart"></div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 最近活动 -->
    <el-row :gutter="20" class="activity-row">
      <el-col :span="24">
        <el-card class="activity-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>最近活动</span>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="activity in recentActivities"
              :key="activity.id"
              :timestamp="activity.time"
              :type="activity.type"
            >
              {{ activity.content }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import * as echarts from 'echarts'

const { t } = useI18n()

// 统计数据
const stats = ref([
  {
    key: 'schools',
    label: t('dashboard.stats.totalSchools'),
    value: 12,
    icon: 'School'
  },
  {
    key: 'teachers',
    label: t('dashboard.stats.totalTeachers'),
    value: 156,
    icon: 'User'
  },
  {
    key: 'courses',
    label: t('dashboard.stats.totalCourses'),
    value: 89,
    icon: 'Reading'
  },
  {
    key: 'timetables',
    label: t('dashboard.stats.totalTimetables'),
    value: 24,
    icon: 'Calendar'
  }
])

// 最近活动
const recentActivities = ref([
  {
    id: 1,
    content: '创建了新的时间表"2024年春季学期"',
    time: '2024-01-15 14:30',
    type: 'primary'
  },
  {
    id: 2,
    content: '调度任务"时间表优化"已完成',
    time: '2024-01-15 13:45',
    type: 'success'
  },
  {
    id: 3,
    content: '添加了新教师"张老师"',
    time: '2024-01-15 11:20',
    type: 'info'
  },
  {
    id: 4,
    content: '更新了课程"高等数学"信息',
    time: '2024-01-15 10:15',
    type: 'warning'
  }
])

// 图表引用
const pieChartRef = ref<HTMLElement>()
const barChartRef = ref<HTMLElement>()

// 初始化饼图
const initPieChart = () => {
  if (!pieChartRef.value) return
  
  const chart = echarts.init(pieChartRef.value)
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '时间表状态',
        type: 'pie',
        radius: '50%',
        data: [
          { value: 8, name: '草稿' },
          { value: 5, name: '运行中' },
          { value: 6, name: '可行' },
          { value: 3, name: '已优化' },
          { value: 2, name: '已发布' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  chart.setOption(option)
}

// 初始化柱状图
const initBarChart = () => {
  if (!barChartRef.value) return
  
  const chart = echarts.init(barChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: ['任务1', '任务2', '任务3', '任务4', '任务5']
    },
    yAxis: {
      type: 'value',
      max: 100
    },
    series: [
      {
        name: '进度',
        type: 'bar',
        data: [85, 92, 78, 95, 88],
        itemStyle: {
          color: '#409eff'
        }
      }
    ]
  }
  
  chart.setOption(option)
}

// 组件挂载后初始化图表
onMounted(async () => {
  await nextTick()
  initPieChart()
  initBarChart()
})
</script>

<style scoped lang="scss">
.dashboard {
  .page-header {
    margin-bottom: 24px;
    
    h1 {
      font-size: 28px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 8px 0;
    }
    
    p {
      font-size: 16px;
      color: #606266;
      margin: 0;
    }
  }
  
  .stats-row {
    margin-bottom: 24px;
    
    .stat-card {
      .stat-content {
        display: flex;
        align-items: center;
        
        .stat-icon {
          margin-right: 16px;
          color: #409eff;
        }
        
        .stat-info {
          .stat-value {
            font-size: 28px;
            font-weight: 600;
            color: #303133;
            line-height: 1;
          }
          
          .stat-label {
            font-size: 14px;
            color: #606266;
            margin-top: 4px;
          }
        }
      }
    }
  }
  
  .charts-row {
    margin-bottom: 24px;
    
    .chart-card {
      .chart-container {
        height: 300px;
        
        .pie-chart,
        .bar-chart {
          width: 100%;
          height: 100%;
        }
      }
    }
  }
  
  .activity-row {
    .activity-card {
      .card-header {
        font-weight: 600;
        color: #303133;
      }
    }
  }
}
</style>