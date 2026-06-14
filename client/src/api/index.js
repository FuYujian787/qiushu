import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// 请求拦截器：自动添加 token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('qiu-shu-token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：统一错误处理
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        localStorage.removeItem('qiu-shu-token')
        localStorage.removeItem('qiu-shu-remember-token')
        // 不在登录页时才重定向
        if (window.location.pathname !== '/auth') {
          window.location.href = '/auth'
        }
      }
      return Promise.reject(data || { message: '请求失败' })
    }
    return Promise.reject({ message: '网络连接失败，请检查网络' })
  }
)

export default api
