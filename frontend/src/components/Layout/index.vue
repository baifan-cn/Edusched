<template>
  <div class="app-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '200px'" class="sidebar">
      <div class="logo">
        <img src="@/assets/logo.svg" alt="Edusched" v-if="!isCollapse" />
        <span v-if="!isCollapse">Edusched</span>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :unique-opened="true"
        router
        class="sidebar-menu"
      >
        <el-menu-item
          v-for="route in menuRoutes"
          :key="route.path"
          :index="route.path"
          :title="route.meta?.title"
        >
          <el-icon>
            <component :is="route.meta?.icon" />
          </el-icon>
          <span>{{ route.meta?.title }}</span>
        </el-menu-item>
      </el-menu>
      
      <div class="sidebar-footer">
        <el-button
          type="text"
          @click="toggleCollapse"
          class="collapse-btn"
        >
          <el-icon>
            <component :is="isCollapse ? 'Expand' : 'Fold'" />
          </el-icon>
        </el-button>
      </div>
    </el-aside>
    
    <!-- 主内容区域 -->
    <el-container class="main-container">
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRoute?.meta?.title">
              {{ currentRoute.meta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-avatar size="small" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
              <span class="username">管理员</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人设置</el-dropdown-item>
                <el-dropdown-item>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 主内容 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const route = useRoute()
const router = useRouter()

// 侧边栏折叠状态
const isCollapse = ref(false)

// 当前路由
const currentRoute = computed(() => route)

// 激活的菜单项
const activeMenu = computed(() => route.path)

// 菜单路由
const menuRoutes = computed(() => {
  const mainRoute = router.getRoutes().find(r => r.name === 'Layout')
  return mainRoute?.children?.filter(r => !r.meta?.hidden) || []
})

// 切换侧边栏折叠状态
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}
</script>

<style scoped lang="scss">
.app-layout {
  height: 100vh;
  display: flex;
}

.sidebar {
  background-color: #304156;
  transition: width 0.3s;
  
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 18px;
    font-weight: bold;
    border-bottom: 1px solid #435266;
    
    img {
      height: 32px;
      margin-right: 8px;
    }
  }
  
  .sidebar-menu {
    border: none;
    background-color: transparent;
    
    :deep(.el-menu-item) {
      color: #bfcbd9;
      
      &:hover {
        background-color: #263445;
        color: #fff;
      }
      
      &.is-active {
        background-color: #409eff;
        color: #fff;
      }
    }
  }
  
  .sidebar-footer {
    position: absolute;
    bottom: 0;
    width: 100%;
    padding: 10px;
    border-top: 1px solid #435266;
    
    .collapse-btn {
      width: 100%;
      color: #bfcbd9;
      
      &:hover {
        color: #fff;
      }
    }
  }
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  
  .header-left {
    .el-breadcrumb {
      line-height: 60px;
    }
  }
  
  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      cursor: pointer;
      
      .username {
        margin-left: 8px;
        color: #606266;
      }
    }
  }
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>