<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['login-success'])

const auth = useAuthStore()
const loading = ref(false)
const formRef = ref(null)

const form = reactive({
  studentId: '',
  password: '',
})

const rules = {
  studentId: [
    { required: true, message: '请输入学号', trigger: 'blur' },
    { pattern: /^\d{6,12}$/, message: '学号格式不正确', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入CAS密码', trigger: 'blur' },
  ],
}

// Track error state for shake animation
const hasError = ref(false)

async function handleSubmit() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  hasError.value = false

  try {
    const result = await auth.casLogin(form.studentId, form.password)
    if (result.success) {
      ElMessage.success('CAS 登录成功！正在同步课程信息...')
      emit('login-success', result.courses || [])
    } else {
      hasError.value = true
      ElMessage.error(result.message || 'CAS 登录失败，请检查学号密码')
      // Reset error animation after it plays
      setTimeout(() => { hasError.value = false }, 600)
    }
  } catch (err) {
    hasError.value = true
    ElMessage.error(err.message || '网络错误，请稍后重试')
    setTimeout(() => { hasError.value = false }, 600)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="cas-login-form" :class="{ 'has-error': hasError }">
    <!-- Header -->
    <div class="cas-header">
      <div class="cas-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="28" height="28">
          <!-- Shield / University icon -->
          <path d="M12 2L3 7v5c0 5.6 3.8 10.7 9 12 5.2-1.3 9-6.4 9-12V7L12 2z" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M9 12l2 2 4-4" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <div class="cas-title-group">
        <h3 class="cas-title">浙大通行证登录</h3>
        <p class="cas-subtitle">使用统一身份认证，自动同步学籍与课程</p>
      </div>
    </div>

    <!-- Form -->
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      @submit.prevent="handleSubmit"
    >
      <el-form-item prop="studentId" label="学号">
        <el-input
          v-model="form.studentId"
          placeholder="请输入10位学号"
          :prefix-icon="null"
          size="large"
          maxlength="12"
          autocomplete="username"
          @keyup.enter="handleSubmit"
        >
          <template #prefix>
            <span class="input-prefix-icon">&#9998;</span>
          </template>
        </el-input>
      </el-form-item>

      <el-form-item prop="password" label="密码">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入CAS密码（与浙大通行证密码一致）"
          size="large"
          show-password
          autocomplete="current-password"
          @keyup.enter="handleSubmit"
        >
          <template #prefix>
            <span class="input-prefix-icon">&#128274;</span>
          </template>
        </el-input>
      </el-form-item>

      <el-button
        type="primary"
        size="large"
        class="cas-submit-btn"
        :loading="loading"
        :disabled="!form.studentId || !form.password"
        @click="handleSubmit"
      >
        <span v-if="!loading">认证并登录</span>
        <span v-else>正在验证身份...</span>
      </el-button>
    </el-form>

    <!-- Footer info -->
    <div class="cas-footer">
      <p class="cas-footer-text">
        使用浙大统一身份认证系统（zjuam.zju.edu.cn）进行安全认证
      </p>
      <p class="cas-footer-hint">
        密码错误？<a href="https://zjuam.zju.edu.cn/cas/login" target="_blank" rel="noopener">访问浙大通行证</a>
      </p>
    </div>
  </div>
</template>

<style scoped>
.cas-login-form {
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: 12px;
  padding: 28px 28px 20px;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.cas-login-form.has-error {
  border-color: #DC2626;
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 50%, 90% { transform: translateX(-4px); }
  30%, 70% { transform: translateX(4px); }
}

/* Header */
.cas-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-default);
}

.cas-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--accent-primary-light);
  color: var(--accent-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

[data-theme="cyber"] .cas-icon {
  background: rgba(0, 212, 255, 0.12);
  color: #00D4FF;
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.15);
}

.cas-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 4px 0;
  font-family: var(--font-display, 'Noto Serif SC', serif);
}

.cas-subtitle {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0;
  line-height: 1.4;
}

/* Form */
:deep(.el-form-item__label) {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  padding-bottom: 6px;
}

:deep(.el-input__wrapper) {
  background: var(--surface-primary);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  box-shadow: none !important;
  transition: border-color 0.2s, box-shadow 0.2s;
  padding: 4px 12px;
}

:deep(.el-input__wrapper:hover) {
  border-color: var(--border-strong);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px var(--accent-primary-light) !important;
}

[data-theme="cyber"] :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.15) !important;
}

:deep(.el-input__inner) {
  color: var(--text-primary);
  font-size: 14px;
}

:deep(.el-input__inner::placeholder) {
  color: var(--text-muted);
  font-size: 13px;
}

.input-prefix-icon {
  font-size: 16px;
  opacity: 0.5;
}

/* Submit */
.cas-submit-btn {
  width: 100%;
  margin-top: 4px;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 8px;
  letter-spacing: 0.5px;
  transition: all 0.2s;
}

.cas-submit-btn:not(:disabled):not(.is-loading):hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(196, 30, 58, 0.3);
}

[data-theme="cyber"] .cas-submit-btn:not(:disabled):not(.is-loading):hover {
  box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3);
}

/* Footer */
.cas-footer {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--border-default);
  text-align: center;
}

.cas-footer-text {
  font-size: 11px;
  color: var(--text-muted);
  margin: 0 0 6px 0;
  line-height: 1.5;
}

.cas-footer-hint {
  font-size: 11px;
  color: var(--text-muted);
  margin: 0;
}

.cas-footer-hint a {
  color: var(--accent-primary);
  text-decoration: none;
  font-weight: 600;
}

.cas-footer-hint a:hover {
  text-decoration: underline;
}
</style>
