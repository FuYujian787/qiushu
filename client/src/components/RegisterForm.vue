<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['switch-mode', 'register-success'])
const auth = useAuthStore()

const form = reactive({
  phone: '',
  password: '',
  confirmPassword: '',
  email: '',
  nickname: '',
})
const loading = ref(false)
const errorMsg = ref('')
const fieldErrors = ref({})

async function handleRegister() {
  errorMsg.value = ''
  fieldErrors.value = {}

  // 前端验证
  if (!/^1[3-9]\d{9}$/.test(form.phone)) {
    fieldErrors.value.phone = '请输入正确的11位手机号'
    return
  }
  if (form.password.length < 8) {
    fieldErrors.value.password = '密码长度不能少于8位'
    return
  }
  if (!/[A-Z]/.test(form.password)) {
    fieldErrors.value.password = '密码需包含至少一个大写字母'
    return
  }
  if (!/[a-z]/.test(form.password)) {
    fieldErrors.value.password = '密码需包含至少一个小写字母'
    return
  }
  if (!/[0-9]/.test(form.password)) {
    fieldErrors.value.password = '密码需包含至少一个数字'
    return
  }
  if (!/[!@#$%^&*]/.test(form.password)) {
    fieldErrors.value.password = '密码需包含至少一个特殊字符 (!@#$%^&*)'
    return
  }
  if (form.password !== form.confirmPassword) {
    fieldErrors.value.confirmPassword = '两次输入的密码不一致'
    return
  }
  if (form.email && !/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(form.email)) {
    fieldErrors.value.email = '邮箱格式不正确'
    return
  }

  loading.value = true
  const result = await auth.register(form.phone, form.password, form.email, form.nickname)
  loading.value = false

  if (result.success) {
    ElMessage.success('注册成功！欢迎加入求书 · 書緣')
    emit('register-success')
  } else {
    errorMsg.value = result.message || '注册失败'
  }
}
</script>

<template>
  <div class="register-form">
    <h2 class="form-title">创建账号</h2>
    <p class="form-subtitle">加入求书 · 書緣，开启二手书之旅</p>

    <div v-if="errorMsg" class="error-banner">{{ errorMsg }}</div>

    <form @submit.prevent="handleRegister">
      <div class="field">
        <label>手机号 <span class="required">*</span></label>
        <input v-model="form.phone" type="text" placeholder="11位手机号" class="input"
          :class="{ error: fieldErrors.phone }" :disabled="loading" />
        <span v-if="fieldErrors.phone" class="field-error">{{ fieldErrors.phone }}</span>
      </div>
      <div class="field">
        <label>昵称</label>
        <input v-model="form.nickname" type="text" placeholder="给自己取个名字吧" class="input" :disabled="loading" />
      </div>
      <div class="field">
        <label>邮箱（选填）</label>
        <input v-model="form.email" type="email" placeholder="you@example.com" class="input"
          :class="{ error: fieldErrors.email }" :disabled="loading" />
        <span v-if="fieldErrors.email" class="field-error">{{ fieldErrors.email }}</span>
      </div>
      <div class="field">
        <label>密码 <span class="required">*</span></label>
        <input v-model="form.password" type="password" placeholder="8位以上，含大小写+数字+特殊字符" class="input"
          :class="{ error: fieldErrors.password }" :disabled="loading" />
        <span v-if="fieldErrors.password" class="field-error">{{ fieldErrors.password }}</span>
        <div class="password-hint">需包含大小写字母、数字和特殊字符 (!@#$%^&*)，不少于8位</div>
      </div>
      <div class="field">
        <label>确认密码 <span class="required">*</span></label>
        <input v-model="form.confirmPassword" type="password" placeholder="再次输入密码" class="input"
          :class="{ error: fieldErrors.confirmPassword }" :disabled="loading" />
        <span v-if="fieldErrors.confirmPassword" class="field-error">{{ fieldErrors.confirmPassword }}</span>
      </div>
      <button type="submit" class="submit-btn" :disabled="loading">
        {{ loading ? '注册中...' : '注册' }}
      </button>
    </form>

    <div class="form-footer">
      <span>已有账号？</span>
      <button class="link-btn" @click="$emit('switch-mode', 'login')">立即登录</button>
    </div>
  </div>
</template>

<style scoped>
.register-form {
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
  padding: 10px 14px;
  background: rgba(196, 30, 58, 0.06);
  border: 1px solid rgba(196, 30, 58, 0.15);
  border-radius: 8px;
  color: #C41E3A;
  font-size: 13px;
  margin-bottom: 16px;
}

.required {
  color: var(--accent-primary);
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

.input.error {
  border-color: #C41E3A;
}

.field-error {
  display: block;
  color: #C41E3A;
  font-size: 12px;
  margin-top: 4px;
}

.password-hint {
  color: var(--text-muted);
  font-size: 11px;
  margin-top: 4px;
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
  margin-top: 8px;
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
