<template>
  <div class="main-layout">
    <div class="sidebar">
      <div class="logo">
        <img src="../assets/logo.png" alt="Fire-GPT" class="logo-img">
        <span class="logo-text">fire-gpt</span>
      </div>
      <el-menu
        router
        :default-active="route.path"
        class="menu"
        background-color="#F5F7FA"
        text-color="#333"
        active-text-color="#6366F1"
      >
        <el-menu-item index="/">
          <el-icon><Grid /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/report">
          <el-icon><Document /></el-icon>
          <span>报告展示</span>
        </el-menu-item>
        <el-menu-item index="/analysis">
          <el-icon><TrendCharts /></el-icon>
          <span>报告分析</span>
        </el-menu-item>
        <el-menu-item index="/expert">
          <el-icon><Star /></el-icon>
          <span>专家评分</span>
        </el-menu-item>
      </el-menu>
      <div class="decoration">
        <div class="decoration-background"></div>
        <img src="../assets/fire-bottle-new.png" alt="decoration" class="decoration-img">
      </div>
    </div>
    <div class="main-content">
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Grid, Document, TrendCharts, Star } from '@element-plus/icons-vue'
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<style scoped>
.main-layout {
  height: 100vh;
  width: 100vw;
  display: flex;
  overflow: hidden;
}

.sidebar {
  width: 20%;
  min-width: 220px;
  max-width: 280px;
  background-color: #F5F7FA;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #E5E7EB;
  overflow: hidden;
}

.logo {
  padding: 20px 0 20px 0;
  display: flex;
  align-items: center;
  margin-left: -8px;
}

.logo-img {
  width: 210px;
  height: 69px;
  object-fit: contain;
}

.logo-text {
  display: none;  
}

.menu {
  flex: 1;
  border: none;
}

:deep(.el-menu-item) {
  padding-left: 20px !important;
  height: 50px;
  line-height: 50px;
  margin: 4px 0;
}

:deep(.el-menu-item.is-active) {
  background-color: #EEF2FF !important;
}

:deep(.el-menu-item:hover) {
  background-color: #F3F4F6 !important;
}

:deep(.el-menu-item .el-icon) {
  font-size: 18px;
}

.decoration {
  padding: 24px;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  margin-top: auto;
  position: relative;
}

.decoration-background {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 160px;
  height: 80px;
  background-color: #D1E9FF;
  border-radius: 16px;
  z-index: 0;
}

.decoration-img {
  width: 200px;
  height: 200px;
  object-fit: contain;
  position: relative;
  z-index: 1;
}

.main-content {
  flex: 1;
  overflow: hidden;
  background-color: #F9FAFB;
  display: flex;
  justify-content: center;
}

.main-content :deep(> *) {
  width: 100%;
  max-width: 860px;
  margin: 0 auto;
  height: 100%;
  overflow: hidden;
}
</style>
