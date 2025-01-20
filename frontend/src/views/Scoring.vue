<template>
  <div class="scoring">
    <div class="report-title">{{ reportName }}</div>
    
    <div class="main-content">
      <!-- 文件列表和预览模块 -->
      <div class="content-module file-preview-module">
        <div class="module-left">
          <div class="module-title">文件列表</div>
          <div class="module-content">
            <el-tree
              v-if="fileTree.length > 0"
              :data="fileTree"
              :props="defaultProps"
              @node-click="handleFileClick"
            >
              <template #default="{ node, data }">
                <span class="custom-tree-node">
                  <el-icon v-if="data.type === 'directory'"><Folder /></el-icon>
                  <el-icon v-else-if="isImage(data.name)"><Picture /></el-icon>
                  <el-icon v-else><Document /></el-icon>
                  <span>{{ node.label }}</span>
                </span>
              </template>
            </el-tree>
            <div v-else class="empty-list">
              <el-empty description="加载中..." />
            </div>
          </div>
        </div>
        <div class="module-divider"></div>
        <div class="module-right">
          <div class="module-title">文件预览</div>
          <div class="module-content">
            <template v-if="selectedFile">
              <div class="preview-content">
                <img 
                  v-if="isImage(selectedFile.name)" 
                  :src="previewUrl" 
                  class="preview-image"
                  alt="预览图"
                >
                <pre v-else-if="isJSON(selectedFile.name)" class="preview-json" v-html="formatJSON(jsonContent)"></pre>
                <div v-else class="preview-empty">
                  暂不支持预览该类型文件
                </div>
              </div>
            </template>
            <div v-else class="preview-empty">
              <el-empty description="选择文件以预览" />
            </div>
          </div>
        </div>
      </div>

      <!-- 事件图谱和报告展示模块 -->
      <div class="content-module report-section">
        <div class="module-left">
          <div class="module-title">事件图谱</div>
          <div class="module-content graph-content">
            <iframe
              v-if="graphUrl"
              :src="graphUrl"
              class="graph-iframe"
              frameborder="0"
            ></iframe>
            <div v-else class="empty-content">
              <el-empty description="加载中..." />
            </div>
          </div>
        </div>
        <div class="module-divider"></div>
        <div class="module-right">
          <div class="module-title">火灾报告</div>
          <div class="module-content">
            <template v-if="report">
              <div class="report-content">
                <div v-for="(value, key) in report" :key="key" class="report-item">
                  <div class="report-title">{{ key }}</div>
                  <div class="report-value">{{ value }}</div>
                </div>
              </div>
            </template>
            <div v-else class="empty-content">
              <el-empty description="加载中..." />
            </div>
          </div>
        </div>
      </div>

      <!-- 评分模块 -->
      <div class="content-module score-module">
        <div class="scoring-section">
          <div class="scoring-container">
            <div class="rating-stars">
              <el-rate v-model="score" :texts="['极差', '较差', '一般', '不错', '很棒']" show-text />
            </div>
            <div class="comment-input">
              <el-input v-model="comment" placeholder="补充意见..." />
            </div>
            <div class="submit-button">
              <el-button type="primary" @click="submitScore">评分提交</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Folder, Document, Picture } from '@element-plus/icons-vue'
import { API_BASE_URL, CONFIG } from '../config'

const route = useRoute()
const router = useRouter()

// 案例信息
const caseId = ref(route.query.caseId)
const reportName = ref(route.query.caseName || '')

// 评分相关
const score = ref(null)
const comment = ref('')
const submitting = ref(false)

// 文件树相关
const fileTree = ref([])
const selectedFile = ref(null)
const report = ref(null)
const previewUrl = ref('')
const graphUrl = ref('')
const jsonContent = ref(null)

// 树形控件配置
const defaultProps = {
  children: 'children',
  label: 'name'
}

// 获取案例详细信息
const fetchCaseDetails = async () => {
  if (!caseId.value) return
  
  try {
    // 获取文件树结构
    const filesResponse = await fetch(`${API_BASE_URL}/api/cases/${caseId.value}/files`)
    if (!filesResponse.ok) {
      throw new Error(`HTTP error! status: ${filesResponse.status}`)
    }
    const filesData = await filesResponse.json()
    fileTree.value = filesData
    
    // 获取报告内容
    const reportResponse = await fetch(`${API_BASE_URL}/api/cases/${caseId.value}/file?path=report.json`)
    if (!reportResponse.ok) {
      throw new Error(`HTTP error! status: ${reportResponse.status}`)
    }
    const reportData = await reportResponse.json()
    
    // 重新组织报告数据的顺序
    const orderedReport = {}
    // 首先添加固定顺序的字段
    const orderedFields = ['背景信息', '火灾原因', '事故防范和整改措施意见']
    orderedFields.forEach(field => {
      if (reportData[field]) {
        orderedReport[field] = reportData[field]
      }
    })
    // 然后添加其他字段
    Object.keys(reportData).forEach(key => {
      if (!orderedFields.includes(key)) {
        orderedReport[key] = reportData[key]
      }
    })
    report.value = orderedReport
    
    // 设置图谱URL
    graphUrl.value = `${API_BASE_URL}/api/cases/${caseId.value}/file?path=graph.html`
    
    console.log('获取到的报告数据:', reportData)  // 添加日志
  } catch (error) {
    console.error('获取案例详情失败:', error)
    ElMessage.error('获取案例详情失败')
    report.value = null
    graphUrl.value = ''
  }
}

// 处理文件点击
const handleFileClick = async (data) => {
  if (data.type === 'directory') return
  
  selectedFile.value = data
  try {
    // 构建文件路径，只考虑父目录和当前文件名
    const filePath = data.parent?.name 
      ? `${data.parent.name}/${encodeURIComponent(data.name)}`
      : encodeURIComponent(data.name)
    
    console.log('请求文件路径:', filePath)
    const url = `${API_BASE_URL}/api/cases/${caseId.value}/file?path=${filePath}`
    console.log('完整URL:', url)
    
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      const jsonData = await response.json()
      jsonContent.value = jsonData
      console.log('JSON内容:', jsonData)
      previewUrl.value = ''
    } else if (isImage(data.name)) {
      if (previewUrl.value) {
        URL.revokeObjectURL(previewUrl.value)
      }
      previewUrl.value = url
      jsonContent.value = null
    } else {
      jsonContent.value = null
      previewUrl.value = ''
    }
  } catch (error) {
    console.error('获取文件预览失败:', error)
    ElMessage.error('获取文件预览失败')
    jsonContent.value = null
    previewUrl.value = ''
  }
}

// 格式化JSON并添加语法高亮
const formatJSON = (json) => {
  if (!json) return '';
  try {
    // 自定义格式化JSON
    const formatObject = (obj, indent = 0) => {
      if (obj === null) return '<span class="json-null">null</span>';
      
      switch (typeof obj) {
        case 'string':
          return `<span class="json-string">"${obj}"</span>`;
        case 'number':
          return `<span class="json-number">${obj}</span>`;
        case 'boolean':
          return `<span class="json-boolean">${obj}</span>`;
        case 'object':
          if (Array.isArray(obj)) {
            if (obj.length === 0) return '[]';
            const items = obj.map(item => formatObject(item, indent + 2)).join(', ');
            return `[${items}]`;
          } else {
            if (Object.keys(obj).length === 0) return '{}';
            const items = Object.entries(obj).map(([key, value]) => {
              const formattedValue = formatObject(value, indent + 2);
              return `\n${' '.repeat(indent + 2)}<span class="json-key">"${key}"</span>: ${formattedValue}`;
            }).join(',');
            return `{${items}\n${' '.repeat(indent)}}`;
          }
      }
    };

    return formatObject(json);
  } catch (e) {
    console.error('JSON格式化失败:', e);
    return String(json);
  }
};

// 判断文件类型
const isImage = (filename) => {
  const ext = filename.substring(filename.lastIndexOf('.')).toLowerCase()
  return CONFIG.supportedImageFormats.includes(ext)
}

const isJSON = (filename) => /\.json$/i.test(filename)

// 提交评分
const submitScore = async () => {
  // 检查是否已登录
  const token = localStorage.getItem('token');
  if (!token) {
    ElMessage.warning('请先登录');
    router.push('/login');
    return;
  }

  if (!score.value) {
    ElMessage.warning('请选择评分');
    return;
  }

  try {
    submitting.value = true;
    const response = await fetch(`${API_BASE_URL}/api/scoring`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        report_id: caseId.value,
        score: score.value * 20, // 将5星制转换为100分制
        comments: comment.value
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || '评分提交失败');
    }

    ElMessage.success('评分提交成功');
    
    // 通知父页面更新状态
    window.postMessage({
      type: 'scoreUpdate'
    }, window.location.origin);
    
    router.push('/expert');
  } catch (error) {
    console.error('评分提交失败:', error);
    ElMessage.error(error.message || '评分提交失败');
  } finally {
    submitting.value = false;
  }
};

// 获取已有评分
const fetchExistingScore = async () => {
  const token = localStorage.getItem('token');
  if (!token || !caseId.value) return;

  try {
    const response = await fetch(`${API_BASE_URL}/api/scoring/${caseId.value}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.ok) {
      const data = await response.json();
      if (data.score) {
        score.value = data.score / 20; // 将100分制转换为5星制
        comment.value = data.comments || '';
      }
    }
  } catch (error) {
    console.error('获取评分记录失败:', error);
  }
};

// 在组件挂载时获取评分记录
onMounted(() => {
  if (!route.query.caseId) {
    ElMessage.warning('未选择评分案例');
    router.push('/expert');
    return;
  }
  fetchCaseDetails();
  fetchExistingScore(); // 获取已有评分
});

// 监听路由变化
watch(() => route.query.caseId, (newId) => {
  if (newId && newId !== caseId.value) {
    caseId.value = newId
    reportName.value = route.query.caseName || ''
    fetchCaseDetails()
    fetchExistingScore() // 获取已有评分
  }
})

// 组件卸载时清理URL对象
onUnmounted(() => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
})
</script>

<style scoped>
.scoring {
  padding: 20px;
  height: 100vh;
  background-color: #F3F4F6;
  display: flex;
  flex-direction: column;
}

.report-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
  padding: 0 8px;
  text-align: center;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
}

.content-module {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.file-preview-module,
.report-section {
  display: flex;
  height: calc((100vh - 240px) * 0.6);
  overflow: hidden;
}

.module-left,
.module-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 400px;
}

.module-divider {
  width: 1px;
  margin: 16px 0;
  background-color: #e4e7ed;
}

.module-title {
  font-weight: 600;
  height: 32px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  font-size: 14px;
  color: #303133;
  flex-shrink: 0;
  line-height: 32px;
}

.module-content {
  padding: 16px;
  flex-grow: 1;
  background-color: white;
  position: relative;
  overflow-y: auto;
  overflow-x: hidden;
}

.preview-content {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.preview-json {
  margin: 0;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
  font-size: 14px;  /* 从 13px 调整到 14px */
  line-height: 1.5;  /* 相应调整行高从 1.4 到 1.5 */
  white-space: pre-wrap;
  word-wrap: break-word;
  color: #333;
  max-height: 100%;
  overflow-y: auto;
  box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.1);
  text-align: left;
}

.preview-json .json-key {
  color: #881391;
  font-weight: 500;
}

.preview-json .json-string {
  color: #268bd2;
}

.preview-json .json-number {
  color: #859900;
}

.preview-json .json-boolean {
  color: #b58900;
}

.preview-json .json-null {
  color: #dc322f;
}

.preview-empty {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  color: #6b7280;
  font-size: 14px;
}

.graph-content {
  padding: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.graph-iframe {
  width: calc(100% - 16px);
  height: calc(100% - 16px);
  border: none;
}

.report-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 8px;
}

.report-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.report-item .report-title {
  color: #374151;
  font-weight: 600;
  font-size: 14px;
  text-align: left;
  padding-left: 4px;
  margin-bottom: 0;
}

.report-item .report-value {
  color: #4B5563;
  line-height: 1.5;
  font-size: 13px;
  background-color: #f8f9fa;
  padding: 8px 12px;
  border-radius: 4px;
  text-align: left;
}

.custom-tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 评分模块样式 */
.scoring-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 16px;
  height: calc((100vh - 240px) * 0.12);
  display: flex;
  align-items: center;
}

.scoring-container {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
  padding: 0 16px;
}

.rating-stars {
  flex: none;
}

.rating-stars :deep(.el-rate__icon) {
  font-size: 24px;
  margin-right: 4px;
  color: #F7BA2A;  /* 设置星星颜色为黄色 */
}

.rating-stars :deep(.el-rate__text) {
  font-size: 14px;
}

.comment-input {
  flex: 1;
  margin: 0 16px;
}

.input-box {
  width: 100%;
}

.submit-button {
  flex: none;
  padding: 0 24px;
  height: 32px;
}

/* 自定义滚动条样式 */
:deep(*::-webkit-scrollbar) {
  width: 14px;
  height: 14px;
}

:deep(*::-webkit-scrollbar-thumb) {
  background-color: rgba(96, 98, 102, 0.8);  /* 更深的灰色 */
  border-radius: 7px;
  border: 2px solid transparent;
  background-clip: content-box;
  min-height: 80px;  /* 设置最小高度确保滚动条不会太短 */
}

:deep(*::-webkit-scrollbar-thumb:hover) {
  background-color: rgba(96, 98, 102, 0.9);
}

:deep(*::-webkit-scrollbar-track) {
  background-color: transparent;
}

:deep(*::-webkit-scrollbar-corner) {
  background-color: transparent;
}

:deep(*::-webkit-scrollbar-button:vertical:start) {
  width: 14px;
  height: 14px;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 14 14'%3E%3Cpath fill='rgba(96, 98, 102, 0.8)' d='M2 7l5-5 5 5z'/%3E%3C/svg%3E") center/10px no-repeat;
}

:deep(*::-webkit-scrollbar-button:vertical:end) {
  width: 14px;
  height: 14px;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 14 14'%3E%3Cpath fill='rgba(96, 98, 102, 0.8)' d='M2 5l5 5 5-5z'/%3E%3C/svg%3E") center/10px no-repeat;
}
</style>
