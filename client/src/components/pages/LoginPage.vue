<template>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="logo-section">
        <div class="logo-icon"><LogoIcon :size="64" /></div>
        <h1 class="login-brand-title">紫金求思</h1>
        <p>你的校园智慧购书管家</p>
      </div>
      <div class="form-section">
        <h2>账号登录</h2>
        <div class="form-fields">
          <div class="field">
            <label>用户名</label>
            <div class="input-wrap">
              <span class="input-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="8" r="4.5"/>
                  <path d="M3 21c0-4 4-7 9-7s9 3 9 7"/>
                </svg>
              </span>
              <input v-model="username" placeholder="请输入用户名" type="text" class="input-field" />
            </div>
          </div>
          <div class="field">
            <label>密码</label>
            <div class="input-wrap">
              <span class="input-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
              </span>
              <input v-model="password" placeholder="请输入密码" type="password" class="input-field" @keyup.enter="doLogin" />
            </div>
          </div>
        </div>
        <div class="form-options">
          <label class="checkbox-label"><input type="checkbox" checked class="checkbox" />记住我</label>
          <a class="forgot-link">忘记密码？</a>
        </div>
        <label class="agree-label"><input type="checkbox" checked class="checkbox" />我已阅读并同意 <a>《服务协议》</a> 和 <a>《隐私协议》</a></label>
        <button class="login-btn" @click="doLogin">登录</button>
        <div class="register-link">还没有账号？<a @click="goRegister">前往注册</a></div>
      </div>
    </div>
    <footer class="footer">© 2026 紫金求思校园二手书平台</footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useStore } from '../../stores/useStore'
import LogoIcon from '../../components/LogoIcon.vue'

const store = useStore()
const username = ref('张伟')
const password = ref('')

function doLogin() {
  if (!username.value || !password.value) {
    alert('请输入用户名和密码')
    return
  }
  const user = store.findUser(username.value, password.value)
  if (user) {
    store.login(user)
    store.navigateTo('home')
  } else {
    alert('登录失败，请检查账号密码')
  }
}

function goRegister() {
  store.navigateTo('register')
}
</script>

<style scoped>
.login-wrapper {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
.login-card {
  width: 100%;
  max-width: 28rem;
}
.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
}
.logo-icon {
  width: 5rem;
  height: 5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
}
.login-brand-title {
  font-size: 2.25rem;
  font-weight: 700;
  margin: 0;
  font-family: var(--font-brand);
  letter-spacing: 0.12em;
  line-height: 1.2;
  background: linear-gradient(135deg, #4A3B5A 0%, #7A6B8A 40%, #C4B5E0 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  text-shadow:
    0 0 40px rgba(196, 181, 224, 0.12),
    0 0 80px rgba(220, 208, 255, 0.06),
    0 4px 12px rgba(74, 59, 90, 0.06);
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.login-brand-title:hover {
  letter-spacing: 0.16em;
  text-shadow:
    0 0 60px rgba(196, 181, 224, 0.25),
    0 0 100px rgba(220, 208, 255, 0.12),
    0 4px 20px rgba(74, 59, 90, 0.10);
  background: linear-gradient(135deg, #C4B5E0 0%, #DCD0FF 40%, #B8A9DA 70%, #4A3B5A 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
}
.logo-section p { color: var(--text-tertiary); margin-top: 0.5rem; }
.form-section {
  background: var(--glass-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--glass-border);
  border-radius: 1.5rem;
  padding: 2.5rem;
  box-shadow: var(--glass-shadow-hover);
  display: flex;
  flex-direction: column;
}
.form-section h2 { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin: 0 0 2rem 0; }
.form-fields { display: flex; flex-direction: column; gap: 1.25rem; margin-bottom: 1.5rem; }
.field label { display: block; font-size: 0.875rem; font-weight: 500; color: var(--text-primary); margin-bottom: 0.375rem; margin-left: 0.25rem; }
.input-wrap { position: relative; }
.input-icon { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: var(--text-tertiary); }
.input-field {
  width: 100%; padding: 0.875rem 1rem 0.875rem 2.75rem;
  background: rgba(255,255,255,0.7); border: 1px solid var(--glass-border);
  border-radius: 0.75rem; outline: none; box-sizing: border-box;
  transition: all 0.2s;
}
.input-field:focus { border-color: var(--lavender-accent-soft); box-shadow: 0 0 0 4px rgba(220,208,255,0.15); }
.form-options { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.checkbox-label, .agree-label { display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; color: var(--text-secondary); cursor: pointer; }
.checkbox { width: 1rem; height: 1rem; accent-color: var(--lavender-accent); border-radius: 0.25rem; }
.forgot-link { font-size: 0.875rem; color: var(--lavender-accent); font-weight: 500; cursor: pointer; }
.agree-label { margin-bottom: 2rem; }
.agree-label a { color: var(--lavender-accent); font-weight: 500; }
.login-btn {
  width: 100%; padding: 1rem;
  background: var(--gradient-brand); color: var(--text-primary);
  border: none; border-radius: 0.75rem;
  font-weight: 700; font-size: 1rem;
  cursor: pointer; margin-bottom: 1.5rem;
  box-shadow: 0 4px 12px rgba(155, 142, 196, 0.3);
}
.login-btn:hover { background: var(--gradient-brand); filter: brightness(0.95); }
.register-link { text-align: center; font-size: 0.875rem; color: var(--text-tertiary); }
.register-link a { color: var(--lavender-accent); font-weight: 700; margin-left: 0.25rem; cursor: pointer; }
.footer { margin-top: 3rem; color: var(--text-tertiary); font-size: 0.75rem; }
</style>
