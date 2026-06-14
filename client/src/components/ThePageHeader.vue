<template>
  <header class="page-header apple-liquid-header">
    <div class="header-left">
      <h2 class="greeting-msg">{{ greetingText }}</h2>
      <p class="date-text">今天是 {{ todayDate }}，来看点新书吧</p>
    </div>
    <div class="header-right">
      <div class="search-box" role="search">
        <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input class="search-input" v-model="searchVal" placeholder="搜索书名、作者或 ISBN..." type="search" aria-label="搜索书名、作者或 ISBN" @input="onSearch" />
      </div>
      <div class="header-actions">
        <span class="action-btn" aria-label="帮助" role="button" tabindex="0"><span class="iconify" data-icon="solar:question-circle-linear" data-width="24" aria-hidden="true"></span></span>
        <span class="action-btn notif-btn" @click="store.navigateTo('notifications')" aria-label="消息通知" role="button" tabindex="0" @keydown.enter="store.navigateTo('notifications')"><span class="iconify" data-icon="solar:bell-linear" data-width="24" aria-hidden="true"></span></span>
        <div class="avatar-wrap" @click="handleAvatarClick" role="button" tabindex="0" aria-label="个人中心" @keydown.enter="handleAvatarClick">
          <div class="avatar-ring">
            <img :src="avatarSrc" alt="用户头像" class="avatar-img" />
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useStore } from '../stores/useStore'

const store = useStore()
const searchVal = ref('')

const todayDate = computed(() => new Date().toISOString().slice(0, 10))

const greetingText = computed(() => {
  if (store.isLoggedIn.value && store.currentUser.value) {
    const hour = new Date().getHours()
    let g = 'Good Morning'
    if (hour >= 12 && hour < 18) g = 'Good Afternoon'
    else if (hour >= 18) g = 'Good Evening'
    return `${g}, ${store.currentUser.value.name}!`
  }
  return 'Good Morning, 访客!'
})

const avatarSrc = computed(() => {
  if (store.isLoggedIn.value && store.currentUser.value) {
    return store.currentUser.value.avatar || store.DEFAULT_AVATAR
  }
  return store.DEFAULT_AVATAR
})

function handleAvatarClick() {
  if (store.isLoggedIn.value) {
    store.navigateTo('profile')
  } else {
    store.navigateTo('login')
  }
}

function onSearch(e) {
  const val = e.target.value.trim()
  if (val) {
    store.searchQuery.value = val
    store.procurementPage.value = 1
    store.navigateTo('procurement')
  } else if (store.searchQuery.value) {
    store.searchQuery.value = ''
    if (store.currentPage.value === 'procurement') {
      store.procurementPage.value = 1
    }
  }
}
</script>

<style scoped>
.page-header {
  height: 6rem;
  background: var(--glass-bg);
  backdrop-filter: blur(28px) saturate(1.5);
  -webkit-backdrop-filter: blur(28px) saturate(1.5);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2.5rem;
  flex-shrink: 0;
  border-bottom: 1px solid var(--glass-border);
}
.header-left {}
.greeting-msg {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  font-family: var(--font-serif-display);
}
.date-text {
  font-size: 0.875rem;
  color: var(--text-tertiary);
  margin: 0;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}
.search-box {
  position: relative;
}
.search-icon {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
}
.search-input {
  width: 20rem;
  height: 3rem;
  padding: 0 1rem 0 2.75rem;
  background: rgba(255,255,255,0.45);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  font-size: 0.875rem;
  outline: none;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.06), 0 1px 0 rgba(255,255,255,0.4);
  transition: all 0.25s var(--ease-out, cubic-bezier(0.16,1,0.3,1));
}
.search-input::placeholder {
  color: var(--text-tertiary);
}
.search-input:focus {
  border-color: rgba(100,140,220,0.4);
  box-shadow: inset 0 2px 6px rgba(0,0,0,0.06), 0 0 0 4px rgba(100,140,220,0.07), 0 1px 0 rgba(255,255,255,0.4);
  background: rgba(255,255,255,0.65);
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  border-left: 1px solid var(--glass-border);
  padding-left: 1.5rem;
}
.action-btn {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 0.75rem;
  transition: all 0.2s;
}
.action-btn:hover {
  color: var(--lavender-accent);
}
.avatar-wrap {
  cursor: pointer;
}
.avatar-ring {
  width: 2.6rem;
  height: 2.6rem;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.55);
  box-shadow: 0 2px 8px rgba(0,0,0,0.08), 0 0 0 1px rgba(255,255,255,0.2);
  transition: all 0.25s var(--ease-out, cubic-bezier(0.16,1,0.3,1));
}
.avatar-ring:hover {
  box-shadow: 0 2px 12px rgba(0,0,0,0.12), 0 0 0 2px rgba(175, 82, 222, 0.25);
  border-color: rgba(255, 255, 255, 0.8);
}
.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
