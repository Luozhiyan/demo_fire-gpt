<template>
  <div class="report-analysis">
    <div class="upload-generate-section">
      <div class="upload-area">
        <div class="upload-label-container">
          <span class="upload-label">上传附件：</span>
          <div class="upload-container">
            <el-upload
              ref="uploadRef"
              class="file-uploader"
              :action="`${API_URL}/upload`"
              :auto-upload="true"
              :show-file-list="false"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
              :before-upload="beforeUpload"
              :multiple="true"
              :limit="10"
              accept=".png,.jpg,.gif,.jpeg,.pdf,.doc,.docx"
              name="file"
              :headers="{}"
            >
              <el-button 
                type="primary" 
                :icon="Plus"
              >
                上传附件
              </el-button>
              <div class="upload-format-info">
                支持.png .jpg .gif .jpeg .pdf .doc，不超过 5MB
              </div>
            </el-upload>
          </div>
        </div>
        <el-button type="primary" @click="generateReport" :loading="generating">
          报告生成
        </el-button>
      </div>
    </div>

    <div class="content-modules">
      <div class="file-preview-module">
        <div class="module-left">
          <div class="module-title">文件列表</div>
          <div class="module-content">
            <div class="file-list-grid">
              <template v-if="fileList.length > 0">
                <div 
                  v-for="file in fileList" 
                  :key="file.uid" 
                  class="file-card"
                  :class="{ 'selected': selectedFile?.uid === file.uid }"
                >
                  <div class="file-info" @click="handlePreview(file)">
                    <div class="file-name">{{ getDisplayFileName(file.original_name) }}</div>
                    <div class="file-meta">{{ formatFileSize(file.size) }} - {{ file.upload_time }}</div>
                  </div>
                  <el-button
                    type="danger"
                    size="small"
                    link
                    class="delete-btn"
                    @click="handleDeleteFile(file)"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </template>
              <div v-else class="empty-tip">
                暂无文件，请上传
              </div>
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
                  v-if="isImage(selectedFile)" 
                  :src="selectedFile.url" 
                  class="preview-image"
                  alt="预览图片"
                >
                <div v-else-if="isPDF(selectedFile)" class="preview-pdf">
                  <iframe :src="selectedFile.url" width="100%" height="100%"></iframe>
                </div>
                <div v-else class="preview-unsupported">
                  该文件类型暂不支持预览
                </div>
              </div>
            </template>
            <div v-else class="empty-tip">
              请从左侧选择文件进行预览
            </div>
          </div>
        </div>
      </div>

      <div class="report-graph-module">
        <div class="module-left">
          <div class="module-title">事件图谱</div>
          <div class="module-content">
            <template v-if="reportGenerated">
              <img src="../assets/graph.png" alt="事件图谱" class="graph-img">
            </template>
            <div v-else class="empty-graph">
              <el-empty description="报告生成后显示事件图谱" />
            </div>
          </div>
        </div>
        <div class="module-divider"></div>
        <div class="module-right">
          <div class="module-title">火灾报告</div>
          <div class="module-content">
            <template v-if="reportGenerated">
              <h3>一、火灾基本信息</h3>
              <ul>
                <li>火灾发生时间: {{ basicInfo.time }}</li>
                <li>火灾发生地点: {{ basicInfo.location }}</li>
                <li>火灾类型: {{ basicInfo.type }}</li>
                <li>火灾报警时间: {{ basicInfo.alarmTime }}</li>
                <li>消防队到达时间: {{ basicInfo.arrivalTime }}</li>
                <li>火灾扑灭时间: {{ basicInfo.extinguishTime }}</li>
              </ul>
              <h3>二、火灾原因</h3>
              <ul>
                <li>起火点: {{ cause.startPoint }}</li>
                <li>初步起火原因: {{ cause.initialReason }}</li>
                <li>火灾传播情况: {{ cause.spreadInfo }}</li>
              </ul>
            </template>
            <div v-else class="empty-report">
              <el-empty description="点击报告生成查看详情" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const API_URL = 'http://localhost:5000/api'
const uploadRef = ref()
const fileList = ref<any[]>([])
const selectedFile = ref<any>(null)
const generating = ref(false)
const reportGenerated = ref(false)

const basicInfo = ref({
  time: '[填写时间]',
  location: '[填写具体地点]',
  type: '[如：建筑火灾、森林火灾、工业火灾等]',
  alarmTime: '[填写时间]',
  arrivalTime: '[填写时间]',
  extinguishTime: '[填写时间]'
})

const cause = ref({
  startPoint: '[描述起火点，如"厨房炉灶"、"电气设备"]',
  initialReason: '[描述可能的原因，如"线路短路"、"明火操作不当"]',
  spreadInfo: '[描述火势传播的过程]'
})

// 上传前验证
const beforeUpload = (file: File) => {
  // 检查文件大小（5MB）
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过5MB')
    return false
  }

  // 检查文件类型
  const allowedTypes = [
    'image/png',
    'image/jpg',
    'image/jpeg',
    'image/gif',
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ]
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('不支持的文件类型')
    return false
  }

  return true
}

// 上传成功处理
const handleUploadSuccess = async (response: any) => {
  ElMessage.success('文件上传成功')
  await refreshFileList()
}

// 上传失败处理
const handleUploadError = (error: any) => {
  console.error('上传错误:', error)
  ElMessage.error('文件上传失败，请重试')
}

// 刷新文件列表
const refreshFileList = async () => {
  try {
    const response = await axios.get(`${API_URL}/files`)
    fileList.value = response.data.map((file: any) => ({
      ...file,
      uid: file.filename,
      name: file.original_name || file.filename,
      url: `${API_URL}/preview/${encodeURIComponent(file.filename)}`
    }))
  } catch (error) {
    console.error('获取文件列表失败:', error)
    ElMessage.error('获取文件列表失败')
  }
}

// 处理文件预览
const handlePreview = (file: any) => {
  selectedFile.value = file
}

// 处理文件删除
const handleDeleteFile = async (file: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文件 ${file.original_name} 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    const response = await axios.delete(`${API_URL}/files/${file.uid}`)
    
    if (response.status === 200) {
      ElMessage.success('文件删除成功')
      // 如果删除的是当前选中的文件，清空预览
      if (selectedFile.value?.uid === file.uid) {
        selectedFile.value = null
      }
      // 刷新文件列表
      await refreshFileList()
    } else {
      throw new Error('删除文件失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除文件失败')
    }
  }
}

// 判断是否为图片
const isImage = (file: any) => {
  const imageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg']
  return imageTypes.includes(file.type)
}

// 判断是否为PDF
const isPDF = (file: any) => {
  return file.type === 'application/pdf'
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (!bytes) return '0B'
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  return `${size.toFixed(size >= 10 ? 0 : 1)}${units[unitIndex]}`
}

// 格式化日期
const formatDate = (timestamp: string) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  return `${year}.${month}.${day} ${hour}:${minute}`
}

// 获取显示用的文件名（去掉时间戳部分）
const getDisplayFileName = (filename: string) => {
  // 如果文件名中包含时间戳（格式为 _YYYYMMDD_HHMMSS），则去掉它
  const match = filename.match(/(.+?)(?:_\d{8}_\d{6})?(\.[^.]+)?$/);
  if (match) {
    return (match[1] + (match[2] || '')).trim();
  }
  return filename;
}

// 生成报告
const generateReport = async () => {
  generating.value = true
  try {
    // 实现报告生成逻辑
    await new Promise(resolve => setTimeout(resolve, 1000))
    reportGenerated.value = true
    ElMessage.success('报告生成成功')
  } catch (error) {
    ElMessage.error('报告生成失败')
  } finally {
    generating.value = false
  }
}

// 初始化时加载文件列表
onMounted(() => {
  refreshFileList()
})
</script>

<style scoped>
.report-analysis {
  padding: 24px;
  height: 100vh;
  background-color: #F3F4F6;
  display: flex;
  flex-direction: column;
}

.upload-generate-section {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  height: 72px;
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}

.upload-area {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0 16px;
}

.upload-label-container {
  display: flex;
  align-items: center;
}

.upload-label {
  color: #909399;
  font-weight: 400;
  font-size: 13px;
  white-space: nowrap;
  margin-right: 16px;
}

.upload-format-info {
  color: #909399;
  font-size: 12px;
  white-space: nowrap;
}

.content-modules {
  display: flex;
  flex-direction: column;
  gap: 24px;
  flex: 1;
}

.file-preview-module,
.report-graph-module {
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
}

.module-divider {
  width: 1px;
  background-color: #e4e7ed;
  margin: 16px 0;
}

.module-title {
  height: 32px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  font-weight: 600;
  font-size: 14px;
  color: #303133;
  flex-shrink: 0;
  line-height: 32px;
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.module-content {
  flex-grow: 1;
  padding: 16px;
  overflow-y: auto;
}

.empty-list, .preview-empty, 
.empty-graph, .empty-report {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  background-color: #f5f7fa;
}

.file-list-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  padding: 8px;
}

.file-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  height: 45px;
  min-width: 0;
}

.file-card:hover {
  background-color: #f5f7fa;
}

.file-card.selected {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.file-info {
  flex: 1;
  min-width: 0;
  margin-right: 8px;
}

.file-name {
  font-size: 13px;
  font-weight: 500;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
  margin-bottom: 2px;
  text-align: left;
}

.file-meta {
  font-size: 12px;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
  text-align: left;
}

.delete-btn {
  opacity: 0;
  transition: opacity 0.3s;
  padding: 4px;
}

.file-card:hover .delete-btn {
  opacity: 1;
}

.empty-tip {
  grid-column: 1 / -1;
  text-align: center;
  color: #909399;
  padding: 20px;
}

.graph-section, .report-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
}

.section-header {
  height: 40px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.report-meta {
  font-size: 12px;
  color: #909399;
  margin-left: auto;
}

.graph-content {
  display: flex;
  justify-content: center;
  align-items: center;
  height: calc(100% - 60px);
}

.graph-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.report-body {
  font-size: 14px;
}

.report-body h3 {
  margin: 16px 0 8px;
  font-size: 16px;
}

.report-body ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.report-body li {
  margin: 8px 0;
  color: #666;
}

.preview-content {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f8f9fa;
  border-radius: 4px;
  overflow: hidden;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.preview-pdf {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: white;
}

.preview-pdf iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.preview-unsupported {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #909399;
  font-size: 14px;
}

.empty-tip {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #909399;
  font-size: 14px;
  background-color: #f8f9fa;
  border-radius: 4px;
}
</style>
