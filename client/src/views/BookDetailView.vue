<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useVirtualData } from '@/composables/useVirtualData'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import BookJourney from '@/components/BookJourney.vue'

const route = useRoute()
const router = useRouter()
const { getBookById } = useVirtualData()
const auth = useAuthStore()

const book = ref(null)
const loading = ref(true)
const isFavorited = ref(false)
const currentImageIndex = ref(0)
const aiSummary = ref(null)
const aiSummaryLoading = ref(false)

// Resolve cover image: prefer DB images, fallback to mock cover
const images = computed(() => {
  if (book.value?.images && book.value.images.length > 0) {
    return book.value.images
  }
  // Use the resolved image URL (DB returns '/mock/images/book_X.jpg', mock returns 'images/book_X.jpg')
  const img = book.value?.image || book.value?.cover_image
  const src = img
    ? (img.startsWith('/') ? img : `/mock/${img}`)
    : '/mock/images/_5_鱼鱼何包蛋_来自小红书网页版.jpg'
  return [{ url: src }]
})

const conditionColorMap = {
  '全新': { bg: '#E8F5E9', text: '#2E7D32' },
  '良好': { bg: '#FFF8E1', text: '#F57F17' },
  '有笔记': { bg: '#FCE4EC', text: '#C62828' },
  '旧': { bg: '#F5F5F5', text: '#616161' },
}

onMounted(async () => {
  const id = route.params.id
  loading.value = true
  // Try API first, fallback to virtual data
  try {
    const res = await api.get(`/books/${id}`)
    book.value = res.data
  } catch {
    const virtualBook = getBookById(id)
    if (virtualBook) book.value = virtualBook
  }
  loading.value = false

  // 加载 AI 评价摘要（评论 > 10 条时）
  if (book.value && book.value.reviews && book.value.reviews.length >= 10) {
    aiSummaryLoading.value = true
    try {
      const summaryRes = await api.get(`/ai/summarize/${book.value.id}`)
      if (summaryRes.data?.summary) {
        aiSummary.value = summaryRes.data
      }
    } catch { /* AI 服务不可用时静默降级 */ }
    aiSummaryLoading.value = false
  }

  if (auth.isLoggedIn) {
    try {
      const res = await api.get(`/favorites/check/${id}`)
      isFavorited.value = res.data?.is_favorited || false
    } catch { /* ignore */ }
  }
})

async function toggleFavorite() {
  if (!auth.isLoggedIn) {
    router.push({ name: 'Auth', query: { redirect: route.fullPath } })
    return
  }
  try {
    if (isFavorited.value) {
      await api.delete(`/favorites/${book.value.id}`)
      isFavorited.value = false
      ElMessage.success('已取消收藏')
    } else {
      await api.post('/favorites', { book_id: book.value.id })
      isFavorited.value = true
      ElMessage.success('已收藏')
    }
  } catch { ElMessage.error('操作失败') }
}

async function buyNow() {
  if (!auth.isLoggedIn) {
    router.push({ name: 'Auth', query: { redirect: route.fullPath } })
    return
  }
  if (!book.value) return
  try {
    const res = await api.post('/orders', { book_id: book.value.id })
    ElMessage.success('订单已创建，等待卖家确认')
    router.push({ name: 'Orders' })
  } catch (err) {
    ElMessage.error(err.message || '创建订单失败')
  }
}

function contactSeller() {
  if (!book.value) return
  router.push({
    name: 'Messages',
    query: {
      user_id: book.value.user_id,
      user_name: book.value.seller_name,
      book_id: book.value.id,
      book_title: book.value.title,
    },
  })
}

function goBack() {
  router.back()
}
</script>

<template>
  <div class="detail-page page-enter">
    <div class="page-container">
      <button class="back-btn" @click="goBack">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <path d="M19 12H5m7-7l-7 7 7 7" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        返回
      </button>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div class="skeleton skeleton-main"></div>
      </div>

      <!-- Book Detail -->
      <div v-else-if="book" class="detail-layout">
        <!-- Image Gallery -->
        <div class="detail-gallery">
          <div class="main-image">
            <img
              :src="images[currentImageIndex]?.url || images[0]?.url"
              :alt="book.title"
              class="detail-cover-img"
            />
          </div>
          <div v-if="images.length > 1" class="thumbnails">
            <img
              v-for="(img, i) in images"
              :key="i"
              :src="img.url"
              :class="{ active: i === currentImageIndex }"
              @click="currentImageIndex = i"
            />
          </div>
        </div>

        <!-- Book Info -->
        <div class="detail-info">
          <h1 class="book-title">{{ book.title }}</h1>
          <p class="book-author">作者：{{ book.author }}</p>
          <p v-if="book.isbn" class="book-isbn">ISBN：{{ book.isbn }}</p>
          <p class="book-category">分类：{{ book.category }}</p>

          <div class="price-section">
            <span class="current-price">
              <span class="price-symbol">¥</span>{{ book.price }}
            </span>
            <span v-if="book.original_price" class="original-price">¥{{ book.original_price }}</span>
          </div>

          <div class="condition-badge" :style="{
            background: conditionColorMap[book.condition]?.bg,
            color: conditionColorMap[book.condition]?.text
          }">
            {{ book.condition }}
          </div>

          <p v-if="book.description" class="book-desc">{{ book.description }}</p>

          <div class="seller-info" v-if="book.seller_name">
            <span class="seller-label">卖家</span>
            <span class="seller-name">{{ book.seller_name }}</span>
            <span v-if="book.seller_college" class="seller-college">{{ book.seller_college }}</span>
          </div>

          <!-- 书籍状态标签 -->
          <div v-if="book.status === '预定了'" class="status-tag reserved-tag">
            🔖 该书籍已被其他买家预定
          </div>
          <div v-else-if="book.status === '已售'" class="status-tag sold-tag">
            ✅ 该书籍已售出
          </div>

          <div class="detail-actions">
            <button
              v-if="book.status === '在售'"
              class="buy-btn"
              @click="buyNow"
            >立即购买</button>
            <button
              v-else-if="book.status === '预定了'"
              class="buy-btn reserved-btn"
              disabled
            >已被预定</button>
            <button
              v-else-if="book.status === '已售'"
              class="buy-btn sold-btn"
              disabled
            >已售出</button>
            <button
              v-if="book.seller_name && auth.isLoggedIn && auth.currentUser?.id !== book.user_id"
              class="contact-btn"
              @click="contactSeller"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              联系卖家
            </button>
            <button :class="['fav-btn', { active: isFavorited }]" @click="toggleFavorite">
              <svg viewBox="0 0 24 24" :fill="isFavorited ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2" width="18" height="18">
                <path d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>{{ isFavorited ? '已收藏' : '收藏' }}</span>
            </button>
          </div>
        </div>

        <!-- AI 评价摘要 -->
        <div v-if="aiSummaryLoading" class="ai-summary loading-summary">
          <div class="ai-summary-header">
            <span class="ai-icon">🤖</span>
            <span>AI 正在分析评价...</span>
          </div>
        </div>
        <div v-else-if="aiSummary" class="ai-summary">
          <div class="ai-summary-header">
            <span class="ai-icon">🤖</span>
            <span>AI 评价摘要</span>
            <span class="ai-badge">基于 {{ aiSummary.review_count }} 条评价</span>
          </div>
          <p class="ai-summary-text">{{ aiSummary.summary }}</p>
          <p class="ai-disclaimer">以上摘要由 AI 自动生成，仅供参考</p>
        </div>

        <!-- Book Journey Timeline -->
        <BookJourney :journeys="book.journeys || []" />

      </div>

      <div v-else class="loading-state">
        <p class="not-found">书籍不存在或已下架</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 14px;
  cursor: pointer;
  margin-bottom: 20px;
  padding: 4px 0;
}

.back-btn:hover { color: var(--accent-primary); }

.detail-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
}

.main-image {
  width: 100%;
  aspect-ratio: 3/4;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--surface-tertiary);
}

.main-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnails {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.thumbnails img {
  width: 60px;
  height: 80px;
  object-fit: cover;
  border-radius: 6px;
  cursor: pointer;
  border: 2px solid transparent;
  opacity: 0.7;
}

.thumbnails img.active,
.thumbnails img:hover {
  border-color: var(--accent-primary);
  opacity: 1;
}

.detail-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.book-title {
  font-family: var(--font-display);
  font-size: 28px;
  color: var(--text-primary);
  font-weight: 700;
}

.book-author,
.book-isbn,
.book-category {
  color: var(--text-secondary);
  font-size: 14px;
}

.price-section {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.current-price {
  font-family: var(--font-mono);
  font-size: 32px;
  font-weight: 700;
  color: var(--accent-primary);
}

.price-symbol { font-size: 18px; }

.original-price {
  font-family: var(--font-mono);
  font-size: 16px;
  color: var(--text-muted);
  text-decoration: line-through;
}

.condition-badge {
  display: inline-block;
  padding: 4px 14px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  width: fit-content;
}

.book-desc {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
}

.seller-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--surface-tertiary);
  border-radius: 8px;
}

.seller-label { color: var(--text-muted); font-size: 13px; }
.seller-name { font-weight: 600; font-size: 14px; color: var(--text-primary); }
.seller-college { color: var(--text-muted); font-size: 12px; }

.detail-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.buy-btn {
  flex: 1;
  padding: 14px 24px;
  background: var(--accent-primary);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.buy-btn:hover {
  background: var(--accent-primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(196,30,58,0.3);
}

[data-theme="cyber"] .buy-btn {
  background: linear-gradient(135deg, #00D4FF, #A855F7);
}

.fav-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 14px 20px;
  border: 1px solid var(--border-default);
  border-radius: 8px;
  background: var(--surface-secondary);
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.fav-btn:hover, .fav-btn.active {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

/* 状态标签 */
.status-tag {
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
}
.reserved-tag {
  background: rgba(255, 152, 0, 0.1);
  color: #E65100;
  border: 1px solid rgba(255, 152, 0, 0.3);
}
.sold-tag {
  background: rgba(76, 175, 80, 0.1);
  color: #2E7D32;
  border: 1px solid rgba(76, 175, 80, 0.3);
}
[data-theme="cyber"] .reserved-tag {
  background: rgba(255, 152, 0, 0.08);
  color: #FFB74D;
  border-color: rgba(255, 152, 0, 0.2);
}
[data-theme="cyber"] .sold-tag {
  background: rgba(76, 175, 80, 0.08);
  color: #81C784;
  border-color: rgba(76, 175, 80, 0.2);
}

/* 禁用按钮 */
.buy-btn:disabled,
.buy-btn.reserved-btn,
.buy-btn.sold-btn {
  cursor: not-allowed;
  opacity: 0.6;
}
.buy-btn.reserved-btn {
  background: #FF9800;
}
.buy-btn.sold-btn {
  background: #9E9E9E;
}
[data-theme="cyber"] .buy-btn.reserved-btn {
  background: rgba(255, 152, 0, 0.3);
}
[data-theme="cyber"] .buy-btn.sold-btn {
  background: rgba(158, 158, 158, 0.3);
}

/* 联系卖家按钮 */
.contact-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 14px 20px;
  border: 1px solid var(--accent-primary);
  border-radius: 8px;
  background: transparent;
  color: var(--accent-primary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.contact-btn:hover {
  background: var(--accent-primary-light);
}
[data-theme="cyber"] .contact-btn:hover {
  box-shadow: 0 0 16px rgba(0, 212, 255, 0.15);
}

.not-found { text-align: center; color: var(--text-muted); padding: 40px; }

/* ========== AI Summary ========== */
.ai-summary {
  grid-column: 1 / -1;
  margin-top: 24px;
  padding: 20px 24px;
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--accent-primary);
}
[data-theme="cyber"] .ai-summary {
  border-left-color: #A855F7;
  background: rgba(168,85,247,0.03);
}
.loading-summary {
  opacity: 0.7;
}
.ai-summary-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}
.ai-icon {
  font-size: 18px;
}
.ai-badge {
  font-size: 11px;
  color: var(--text-muted);
  background: var(--surface-tertiary);
  padding: 2px 10px;
  border-radius: 10px;
  font-weight: 400;
}
.ai-summary-text {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin: 0;
}
.ai-disclaimer {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 10px;
  margin-bottom: 0;
  font-style: italic;
}

@media (max-width: 768px) {
  .detail-layout { grid-template-columns: 1fr; gap: 24px; }
  .book-title { font-size: 22px; }
}
</style>
