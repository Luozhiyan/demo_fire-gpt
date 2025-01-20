<template>
  <div class="case-show">
    <!-- 事件选择下拉框 -->
    <el-select v-model="selectedCase" placeholder="请选择事件" @change="handleCaseChange">
      <el-option
        v-for="item in cases"
        :key="item.id"
        :label="item.name"
        :value="item.id"
      />
    </el-select>

    <div class="content" v-if="selectedCase">
      <div class="left-panel">
        <!-- 文件列表 -->
        <el-tree
          :data="fileTree"
          :props="{ label: 'name' }"
          @node-click="handleNodeClick"
        />
      </div>
      
      <div class="right-panel">
        <!-- 文件预览 -->
        <div class="preview-panel" v-if="selectedFile">
          <!-- 图片预览 -->
          <img 
            v-if="selectedFile.type === 'image'"
            :src="previewUrl"
            class="preview-image"
          />
          <!-- JSON预览 -->
          <pre v-else-if="selectedFile.type === 'json'" class="preview-json">
            {{ JSON.stringify(jsonContent, null, 2) }}
          </pre>
          <!-- HTML预览 (知识图谱) -->
          <iframe
            v-else-if="selectedFile.type === 'html'"
            :src="previewUrl"
            class="preview-iframe"
          ></iframe>
        </div>

        <!-- 火灾报告 -->
        <div class="report-panel" v-if="report">
          <h2>火灾报告</h2>
          <div v-for="(value, key) in report" :key="key" class="report-item">
            <strong>{{ key }}:</strong>
            <span>{{ value }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const cases = ref([])
const selectedCase = ref('')
const fileTree = ref([])
const selectedFile = ref(null)
const jsonContent = ref(null)
const previewUrl = ref('')
const report = ref(null)

// 获取案例列表
const fetchCases = async () => {
  try {
    const response = await fetch('/api/cases/list')
    cases.value = await response.json()
  } catch (error) {
    console.error('获取案例列表失败:', error)
  }
}

// 获取案例文件结构
const fetchCaseFiles = async (caseId) => {
  try {
    const response = await fetch(`/api/cases/${caseId}/files`)
    fileTree.value = await response.json()
  } catch (error) {
    console.error('获取文件结构失败:', error)
  }
}

// 获取报告内容
const fetchReport = async (caseId) => {
  try {
    const response = await fetch(`/api/cases/${caseId}/file?path=report.json`)
    report.value = await response.json()
  } catch (error) {
    console.error('获取报告失败:', error)
  }
}

// 处理案例选择变更
const handleCaseChange = async (caseId) => {
  selectedFile.value = null
  jsonContent.value = null
  previewUrl.value = ''
  
  await Promise.all([
    fetchCaseFiles(caseId),
    fetchReport(caseId)
  ])
}

// 处理文件点击
const handleNodeClick = async (node) => {
  if (node.type === 'directory') return

  const path = getNodePath(node)
  selectedFile.value = {
    type: getFileType(node.name),
    path
  }

  try {
    const response = await fetch(`/api/cases/${selectedCase.value}/file?path=${path}`)
    
    if (selectedFile.value.type === 'json') {
      jsonContent.value = await response.json()
    } else {
      previewUrl.value = URL.createObjectURL(await response.blob())
    }
  } catch (error) {
    console.error('获取文件内容失败:', error)
  }
}

// 获取文件类型
const getFileType = (filename) => {
  const ext = filename.split('.').pop().toLowerCase()
  if (['jpg', 'jpeg', 'png', 'gif'].includes(ext)) return 'image'
  if (ext === 'json') return 'json'
  if (ext === 'html') return 'html'
  return 'unknown'
}

// 获取节点完整路径
const getNodePath = (node) => {
  const path = []
  let current = node
  while (current.parent) {
    path.unshift(current.name)
    current = current.parent
  }
  path.unshift(current.name)
  return path.join('/')
}

onMounted(fetchCases)
</script>

<style scoped>
.case-show {
  padding: 20px;
}

.content {
  display: flex;
  margin-top: 20px;
  gap: 20px;
  height: calc(100vh - 120px);
}

.left-panel {
  width: 300px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
}

.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.preview-panel {
  flex: 1;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
  overflow: auto;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
}

.preview-json {
  margin: 0;
  white-space: pre-wrap;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.report-panel {
  height: 300px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
  overflow: auto;
}

.report-item {
  margin-bottom: 10px;
}
</style>
