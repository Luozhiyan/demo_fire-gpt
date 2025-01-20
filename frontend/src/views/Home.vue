<template>
  <div class="home-container">
    <div class="header">
      <h1 class="title">Fire - gpt</h1>
      <el-button type="primary" class="login-button" @click="goToLogin">登录</el-button>
    </div>
    <div class="content">
      <!-- 这里可以添加首页的其他内容 -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Document, DataAnalysis, Star } from '@element-plus/icons-vue'

const router = useRouter()

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  padding: 0;  
  position: relative;  
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;  
}

.title {
  font-size: 2.5em;
  color: #409EFF;
  margin: 0;
}

.login-button {
  position: absolute;
  top: 12px;
  right: 5px;
  padding: 10px 20px;
  font-size: 16px;
}

.content {
  margin-top: 40px;
}
</style>
