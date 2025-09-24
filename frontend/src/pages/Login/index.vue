<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-form">
        <div class="login-header">
          <h1>Edusched</h1>
          <p>智能教育调度平台</p>
        </div>

        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          label-position="top"
          size="large"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              :prefix-icon="User"
            />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-form-item>
            <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
            <el-link type="primary" class="forget-pwd">忘记密码？</el-link>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              style="width: 100%"
              :loading="loading"
              @click="handleLogin"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>

        <div class="login-footer">
          <p>© 2024 Edusched. All rights reserved.</p>
        </div>
      </div>

      <div class="login-illustration">
        <div class="illustration-content">
          <h2>智能排课</h2>
          <h3>高效 · 智能 · 便捷</h3>
          <p>基于先进算法的智能教育调度解决方案</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  remember: false
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    await loginFormRef.value.validate()
    loading.value = true

    // TODO: 实现登录逻辑
    // 模拟登录成功
    setTimeout(() => {
      ElMessage.success('登录成功')
      router.push('/')
      loading.value = false
    }, 1000)

  } catch (error) {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-container {
  width: 100%;
  max-width: 1200px;
  height: 600px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  display: flex;
  overflow: hidden;
}

.login-form {
  flex: 1;
  padding: 60px;
  display: flex;
  flex-direction: column;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h1 {
  font-size: 32px;
  color: #333;
  margin: 0 0 10px 0;
  font-weight: bold;
}

.login-header p {
  color: #666;
  margin: 0;
  font-size: 16px;
}

.login-illustration {
  flex: 1;
  background: linear-gradient(135deg, #409EFF 0%, #67C23A 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.illustration-content {
  text-align: center;
  color: white;
  z-index: 2;
}

.illustration-content h2 {
  font-size: 48px;
  margin: 0 0 20px 0;
  font-weight: bold;
}

.illustration-content h3 {
  font-size: 24px;
  margin: 0 0 20px 0;
  font-weight: 300;
}

.illustration-content p {
  font-size: 16px;
  opacity: 0.9;
  line-height: 1.6;
}

.forget-pwd {
  float: right;
}

.login-footer {
  margin-top: auto;
  text-align: center;
  color: #999;
  font-size: 14px;
}

/* 背景装饰 */
.login-illustration::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="2" fill="rgba(255,255,255,0.1)"/></svg>');
  background-size: 50px 50px;
  z-index: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    max-width: 400px;
    height: auto;
    flex-direction: column;
  }

  .login-form {
    padding: 40px 30px;
  }

  .login-illustration {
    display: none;
  }
}
</style>