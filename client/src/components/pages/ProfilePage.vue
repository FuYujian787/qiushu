<template>
  <div class="profile-page">
    <div class="profile-card">
      <div class="profile-avatar-section">
        <div class="avatar-wrap" @click="triggerFileInput">
          <img :id="'profileAvatar'" :src="user.avatar || store.DEFAULT_AVATAR" class="profile-avatar" />
          <div class="avatar-overlay"><span class="iconify" data-icon="solar:camera-outline" data-width="28"></span></div>
        </div>
        <input ref="fileInput" type="file" accept="image/*" class="hidden-input" @change="onAvatarChange" />
        <h3 class="profile-name">{{ user.name }}</h3>
        <p class="profile-meta">{{ user.college }} · {{ user.grade }}</p>
      </div>
      <div class="profile-form">
        <div class="form-group"><label>用户名</label><input v-model="editName" class="form-input" /></div>
        <div class="form-group"><label>新密码</label><input v-model="editPw" type="password" placeholder="留空则不修改" class="form-input" /></div>
        <div class="form-group"><label>确认新密码</label><input v-model="editPw2" type="password" placeholder="再次输入新密码" class="form-input" /></div>
        <div class="form-group"><label>学院</label><input v-model="editCollege" class="form-input" /></div>
        <div class="form-group"><label>年级</label><select v-model="editGrade" class="form-input"><option v-for="g in grades" :key="g" :value="g" :selected="editGrade === g">{{ g }}</option></select></div>
        <div class="form-group"><label>收货地址</label><input v-model="editAddress" placeholder="请输入详细地址" class="form-input" /></div>
      </div>
      <div class="profile-actions">
        <button class="save-btn" @click="saveProfile">保存修改</button>
        <button class="logout-btn" @click="doLogout">退出登录</button>
      </div>
      <div class="profile-chat-section">
        <p class="profile-chat-label">快速私聊其他用户：</p>
        <div class="profile-chat-row">
          <input v-model="chatTarget" placeholder="输入用户名" class="form-input" />
          <button class="chat-btn" @click="startChat" :disabled="!chatTarget.trim()">💬 私聊</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useStore } from '../../stores/useStore'

const store = useStore()
const fileInput = ref(null)
const grades = ['大一', '大二', '大三', '大四', '研究生']

const user = computed(() => store.currentUser.value || {
  name: '张伟', college: '管理学院', grade: '大三', address: '', avatar: store.DEFAULT_AVATAR,
})

const editName = ref(user.value.name)
const editPw = ref('')
const editPw2 = ref('')
const editCollege = ref(user.value.college)
const editGrade = ref(user.value.grade)
const editAddress = ref(user.value.address || '')
let currentAvatarSrc = user.value.avatar || store.DEFAULT_AVATAR

function triggerFileInput() {
  fileInput.value?.click()
}

function onAvatarChange(e) {
  const file = e.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (ev) => {
      currentAvatarSrc = ev.target.result
      const el = document.getElementById('profileAvatar')
      if (el) el.src = ev.target.result
    }
    reader.readAsDataURL(file)
  }
}

function saveProfile() {
  if (!store.isLoggedIn.value || !store.currentUser.value) return
  if (!editName.value) { alert('用户名不能为空'); return }
  if (editPw.value && editPw.value !== editPw2.value) { alert('两次密码不一致'); return }
  const oldName = store.currentUser.value.name
  if (editName.value !== oldName && store.userExists(editName.value)) {
    alert('用户名已被占用'); return
  }
  const updates = { name: editName.value, college: editCollege.value, grade: editGrade.value, address: editAddress.value, avatar: currentAvatarSrc }
  if (editPw.value) updates.password = editPw.value
  store.updateUser(oldName, updates)
  store.currentUser.value = { ...store.currentUser.value, ...updates }
  alert('个人资料已更新')
}

function doLogout() {
  store.logout()
}

const chatTarget = ref('')

function startChat() {
  const target = chatTarget.value.trim()
  if (!target) return
  if (!store.isLoggedIn.value) {
    alert('请先登录')
    return
  }
  if (target === store.currentUser.value?.name) {
    alert('不能和自己私聊')
    return
  }
  sessionStorage.setItem('chat_target_user', target)
  store.navigateTo('chat')
}
</script>

<style scoped>
.profile-page { display: flex; justify-content: center; }
.profile-card { max-width: 32rem; width: 100%; background: var(--glass-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--glass-border); border-radius: 1.5rem; padding: 2rem; box-shadow: var(--glass-shadow); }
.profile-avatar-section { text-align: center; margin-bottom: 2rem; }
.avatar-wrap { width: 8rem; height: 8rem; margin: 0 auto; border-radius: 1.5rem; background: var(--lavender-accent-mist); overflow: hidden; position: relative; cursor: pointer; }
.profile-avatar { width: 100%; height: 100%; object-fit: cover; }
.avatar-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.2s; }
.avatar-wrap:hover .avatar-overlay { opacity: 1; }
.avatar-overlay :deep(.iconify) { color: white; }
.hidden-input { display: none; }
.profile-name { font-size: 1.5rem; font-weight: 700; margin: 1rem 0 0.25rem 0; color: var(--text-primary); }
.profile-meta { color: var(--lavender-accent); margin: 0; font-size: 0.875rem; }
.profile-form { display: flex; flex-direction: column; gap: 1.25rem; }
.form-group {}
.form-group label { display: block; font-size: 0.875rem; font-weight: 500; color: var(--text-primary); margin-bottom: 0.25rem; }
.form-input { width: 100%; padding: 0.75rem 1rem; background: rgba(255,255,255,0.7); border: 1px solid var(--glass-border); border-radius: 0.75rem; outline: none; box-sizing: border-box; }
.form-input:focus { border-color: var(--lavender-accent-soft); box-shadow: 0 0 0 4px rgba(220,208,255,0.15); }
.profile-actions { display: flex; gap: 1rem; margin-top: 2rem; }
.save-btn { flex: 1; padding: 0.75rem; background: var(--gradient-brand); color: var(--text-primary); border: none; border-radius: 0.75rem; font-weight: 700; cursor: pointer; box-shadow: 0 4px 12px rgba(155, 142, 196, 0.3); }
.save-btn:hover { filter: brightness(0.95); }
.logout-btn { flex: 1; padding: 0.75rem; background: rgba(254,242,242,0.8); color: #ef4444; border: none; border-radius: 0.75rem; font-weight: 700; cursor: pointer; }
.logout-btn:hover { background: rgba(254,226,226,0.9); }

.profile-chat-section {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--glass-border);
}

.profile-chat-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0 0 0.75rem 0;
  font-weight: 500;
}

.profile-chat-row {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.profile-chat-row .form-input {
  flex: 1;
}

.chat-btn {
  padding: 0.75rem 1.25rem;
  background: var(--gradient-brand);
  color: var(--text-primary);
  border: none;
  border-radius: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(155, 142, 196, 0.3);
}

.chat-btn:hover:not(:disabled) {
  filter: brightness(0.95);
}

.chat-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
