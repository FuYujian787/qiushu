<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'
import ThemeToggle from './ThemeToggle.vue'
import api from '@/api'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const { theme, toggle } = useTheme()

const mobileMenuOpen = ref(false)
const searchQuery = ref('')
const unreadMsgCount = ref(0)
let unreadTimer = null

const navItems = [
  { name: '首页', path: '/', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { name: '浏览', path: '/browse', icon: 'M4 6h16M4 10h16M4 14h16M4 18h16' },
  { name: '消息', path: '/messages', icon: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z', requiresAuth: true, badge: true },
  { name: '发布', path: '/publish', icon: 'M12 4v16m8-8H4', requiresAuth: true },
  { name: '论坛', path: '/forum', icon: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z' },
  { name: '许愿墙', path: '/wishes', icon: 'M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z' },
  { name: '换书', path: '/exchange', icon: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15' },
  { name: '传承', path: '/tree', icon: 'M3 3v18h18M7 16l4-8 4 4 4-6' },
  { name: '我的', path: '/profile', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z', requiresAuth: true },
]

async function fetchUnreadCount() {
  if (!auth.isLoggedIn) return
  try {
    const res = await api.get('/messages/unread-count')
    unreadMsgCount.value = res.data?.count || 0
  } catch { /* ignore */ }
}

onMounted(() => {
  if (auth.isLoggedIn) {
    fetchUnreadCount()
    unreadTimer = setInterval(fetchUnreadCount, 15000)  // poll every 15s
  }
})

onUnmounted(() => {
  if (unreadTimer) clearInterval(unreadTimer)
})

const visibleNavItems = computed(() =>
  navItems.filter((item) => !item.requiresAuth || auth.isLoggedIn)
)

function handleSearch(e) {
  if (e) e.preventDefault()
  if (searchQuery.value.trim()) {
    router.push({ name: 'Browse', query: { q: searchQuery.value.trim() } })
    searchQuery.value = ''
    mobileMenuOpen.value = false
  }
}

function navigateTo(path) {
  router.push(path)
  mobileMenuOpen.value = false
}
</script>

<template>
  <nav class="navbar">
    <div class="navbar-inner">
      <!-- Logo -->
      <div class="navbar-left">
        <router-link to="/" class="logo" @click="mobileMenuOpen = false">
          <span class="logo-seal">求书</span>
          <span class="logo-text">·書緣</span>
        </router-link>
      </div>

      <!-- Desktop Nav -->
      <div class="navbar-center">
        <router-link
          v-for="item in visibleNavItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: route.path === item.path }"
        >
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path :d="item.icon" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>{{ item.name }}</span>
          <span v-if="item.badge && unreadMsgCount > 0" class="nav-badge">{{ unreadMsgCount > 99 ? '99+' : unreadMsgCount }}</span>
        </router-link>
      </div>

      <!-- Desktop Right -->
      <div class="navbar-right">
        <form class="search-mini" @submit="handleSearch">
          <input
            v-model="searchQuery"
            placeholder="搜索书籍..."
            class="search-input"
          />
          <button type="submit" class="search-btn">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
              <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </form>
        <ThemeToggle />
        <div class="auth-area">
          <template v-if="auth.isLoggedIn">
            <router-link to="/profile" class="user-btn">
              <span class="user-avatar-small">{{ (auth.currentUser?.nickname || '书友')[0] }}</span>
            </router-link>
          </template>
          <template v-else>
            <router-link to="/auth" class="login-btn">登录</router-link>
          </template>
        </div>
      </div>

      <!-- Mobile Menu Toggle -->
      <button class="mobile-toggle" @click="mobileMenuOpen = !mobileMenuOpen">
        <span></span><span></span><span></span>
      </button>
    </div>

    <!-- Mobile Menu -->
    <div class="mobile-menu" :class="{ open: mobileMenuOpen }">
      <form class="mobile-search" @submit="handleSearch">
        <input v-model="searchQuery" placeholder="搜索书籍..." class="mobile-search-input" />
      </form>
      <router-link
        v-for="item in visibleNavItems"
        :key="item.path"
        :to="item.path"
        class="mobile-nav-item"
        :class="{ active: route.path === item.path }"
        @click="navigateTo(item.path)"
      >
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path :d="item.icon" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span>{{ item.name }}</span>
        <span v-if="item.badge && unreadMsgCount > 0" class="nav-badge">{{ unreadMsgCount > 99 ? '99+' : unreadMsgCount }}</span>
      </router-link>
      <div class="mobile-auth">
        <template v-if="auth.isLoggedIn">
          <button @click="auth.logout(); mobileMenuOpen = false" class="mobile-logout">退出登录</button>
        </template>
        <template v-else>
          <router-link to="/auth" class="mobile-login" @click="mobileMenuOpen = false">登录 / 注册</router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  z-index: 1000;
  background: var(--surface-glass);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-default);
  transition: background-color 0.5s ease-in-out;
}

[data-theme="cyber"] .navbar {
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.05);
}

.navbar-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 24px;
  height: 100%;
  display: flex;
  align-items: center;
  gap: 24px;
}

.navbar-left {
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 4px;
  text-decoration: none;
}

.logo-seal {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: var(--accent-primary);
  color: #fff;
  font-family: var(--font-brush);
  font-size: 16px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.logo-text {
  font-family: var(--font-brush);
  font-size: 20px;
  color: var(--text-primary);
  transition: color 0.3s;
}

.navbar-center {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 14px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.2s;
  position: relative;
}

.nav-item:hover {
  color: var(--accent-primary);
  background: var(--accent-primary-light);
  box-shadow: 0 0 12px rgba(196, 30, 58, 0.1);
}

.nav-item.active {
  color: var(--accent-primary);
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 2px;
  background: var(--accent-primary);
  border-radius: 1px;
  box-shadow: 0 0 8px var(--accent-primary);
}

[data-theme="cyber"] .nav-item:hover {
  background: rgba(0, 212, 255, 0.08);
  box-shadow: 0 0 16px rgba(0, 212, 255, 0.15);
}

.nav-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.nav-badge {
  position: absolute;
  top: 2px;
  right: 6px;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  background: var(--accent-primary);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  line-height: 1;
}
[data-theme="cyber"] .nav-badge {
  background: #FF1744;
  box-shadow: 0 0 8px rgba(255, 23, 68, 0.5);
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.search-mini {
  display: flex;
  align-items: center;
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  padding: 0 12px;
  transition: all 0.3s;
}

.search-mini:focus-within {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px var(--accent-primary-light);
}

.search-input {
  border: none;
  background: none;
  outline: none;
  padding: 7px 8px;
  font-size: 13px;
  color: var(--text-primary);
  width: 140px;
  font-family: var(--font-body);
}

.search-btn {
  border: none;
  background: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
}

.search-btn:hover {
  color: var(--accent-primary);
}

.auth-area {
  display: flex;
  align-items: center;
}

.login-btn {
  padding: 6px 18px;
  background: var(--accent-primary);
  color: #fff !important;
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
}

.login-btn:hover {
  background: var(--accent-primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(196, 30, 58, 0.3);
}

[data-theme="cyber"] .login-btn {
  background: linear-gradient(135deg, #00D4FF, #A855F7);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
}

[data-theme="cyber"] .login-btn:hover {
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.4);
}

.user-btn {
  text-decoration: none;
}

.user-avatar-small {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--accent-primary-light);
  color: var(--accent-primary);
  font-size: 14px;
  font-weight: 600;
}

[data-theme="cyber"] .user-avatar-small {
  background: rgba(0, 212, 255, 0.12);
  color: #00D4FF;
  border: 1px solid rgba(0, 212, 255, 0.3);
}

/* Mobile Toggle */
.mobile-toggle {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
}

.mobile-toggle span {
  display: block;
  width: 22px;
  height: 2px;
  background: var(--text-primary);
  border-radius: 1px;
  transition: all 0.3s;
}

/* Mobile Menu */
.mobile-menu {
  display: none;
  position: fixed;
  top: 64px;
  left: 0;
  right: 0;
  background: var(--surface-primary);
  border-bottom: 1px solid var(--border-default);
  padding: 12px;
  flex-direction: column;
  gap: 4px;
  transform: translateY(-100%);
  opacity: 0;
  transition: all 0.3s;
  z-index: 999;
  max-height: calc(100vh - 64px);
  overflow-y: auto;
}

.mobile-menu.open {
  transform: translateY(0);
  opacity: 1;
}

.mobile-search {
  padding: 8px 0;
}

.mobile-search-input {
  width: 100%;
  padding: 10px 16px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  background: var(--surface-secondary);
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  font-family: var(--font-body);
}

.mobile-nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  color: var(--text-primary);
  text-decoration: none;
  border-radius: 8px;
  font-size: 15px;
}

.mobile-nav-item:hover,
.mobile-nav-item.active {
  background: var(--surface-tertiary);
  color: var(--accent-primary);
}

.mobile-auth {
  padding: 12px 16px;
  border-top: 1px solid var(--border-default);
  margin-top: 4px;
}

.mobile-login,
.mobile-logout {
  display: block;
  width: 100%;
  text-align: center;
  padding: 10px;
  border-radius: 8px;
  font-size: 14px;
  text-decoration: none;
}

.mobile-login {
  background: var(--accent-primary);
  color: #fff !important;
}

.mobile-logout {
  border: 1px solid var(--border-default);
  color: var(--text-secondary);
  background: none;
  cursor: pointer;
}

/* Responsive */
@media (max-width: 900px) {
  .navbar-center { display: none; }
  .search-mini { display: none; }
  .mobile-toggle { display: flex; }
  .mobile-menu { display: flex; }
}

@media (max-width: 768px) {
  .navbar { height: 56px; }
  .navbar-inner { padding: 0 16px; }
  .logo-seal { width: 32px; height: 32px; font-size: 14px; }
  .logo-text { font-size: 17px; }
  .mobile-menu { top: 56px; }
}
</style>
