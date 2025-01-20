import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import MainLayout from '../layout/MainLayout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('../views/Home.vue'),
        meta: {
          title: '首页'
        }
      },
      {
        path: 'report',
        name: 'report',
        component: () => import('../views/ReportDisplay.vue'),
        meta: {
          title: '报告展示'
        }
      },
      {
        path: 'analysis',
        name: 'analysis',
        component: () => import('../views/ReportAnalysis.vue'),
        meta: {
          title: '报告分析'
        }
      },
      {
        path: 'expert',
        name: 'expert',
        component: () => import('../views/ExpertScore.vue'),
        meta: {
          title: '专家评分'
        }
      },
      {
        path: 'scoring',
        name: 'scoring',
        component: () => import('../views/Scoring.vue'),
        meta: {
          title: '评分'
        }
      }
    ]
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: {
      title: '登录'
    }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/Register.vue'),
    meta: {
      title: '注册'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
