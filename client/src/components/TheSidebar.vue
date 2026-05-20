<template>
  <aside class="sidebar">
    <div class="sidebar-logo" @click="store.navigateTo('home')">
      <div class="logo-icon">
        <span class="iconify" data-icon="ph:books-duotone" data-width="36"></span>
      </div>
      <h1 class="logo-text">求书</h1>
    </div>
    <nav class="sidebar-nav" id="sidebarNav">
      <a v-for="item in navItems" :key="item.page" class="sidebar-item" :class="{ 'sidebar-active': store.currentPage.value === item.page }" @click.prevent="store.navigateTo(item.page)">
        <span class="iconify mr-3" :data-icon="item.icon" data-width="22"></span>
        <span>{{ item.label }}</span>
        <span v-if="item.page === 'notifications' && hasNotifBadge" class="notif-dot"></span>
      </a>
    </nav>
    <div class="sidebar-footer">
      <div class="publish-btn" @click="handlePublishClick">
        <span class="iconify" data-icon="solar:add-circle-bold" data-width="24"></span>
        <span>发布闲置</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from '../stores/useStore'

const store = useStore()

const hasNotifBadge = computed(() => {
  if (!store.isLoggedIn.value || !store.currentUser.value) return false
  return store.hasUnread(store.currentUser.value.name)
})

const navItems = [
  { page: 'home', label: '首页', icon: 'solar:home-2-outline' },
  { page: 'procurement', label: '采购', icon: 'solar:shop-2-outline' },
  { page: 'cart', label: '购物车', icon: 'solar:cart-large-2-outline' },
  { page: 'orders', label: '订单管理', icon: 'solar:bill-list-outline' },
  { page: 'notifications', label: '消息通知', icon: 'solar:bell-bing-outline' },
  { page: 'community', label: '学习社区', icon: 'solar:users-group-two-rounded-outline' },
  { page: 'profile', label: '个人中心', icon: 'solar:user-circle-outline' },
]

function handlePublishClick() {
  if (store.isLoggedIn.value) {
    store.navigateTo('publish')
  } else {
    store.navigateTo('login')
  }
}
</script>

<style scoped>
.sidebar {
  width: 16rem;
  background: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem 0;
  box-shadow: 0 0 8px rgba(0,0,0,0.06);
  z-index: 10;
  flex-shrink: 0;
}
.sidebar-logo {
  margin-bottom: 3rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}
.logo-icon {
  width: 4rem;
  height: 4rem;
  background: #f3f4f6;
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
}
.logo-icon :deep(.iconify) {
  color: #7c3aed;
}
.logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  color: #374151;
  letter-spacing: 0.05em;
  margin: 0;
}
.sidebar-nav {
  width: 100%;
  padding: 0 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex-grow: 1;
  overflow-y: auto;
}
.sidebar-nav::-webkit-scrollbar {
  width: 4px;
}
.sidebar-nav::-webkit-scrollbar-thumb {
  background: #ddd6fe;
  border-radius: 10px;
}
.sidebar-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  color: #6b7280;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.3s ease;
  position: relative;
}
.sidebar-item:hover {
  background: rgba(139, 92, 246, 0.1);
  color: #7c3aed;
}
.sidebar-active {
  background: linear-gradient(90deg, #a78bfa, #7c3aed);
  color: white;
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
}
.notif-dot {
  position: absolute;
  right: 0.5rem;
  top: 0.5rem;
  width: 0.5rem;
  height: 0.5rem;
  background: #ef4444;
  border-radius: 50%;
}
.sidebar-footer {
  margin-top: auto;
  padding: 0 1rem;
  width: 100%;
}
.publish-btn {
  width: 100%;
  padding: 1rem;
  background: #ede9fe;
  color: #7c3aed;
  border-radius: 1rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.3s;
}
.publish-btn:hover {
  background: #ddd6fe;
}
</style>
