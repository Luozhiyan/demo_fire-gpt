<template>
  <div class="page-container">
    <!-- 左侧信息区域 -->
    <div class="info-section">
      <div class="logo-container">
        <h1 class="logo-text">fire-gpt</h1>
      </div>
      <div class="info-content">
        <h2 class="info-title">以最佳的方式分析火灾的相关信息</h2>
        <p class="info-description">太棒了，我们为您创建了存储所有文档的完美场所。</p>
        <img :src="logoImage" alt="文件夹图标" class="folder-icon">
      </div>
    </div>

    <!-- 右侧登录表单 -->
    <div class="form-section">
      <div class="form-container">
        <h2>登录</h2>
        <el-form :model="loginForm" @submit.prevent="handleLogin">
          <el-form-item>
            <el-input 
              v-model="loginForm.username" 
              placeholder="用户名"
              prefix-icon="User"
            />
          </el-form-item>
          <el-form-item>
            <el-input 
              v-model="loginForm.email" 
              placeholder="电子邮件" 
              type="email"
              prefix-icon="Message"
            />
          </el-form-item>
          <el-form-item>
            <el-input 
              v-model="loginForm.password" 
              placeholder="密码" 
              type="password"
              prefix-icon="Lock"
            />
          </el-form-item>
          <div class="remember-forgot">
            <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
            <el-link type="primary" @click="forgotPassword">忘记密码？</el-link>
          </div>
          <el-button type="primary" native-type="submit" class="submit-button" :loading="loading">
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
          <div class="form-footer">
            <span>还没有账户？</span>
            <el-link type="primary" @click="goToRegister">立即注册</el-link>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Message, Lock } from '@element-plus/icons-vue'
import axios from 'axios'
import logoImage from '../assets/logo2.png'

const router = useRouter()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  email: '',
  password: '',
  remember: false
})

const validateEmail = (email: string) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }

  if (!validateEmail(loginForm.email)) {
    ElMessage.warning('请输入有效的电子邮件地址')
    return
  }

  loading.value = true
  try {
    const response = await axios.post('http://localhost:5000/api/auth/login', {
      username: loginForm.username,
      email: loginForm.email,
      password: loginForm.password
    })

    const { token, username } = response.data
    localStorage.setItem('token', token)
    localStorage.setItem('username', username)
    
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error: any) {
    const message = error.response?.data?.error || '登录失败'
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}

const forgotPassword = () => {
  ElMessage.info('忘记密码功能开发中')
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.page-container {
  display: flex;
  height: 100vh;
  background-color: white;
  overflow: hidden;
}

.info-section {
  flex: 1;
  background-color: #6366f1;
  color: white;
  padding: 40px;
  display: flex;
  flex-direction: column;
  border: none;
  box-shadow: none;
}

.logo-container {
  margin-bottom: 60px;
}

.logo-text {
  font-size: 36px;
  font-weight: 600;
  margin: 0;
}

.info-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.info-title {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 20px;
  line-height: 1.4;
}

.info-description {
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 40px;
}

.folder-icon {
  width: 280px;
  height: auto;
  margin-top: 40px;
}

.form-section {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
  height: 100vh;
  margin: 0;
  padding: 0;
}

.form-container {
  width: 400px;
  padding: 40px;
  background: transparent;
  border-radius: 0;
  box-shadow: none;
}

.form-container h2 {
  text-align: center;
  font-size: 24px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 32px;
}

.remember-forgot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0;
}

.submit-button {
  width: 100%;
  height: 40px;
  font-size: 16px;
  margin: 24px 0;
}

.form-footer {
  text-align: center;
  color: #6b7280;
}

:deep(.el-input__wrapper) {
  background-color: white;
  border: none;
  height: 40px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

:deep(.el-input__inner) {
  height: 40px;
}

:deep(.el-checkbox__label) {
  color: #6b7280;
}
</style>
