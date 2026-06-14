<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const router = useRouter()
const auth = useAuthStore()
const books = ref([])
const loading = ref(false)
const error = ref('')

onMounted(async () => {
  await loadRecommendations()
})

async function loadRecommendations() {
  loading.value = true
  error.value = ''
  try {
    if (auth.isLoggedIn) {
      const res = await api.get('/ai/recommend')
      books.value = res.data || []
    } else {
      // 未登录时显示热门推荐
      const res = await api.get('/books', { params: { sort: 'created_at', order: 'desc', per_page: 6 } })
      books.value = res.data?.books || []
      books.value.forEach(b => { b.recommend_reason = '热门推荐' })
    }
  } catch {
    error.value = '推荐加载失败'
  } finally {
    loading.value = false
  }
}

function goToBook(book) {
  router.push({ name: 'BookDetail', params: { id: book.id } })
}

defineExpose({ loadRecommendations })
</script>

<template>
  <section class="recommend-section">
    <div class="section-header">
      <h2 class="section-title">
        <span class="title-icon">🤖</span>
        {{ auth.isLoggedIn ? '为你推荐' : '热门推荐' }}
      </h2>
      <span class="ai-badge">AI 推荐</span>
    </div>

    <div v-if="loading" class="loading">
      <div class="skeleton-list">
        <div v-for="i in 6" :key="i" class="skeleton-card"></div>
      </div>
    </div>

    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else-if="books.length === 0" class="empty">
      暂无推荐
    </div>

    <div v-else class="recommend-grid">
      <div
        v-for="book in books"
        :key="book.id"
        class="recommend-card"
        @click="goToBook(book)"
      >
        <div class="card-cover">
          <img
            :src="book.image || book.images?.[0]?.url || '/mock/images/_5_鱼鱼何包蛋_来自小红书网页版.jpg'"
            :alt="book.title"
            class="cover-img"
          />
        </div>
        <div class="card-body">
          <h3 class="book-title">{{ book.title }}</h3>
          <p class="book-author" v-if="book.author">{{ book.author }}</p>
          <p class="book-reason" v-if="book.recommend_reason">
            💡 {{ book.recommend_reason }}
          </p>
          <div class="card-footer">
            <span class="book-price">¥{{ book.price }}</span>
            <span class="book-condition">{{ book.condition }}</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.recommend-section {
  padding: 48px 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
}

.section-title {
  font-family: var(--font-display);
  font-size: 22px;
  color: var(--text-primary);
  font-weight: 700;
}

.title-icon { margin-right: 4px; }

.ai-badge {
  padding: 3px 12px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
}

[data-theme="cyber"] .ai-badge {
  background: linear-gradient(135deg, #00D4FF, #A855F7);
}

.recommend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.recommend-card {
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.recommend-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-md);
  border-color: var(--accent-primary);
}

[data-theme="cyber"] .recommend-card:hover {
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.1);
}

.card-cover {
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--surface-tertiary), var(--surface-secondary));
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-body { padding: 12px; }

.book-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-author {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}

.book-reason {
  font-size: 11px;
  color: var(--accent-primary);
  margin-top: 6px;
  line-height: 1.3;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.book-price {
  font-family: var(--font-mono);
  font-size: 18px;
  font-weight: 700;
  color: var(--accent-primary);
}

.book-condition {
  font-size: 11px;
  color: var(--text-muted);
  padding: 1px 6px;
  background: var(--surface-tertiary);
  border-radius: 4px;
}

.loading { padding: 32px 0; }
.skeleton-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; }
.skeleton-card {
  height: 240px;
  background: var(--surface-tertiary);
  border-radius: var(--radius-md);
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

.error, .empty { text-align: center; padding: 32px; color: var(--text-muted); }

@media (max-width: 768px) {
  .recommend-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
}
</style>
