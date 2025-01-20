<template>
  <div class="expert-score">
    <div class="content-card">
      <el-table
        :data="reports.slice((currentPage - 1) * pageSize, currentPage * pageSize)"
        style="width: 100%"
        :header-cell-style="{
          backgroundColor: '#F5F7FA',
          color: '#374151',
          fontWeight: '600',
          height: '32px',
          padding: '4px 12px'
        }"
        :cell-style="{
          padding: '8px 12px'
        }"
      >
        <el-table-column prop="name" label="报告名称" min-width="200">
          <template #default="{ row }">
            <span class="report-name">{{ row.name }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="120" align="center">
          <template #default="{ row }">
            <div class="status-dot" :class="row.status === '已评分' ? 'scored' : 'unscored'"></div>
            <span class="status-text">{{ row.status }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="score" label="分数" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.score">{{ row.score }}/100</span>
            <span v-else>无</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="createTime" label="创建时间" width="180" align="center">
          <template #default="{ row }">
            {{ formatDate(row.createTime) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150" align="center">
          <template #default="{ row }">
            <div class="operation-links">
              <el-link 
                type="primary" 
                :class="{ disabled: row.status === '已评分' }"
                @click="handleScore(row)"
              >
                评分
              </el-link>
              <el-divider direction="vertical" />
              <el-dropdown trigger="click" @command="handleCommand($event, row)">
                <el-link type="primary">更多</el-link>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="view">查看报告</el-dropdown-item>
                    <el-dropdown-item command="rescore">重新评分</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          background
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { More } from '@element-plus/icons-vue'
import { API_BASE_URL, CONFIG } from '../config'

interface Report {
  id: number
  name: string
  status: string
  score: number | null
  createTime: string
}

interface ReportScore {
  reportId: number
  score: number
  status: string
}

const router = useRouter()
const route = useRoute()
const currentPage = ref(1)
const pageSize = ref(CONFIG.defaultPageSize)
const total = ref(0)

// 初始报告数据从文件系统获取
const reports = ref([])

// 从后端获取评分状态
const loadScoreStates = async () => {
  try {
    const token = localStorage.getItem('token');
    if (!token) return;

    const response = await fetch(`${API_BASE_URL}/api/user_scores`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error('获取评分状态失败');
    }

    const userScores = await response.json();
    console.log('获取到用户评分:', userScores);

    // 更新报告列表的评分状态
    reports.value = reports.value.map(report => {
      const savedScore = userScores.find(s => s.report_id === report.id);
      if (savedScore) {
        return {
          ...report,
          status: '已评分',
          score: savedScore.score
        };
      }
      return {
        ...report,
        status: '未评分',
        score: null
      };
    });
  } catch (error) {
    console.error('获取评分状态失败:', error);
    ElMessage.error('获取评分状态失败');
  }
};

// 监听来自评分页面的消息
const handleMessage = (event: MessageEvent) => {
  if (event.origin !== window.location.origin) {
    return;
  }

  console.log('收到消息:', event.data);

  const data = event.data;
  if (data && data.type === 'scoreUpdate') {
    // 重新加载评分状态
    loadScoreStates();
  }
};

// 获取案例列表
const fetchCases = async () => {
  try {
    console.log('开始获取案例列表...');
    const response = await fetch(`${API_BASE_URL}/api/cases/list`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('获取到的数据:', data);
    
    reports.value = data.map(item => ({
      id: item.id,
      name: item.name,
      status: '未评分',
      score: null,
      createTime: item.createTime || new Date().toISOString()
    }));
    
    total.value = reports.value.length;
    
    // 加载评分状态
    await loadScoreStates();
  } catch (error) {
    console.error('获取案例列表失败:', error);
    ElMessage.error('获取案例列表失败');
  }
};

// 组件挂载时获取案例列表
onMounted(() => {
  fetchCases();
  window.addEventListener('message', handleMessage);
});

// 组件卸载前移除消息监听
onBeforeUnmount(() => {
  window.removeEventListener('message', handleMessage);
});

// 格式化日期
const formatDate = (dateStr) => {
  try {
    return new Date(dateStr).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (error) {
    console.error('日期格式化失败:', error);
    return dateStr;
  }
};

const handleScore = (row: Report) => {
  if (row.status === '已评分') return;
  
  console.log('跳转到评分页面:', row);
  router.push({
    name: 'scoring',  // 使用路由名称而不是路径
    query: { 
      caseId: row.id,
      caseName: row.name
    }
  });
};

const handleCommand = (command: string, row: Report) => {
  switch (command) {
    case 'view':
      router.push({
        path: '/report',
        query: { caseId: row.id }
      });
      break;
    case 'rescore':
      router.push({
        name: 'scoring',
        query: { 
          caseId: row.id,
          caseName: row.name,
          rescore: true
        }
      });
      break;
  }
};

const handleCurrentChange = (val: number) => {
  currentPage.value = val;
};
</script>

<style scoped>
.expert-score {
  padding: 32px;
  height: 100%;
  display: flex;
  background-color: #F3F4F6;
  box-sizing: border-box;
  justify-content: center;
  overflow: hidden;
}

.content-card {
  flex: 1;
  max-width: calc(1200px * 0.75);  
  background: white;
  border-radius: 8px;
  padding: 16px 24px 48px;
  display: flex;
  flex-direction: column;
  position: relative;
  min-height: 0;
  max-height: 100%;
  overflow: hidden;
}

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}

.status-dot.scored {
  background-color: #10B981;
}

.status-dot.unscored {
  background-color: #EF4444;
}

.status-text {
  color: #374151;
}

.operation-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.operation-links .disabled {
  color: #9CA3AF;
  cursor: not-allowed;
}

.pagination {
  position: absolute;
  bottom: 24px;
  right: 24px;
}

:deep(.el-table) {
  --el-table-border-color: #E5E7EB;
  --el-table-header-bg-color: #F5F7FA;
  --el-table-row-hover-bg-color: #F9FAFB;
  flex: 1;
  overflow: hidden;
  height: 100%;
}

:deep(.el-table__inner-wrapper) {
  height: 100%;
  border-bottom: none;
}

:deep(.el-table__body-wrapper) {
  overflow-y: auto;
  height: calc(100% - 40px); /* 减去表头高度 */
}

:deep(.el-pagination.is-background .el-pager li:not(.disabled).active) {
  background-color: #3B82F6;
}

:deep(.el-pagination) {
  --el-pagination-border-radius: 0;
  --el-pagination-button-height: 32px;
  --el-pagination-button-width: 32px;
}

:deep(.el-pagination .el-pager li),
:deep(.el-pagination button) {
  border-top: none !important;
  box-shadow: none !important;
}

:deep(.el-table--fit .el-table__inner-wrapper:before) {
  display: none;
}

:deep(.el-scrollbar__wrap) {
  overflow-x: hidden !important;
}

:deep(.el-scrollbar__bar.is-horizontal) {
  display: none !important;
}

:deep(.el-table__body-wrapper)::-webkit-scrollbar {
  display: none !important;
}

:deep(.el-table__body-wrapper) {
  overflow-x: hidden !important;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none;  /* IE and Edge */
}
</style>
