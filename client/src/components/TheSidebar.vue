<template>
  <aside class="sidebar">
    <div class="sidebar-logo" @click="store.navigateTo('home')">
      <div class="logo-icon">
        <LogoIcon :size="64" />
      </div>
      <h1 class="logo-text brand-text-hover brand-underline">紫金求思</h1>
    </div>
    <nav class="sidebar-nav" id="sidebarNav">
      <a v-for="item in navItems" :key="item.page" class="sidebar-item" :class="{ 'sidebar-active': store.currentPage.value === item.page }" @click.prevent="store.navigateTo(item.page)">
        <span class="iconify mr-3" :data-icon="item.icon" data-width="22"></span>
        <span>{{ item.label }}</span>
        <span v-if="item.page === 'notifications' && hasNotifBadge" class="notif-dot"></span>
      </a>
    </nav>
    <!-- 求是书摊 — 侧栏快捷预览卡片 -->
    <div class="stall-card" v-if="statsLoaded" @click="store.navigateTo('stall')">
      <div class="stall-card-header">
        <span class="iconify" data-icon="ph:storefront-duotone" data-width="16" style="color: var(--lavender-accent);"></span>
        <span class="stall-card-title">我的书摊</span>
        <span class="stall-card-arrow">→</span>
      </div>
      <div class="stall-card-stats">
        <div class="stall-stat">
          <span class="stall-stat-value">{{ sellerStats.total_books_sold }}</span>
          <span class="stall-stat-label">已售</span>
        </div>
        <div class="stall-stat-divider"></div>
        <div class="stall-stat">
          <span class="stall-stat-value">¥{{ sellerStats.total_earnings }}</span>
          <span class="stall-stat-label">收益</span>
        </div>
      </div>
    </div>
    <div class="sidebar-footer">
      <div class="publish-btn" @click="handlePublishClick">
        <span class="iconify" data-icon="solar:add-circle-bold" data-width="24"></span>
        <span>发布闲置</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useStore } from '../stores/useStore'
import LogoIcon from './LogoIcon.vue'

const store = useStore()
const statsLoaded = ref(false)
const sellerStats = ref({ total_books_sold: 0, total_earnings: 0.00 })

const hasNotifBadge = computed(() => {
  if (!store.isLoggedIn.value || !store.currentUser.value) return false
  return store.hasUnread(store.currentUser.value.name)
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
})

watch(() => store.currentPage.value, () => {
  loadSellerStats()
})
</script>

<style scoped>
.sidebar {
  width: 16rem;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
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
  font-family: var(--font-brand);
  letter-spacing: 0.08em;
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
  border-radius: 0.75rem;
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
.sidebar-active {
  background: var(--gradient-brand);
  color: var(--text-primary);
  box-shadow: 0 4px 12px rgba(155, 142, 196, 0.3);
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

/* ===== 求是书摊 — 侧栏快捷预览卡片 ===== */
.stall-card {
  width: calc(100% - 2rem);
  margin: 0.5rem 1rem 0.25rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, rgba(243, 239, 255, 0.7), rgba(220, 208, 255, 0.25));
  border: 1px solid rgba(220, 208, 255, 0.35);
  border-radius: 1rem;
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
  padding: 1rem;
  background: var(--lavender-accent-mist);
  color: var(--lavender-accent);
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
  background: rgba(220, 208, 255, 0.3);
}
</style>
