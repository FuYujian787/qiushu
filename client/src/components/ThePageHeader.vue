<template>
  <header class="page-header">
    <div class="header-left">
      <h2 class="greeting-msg">{{ greetingText }}</h2>
      <p class="date-text">今天是 {{ todayDate }}，来看点新书吧</p>
    </div>
    <div class="header-right">
      <div class="search-box">
        <span class="iconify search-icon" data-icon="solar:magnifer-linear" data-width="20"></span>
        <input class="search-input" v-model="searchVal" placeholder="搜索书名、作者或 ISBN..." type="text" @input="onSearch" />
      </div>
      <div class="header-actions">
        <span class="action-btn"><span class="iconify" data-icon="solar:question-circle-linear" data-width="24"></span></span>
        <span class="action-btn notif-btn" @click="store.navigateTo('notifications')"><span class="iconify" data-icon="solar:bell-linear" data-width="24"></span></span>
        <div class="avatar-wrap" @click="handleAvatarClick">
          <div class="avatar-ring">
            <img :src="avatarSrc" alt="头像" class="avatar-img" />
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
  background: rgba(255,255,255,0.5);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2.5rem;
  flex-shrink: 0;
  border-bottom: 1px solid #f3f4f6;
}
.header-left {}
.greeting-msg {
  font-size: 1.5rem;
  font-weight: 700;
  color: #374151;
  margin: 0;
}
.date-text {
  font-size: 0.875rem;
  color: #9ca3af;
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
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}
.search-input {
  width: 20rem;
  height: 3rem;
  padding: 0 1rem 0 3rem;
  background: white;
  border: 1px solid #f3f4f6;
  border-radius: 1rem;
  font-size: 0.875rem;
  outline: none;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.search-input:focus {
  border-color: #a78bfa;
  box-shadow: 0 0 0 3px rgba(124,58,237,0.1);
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  border-left: 1px solid #e5e7eb;
  padding-left: 1.5rem;
}
.action-btn {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  cursor: pointer;
  border-radius: 0.75rem;
  transition: all 0.2s;
}
.action-btn:hover {
  color: #7c3aed;
}
.avatar-wrap {
  cursor: pointer;
}
.avatar-ring {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.75rem;
  overflow: hidden;
  transition: all 0.2s;
}
.avatar-ring:hover {
  box-shadow: 0 0 0 3px #e9d5ff;
}
.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
