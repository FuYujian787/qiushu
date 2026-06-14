<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import LoginForm from '@/components/LoginForm.vue'
import RegisterForm from '@/components/RegisterForm.vue'
import CasLoginForm from '@/components/CasLoginForm.vue'

const router = useRouter()
const route = useRoute()
const mode = ref('login')
// 'cas' = CAS login card visible, 'login' = phone login, 'register' = phone register
const casMode = ref(false)

function onLoginSuccess() {
  const redirect = route.query.redirect || '/'
  router.push(redirect)
}

function onRegisterSuccess() {
  router.push('/')
}

function onCasLoginSuccess(courses) {
  ElMessage.success({
    message: `CAS 登录成功！已同步 ${courses?.length || 0} 门课程`,
    duration: 3000,
  })
  const redirect = route.query.redirect || '/'
  router.push(redirect)
}

function toggleCasLogin() {
  casMode.value = !casMode.value
}
</script>

<template>
  <div class="auth-page page-enter">
    <div class="auth-container">
      <div class="auth-card">
        <!-- Tabs -->
        <div class="auth-tabs">
          <button
            :class="['tab', { active: mode === 'login' }]"
            @click="mode = 'login'"
          >
            登录
          </button>
          <button
            :class="['tab', { active: mode === 'register' }]"
            @click="mode = 'register'"
          >
            注册
          </button>
        </div>

        <!-- Form -->
        <LoginForm
          v-if="mode === 'login'"
          @switch-mode="mode = $event"
          @login-success="onLoginSuccess"
        />
        <RegisterForm
          v-else
          @switch-mode="mode = $event"
          @register-success="onRegisterSuccess"
        />

        <!-- CAS Login Form -->
        <div v-if="mode === 'login'" class="cas-section">
          <div class="divider">
            <span>或</span>
          </div>

          <!-- Toggle: show CAS button or CAS form -->
          <div v-if="!casMode" class="cas-toggle-area">
            <button class="cas-btn" @click="toggleCasLogin">
              <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
                <path d="M12 2L3 7v5c0 5.6 3.8 10.7 9 12 5.2-1.3 9-6.4 9-12V7L12 2z" stroke="currentColor" stroke-width="1.2" fill="none"/>
                <path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>浙大通行证登录</span>
            </button>
            <p class="cas-hint">使用浙大统一身份认证登录，自动同步学籍与课程信息</p>
          </div>

          <CasLoginForm
            v-else
            @login-success="onCasLoginSuccess"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: var(--surface-primary);
}

.auth-container {
  width: 100%;
  max-width: 440px;
}

.auth-card {
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.auth-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-default);
}

.tab {
  flex: 1;
  padding: 16px;
  background: none;
  border: none;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.tab.active {
  color: var(--accent-primary);
}

.tab.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 20%;
  right: 20%;
  height: 2px;
  background: var(--accent-primary);
  border-radius: 1px;
}

.tab:hover:not(.active) {
  color: var(--text-secondary);
}

.cas-section {
  padding: 0 32px 32px;
}

.divider {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  color: var(--text-muted);
  font-size: 12px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border-default);
}

/* CAS toggle area */
.cas-toggle-area {
  text-align: center;
}

.cas-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 14px 12px;
  border: 1.5px dashed var(--border-strong);
  border-radius: 10px;
  background: var(--surface-primary);
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  letter-spacing: 0.3px;
}

.cas-btn:hover {
  border-color: var(--accent-primary);
  border-style: solid;
  color: var(--accent-primary);
  background: var(--accent-primary-light);
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(196, 30, 58, 0.08);
}

[data-theme="cyber"] .cas-btn {
  border-style: solid;
  border-color: rgba(255, 255, 255, 0.08);
  background: var(--surface-glass);
}

[data-theme="cyber"] .cas-btn:hover {
  border-color: #00D4FF;
  color: #00D4FF;
  background: rgba(0, 212, 255, 0.06);
  box-shadow: 0 0 24px rgba(0, 212, 255, 0.12);
}

.cas-hint {
  text-align: center;
  color: var(--text-muted);
  font-size: 11px;
  margin-top: 12px;
  line-height: 1.5;
}
</style>
