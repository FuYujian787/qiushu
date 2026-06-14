<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['switch-mode', 'login-success'])
const auth = useAuthStore()

const form = ref({
  phone: '',
  password: '',
  rememberMe: false,
})
const loading = ref(false)
const errorMsg = ref('')

async function handleLogin() {
  errorMsg.value = ''
  if (!form.value.phone || !form.value.password) {
    errorMsg.value = '请输入手机号和密码'
    return
  }

  loading.value = true
  const result = await auth.login(form.value.phone, form.value.password, form.value.rememberMe)
  loading.value = false

  if (result.success) {
    ElMessage.success('登录成功！欢迎回来')
    emit('login-success')
  } else {
    errorMsg.value = result.message || '学号或密码错误'
  }
}
</script>

<template>
  <div class="login-form">
    <h2 class="form-title">欢迎回来</h2>
    <p class="form-subtitle">登录求书 · 書緣，发现二手好教材</p>

    <div v-if="errorMsg" class="error-banner">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
        <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round"/>
      </svg>
      <span>{{ errorMsg }}</span>
    </div>

    <form @submit.prevent="handleLogin">
      <div class="field">
        <label>手机号</label>
        <input
          v-model="form.phone"
          type="text"
          placeholder="请输入手机号"
          class="input"
          :disabled="loading"
        />
      </div>
      <div class="field">
        <label>密码</label>
        <input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          class="input"
          :disabled="loading"
        />
      </div>
      <div class="field-row">
        <label class="checkbox-label">
          <input v-model="form.rememberMe" type="checkbox" />
          <span>记住我</span>
        </label>
      </div>
      <button type="submit" class="submit-btn" :disabled="loading">
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </form>

    <div class="form-footer">
      <span>还没有账号？</span>
      <button class="link-btn" @click="$emit('switch-mode', 'register')">立即注册</button>
    </div>
  </div>
</template>

<style scoped>
.login-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 32px;
}

.form-title {
  font-family: var(--font-display);
  font-size: 24px;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.form-subtitle {
  color: var(--text-muted);
  font-size: 14px;
  margin-bottom: 24px;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(196, 30, 58, 0.06);
  border: 1px solid rgba(196, 30, 58, 0.15);
  border-radius: 8px;
  color: #C41E3A;
  font-size: 13px;
  margin-bottom: 16px;
}

[data-theme="cyber"] .error-banner {
  background: rgba(0, 212, 255, 0.06);
  border-color: rgba(0, 212, 255, 0.2);
  color: #00D4FF;
}

.field {
  margin-bottom: 16px;
}

.field label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 6px;
  font-weight: 500;
}

.input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border-default);
  border-radius: 8px;
  font-size: 14px;
  background: var(--surface-secondary);
  color: var(--text-primary);
  outline: none;
  transition: all 0.2s;
  font-family: var(--font-body);
}

.input:focus {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px var(--accent-primary-light);
}

.field-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background: var(--accent-primary);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: var(--accent-primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(196, 30, 58, 0.3);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

[data-theme="cyber"] .submit-btn {
  background: linear-gradient(135deg, #00D4FF, #A855F7);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
}

.form-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 13px;
  color: var(--text-muted);
}

.link-btn {
  background: none;
  border: none;
  color: var(--accent-primary);
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  padding: 0;
}

.link-btn:hover {
  text-decoration: underline;
}
</style>
