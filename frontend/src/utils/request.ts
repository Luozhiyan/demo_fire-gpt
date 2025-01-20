import axios from 'axios'

const request = axios.create({
  baseURL: '/api', // 基础请求路径
  timeout: 10000, // 请求超时时间
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 可以在这里添加token等
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    // 处理错误响应
    return Promise.reject(error)
  }
)

export default request
