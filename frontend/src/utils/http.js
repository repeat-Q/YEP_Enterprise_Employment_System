import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({ baseURL: '/api/v1', timeout: 15000 })

http.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

http.interceptors.response.use(
  res => res.data,
  err => {
    const msg = err.response?.data?.detail || '请求失败'
    if (err.response?.status === 401) {
      localStorage.clear()
      window.location.href = '/login'
    } else {
      ElMessage.error(typeof msg === 'string' ? msg : JSON.stringify(msg))
    }
    return Promise.reject(err)
  }
)

export default http
