<template>
  <div class="register-wrapper">
    <div class="register-card">
      <div class="logo-section">
        <div class="logo-icon"><LogoIcon :size="64" /></div>
        <h1 class="register-brand-title">紫金求思</h1>
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
          <div class="field-row">
            <div class="field field-half"><label>学院</label><input v-model="zjuCollege" disabled class="input-field disabled" /></div>
            <div class="field field-half"><label>年级</label><input v-model="zjuGrade" disabled class="input-field disabled" /></div>
          </div>
          <div class="field"><label>专业</label><input v-model="zjuDepartment" disabled class="input-field disabled" /></div>
          <div class="field-row">
            <div class="field field-half"><label>校区</label><input v-model="zjuCampus" disabled class="input-field disabled" /></div>
            <div class="field field-half"><label>班级</label><input v-model="zjuClassName" disabled class="input-field disabled" /></div>
          </div>
          <div class="data-source-badge data-source-badge--cas" v-if="dataSource === 'cas'">
            <span class="iconify" data-icon="solar:check-circle-outline" data-width="14"></span>
            浙大 CAS 统一认证通过，姓名和学院为真实数据
          </div>
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
    <footer class="footer">© 2026 紫金求思校园二手书平台</footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useStore } from '../../stores/useStore'
import LogoIcon from '../../components/LogoIcon.vue'

const store = useStore()
const zjuStuid = ref('')
const zjuPassword = ref('')
const zjuRealName = ref('')
const zjuCollege = ref('')
const zjuGrade = ref('')
const zjuDepartment = ref('')
const zjuCampus = ref('')
const zjuClassName = ref('')
const dataSource = ref('')
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
    
    // 检查 HTTP 状态码
    if (!res.ok) {
      verifyMsg.value = `❌ 服务器错误：${res.status}`
      verifyStatus.value = 'error'
      return
    }
    
    const data = await res.json()
    if (data.success) {
      zjuStudentInfo = data.student
      dataSource.value = data.data_source || 'cas'
      const srcLabel = '教务网实名认证'
      verifyMsg.value = `✅ 验证成功（${srcLabel}）！姓名：${data.student.name}`
      verifyStatus.value = 'success'
      zjuRealName.value = data.student.name || ''
      zjuCollege.value = data.student.college || ''
      zjuGrade.value = data.student.grade || ''
      zjuDepartment.value = data.student.department || ''
      zjuCampus.value = data.student.campus || ''
      zjuClassName.value = data.student.class_name || ''
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
    department: zjuDepartment.value || '', campus: zjuCampus.value || '',
    className: zjuClassName.value || '', studentId: stuid,
    address: '', avatar: store.DEFAULT_AVATAR,
  }
  if (store.userExists(stuid)) {
    alert('该学号已注册过，请直接登录')
    return
  }
  store.addUser(newUser)
  store.login(newUser)
  alert('注册成功！欢迎加入紫金求思')
  store.navigateTo('welcome')
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
  store.navigateTo('welcome')
}

function goLogin() { store.navigateTo('login') }
</script>

<style scoped>
.register-wrapper { min-height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 1rem; }
.register-card { width: 100%; max-width: 28rem; }
.logo-section { display: flex; flex-direction: column; align-items: center; margin-bottom: 2rem; }
.logo-icon { width: 5rem; height: 5rem; display: flex; align-items: center; justify-content: center; margin-bottom: 0.75rem; }
.register-brand-title {
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
.register-brand-title:hover {
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
.zju-section, .platform-section, .normal-section { background: var(--glass-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--glass-border); border-radius: 1.5rem; padding: 1.5rem; box-shadow: var(--glass-shadow-hover); margin-bottom: 1.5rem; }
.zju-section h2, .platform-section h3, .normal-section h3 { font-size: 1.125rem; font-weight: 700; color: var(--text-primary); margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem; }
.form-fields { display: flex; flex-direction: column; gap: 1rem; }
.field label { display: block; font-size: 0.875rem; font-weight: 500; color: var(--text-primary); margin-bottom: 0.25rem; margin-left: 0.25rem; }
.input-wrap { position: relative; }
.input-icon { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: var(--text-tertiary); }
.input-field { width: 100%; padding: 0.75rem 1rem 0.75rem 2.75rem; background: rgba(255,255,255,0.7); border: 1px solid var(--glass-border); border-radius: 0.75rem; outline: none; box-sizing: border-box; transition: all 0.2s; }
.input-field:focus { border-color: var(--lavender-accent-soft); box-shadow: 0 0 0 4px rgba(220,208,255,0.15); }
.input-field.disabled { background: rgba(243,244,246,0.5); color: var(--text-secondary); }
.field-row { display: flex; gap: 0.75rem; }
.field-half { flex: 1; min-width: 0; }
.data-source-badge {
  display: flex; align-items: center; gap: 0.4rem;
  font-size: 0.75rem; color: #b45309; background: rgba(251,191,36,0.08);
  border: 1px solid rgba(251,191,36,0.2); border-radius: 0.5rem;
  padding: 0.45rem 0.7rem; margin-top: 0.25rem;
}
.data-source-badge--cas {
  color: #0d6b4e; background: rgba(22,163,74,0.08);
  border: 1px solid rgba(22,163,74,0.2);
}
.zju-btn { width: 100%; padding: 0.75rem; background: var(--gradient-brand); color: var(--text-primary); border: none; border-radius: 0.75rem; font-weight: 700; cursor: pointer; }
.zju-btn:hover { filter: brightness(0.95); }
.register-btn { width: 100%; padding: 1rem; background: var(--gradient-brand); color: var(--text-primary); border: none; border-radius: 0.75rem; font-weight: 700; cursor: pointer; box-shadow: 0 4px 12px rgba(155, 142, 196, 0.3); }
.register-btn:hover { filter: brightness(0.95); }
.verify-result { text-align: center; font-size: 0.875rem; }
.verify-result.success { color: #16a34a; }
.verify-result.error { color: #dc2626; }
.verify-result.loading { color: var(--lavender-accent); }
.divider { display: flex; align-items: center; gap: 1rem; margin: 1.5rem 0; }
.divider::before, .divider::after { flex-grow: 1; border-top: 1px solid var(--glass-border); content: ''; }
.divider span { color: var(--text-tertiary); font-size: 0.875rem; }
.agree-label { display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 1.5rem; }
.agree-label a { color: var(--lavender-accent); font-weight: 500; }
.checkbox { width: 1rem; height: 1rem; accent-color: var(--lavender-accent); }
.login-link { text-align: center; font-size: 0.875rem; color: var(--text-tertiary); margin-top: 1rem; }
.login-link a { color: var(--lavender-accent); font-weight: 700; cursor: pointer; }
.footer { margin-top: 3rem; color: var(--text-tertiary); font-size: 0.75rem; text-align: center; }
</style>
