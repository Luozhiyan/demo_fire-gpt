<template>
  <div class="report-display">
    <div class="module-container">
      <div class="event-select-module">
        <div class="select-section">
          <el-select
            v-model="selectedCase"
            placeholder="请选择事件"
            class="event-select"
            size="large"
            @change="handleCaseChange"
          >
            <el-option
              v-for="item in cases"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </div>
      </div>
      <div class="module-section">
        <div class="module-left">
          <div class="module-title">文件列表</div>
          <div class="module-content">
            <el-tree
              v-if="fileTree.length > 0"
              :data="fileTree"
              :props="defaultProps"
              @node-click="handleNodeClick"
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
              <el-empty description="请选择事件" />
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
      <div class="module-section">
        <div class="module-left">
          <div class="module-title">事件图谱</div>
          <div class="module-content graph-content">
            <iframe
              v-if="selectedCase"
              :src="graphUrl"
              class="graph-iframe"
              frameborder="0"
            ></iframe>
            <div v-else class="empty-content">
              <el-empty description="请选择事件" />
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
              <el-empty description="请选择事件" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Folder, Document, Picture } from '@element-plus/icons-vue'
import { API_BASE_URL, CONFIG } from '../config'

// 案例相关
const cases = ref([])
const selectedCase = ref('')
const fileTree = ref([])
const selectedFile = ref(null)
const jsonContent = ref(null)
const previewUrl = ref('')
const report = ref(null)
const graphUrl = ref('')

// 判断文件类型
const isImage = (filename) => {
  const ext = filename.substring(filename.lastIndexOf('.')).toLowerCase()
  return CONFIG.supportedImageFormats.includes(ext)
}

const isJSON = (filename) => /\.json$/i.test(filename)

const defaultProps = {
  children: 'children',
  label: 'name'
}

// 获取案例列表
const fetchCases = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/cases/list`)
    const data = await response.json()
    cases.value = data
    console.log('获取到的案例列表:', data)
    
    // 如果有案例，自动选择第一个
    if (data && data.length > 0) {
      selectedCase.value = data[0].id
      handleCaseChange(data[0].id)
    }
  } catch (error) {
    console.error('获取案例列表失败:', error)
    ElMessage.error('获取案例列表失败')
  }
}

// 处理案例选择变更
const handleCaseChange = async (caseId) => {
  if (!caseId) return
  
  selectedFile.value = null
  jsonContent.value = null
  previewUrl.value = ''
  
  try {
    // 获取文件树结构
    const response = await fetch(`${API_BASE_URL}/api/cases/${caseId}/files`)
    const data = await response.json()
    fileTree.value = data
    
    // 获取报告内容
    const reportResponse = await fetch(`${API_BASE_URL}/api/cases/${caseId}/file?path=report.json`)
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
    graphUrl.value = `${API_BASE_URL}/api/cases/${caseId}/file?path=graph.html`
  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error('获取数据失败')
  }
}

// 处理文件点击
const handleNodeClick = async (data) => {
  if (data.type === 'directory') return
  
  selectedFile.value = data
  // 对文件名进行编码，保持目录名不变
  const filePath = data.parent?.name 
    ? `${data.parent.name}/${encodeURIComponent(data.name)}`
    : encodeURIComponent(data.name)
  
  console.log('File path:', filePath)  // 添加日志
  
  try {
    const url = `${API_BASE_URL}/api/cases/${selectedCase.value}/file?path=${filePath}`
    console.log('Request URL:', url)  // 添加日志
    
    if (isImage(data.name)) {
      previewUrl.value = url
      jsonContent.value = null
    } else if (isJSON(data.name)) {
      const response = await fetch(url)
      if (!response.ok) {
        console.error('HTTP Error:', response.status, response.statusText)
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const json = await response.json()
      jsonContent.value = json
      previewUrl.value = ''
    } else {
      jsonContent.value = null
      previewUrl.value = ''
    }
  } catch (error) {
    console.error('获取文件预览失败:', error)
    ElMessage.error('获取文件预览失败')
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
    return String(json);
  }
};

// 组件挂载时获取案例列表
onMounted(fetchCases)
</script>

<style scoped>
.report-display {
  padding: 24px;
  height: 100vh;
  background-color: #F3F4F6;
  display: flex;
  flex-direction: column;
}

.module-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.event-select-module {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 16px;
}

.select-section {
  display: flex;
  gap: 16px;
  align-items: center;
}

.event-select {
  width: 300px;
}

.module-section {
  display: flex;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  height: calc((100vh - 200px) / 3 * 1.7);
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
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
  font-size: 14px;
  line-height: 1.5;
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

.custom-tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
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
  gap: 8px;
}

.report-title {
  color: #374151;
  font-weight: 600;
  font-size: 14px;
  text-align: left;
  padding-left: 4px;
}

.report-value {
  color: #4B5563;
  line-height: 1.5;
  font-size: 13px;
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  text-align: left;
}

.empty-list,
.empty-content,
.preview-empty {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  background-color: #f5f7fa;
}
</style>
