<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import api from '@/api'

const router = useRouter()
const auth = useAuthStore()

// State
const books = ref([])
const matches = ref([])
const myBooks = ref([])
const loading = ref(false)
const activeTab = ref('browse') // browse | matches | my

// Filters
const searchQuery = ref('')
const filterCategory = ref('')
const filterCondition = ref('')
const currentPage = ref(1)
const totalBooks = ref(0)
const totalPages = ref(1)

const categories = ['数学', '计算机', '外语', '经管', '理工', '人文']
const conditions = ['全新', '良好', '有笔记', '旧']

const tabs = [
  { key: 'browse', label: '浏览换书', icon: '📚' },
  { key: 'matches', label: '智能匹配', icon: '🔗' },
  { key: 'my', label: '我的换书', icon: '📦' },
]

// Methods
async function fetchBooks(page = 1) {
  loading.value = true
  try {
    const params = { page, per_page: 20 }
    if (searchQuery.value) params.q = searchQuery.value
    if (filterCategory.value) params.category = filterCategory.value
    if (filterCondition.value) params.condition = filterCondition.value

    const res = await api.get('/exchange', { params })
    books.value = res.data?.books || []
    totalBooks.value = res.data?.total || 0
    totalPages.value = res.data?.pages || 1
    currentPage.value = res.data?.page || 1
  } catch {
    books.value = []
  } finally {
    loading.value = false
  }
}

async function fetchMatches() {
  loading.value = true
  try {
    const res = await api.get('/exchange/matches')
    matches.value = res.data?.matches || []
  } catch {
    matches.value = []
  } finally {
    loading.value = false
  }
}

async function fetchMyBooks() {
  if (!auth.isLoggedIn) { myBooks.value = []; return }
  loading.value = true
  try {
    const res = await api.get('/exchange/my')
    myBooks.value = res.data?.books || []
  } catch {
    myBooks.value = []
  } finally {
    loading.value = false
  }
}

async function toggleExchange(bookId) {
  try {
    const res = await api.post(`/exchange/toggle/${bookId}`)
    ElMessage.success(res.message || '操作成功')
    await fetchMyBooks()
    if (activeTab.value === 'browse') await fetchBooks(currentPage.value)
  } catch (err) {
    ElMessage.error(err.message || '操作失败')
  }
}

function switchTab(tab) {
  activeTab.value = tab
  if (tab === 'browse') fetchBooks(1)
  else if (tab === 'matches') fetchMatches()
  else if (tab === 'my') fetchMyBooks()
}

function goToBook(id) {
  router.push({ name: 'BookDetail', params: { id } })
}

function changePage(page) {
  currentPage.value = page
  fetchBooks(page)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// Debounced search
let searchTimer = null
watch([searchQuery, filterCategory, filterCondition], () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => fetchBooks(1), 300)
})

onMounted(() => {
  fetchBooks(1)
})

const highlightMatch = (bookTitle, wantedTitle) => {
  if (!bookTitle || !wantedTitle) return bookTitle
  // Simple highlight by returning both; the template will handle display
  return bookTitle
}
</script>

<template>
  <div class="exchange-page page-enter">
    <div class="page-container">
      <!-- Header -->
      <div class="exchange-header">
        <h1 class="page-title">🔄 以书换书</h1>
        <p class="page-subtitle">用闲置教材换你需要的书，零现金交流</p>
      </div>

      <!-- Tabs -->
      <div class="tab-bar">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          :class="['tab-btn', { active: activeTab === tab.key }]"
          @click="switchTab(tab.key)"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <!-- ============ BROWSE TAB ============ -->
      <div v-if="activeTab === 'browse'" class="tab-content">
        <!-- Filters -->
        <div class="filter-bar">
          <input
            v-model="searchQuery"
            placeholder="搜索书名或作者..."
            class="filter-search"
          />
          <select v-model="filterCategory" class="filter-select">
            <option value="">全部分类</option>
            <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
          </select>
          <select v-model="filterCondition" class="filter-select">
            <option value="">全部书况</option>
            <option v-for="con in conditions" :key="con" :value="con">{{ con }}</option>
          </select>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="loading-state">
          <div class="skeleton-grid">
            <div v-for="n in 6" :key="n" class="skeleton-card"></div>
          </div>
        </div>

        <!-- Empty -->
        <div v-else-if="books.length === 0" class="empty-state">
          <div class="empty-icon">📚</div>
          <p class="empty-title">暂无可交换的书籍</p>
          <p class="empty-hint">成为第一个开启以书换书的用户吧</p>
        </div>

        <!-- Book Grid -->
        <div v-else class="exchange-grid">
          <div
            v-for="book in books"
            :key="book.id"
            class="exchange-card"
            @click="goToBook(book.id)"
          >
            <!-- Match Badge -->
            <span v-if="book.has_wanted_match" class="match-badge" title="有人正在求购此书！">
              🔗 可匹配
            </span>

            <!-- Cover -->
            <div class="card-cover">
              <img
                :src="(book.image && book.image.startsWith('/')) ? book.image : `/mock/${book.image || 'images/_5_鱼鱼何包蛋_来自小红书网页版.jpg'}`"
                :alt="book.title"
                @error="$event.target.src = '/mock/images/_5_鱼鱼何包蛋_来自小红书网页版.jpg'"
              />
            </div>

            <!-- Info -->
            <div class="card-info">
              <h3 class="card-title">{{ book.title }}</h3>
              <p class="card-author">{{ book.author }}</p>
              <div class="card-bottom">
                <span class="card-price">
                  <span class="price-symbol">¥</span>{{ book.price }}
                </span>
                <span class="card-condition">{{ book.condition }}</span>
              </div>
              <p v-if="book.seller_name" class="card-seller">{{ book.seller_name }} · {{ book.seller_college || '浙大' }}</p>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="pagination-bar">
          <button
            :disabled="currentPage <= 1"
            @click="changePage(currentPage - 1)"
            class="page-btn"
          >
            ← 上一页
          </button>
          <span class="page-info">{{ currentPage }} / {{ totalPages }}（共 {{ totalBooks }} 本）</span>
          <button
            :disabled="currentPage >= totalPages"
            @click="changePage(currentPage + 1)"
            class="page-btn"
          >
            下一页 →
          </button>
        </div>
      </div>

      <!-- ============ MATCHES TAB ============ -->
      <div v-if="activeTab === 'matches'" class="tab-content">
        <div v-if="loading" class="loading-state">
          <p>正在智能匹配...</p>
        </div>
        <div v-else-if="matches.length === 0" class="empty-state">
          <div class="empty-icon">🔗</div>
          <p class="empty-title">暂无匹配</p>
          <p class="empty-hint">当有人发布的换书与求购帖匹配时，会自动出现在这里</p>
        </div>
        <div v-else class="matches-list">
          <div
            v-for="(match, i) in matches"
            :key="i"
            class="match-item"
          >
            <div class="match-card offer-card" @click="goToBook(match.book.id)">
              <span class="match-label">提供</span>
              <h4>{{ match.book.title }}</h4>
              <p class="match-price">¥{{ match.book.price }}</p>
              <p class="match-seller">{{ match.book.seller_name || '书友' }}</p>
            </div>
            <div class="match-connector">
              <span class="match-type-badge" :class="match.match_score">
                {{ match.match_score === 'exact' ? '精确匹配' : '模糊匹配' }}
              </span>
              <span class="match-arrow">⟷</span>
            </div>
            <div class="match-card want-card">
              <span class="match-label want-label">求购</span>
              <h4>{{ match.wanted.title }}</h4>
              <p class="match-author">{{ match.wanted.author }}</p>
              <p class="match-requester">{{ match.wanted.user_name || '书友' }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- ============ MY BOOKS TAB ============ -->
      <div v-if="activeTab === 'my'" class="tab-content">
        <div v-if="!auth.isLoggedIn" class="empty-state">
          <div class="empty-icon">🔐</div>
          <p class="empty-title">请先登录</p>
          <p class="empty-hint">登录后可以管理你的换书列表</p>
        </div>
        <div v-else-if="loading" class="loading-state">
          <p>加载中...</p>
        </div>
        <div v-else-if="myBooks.length === 0" class="empty-state">
          <div class="empty-icon">📦</div>
          <p class="empty-title">你还没有发布任何书籍</p>
          <p class="empty-hint">发布书籍后，可以在详情页开启以书换书</p>
        </div>
        <div v-else class="my-books-list">
          <div
            v-for="book in myBooks"
            :key="book.id"
            :class="['my-book-item', { exchangeable: book.accept_exchange }]"
          >
            <div class="my-book-info" @click="goToBook(book.id)">
              <img
                :src="(book.image && book.image.startsWith('/')) ? book.image : `/mock/${book.image || 'images/_5_鱼鱼何包蛋_来自小红书网页版.jpg'}`"
                :alt="book.title"
                class="my-book-cover"
                @error="$event.target.src = '/mock/images/_5_鱼鱼何包蛋_来自小红书网页版.jpg'"
              />
              <div class="my-book-details">
                <h4>{{ book.title }}</h4>
                <p>{{ book.author }} · ¥{{ book.price }} · {{ book.condition }}</p>
              </div>
            </div>
            <button
              :class="['exchange-toggle-btn', { on: book.accept_exchange }]"
              @click.stop="toggleExchange(book.id)"
            >
              {{ book.accept_exchange ? '✓ 已开启交换' : '开启交换' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ========== Header ========== */
.exchange-header {
  text-align: center;
  margin-bottom: 28px;
}
.page-title {
  font-family: var(--font-display);
  font-size: 28px;
  color: var(--text-primary);
  font-weight: 700;
  margin-bottom: 8px;
}
.page-subtitle {
  color: var(--text-muted);
  font-size: 14px;
}

/* ========== Tabs ========== */
.tab-bar {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--border-default);
  padding-bottom: 0;
}
.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border: none;
  background: none;
  color: var(--text-muted);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  font-family: var(--font-body);
}
.tab-btn:hover {
  color: var(--text-primary);
}
.tab-btn.active {
  color: var(--accent-primary);
  border-bottom-color: var(--accent-primary);
}
.tab-icon { font-size: 16px; }

/* ========== Filter Bar ========== */
.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.filter-search {
  flex: 1;
  min-width: 200px;
  padding: 10px 16px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  background: var(--surface-secondary);
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  font-family: var(--font-body);
  transition: border-color 0.2s;
}
.filter-search:focus {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px var(--accent-primary-light);
}
.filter-select {
  padding: 10px 14px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  background: var(--surface-secondary);
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
  cursor: pointer;
  font-family: var(--font-body);
}

/* ========== Exchange Grid ========== */
.exchange-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}
.exchange-card {
  position: relative;
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.25s ease;
}
.exchange-card:hover {
  border-color: var(--accent-primary);
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}
[data-theme="cyber"] .exchange-card:hover {
  box-shadow: 0 0 20px rgba(0,212,255,0.15);
}

/* Match Badge */
.match-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 2;
  background: linear-gradient(135deg, #5B8C5A, #4CAF50);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(76,175,80,0.3);
}

/* Card Cover */
.card-cover {
  width: 100%;
  aspect-ratio: 3/4;
  overflow: hidden;
  background: var(--surface-tertiary);
}
.card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}
.exchange-card:hover .card-cover img {
  transform: scale(1.04);
}

/* Card Info */
.card-info {
  padding: 14px;
}
.card-title {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 600;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.card-author {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 10px;
}
.card-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.card-price {
  font-family: var(--font-mono);
  font-size: 18px;
  font-weight: 700;
  color: var(--accent-primary);
}
.price-symbol { font-size: 12px; }
.card-condition {
  font-size: 11px;
  color: var(--text-muted);
  background: var(--surface-tertiary);
  padding: 2px 8px;
  border-radius: 4px;
}
.card-seller {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 8px;
}

/* ========== Matches List ========== */
.matches-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.match-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  transition: all 0.2s;
}
.match-item:hover {
  border-color: var(--accent-primary-light);
}
.match-card {
  flex: 1;
  padding: 12px;
  background: var(--surface-primary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
}
.match-card:hover {
  background: var(--surface-tertiary);
}
.offer-card { border-left: 3px solid #5B8C5A; }
.want-card { border-left: 3px solid #C41E3A; }
.match-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.offer-card .match-label { color: #5B8C5A; }
.want-label { color: #C41E3A; }
.match-card h4 {
  font-size: 15px;
  color: var(--text-primary);
  margin: 4px 0;
}
.match-card p {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0;
}
.match-connector {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}
.match-type-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 10px;
}
.match-type-badge.exact {
  background: #E8F5E9;
  color: #2E7D32;
}
.match-type-badge.partial {
  background: #FFF8E1;
  color: #F57F17;
}
.match-arrow {
  font-size: 20px;
  color: var(--accent-primary);
}

/* ========== My Books ========== */
.my-books-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.my-book-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  gap: 16px;
  transition: all 0.2s;
}
.my-book-item.exchangeable {
  border-color: var(--accent-secondary);
  background: rgba(91,140,90,0.03);
}
[data-theme="cyber"] .my-book-item.exchangeable {
  border-color: rgba(0,212,255,0.3);
  background: rgba(0,212,255,0.03);
}
.my-book-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  cursor: pointer;
  min-width: 0;
}
.my-book-cover {
  width: 48px;
  height: 64px;
  object-fit: cover;
  border-radius: 4px;
  flex-shrink: 0;
}
.my-book-details h4 {
  font-size: 14px;
  color: var(--text-primary);
  margin: 0 0 2px 0;
}
.my-book-details p {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0;
}
.exchange-toggle-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  background: var(--surface-primary);
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  font-family: var(--font-body);
}
.exchange-toggle-btn:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}
.exchange-toggle-btn.on {
  background: var(--accent-secondary);
  color: #fff;
  border-color: var(--accent-secondary);
}

/* ========== States ========== */
.loading-state {
  text-align: center;
  padding: 60px 24px;
  color: var(--text-muted);
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 24px;
  text-align: center;
}
.empty-icon { font-size: 48px; margin-bottom: 14px; }
.empty-title { font-size: 16px; color: var(--text-primary); font-weight: 600; margin-bottom: 6px; }
.empty-hint { font-size: 13px; color: var(--text-muted); max-width: 320px; }

/* ========== Pagination ========== */
.pagination-bar {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 32px;
  padding-top: 20px;
}
.page-btn {
  padding: 8px 18px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  background: var(--surface-secondary);
  color: var(--text-primary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: var(--font-body);
}
.page-btn:hover:not(:disabled) {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}
.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.page-info {
  font-size: 13px;
  color: var(--text-muted);
}

/* ========== Skeleton ========== */
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}
.skeleton-card {
  aspect-ratio: 3/4;
  background: var(--surface-tertiary);
  border-radius: var(--radius-md);
  animation: shimmer 1.5s infinite;
}
@keyframes shimmer {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

/* ========== Responsive ========== */
@media (max-width: 768px) {
  .exchange-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
  .match-item {
    flex-direction: column;
    gap: 10px;
  }
  .match-connector {
    flex-direction: row;
  }
  .filter-bar {
    flex-direction: column;
  }
  .my-book-item {
    flex-direction: column;
    align-items: stretch;
  }
  .exchange-toggle-btn {
    width: 100%;
    text-align: center;
  }
}
</style>
