import axios from 'axios'

const API_URL = 'http://localhost:5000/api'

export const uploadFile = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await axios.post(`${API_URL}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return response.data
}

export const getFilePreview = (filename: string) => {
  return `${API_URL}/preview/${encodeURIComponent(filename)}`
}

export const listFiles = async () => {
  const response = await axios.get(`${API_URL}/files`)
  return response.data
}
