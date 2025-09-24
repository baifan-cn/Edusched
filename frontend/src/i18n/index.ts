import { createI18n } from 'vue-i18n'

const messages = {
  'zh-CN': {
    common: {
      add: '添加',
      edit: '编辑',
      delete: '删除',
      save: '保存',
      cancel: '取消',
      confirm: '确认',
      search: '搜索',
      reset: '重置',
      loading: '加载中...',
      noData: '暂无数据',
      operation: '操作',
      status: '状态',
      createTime: '创建时间',
      updateTime: '更新时间'
    },
    menu: {
      dashboard: '仪表板',
      schools: '学校管理',
      teachers: '教师管理',
      courses: '课程管理',
      timetables: '时间表管理',
      scheduling: '调度引擎'
    },
    dashboard: {
      title: '智能教育调度平台',
      subtitle: '为学校生成可行且优化的课程表',
      stats: {
        totalSchools: '总学校数',
        totalTeachers: '总教师数',
        totalCourses: '总课程数',
        totalTimetables: '总时间表数'
      }
    },
    schools: {
      title: '学校管理',
      addSchool: '添加学校',
      editSchool: '编辑学校',
      schoolName: '学校名称',
      schoolCode: '学校代码',
      address: '地址',
      phone: '电话',
      email: '邮箱',
      website: '网站',
      timezone: '时区',
      academicYear: '学年',
      semester: '学期'
    },
    teachers: {
      title: '教师管理',
      addTeacher: '添加教师',
      editTeacher: '编辑教师',
      employeeId: '工号',
      teacherName: '教师姓名',
      department: '部门',
      jobTitle: '职称',
      maxHoursPerDay: '每日最大课时',
      maxHoursPerWeek: '每周最大课时'
    },
    courses: {
      title: '课程管理',
      addCourse: '添加课程',
      editCourse: '编辑课程',
      courseName: '课程名称',
      courseCode: '课程代码',
      subject: '学科',
      credits: '学分',
      hoursPerWeek: '每周课时',
      totalHours: '总课时'
    },
    timetables: {
      title: '时间表管理',
      addTimetable: '添加时间表',
      editTimetable: '编辑时间表',
      timetableName: '时间表名称',
      calendar: '日历',
      status: '状态',
      publish: '发布',
      assignments: '分配'
    },
    scheduling: {
      title: '调度引擎',
      startScheduling: '启动调度',
      schedulingJobs: '调度任务',
      progress: '进度',
      cancel: '取消',
      validate: '验证约束'
    }
  },
  'en-US': {
    common: {
      add: 'Add',
      edit: 'Edit',
      delete: 'Delete',
      save: 'Save',
      cancel: 'Cancel',
      confirm: 'Confirm',
      search: 'Search',
      reset: 'Reset',
      loading: 'Loading...',
      noData: 'No Data',
      operation: 'Operation',
      status: 'Status',
      createTime: 'Create Time',
      updateTime: 'Update Time'
    },
    menu: {
      dashboard: 'Dashboard',
      schools: 'Schools',
      teachers: 'Teachers',
      courses: 'Courses',
      timetables: 'Timetables',
      scheduling: 'Scheduling'
    },
    dashboard: {
      title: 'Intelligent Education Scheduling Platform',
      subtitle: 'Generate feasible and optimized timetables for schools',
      stats: {
        totalSchools: 'Total Schools',
        totalTeachers: 'Total Teachers',
        totalCourses: 'Total Courses',
        totalTimetables: 'Total Timetables'
      }
    }
  }
}

const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'en-US',
  messages
})

export default i18n