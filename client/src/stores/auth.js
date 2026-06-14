import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('qiu-shu-token') || '')
  const loading = ref(false)

  const isLoggedIn = computed(() => !!token.value)
  const currentUser = computed(() => user.value)
  const userId = computed(() => user.value?.id || null)

  function setToken(newToken) {
    token.value = newToken
    localStorage.setItem('qiu-shu-token', newToken)
  }

  function setUser(userData) {
    user.value = userData
  }

  function clearAuth() {
    token.value = ''
    user.value = null
    localStorage.removeItem('qiu-shu-token')
    localStorage.removeItem('qiu-shu-remember-token')
  }

  async function login(phone, password, rememberMe = false) {
    loading.value = true
    try {
      const res = await api.post('/auth/login', { phone, password, remember_me: rememberMe })
      if (res.status === 'success') {
        setToken(res.data.token)
        setUser(res.data.user)
        if (rememberMe) {
          localStorage.setItem('qiu-shu-remember-token', res.data.token)
        }
        return { success: true }
      }
      return { success: false, message: res.message || '登录失败' }
    } catch (err) {
      return { success: false, message: err.message || '登录失败' }
    } finally {
      loading.value = false
    }
  }

  async function register(phone, password, email, nickname) {
    loading.value = true
    try {
      const res = await api.post('/auth/register', { phone, password, email, nickname })
      if (res.status === 'success') {
        setToken(res.data.token)
        setUser(res.data.user)
        return { success: true }
      }
      return { success: false, message: res.message || '注册失败' }
    } catch (err) {
      return { success: false, message: err.message || '注册失败' }
    } finally {
      loading.value = false
    }
  }

  async function casLogin(studentId, password) {
    loading.value = true
    try {
      const res = await api.post('/auth/cas/login', { student_id: studentId, password })
      if (res.status === 'success') {
        setToken(res.data.token)
        setUser(res.data.user)
        return {
          success: true,
          courses: res.data.courses || [],
          schedule: res.data.schedule || [],
          textbooks: res.data.textbooks || [],
        }
      }
      return { success: false, message: res.message || 'CAS 登录失败' }
    } catch (err) {
      return { success: false, message: err.message || 'CAS 登录失败' }
    } finally {
      loading.value = false
    }
  }

  async function tryAutoLogin() {
    const savedToken = localStorage.getItem('qiu-shu-remember-token')
    if (!savedToken) return false

    try {
      const res = await api.get('/auth/verify', {
        headers: { Authorization: `Bearer ${savedToken}` },
      })
      if (res.status === 'success') {
        setToken(savedToken)
        setUser(res.data.user)
        return true
      }
    } catch {
      localStorage.removeItem('qiu-shu-remember-token')
    }
    return false
  }

  async function logout() {
    try {
      await api.post('/auth/logout', { token: token.value })
    } catch {
      // ignore logout errors
    } finally {
      clearAuth()
    }
  }

  async function fetchProfile() {
    try {
      const res = await api.get('/auth/me')
      if (res.status === 'success') {
        setUser(res.data)
      }
    } catch {
      // silently fail
    }
  }

  return {
    user,
    token,
    loading,
    isLoggedIn,
    currentUser,
    userId,
    setToken,
    setUser,
    clearAuth,
    login,
    register,
    casLogin,
    tryAutoLogin,
    logout,
    fetchProfile,
  }
})
