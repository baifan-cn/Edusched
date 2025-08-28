import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/components/Layout/index.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/pages/Dashboard/index.vue'),
        meta: {
          title: '仪表板',
          icon: 'Odometer'
        }
      },
      {
        path: '/schools',
        name: 'Schools',
        component: () => import('@/pages/Schools/index.vue'),
        meta: {
          title: '学校管理',
          icon: 'School'
        }
      },
      {
        path: '/teachers',
        name: 'Teachers',
        component: () => import('@/pages/Teachers/index.vue'),
        meta: {
          title: '教师管理',
          icon: 'User'
        }
      },
      {
        path: '/courses',
        name: 'Courses',
        component: () => import('@/pages/Courses/index.vue'),
        meta: {
          title: '课程管理',
          icon: 'Reading'
        }
      },
      {
        path: '/timetables',
        name: 'Timetables',
        component: () => import('@/pages/Timetables/index.vue'),
        meta: {
          title: '时间表管理',
          icon: 'Calendar'
        }
      },
      {
        path: '/scheduling',
        name: 'Scheduling',
        component: () => import('@/pages/Scheduling/index.vue'),
        meta: {
          title: '调度引擎',
          icon: 'Cpu'
        }
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login/index.vue'),
    meta: {
      title: '登录',
      hidden: true
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/pages/404/index.vue'),
    meta: {
      title: '404',
      hidden: true
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - Edusched` : 'Edusched'
  
  // TODO: 实现认证逻辑
  next()
})

export default router