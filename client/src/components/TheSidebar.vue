<template>
  <aside class="sidebar apple-liquid-sidebar" role="navigation" aria-label="主导航">
    <div class="sidebar-logo" @click="store.navigateTo('home')" role="button" tabindex="0" aria-label="返回首页" @keydown.enter="store.navigateTo('home')">
      <div class="logo-icon">
        <LogoIcon :size="64" />
      </div>
      <h1 class="logo-text apple-text-gradient-accent">紫金求思</h1>
    </div>
    <nav class="sidebar-nav" id="sidebarNav" aria-label="功能导航">
      <a v-for="item in navItems" :key="item.page" 
         class="sidebar-item apple-liquid-nav-item" 
         :class="{ 'active': store.currentPage.value === item.page }" 
         @click.prevent="handleNavClick(item.page)"
         :aria-label="item.label"
         :aria-current="store.currentPage.value === item.page ? 'page' : undefined"
         role="button"
         tabindex="0"
         @keydown.enter.prevent="handleNavClick(item.page)">
        <span class="iconify mr-3" :data-icon="item.icon" data-width="22" aria-hidden="true"></span>
        <span>{{ item.label }}</span>
        <span v-if="item.page === 'notifications' && showNotifDot" class="red-dot"></span>
        <span v-if="item.page === 'chat' && showChatDot" class="red-dot"></span>
      </a>
    </nav>
    <!-- 求是书摊 — 侧栏快捷预览卡片 -->
    <div class="stall-card apple-liquid-card" v-if="statsLoaded" @click="store.navigateTo('stall')" role="button" tabindex="0" aria-label="查看我的书摊数据" @keydown.enter="store.navigateTo('stall')">
      <div class="stall-card-header">
        <span class="iconify" data-icon="ph:storefront-duotone" data-width="16" style="color: var(--apple-purple);" aria-hidden="true"></span>
        <span class="stall-card-title">我的书摊</span>
        <span class="stall-card-arrow" aria-hidden="true">→</span>
      </div>
      <div class="stall-card-stats">
        <div class="stall-stat">
          <span class="stall-stat-value apple-text-gradient-accent">{{ sellerStats.total_books_sold }}</span>
          <span class="stall-stat-label">已售</span>
        </div>
        <div class="stall-stat-divider" aria-hidden="true"></div>
        <div class="stall-stat">
          <span class="stall-stat-value apple-text-gradient-accent">¥{{ sellerStats.total_earnings }}</span>
          <span class="stall-stat-label">收益</span>
        </div>
      </div>
    </div>
    <div class="sidebar-footer">
      <div class="publish-btn apple-liquid-btn" @click="handlePublishClick" role="button" tabindex="0" aria-label="发布闲置书籍" @keydown.enter="handlePublishClick">
        <span class="iconify" data-icon="solar:add-circle-bold" data-width="24" aria-hidden="true"></span>
        <span>发布闲置</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import { useStore } from '../stores/useStore'
import LogoIcon from './LogoIcon.vue'

const store = useStore()
const statsLoaded = ref(false)
const sellerStats = ref({ total_books_sold: 0, total_earnings: 0.00 })
const API_BASE = 'http://127.0.0.1:5000'
let chatPollTimer = null

const showNotifDot = computed(() => {
  if (!store.isLoggedIn.value || !store.currentUser.value) return false
  return store.hasUnreadNotif(store.currentUser.value.name)
})

const showChatDot = computed(() => {
  if (!store.isLoggedIn.value) return false
  return store.hasChatUnread()
})

const navItems = [
  { page: 'home', label: '首页', icon: 'solar:home-2-outline' },
  { page: 'procurement', label: '采购', icon: 'solar:shop-2-outline' },
  { page: 'stall', label: '求是书摊', icon: 'ph:storefront-duotone' },
  { page: 'cart', label: '购物车', icon: 'solar:cart-large-2-outline' },
  { page: 'orders', label: '订单管理', icon: 'solar:bill-list-outline' },
  { page: 'notifications', label: '消息通知', icon: 'solar:bell-bing-outline' },
  { page: 'chat', label: '私信', icon: 'solar:chat-round-dots-outline' },
  { page: 'community', label: '学习社区', icon: 'solar:users-group-two-rounded-outline' },
  { page: 'profile', label: '个人中心', icon: 'solar:user-circle-outline' },
]

function handleNavClick(page) {
  if (page === 'notifications' && store.currentUser.value) {
    store.markNotifRead()
  }
  if (page === 'chat') {
    store.resetChatUnreadCount()
  }
  store.navigateTo(page)
}

function handlePublishClick() {
  if (store.isLoggedIn.value) {
    store.navigateTo('publish')
  } else {
    store.navigateTo('login')
  }
}

function loadSellerStats() {
  if (!store.isLoggedIn.value || !store.currentUser.value) {
    statsLoaded.value = false
    return
  }
  try {
    const data = store.fetchSellerStats(store.currentUser.value.name)
    if (data.success) {
      sellerStats.value = {
        total_books_sold: data.total_books_sold ?? 0,
        total_earnings: data.total_earnings ?? 0.00,
      }
      statsLoaded.value = true
    }
  } catch (e) {
    statsLoaded.value = false
  }
}

onMounted(() => {
  loadSellerStats()
  startChatPolling()
})

onUnmounted(() => {
  stopChatPolling()
})

watch(() => store.currentPage.value, () => {
  loadSellerStats()
})

/** 轻量轮询：当不在私信页面时，定时获取私信未读数 */
async function pollChatUnread() {
  if (!store.isLoggedIn.value || !store.currentUser.value) return
  if (store.currentPage.value === 'chat') return
  try {
    const userName = store.currentUser.value.name
    const res = await fetch(`${API_BASE}/api/chat/conversations?user=${encodeURIComponent(userName)}`)
    const data = await res.json()
    if (data.success && data.conversations) {
      const total = data.conversations.reduce((sum, c) => sum + (c.unreadCount || 0), 0)
      if (total > 0) {
        store.updateChatUnreadCount(total)
      }
    }
  } catch {
    // 后端未启动时静默失败
  }
}

function startChatPolling() {
  stopChatPolling()
  chatPollTimer = setInterval(pollChatUnread, 10000)
}

function stopChatPolling() {
  if (chatPollTimer) {
    clearInterval(chatPollTimer)
    chatPollTimer = null
  }
}
</script>

<style scoped>
.sidebar {
  width: 16rem;
  background: var(--glass-bg);
  backdrop-filter: blur(28px) saturate(1.5);
  -webkit-backdrop-filter: blur(28px) saturate(1.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem 0;
  border-right: 1px solid var(--glass-border);
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
  width: 5rem;
  height: 5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
}
.logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  font-family: var(--font-serif-display);
  letter-spacing: 0.06em;
  line-height: 1.3;
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
  background: var(--lavender-primary);
  border-radius: 10px;
}
.sidebar-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  color: var(--text-secondary);
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.3s ease;
  position: relative;
}
.sidebar-item:hover {
  background: var(--lavender-accent-mist);
  color: var(--lavender-accent);
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

/* 统一红点组件 — 带脉冲动画 */
.red-dot {
  position: absolute;
  right: 0.5rem;
  top: 0.5rem;
  width: 0.6rem;
  height: 0.6rem;
  background: #ff3b30;
  border-radius: 50%;
  box-shadow: 0 0 6px rgba(255, 59, 48, 0.5);
  animation: redDotPulse 2s ease-in-out infinite;
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.red-dot::before {
  content: '';
  position: absolute;
  inset: -3px;
  border-radius: 50%;
  border: 2px solid rgba(255, 59, 48, 0.3);
  animation: redDotRing 2s ease-in-out infinite;
}

@keyframes redDotPulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 6px rgba(255, 59, 48, 0.5);
  }
  50% {
    transform: scale(1.15);
    box-shadow: 0 0 12px rgba(255, 59, 48, 0.8);
  }
}

@keyframes redDotRing {
  0%, 100% {
    transform: scale(1);
    opacity: 0.4;
  }
  50% {
    transform: scale(1.4);
    opacity: 0;
  }
}

/* ===== 求是书摊 — 侧栏快捷预览卡片 ===== */
.stall-card {
  width: calc(100% - 2rem);
  margin: 0.5rem 1rem 0.25rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, rgba(243, 239, 255, 0.7), rgba(220, 208, 255, 0.25));
  border: 1px solid rgba(220, 208, 255, 0.35);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  position: relative;
  overflow: hidden;
  flex-shrink: 0;
}

.stall-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--lavender-primary), transparent);
  opacity: 0.6;
}

.stall-card:hover {
  border-color: rgba(220, 208, 255, 0.6);
  box-shadow: 0 4px 16px rgba(155, 142, 196, 0.15);
  transform: translateY(-1px);
}

.stall-card-header {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  margin-bottom: 0.5rem;
}

.stall-card-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.04em;
  flex: 1;
}

.stall-card-arrow {
  font-size: 0.7rem;
  color: var(--text-tertiary);
  transition: transform 0.3s ease;
}

.stall-card:hover .stall-card-arrow {
  transform: translateX(3px);
  color: var(--lavender-accent);
}

.stall-card-stats {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.stall-stat {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
  flex: 1;
}

.stall-stat-value {
  font-size: 1.1rem;
  font-weight: 800;
  background: linear-gradient(135deg, #8A2BE2, #7B68EE);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
}

.stall-stat-label {
  font-size: 0.7rem;
  color: var(--text-tertiary);
  font-weight: 500;
}

.stall-stat-divider {
  width: 1px;
  height: 1.5rem;
  background: rgba(220, 208, 255, 0.3);
}

.sidebar-footer {
  margin-top: auto;
  padding: 0 1rem;
  width: 100%;
}
.publish-btn {
  width: 86%;
  padding: 0.85rem 1rem;
  background: linear-gradient(135deg, #6c3fc0 0%, #9b59b6 40%, #af52de 100%);
  color: #fff;
  border: none;
  border-radius: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(108, 63, 192, 0.3), 0 0 0 1px rgba(255,255,255,0.12);
  transition: all 0.25s cubic-bezier(0.16,1,0.3,1);
  letter-spacing: 0.02em;
}
.publish-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(108, 63, 192, 0.4), 0 0 0 1px rgba(255,255,255,0.2);
  filter: brightness(1.08);
}
.publish-btn:active {
  transform: scale(0.97);
  filter: brightness(0.95);
}
</style>
