<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox } from 'element-plus'
import api from '@/api'
import UserInfoEdit from '@/components/UserInfoEdit.vue'
import MyBooksList from '@/components/MyBooksList.vue'
import MyOrdersList from '@/components/MyOrdersList.vue'
import MyFavoritesList from '@/components/MyFavoritesList.vue'

const router = useRouter()
const auth = useAuthStore()

const activeTab = ref('books')
const profile = ref({})
const stats = ref({ books_count: 0, sold_count: 0, favorites_count: 0 })
const myBooks = ref([])
const myOrders = ref([])
const myFavorites = ref([])
const loadingBooks = ref(false)
const loadingOrders = ref(false)
const loadingFavs = ref(false)

const tabs = [
  { key: 'info', label: '个人信息' },
  { key: 'books', label: '我的发布' },
  { key: 'orders', label: '我的订单' },
  { key: 'favorites', label: '我的收藏' },
]

onMounted(async () => {
  if (!auth.isLoggedIn) {
    router.push({ name: 'Auth', query: { redirect: '/profile' } })
    return
  }
  await loadProfile()
  await loadBooks()
  await loadOrders()
  await loadFavorites()
})

async function loadProfile() {
  try {
    const res = await api.get('/user/profile')
    if (res.data) {
      profile.value = res.data
      stats.value = res.data.stats || stats.value
    }
  } catch { /* ignore */ }
}

async function loadBooks() {
  loadingBooks.value = true
  try {
    const res = await api.get('/user/books')
    myBooks.value = res.data?.books || []
  } catch { /* ignore */ }
  finally { loadingBooks.value = false }
}

async function loadOrders() {
  loadingOrders.value = true
  try {
    const res = await api.get('/user/orders')
    myOrders.value = res.data?.orders || []
  } catch { /* ignore */ }
  finally { loadingOrders.value = false }
}

async function loadFavorites() {
  loadingFavs.value = true
  try {
    const res = await api.get('/favorites')
    myFavorites.value = res.data || []
  } catch { /* ignore */ }
  finally { loadingFavs.value = false }
}

function onProfileSaved(updated) {
  Object.assign(profile.value, updated)
  auth.fetchProfile()
}

async function onRemoveFavorite(bookId) {
  try {
    await api.delete(`/favorites/${bookId}`)
    await loadFavorites()
    stats.value.favorites_count = Math.max(0, stats.value.favorites_count - 1)
  } catch { /* ignore */ }
}

function goToBook(book) {
  router.push({ name: 'BookDetail', params: { id: book.id } })
}

function goToOrder(order) {
  router.push({ name: 'Orders' })
}

function handleLogout() {
  ElMessageBox.confirm('确定退出登录？').then(async () => {
    await auth.logout()
    router.push('/')
  }).catch(() => {})
}
</script>

<template>
  <div class="profile-page page-enter">
    <div class="page-container">
      <!-- User Header -->
      <div class="profile-header">
        <div class="avatar">
          <span class="avatar-text">{{ (profile.nickname || '书')[0] }}</span>
        </div>
        <div class="user-summary">
          <h2 class="user-name">{{ profile.nickname || '书友' }}</h2>
          <p class="user-detail">
            {{ profile.college || '未设置学院' }}
            <span v-if="profile.major">· {{ profile.major }}</span>
            <span v-if="profile.grade">· {{ profile.grade }}</span>
          </p>
          <div class="user-stats">
            <div class="stat">
              <span class="stat-num">{{ stats.books_count }}</span>
              <span class="stat-label">发布</span>
            </div>
            <div class="stat">
              <span class="stat-num">{{ stats.sold_count }}</span>
              <span class="stat-label">已售</span>
            </div>
            <div class="stat">
              <span class="stat-num">{{ stats.favorites_count }}</span>
              <span class="stat-label">收藏</span>
            </div>
          </div>
        </div>
        <button class="logout-btn" @click="handleLogout">退出登录</button>
      </div>

      <!-- Tabs -->
      <div class="profile-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          :class="['tab', { active: activeTab === tab.key }]"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <UserInfoEdit
          v-if="activeTab === 'info'"
          :user="profile"
          @save="onProfileSaved"
        />

        <MyBooksList
          v-if="activeTab === 'books'"
          :books="myBooks"
          :loading="loadingBooks"
          @book-click="goToBook"
        />

        <MyOrdersList
          v-if="activeTab === 'orders'"
          :orders="myOrders"
          :loading="loadingOrders"
          @order-click="goToOrder"
        />

        <MyFavoritesList
          v-if="activeTab === 'favorites'"
          :favorites="myFavorites"
          :loading="loadingFavs"
          @book-click="goToBook"
          @remove="onRemoveFavorite"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-header {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 32px;
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  margin-bottom: 24px;
}

.avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: var(--accent-primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar-text {
  font-size: 28px;
  font-weight: 700;
  color: var(--accent-primary);
  font-family: var(--font-display);
}

[data-theme="cyber"] .avatar-text { color: #00D4FF; }

.user-summary { flex: 1; min-width: 0; }

.user-name {
  font-family: var(--font-display);
  font-size: 20px;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.user-detail { color: var(--text-muted); font-size: 13px; }

.user-stats { display: flex; gap: 24px; margin-top: 12px; }

.stat { text-align: center; }

.stat-num {
  display: block;
  font-family: var(--font-mono);
  font-size: 18px;
  font-weight: 700;
  color: var(--accent-primary);
}

.stat-label { font-size: 11px; color: var(--text-muted); }

[data-theme="cyber"] .stat-num { color: #00D4FF; }

.logout-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-default);
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  background: transparent;
  color: var(--text-secondary);
  white-space: nowrap;
  align-self: flex-start;
  transition: all 0.2s;
}

.logout-btn:hover { border-color: #C41E3A; color: #C41E3A; }
[data-theme="cyber"] .logout-btn:hover { border-color: #ff4d6a; color: #ff4d6a; }

.profile-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 20px;
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  padding: 4px;
  width: fit-content;
}

.tab {
  padding: 8px 20px;
  border: none;
  background: none;
  border-radius: 6px;
  font-size: 14px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.tab:hover { color: var(--text-primary); }

.tab.active {
  background: var(--accent-primary);
  color: #fff;
  font-weight: 500;
}

[data-theme="cyber"] .tab.active {
  background: linear-gradient(135deg, #00D4FF, #A855F7);
}

@media (max-width: 768px) {
  .profile-header { flex-wrap: wrap; gap: 16px; padding: 20px; }
  .profile-tabs { width: 100%; overflow-x: auto; }
}
</style>
