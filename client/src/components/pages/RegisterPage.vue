<template>
  <div class="register-wrapper">
    <div class="register-card">
      <div class="logo-section">
        <div class="logo-icon"><span class="iconify" data-icon="ph:books-duotone" data-width="36"></span></div>
        <h1>求书</h1>
        <p>加入我们的智慧书享社区</p>
      </div>
      <div class="zju-section">
        <h2><span class="iconify" data-icon="mdi:school" data-width="22"></span> 浙大通行证注册</h2>
        <div class="form-fields">
          <div class="field">
            <label>学号</label>
            <div class="input-wrap"><span class="input-icon iconify" data-icon="solar:user-id-outline" data-width="20"></span><input v-model="zjuStuid" placeholder="请输入学号" type="text" class="input-field" /></div>
          </div>
          <div class="field">
            <label>通行证密码</label>
            <div class="input-wrap"><span class="input-icon iconify" data-icon="solar:lock-password-outline" data-width="20"></span><input v-model="zjuPassword" placeholder="浙大统一认证密码" type="password" class="input-field" /></div>
          </div>
          <button class="zju-btn" @click="verifyZJU">验证身份</button>
          <div class="verify-result" :class="verifyStatus">{{ verifyMsg }}</div>
        </div>
      </div>
      <div v-if="showPlatformCard" class="platform-section">
        <h3>设置平台密码</h3>
        <div class="form-fields">
          <div class="field"><label>真实姓名</label><input v-model="zjuRealName" disabled class="input-field disabled" /></div>
          <div class="field"><label>学院</label><input v-model="zjuCollege" disabled class="input-field disabled" /></div>
          <div class="field"><label>年级</label><input v-model="zjuGrade" disabled class="input-field disabled" /></div>
          <div class="field"><label>设置平台密码</label><input v-model="platformPw" placeholder="6-16位字母或数字" type="password" class="input-field" /></div>
          <div class="field"><label>确认密码</label><input v-model="platformPw2" placeholder="请再次输入密码" type="password" class="input-field" /></div>
          <button class="register-btn" @click="doZJURegister">完成注册</button>
        </div>
      </div>
      <div class="divider"><span>或</span></div>
      <div class="normal-section">
        <h3>创建新账号</h3>
        <div class="form-fields">
          <div class="field">
            <label>用户名</label>
            <div class="input-wrap"><span class="input-icon iconify" data-icon="solar:user-outline" data-width="20"></span><input v-model="regName" placeholder="设置你的用户名" type="text" class="input-field" /></div>
          </div>
          <div class="field">
            <label>设置密码</label>
            <div class="input-wrap"><span class="input-icon iconify" data-icon="solar:lock-password-outline" data-width="20"></span><input v-model="regPw" placeholder="6-16位字母或数字" type="password" class="input-field" /></div>
          </div>
          <div class="field">
            <label>确认密码</label>
            <div class="input-wrap"><span class="input-icon iconify" data-icon="solar:lock-password-outline" data-width="20"></span><input v-model="regPw2" placeholder="请再次输入密码" type="password" class="input-field" /></div>
          </div>
        </div>
        <label class="agree-label"><input type="checkbox" checked class="checkbox" />我已阅读并同意 <a>《服务协议》</a> 和 <a>《隐私协议》</a></label>
        <button class="register-btn" @click="doRegister">注册并登录</button>
        <div class="login-link">已有账号？<a @click="goLogin">前往登录</a></div>
      </div>
    </div>
    <footer class="footer">© 2026 求书校园二手书平台</footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useStore } from '../../stores/useStore'

const store = useStore()
const zjuStuid = ref('')
const zjuPassword = ref('')
const zjuRealName = ref('')
const zjuCollege = ref('')
const zjuGrade = ref('')
const platformPw = ref('')
const platformPw2 = ref('')
const regName = ref('张伟')
const regPw = ref('')
const regPw2 = ref('')
const showPlatformCard = ref(false)
const verifyMsg = ref('')
const verifyStatus = ref('')
let zjuStudentInfo = null

async function verifyZJU() {
  if (!zjuStuid.value || !zjuPassword.value) {
    verifyMsg.value = '请输入学号和密码'
    verifyStatus.value = 'error'
    return
  }
  verifyMsg.value = '正在验证身份...'
  verifyStatus.value = 'loading'
  try {
    const res = await fetch('/api/zju-verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: zjuStuid.value, password: zjuPassword.value }),
    })
    const data = await res.json()
    if (data.success) {
      zjuStudentInfo = data.student
      verifyMsg.value = `✅ 验证成功！姓名：${data.student.name}`
      verifyStatus.value = 'success'
      zjuRealName.value = data.student.name || ''
      zjuCollege.value = data.student.college || ''
      zjuGrade.value = data.student.grade || ''
      showPlatformCard.value = true
    } else {
      verifyMsg.value = `❌ ${data.message || '验证失败'}`
      verifyStatus.value = 'error'
    }
  } catch (e) {
    verifyMsg.value = `❌ 网络错误：${e.message}`
    verifyStatus.value = 'error'
  }
}

function doZJURegister() {
  if (!platformPw.value || platformPw.value !== platformPw2.value) {
    alert('两次密码不一致或为空')
    return
  }
  if (!zjuStudentInfo) {
    alert('请先验证浙大通行证')
    return
  }
  const stuid = zjuStuid.value
  const newUser = {
    name: stuid, password: platformPw.value, role: 'buyer',
    college: zjuCollege.value || '未设置', grade: zjuGrade.value || '大一',
    address: '', avatar: store.DEFAULT_AVATAR,
  }
  if (store.userExists(stuid)) {
    alert('该学号已注册过，请直接登录')
    return
  }
  store.addUser(newUser)
  store.login(newUser)
  alert('注册成功！欢迎加入求书')
  store.navigateTo('home')
}

function doRegister() {
  if (!regName.value || !regPw.value || !regPw2.value) {
    alert('请填写完整信息'); return
  }
  if (regPw.value !== regPw2.value) {
    alert('两次密码不一致'); return
  }
  if (store.userExists(regName.value)) {
    alert('用户名已存在'); return
  }
  const newUser = { name: regName.value, password: regPw.value, role: 'buyer', college: '未设置', grade: '大一', address: '', avatar: store.DEFAULT_AVATAR }
  store.addUser(newUser)
  store.login(newUser)
  alert('注册成功')
  store.navigateTo('home')
}

function goLogin() { store.navigateTo('login') }
</script>

<style scoped>
.register-wrapper { min-height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 1rem; }
.register-card { width: 100%; max-width: 28rem; }
.logo-section { display: flex; flex-direction: column; align-items: center; margin-bottom: 2rem; }
.logo-icon { width: 4rem; height: 4rem; background: white; border-radius: 1rem; display: flex; align-items: center; justify-content: center; margin-bottom: 0.75rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.logo-icon :deep(.iconify) { color: #7c3aed; }
.logo-section h1 { font-size: 1.875rem; font-weight: 700; color: #374151; letter-spacing: 0.05em; margin: 0; }
.logo-section p { color: #9ca3af; margin-top: 0.5rem; }
.zju-section, .platform-section, .normal-section { background: white; border-radius: 1.5rem; padding: 1.5rem; box-shadow: 0 10px 25px rgba(124,58,237,0.08); margin-bottom: 1.5rem; }
.zju-section h2, .platform-section h3, .normal-section h3 { font-size: 1.125rem; font-weight: 700; color: #374151; margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem; }
.form-fields { display: flex; flex-direction: column; gap: 1rem; }
.field label { display: block; font-size: 0.875rem; font-weight: 500; color: #374151; margin-bottom: 0.25rem; margin-left: 0.25rem; }
.input-wrap { position: relative; }
.input-icon { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: #9ca3af; }
.input-field { width: 100%; padding: 0.75rem 1rem 0.75rem 2.75rem; background: #f9fafb; border: 1px solid #f3f4f6; border-radius: 0.75rem; outline: none; box-sizing: border-box; transition: all 0.2s; }
.input-field:focus { border-color: #7c3aed; box-shadow: 0 0 0 4px rgba(124,58,237,0.1); }
.input-field.disabled { background: #f3f4f6; color: #6b7280; }
.zju-btn { width: 100%; padding: 0.75rem; background: #2563eb; color: white; border: none; border-radius: 0.75rem; font-weight: 700; cursor: pointer; }
.zju-btn:hover { background: #1d4ed8; }
.register-btn { width: 100%; padding: 1rem; background: #7c3aed; color: white; border: none; border-radius: 0.75rem; font-weight: 700; cursor: pointer; }
.register-btn:hover { background: #6d28d9; }
.verify-result { text-align: center; font-size: 0.875rem; }
.verify-result.success { color: #16a34a; }
.verify-result.error { color: #dc2626; }
.verify-result.loading { color: #2563eb; }
.divider { display: flex; align-items: center; gap: 1rem; margin: 1.5rem 0; }
.divider::before, .divider::after { flex-grow: 1; border-top: 1px solid #e5e7eb; content: ''; }
.divider span { color: #9ca3af; font-size: 0.875rem; }
.agree-label { display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; color: #6b7280; margin-bottom: 1.5rem; }
.agree-label a { color: #7c3aed; font-weight: 500; }
.checkbox { width: 1rem; height: 1rem; accent-color: #7c3aed; }
.login-link { text-align: center; font-size: 0.875rem; color: #9ca3af; margin-top: 1rem; }
.login-link a { color: #7c3aed; font-weight: 700; cursor: pointer; }
.footer { margin-top: 3rem; color: #9ca3af; font-size: 0.75rem; text-align: center; }
</style>
