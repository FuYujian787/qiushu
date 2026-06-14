<template>
  <div class="bookstall-page">
    <div v-if="!store.isLoggedIn.value" class="empty-state">
      <span class="iconify" data-icon="ph:storefront-duotone" data-width="48"></span>
      <p>请先登录后查看您的书摊</p>
      <button class="login-btn" @click="store.navigateTo('login')">去登录</button>
    </div>
    <div v-else-if="!statsLoaded" class="loading-state">
      <span class="iconify spin" data-icon="svg-spinners:ring-resize" data-width="32"></span>
      <p>加载中...</p>
    </div>
    <div v-else class="bookstall-content">
      <!-- 书摊头部 -->
      <div class="bookstall-header glass-card">
        <div class="header-avatar">
          <img :src="userAvatar" class="avatar-img" />
        </div>
        <div class="header-info">
          <h2 class="stall-name">{{ store.currentUser.value.name }} 的书摊</h2>
          <p class="stall-motto">求是书香，传承知识</p>
        </div>
        <div class="header-badge">
          <span class="iconify" data-icon="ph:crown-duotone" data-width="20"></span>
          <span>求是卖家</span>
        </div>
      </div>

      <!-- 统计数据 -->
      <div class="stats-grid">
        <div class="stat-card glass-card">
          <div class="stat-icon sold-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 256 256"><path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40Zm0,160H40V56H216V200ZM184,96a56,56,0,0,1-112,0,8,8,0,0,1,16,0,40,40,0,0,0,80,0,8,8,0,0,1,16,0Z" fill="currentColor"/></svg>
          </div>
          <div class="stat-body">
            <span class="stat-label">已售出</span>
            <span class="stat-value">{{ sellerStats.total_books_sold }}</span>
            <span class="stat-unit">本</span>
          </div>
        </div>
        <div class="stat-card glass-card">
          <div class="stat-icon earn-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 256 256"><path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm0,192a88,88,0,1,1,88-88A88.1,88.1,0,0,1,128,216Zm12-56h-8V136h8a20,20,0,0,1,0,40Zm0-56h-8V80h8a20,20,0,0,1,0,40Zm0-56a36,36,0,0,0-36,36v8H92a8,8,0,0,0,0,16h12v16H92a8,8,0,0,0,0,16h12v8a36,36,0,0,0,72,0,8,8,0,0,0-16,0,20,20,0,0,1-40,0v-8h8a36,36,0,0,0,0-72Z" fill="currentColor"/></svg>
          </div>
          <div class="stat-body">
            <span class="stat-label">累计收入</span>
            <span class="stat-value">¥{{ sellerStats.total_earnings }}</span>
          </div>
        </div>
        <div class="stat-card glass-card">
          <div class="stat-icon publish-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 256 256"><path d="M215.79,118.17a8,8,0,0,0-5-5.66L153.18,90.9l14.66-73.33a8,8,0,0,0-13.69-7l-112,120a8,8,0,0,0,3,13l57.63,21.61L88.16,238.43a8,8,0,0,0,13.69,7l112-120A8,8,0,0,0,215.79,118.17ZM109.37,214l10.47-52.38a8,8,0,0,0-5-9.06L62,132.71l81.25-87.05L132.78,98.15a8,8,0,0,0,5,9.06l52.8,19.8Z" fill="currentColor"/></svg>
          </div>
          <div class="stat-body">
            <span class="stat-label">快速操作</span>
            <button class="quick-publish-btn" @click="goPublish">
              <span class="iconify" data-icon="ph:plus-bold" data-width="14"></span>
              发布新书
            </button>
          </div>
        </div>
      </div>

      <!-- 在售书籍 -->
      <div class="section">
        <div class="section-header">
          <h3>我的在售书籍</h3>
          <span class="section-count">共 {{ myBooks.length }} 本</span>
        </div>
        <div class="books-grid">
          <div v-for="book in myBooks" :key="book.id" class="book-card glass-card" @click="openDetail(book.id)">
            <div class="book-cover">
              <img :src="book.img" :alt="book.title" class="cover-img" />
            </div>
            <div class="book-info">
              <h4 class="book-title">{{ book.title }}</h4>
              <p class="book-condition">{{ book.condition }}</p>
              <p class="book-price">¥{{ book.price }}</p>
            </div>
          </div>
          <div v-if="myBooks.length === 0" class="empty-books">
            <span class="iconify" data-icon="ph:package-duotone" data-width="40"></span>
            <p>暂无在售书籍</p>
            <button class="publish-link" @click="goPublish">去发布第一本书</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useStore } from '../../stores/useStore'
import { ElMessage } from 'element-plus'

const store = useStore()
const statsLoaded = ref(false)
const sellerStats = ref({ total_books_sold: 0, total_earnings: 0.00 })
const myBooks = ref([])

const userAvatar = computed(() => {
  if (store.currentUser.value?.avatar) return store.currentUser.value.avatar
  return store.DEFAULT_AVATAR
})

onMounted(async () => {
  await Promise.all([loadSellerStats(), loadMyBooks()])
  statsLoaded.value = true
})

async function loadSellerStats() {
  if (!store.isLoggedIn.value || !store.currentUser.value) return
  try {
    const data = await store.fetchSellerStats(store.currentUser.value.name)
    if (data.success) {
      sellerStats.value = {
        total_books_sold: data.total_books_sold ?? 0,
        total_earnings: data.total_earnings ?? 0.00,
      }
    }
  } catch (e) {
    // 静默失败
  }
}

async function loadMyBooks() {
  if (!store.isLoggedIn.value || !store.currentUser.value) return
  try {
    const data = await store.fetchUserBooks(store.currentUser.value.name)
    if (data.books) {
      myBooks.value = data.books
    }
  } catch (e) {
    // 静默失败
  }
}

function goPublish() {
  store.navigateTo('publish')
}

function openDetail(id) {
  store.navigateTo('bookDetail', id)
}
</script>

<style scoped>
.bookstall-page {
  max-width: 56rem;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ===== 空状态 ===== */
.empty-state,
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: var(--text-tertiary);
  gap: 1rem;
}
.empty-state p,
.loading-state p {
  margin: 0;
  font-size: 1rem;
}
.login-btn {
  padding: 0.6rem 1.5rem;
  background: linear-gradient(135deg, var(--lavender-primary), var(--lavender-primary-dark));
  border: none;
  border-radius: 0.75rem;
  font-weight: 700;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}
.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(155, 142, 196, 0.2);
}

/* ===== 书摊头部 ===== */
.bookstall-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.5rem 2rem;
}
.header-avatar {
  width: 4rem;
  height: 4rem;
  border-radius: 1rem;
  overflow: hidden;
  border: 2px solid var(--glass-border);
  flex-shrink: 0;
}
.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.header-info {
  flex: 1;
}
.stall-name {
  font-size: 1.35rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}
.stall-motto {
  font-size: 0.8rem;
  color: var(--text-tertiary);
  margin: 0.25rem 0 0 0;
}
.header-badge {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.9rem;
  background: linear-gradient(135deg, var(--lavender-primary), var(--lavender-primary-dark));
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-primary);
}

/* ===== 统计卡片 ===== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
}
.stat-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.sold-icon {
  background: rgba(138, 43, 226, 0.1);
}
.sold-icon .iconify { color: #8A2BE2; }
.earn-icon {
  background: rgba(123, 104, 238, 0.1);
}
.earn-icon .iconify { color: #7B68EE; }
.publish-icon {
  background: rgba(220, 208, 255, 0.2);
}
.publish-icon .iconify { color: var(--lavender-accent); }
.stat-body {
  display: flex;
  flex-direction: column;
}
.stat-label {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  font-weight: 500;
}
.stat-value {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.2;
}
.stat-unit {
  font-size: 0.75rem;
  color: var(--text-tertiary);
}
.quick-publish-btn {
  margin-top: 0.35rem;
  padding: 0.35rem 0.85rem;
  background: linear-gradient(135deg, var(--lavender-primary), var(--lavender-primary-dark));
  border: none;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.2rem;
  transition: all 0.2s;
}
.quick-publish-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(155, 142, 196, 0.2);
}

/* ===== 在售书籍 ===== */
.section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.section-header h3 {
  font-size: 1.125rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}
.section-count {
  font-size: 0.8rem;
  color: var(--text-tertiary);
}
.books-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}
.book-card {
  padding: 1rem;
  border-radius: 16px;
  cursor: pointer;
  transition: all var(--transition-normal);
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  backdrop-filter: blur(20px) saturate(1.3);
  -webkit-backdrop-filter: blur(20px) saturate(1.3);
}
.book-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--glass-shadow-hover);
  border-color: var(--glass-border-hover);
}
.book-cover {
  width: 100%;
  aspect-ratio: 3/4;
  background: rgba(255,255,255,0.5);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.75rem;
}
.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.book-info {}
.book-title {
  font-size: 0.85rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.book-condition {
  font-size: 0.7rem;
  color: var(--text-caption);
  margin: 0.2rem 0;
}
.book-price {
  font-size: 0.95rem;
  font-weight: 600;
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
  color: var(--text-primary);
  margin: 0.35rem 0 0 0;
  letter-spacing: -0.02em;
}
.empty-books {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem;
  color: var(--text-tertiary);
  gap: 0.75rem;
}
.empty-books p {
  margin: 0;
  font-size: 0.9rem;
}
.publish-link {
  padding: 0.5rem 1.25rem;
  background: linear-gradient(135deg, var(--lavender-primary), var(--lavender-primary-dark));
  border: none;
  border-radius: 0.75rem;
  font-weight: 700;
  font-size: 0.85rem;
  color: var(--text-primary);
  cursor: pointer;
}
.publish-link:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(155, 142, 196, 0.2);
}

/* ===== 动画 ===== */
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>