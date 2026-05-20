<template>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="logo-section">
        <div class="logo-icon"><span class="iconify" data-icon="ph:books-duotone" data-width="36"></span></div>
        <h1>求书</h1>
        <p>你的校园智慧购书管家</p>
      </div>
      <div class="form-section">
        <h2>账号登录</h2>
        <div class="form-fields">
          <div class="field">
            <label>用户名</label>
            <div class="input-wrap"><span class="input-icon iconify" data-icon="solar:user-outline" data-width="20"></span><input v-model="username" placeholder="请输入用户名" type="text" class="input-field" /></div>
          </div>
          <div class="field">
            <label>密码</label>
            <div class="input-wrap"><span class="input-icon iconify" data-icon="solar:lock-password-outline" data-width="20"></span><input v-model="password" placeholder="请输入密码" type="password" class="input-field" @keyup.enter="doLogin" /></div>
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
    <footer class="footer">© 2026 求书校园二手书平台</footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useStore } from '../../stores/useStore'

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
  width: 4rem;
  height: 4rem;
  background: white;
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.logo-icon :deep(.iconify) { color: #7c3aed; }
.logo-section h1 { font-size: 1.875rem; font-weight: 700; color: #374151; letter-spacing: 0.05em; margin: 0; }
.logo-section p { color: #9ca3af; margin-top: 0.5rem; }
.form-section {
  background: white;
  border-radius: 1.5rem;
  padding: 2.5rem;
  box-shadow: 0 10px 25px rgba(124,58,237,0.08);
  display: flex;
  flex-direction: column;
}
.form-section h2 { font-size: 1.5rem; font-weight: 700; color: #374151; margin: 0 0 2rem 0; }
.form-fields { display: flex; flex-direction: column; gap: 1.25rem; margin-bottom: 1.5rem; }
.field label { display: block; font-size: 0.875rem; font-weight: 500; color: #374151; margin-bottom: 0.375rem; margin-left: 0.25rem; }
.input-wrap { position: relative; }
.input-icon { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: #9ca3af; }
.input-field {
  width: 100%; padding: 0.875rem 1rem 0.875rem 2.75rem;
  background: #f9fafb; border: 1px solid #f3f4f6;
  border-radius: 0.75rem; outline: none; box-sizing: border-box;
  transition: all 0.2s;
}
.input-field:focus { border-color: #7c3aed; box-shadow: 0 0 0 4px rgba(124,58,237,0.1); }
.form-options { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.checkbox-label, .agree-label { display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; color: #6b7280; cursor: pointer; }
.checkbox { width: 1rem; height: 1rem; accent-color: #7c3aed; border-radius: 0.25rem; }
.forgot-link { font-size: 0.875rem; color: #7c3aed; font-weight: 500; cursor: pointer; }
.agree-label { margin-bottom: 2rem; }
.agree-label a { color: #7c3aed; font-weight: 500; }
.login-btn {
  width: 100%; padding: 1rem;
  background: #7c3aed; color: white;
  border: none; border-radius: 0.75rem;
  font-weight: 700; font-size: 1rem;
  cursor: pointer; margin-bottom: 1.5rem;
  box-shadow: 0 4px 12px rgba(124,58,237,0.3);
}
.login-btn:hover { background: #6d28d9; }
.register-link { text-align: center; font-size: 0.875rem; color: #9ca3af; }
.register-link a { color: #7c3aed; font-weight: 700; margin-left: 0.25rem; cursor: pointer; }
.footer { margin-top: 3rem; color: #9ca3af; font-size: 0.75rem; }
</style>
