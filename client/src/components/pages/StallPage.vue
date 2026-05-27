<template>
  <div class="stall-page">
    <!-- 页面标题 -->
    <div class="stall-hero">
      <div class="stall-hero-icon">
        <!-- 小店铺 SVG 图标 -->
        <svg width="40" height="40" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="4" y="18" width="40" height="26" rx="3" stroke="#9B8EC4" stroke-width="2.5" fill="rgba(155,142,196,0.12)"/>
          <path d="M4 18L10 6H38L44 18" stroke="#9B8EC4" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M16 18C16 21.3137 18.6863 24 22 24C25.3137 24 28 21.3137 28 18" stroke="#9B8EC4" stroke-width="2" stroke-linecap="round"/>
          <path d="M28 18C28 21.3137 30.6863 24 34 24C37.3137 24 40 21.3137 40 18" stroke="#9B8EC4" stroke-width="2" stroke-linecap="round"/>
          <path d="M10 18C10 21.3137 12.6863 24 16 24C19.3137 24 22 21.3137 22 18" stroke="#9B8EC4" stroke-width="2" stroke-linecap="round"/>
          <rect x="14" y="30" width="8" height="10" rx="1" fill="#DCD0FF" stroke="#9B8EC4" stroke-width="1.5"/>
          <rect x="26" y="30" width="8" height="10" rx="1" fill="#DCD0FF" stroke="#9B8EC4" stroke-width="1.5"/>
        </svg>
      </div>
      <div class="stall-hero-text">
        <h2 class="stall-hero-title">我的求是书摊</h2>
        <p class="stall-hero-subtitle">管理您的闲置书籍销售，查看收益与订单</p>
      </div>
    </div>

    <!-- 核心数据卡片 -->
    <div class="stall-metrics">
      <!-- 一共卖出 -->
      <div class="stall-metric-card">
        <div class="stall-metric-icon sold-icon">
          <svg width="32" height="32" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="6" y="10" width="36" height="28" rx="3" stroke="#8A2BE2" stroke-width="2.5" fill="rgba(138,43,226,0.08)"/>
            <path d="M16 10V6H32V10" stroke="#8A2BE2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M6 20H42" stroke="#8A2BE2" stroke-width="2" stroke-linecap="round"/>
            <path d="M14 28L20 34L34 22" stroke="#8A2BE2" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stall-metric-body">
          <span class="stall-metric-label">一共卖出</span>
          <div class="stall-metric-value-row">
            <span class="stall-metric-value">{{ sellerStats.total_books_sold }}</span>
            <span class="stall-metric-unit">本</span>
          </div>
        </div>
      </div>
      <!-- 一共赚了 -->
      <div class="stall-metric-card">
        <div class="stall-metric-icon earn-icon">
          <svg width="32" height="32" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="4" y="12" width="40" height="28" rx="4" stroke="#7B68EE" stroke-width="2.5" fill="rgba(123,104,238,0.08)"/>
            <circle cx="24" cy="26" r="8" stroke="#7B68EE" stroke-width="2.5"/>
            <path d="M24 20V22" stroke="#7B68EE" stroke-width="2.5" stroke-linecap="round"/>
            <path d="M24 30V32" stroke="#7B68EE" stroke-width="2.5" stroke-linecap="round"/>
            <path d="M20 26H28" stroke="#7B68EE" stroke-width="2.5" stroke-linecap="round"/>
            <path d="M8 18H12" stroke="#7B68EE" stroke-width="2" stroke-linecap="round"/>
            <path d="M36 18H40" stroke="#7B68EE" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="stall-metric-body">
          <span class="stall-metric-label">一共赚了</span>
          <div class="stall-metric-value-row">
            <span class="stall-metric-value">¥{{ sellerStats.total_earnings }}</span>
          </div>
        </div>
      </div>
      <!-- 在售书籍 -->
      <div class="stall-metric-card">
        <div class="stall-metric-icon listed-icon">
          <svg width="32" height="32" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="6" y="4" width="14" height="18" rx="2" stroke="#9B8EC4" stroke-width="2.5" fill="rgba(155,142,196,0.08)"/>
            <rect x="28" y="4" width="14" height="18" rx="2" stroke="#9B8EC4" stroke-width="2.5" fill="rgba(155,142,196,0.08)"/>
            <rect x="6" y="26" width="14" height="18" rx="2" stroke="#9B8EC4" stroke-width="2.5" fill="rgba(155,142,196,0.08)"/>
            <rect x="28" y="26" width="14" height="18" rx="2" stroke="#9B8EC4" stroke-width="2.5" fill="rgba(155,142,196,0.08)"/>
            <path d="M13 10V16" stroke="#9B8EC4" stroke-width="2" stroke-linecap="round"/>
            <path d="M10 13H16" stroke="#9B8EC4" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="stall-metric-body">
          <span class="stall-metric-label">在售书籍</span>
          <div class="stall-metric-value-row">
            <span class="stall-metric-value">{{ myBooks.length }}</span>
            <span class="stall-metric-unit">本</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 在售书籍列表 -->
    <div class="stall-section">
      <div class="stall-section-header">
        <h3 class="stall-section-title">
          <svg width="22" height="22" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle;margin-right:8px;">
            <rect x="6" y="4" width="14" height="18" rx="2" stroke="#9B8EC4" stroke-width="2.5" fill="rgba(155,142,196,0.1)"/>
            <rect x="28" y="4" width="14" height="18" rx="2" stroke="#9B8EC4" stroke-width="2.5" fill="rgba(155,142,196,0.1)"/>
            <rect x="6" y="26" width="14" height="18" rx="2" stroke="#9B8EC4" stroke-width="2.5" fill="rgba(155,142,196,0.1)"/>
            <rect x="28" y="26" width="14" height="18" rx="2" stroke="#9B8EC4" stroke-width="2.5" fill="rgba(155,142,196,0.1)"/>
            <path d="M13 10V16" stroke="#9B8EC4" stroke-width="2" stroke-linecap="round"/>
            <path d="M10 13H16" stroke="#9B8EC4" stroke-width="2" stroke-linecap="round"/>
          </svg>
          我的在售书籍
        </h3>
        <button class="stall-publish-btn" @click="goPublish">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="rgba(155,142,196,0.15)"/>
            <path d="M12 8V16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M8 12H16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span>发布新书</span>
        </button>
      </div>

      <div v-if="myBooks.length === 0" class="stall-empty">
        <svg width="56" height="56" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="12" y="8" width="40" height="48" rx="4" stroke="#AFA0BF" stroke-width="2.5" fill="rgba(175,160,191,0.06)"/>
          <path d="M22 8V4H42V8" stroke="#AFA0BF" stroke-width="2" stroke-linecap="round"/>
          <path d="M20 24H44" stroke="#AFA0BF" stroke-width="2" stroke-linecap="round"/>
          <path d="M20 34H44" stroke="#AFA0BF" stroke-width="2" stroke-linecap="round"/>
          <path d="M20 44H36" stroke="#AFA0BF" stroke-width="2" stroke-linecap="round"/>
          <circle cx="48" cy="48" r="10" stroke="#AFA0BF" stroke-width="2" fill="rgba(175,160,191,0.08)"/>
          <path d="M48 44V52" stroke="#AFA0BF" stroke-width="2" stroke-linecap="round"/>
          <path d="M44 48H52" stroke="#AFA0BF" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <p class="stall-empty-text">您还没有在售书籍</p>
        <button class="stall-empty-btn" @click="goPublish">去发布第一本书</button>
      </div>

      <div v-else class="stall-book-grid">
        <div v-for="book in myBooks" :key="book.id" class="stall-book-card" @click="openDetail(book.id)">
          <div class="stall-book-img-wrap">
            <img :src="book.img" :alt="book.title" class="stall-book-img" />
          </div>
          <div class="stall-book-info">
            <h4 class="stall-book-title">{{ book.title }}</h4>
            <p class="stall-book-author">{{ book.author }}</p>
            <div class="stall-book-meta">
              <span class="stall-book-condition">{{ book.condition }}</span>
              <span class="stall-book-price">¥{{ book.price }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 最近订单 -->
    <div class="stall-section">
      <div class="stall-section-header">
        <h3 class="stall-section-title">
          <svg width="22" height="22" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle;margin-right:8px;">
            <rect x="4" y="10" width="40" height="32" rx="3" stroke="#9B8EC4" stroke-width="2.5" fill="rgba(155,142,196,0.1)"/>
            <path d="M14 10V6H34V10" stroke="#9B8EC4" stroke-width="2" stroke-linecap="round"/>
            <path d="M4 20H44" stroke="#9B8EC4" stroke-width="2" stroke-linecap="round"/>
            <circle cx="16" cy="30" r="3" stroke="#9B8EC4" stroke-width="2" fill="rgba(155,142,196,0.1)"/>
            <circle cx="32" cy="30" r="3" stroke="#9B8EC4" stroke-width="2" fill="rgba(155,142,196,0.1)"/>
            <path d="M22 30H26" stroke="#9B8EC4" stroke-width="2" stroke-linecap="round"/>
          </svg>
          最近售出记录
        </h3>
        <span class="stall-section-link" @click="store.navigateTo('orders')">
          查看全部订单
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle;margin-left:4px;">
            <path d="M9 6L15 12L9 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </span>
      </div>

      <div v-if="soldOrders.length === 0" class="stall-empty">
        <svg width="56" height="56" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="8" y="12" width="48" height="40" rx="4" stroke="#AFA0BF" stroke-width="2.5" fill="rgba(175,160,191,0.06)"/>
          <path d="M8 24H56" stroke="#AFA0BF" stroke-width="2" stroke-linecap="round"/>
          <circle cx="20" cy="36" r="4" stroke="#AFA0BF" stroke-width="2" fill="rgba(175,160,191,0.08)"/>
          <circle cx="44" cy="36" r="4" stroke="#AFA0BF" stroke-width="2" fill="rgba(175,160,191,0.08)"/>
          <path d="M28 36H36" stroke="#AFA0BF" stroke-width="2" stroke-linecap="round"/>
          <path d="M32 12V8" stroke="#AFA0BF" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <p class="stall-empty-text">还没有售出记录</p>
      </div>

      <div v-else class="stall-order-list">
        <div v-for="order in soldOrders" :key="order.id" class="stall-order-item">
          <div class="stall-order-left">
            <span class="stall-order-icon">
              <svg width="22" height="22" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="8" y="6" width="32" height="36" rx="3" stroke="#9B8EC4" stroke-width="2.5" fill="rgba(155,142,196,0.08)"/>
                <path d="M18 6V4H30V6" stroke="#9B8EC4" stroke-width="2" stroke-linecap="round"/>
                <path d="M16 18H32" stroke="#9B8EC4" stroke-width="2" stroke-linecap="round"/>
                <path d="M16 26H32" stroke="#9B8EC4" stroke-width="2" stroke-linecap="round"/>
                <path d="M16 34H26" stroke="#9B8EC4" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </span>
            <div class="stall-order-info">
              <span class="stall-order-title">{{ order.title }}</span>
              <span class="stall-order-buyer">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle;margin-right:3px;">
                  <circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="1.5"/>
                  <path d="M4 22C4 17.5817 7.58172 14 12 14C16.4183 14 20 17.5817 20 22" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                买家：{{ order.buyer }}
                <button
                  v-if="store.isLoggedIn.value && order.buyer !== store.currentUser.value?.name"
                  class="chat-btn-mini"
                  @click.stop="startChat(order.buyer)"
                  title="私聊买家"
                >
                  💬
                </button>
              </span>
            </div>
          </div>
          <div class="stall-order-right">
            <span class="stall-order-price">¥{{ order.price }}</span>
            <span class="stall-order-date">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle;margin-right:3px;">
                <rect x="3" y="4" width="18" height="18" rx="3" stroke="currentColor" stroke-width="1.5"/>
                <path d="M3 10H21" stroke="currentColor" stroke-width="1.5"/>
                <path d="M8 2V6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                <path d="M16 2V6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              {{ order.date }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from '../../stores/useStore'

const store = useStore()
const sellerStats = ref({ total_books_sold: 0, total_earnings: 0.00 })

const myBooks = computed(() => {
  if (!store.isLoggedIn.value || !store.currentUser.value) return []
  const result = store.fetchUserBooks(store.currentUser.value.name)
  return result.books || []
})

const soldOrders = computed(() => {
  if (!store.isLoggedIn.value || !store.currentUser.value) return []
  const allOrders = store.orders.value || []
  const sellerName = store.currentUser.value.name
  return allOrders
    .filter(o => o.seller === sellerName)
    .slice(0, 10)
})

function loadSellerStats() {
  if (!store.isLoggedIn.value || !store.currentUser.value) return
  try {
    const data = store.fetchSellerStats(store.currentUser.value.name)
    if (data.success) {
      sellerStats.value = {
        total_books_sold: data.total_books_sold ?? 0,
        total_earnings: data.total_earnings ?? 0.00,
      }
    }
  } catch (e) {
    // ignore
  }
}

onMounted(() => {
  loadSellerStats()
})

function goPublish() {
  store.navigateTo('publish')
}

function openDetail(id) {
  store.navigateTo('bookDetail', id)
}

/** 私聊买家 */
function startChat(buyerName) {
  if (!store.isLoggedIn.value) {
    alert('请先登录')
    return
  }
  sessionStorage.setItem('chat_target_user', buyerName)
  store.navigateTo('chat')
}
</script>

<style scoped>
.stall-page {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  max-width: 64rem;
  margin: 0 auto;
}

/* ===== 页面标题 ===== */
.stall-hero {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 2rem 2.5rem;
  background: var(--glass-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 1.5rem;
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
}

.stall-hero-icon {
  width: 4.5rem;
  height: 4.5rem;
  background: linear-gradient(135deg, rgba(243, 239, 255, 0.8), rgba(220, 208, 255, 0.3));
  border-radius: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stall-hero-text {
  flex: 1;
}

.stall-hero-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
  letter-spacing: 0.05em;
}

.stall-hero-subtitle {
  font-size: 0.9rem;
  color: var(--text-tertiary);
  margin: 0.375rem 0 0 0;
}

/* ===== 核心数据卡片 ===== */
.stall-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

.stall-metric-card {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.5rem;
  background: var(--glass-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 1.25rem;
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.stall-metric-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--glass-shadow-hover);
}

.stall-metric-icon {
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sold-icon {
  background: rgba(138, 43, 226, 0.08);
}

.earn-icon {
  background: rgba(123, 104, 238, 0.08);
}

.listed-icon {
  background: rgba(155, 142, 196, 0.08);
}

.stall-metric-body {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stall-metric-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.stall-metric-value-row {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
}

.stall-metric-value {
  font-size: 2rem;
  font-weight: 800;
  line-height: 1;
  background: linear-gradient(135deg, #8A2BE2, #7B68EE);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stall-metric-unit {
  font-size: 0.85rem;
  color: var(--text-tertiary);
  font-weight: 500;
}

/* ===== 区块通用 ===== */
.stall-section {
  background: var(--glass-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 1.5rem;
  padding: 1.75rem 2rem;
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
}

.stall-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.stall-section-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  display: flex;
  align-items: center;
}

.stall-section-link {
  font-size: 0.85rem;
  color: var(--lavender-accent-soft);
  cursor: pointer;
  transition: color 0.2s;
  display: flex;
  align-items: center;
}

.stall-section-link:hover {
  color: var(--lavender-accent);
}

.stall-publish-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1.25rem;
  background: linear-gradient(135deg, #DCD0FF, #C4B5E0);
  border: none;
  border-radius: 0.75rem;
  font-weight: 700;
  font-size: 0.85rem;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(155, 142, 196, 0.2);
}

.stall-publish-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(155, 142, 196, 0.3);
}

/* ===== 空状态 ===== */
.stall-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  gap: 1rem;
}

.stall-empty-text {
  font-size: 0.95rem;
  color: var(--text-tertiary);
  margin: 0;
}

.stall-empty-btn {
  padding: 0.625rem 1.5rem;
  background: var(--gradient-brand);
  border: none;
  border-radius: 0.75rem;
  font-weight: 700;
  font-size: 0.85rem;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(155, 142, 196, 0.2);
}

.stall-empty-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(155, 142, 196, 0.3);
}

/* ===== 在售书籍网格 ===== */
.stall-book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(18rem, 1fr));
  gap: 1rem;
}

.stall-book-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(243, 239, 255, 0.4);
  border-radius: 1rem;
  border: 1px solid rgba(220, 208, 255, 0.15);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.stall-book-card:hover {
  background: rgba(243, 239, 255, 0.7);
  border-color: rgba(220, 208, 255, 0.35);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(155, 142, 196, 0.1);
}

.stall-book-img-wrap {
  width: 3.5rem;
  height: 5rem;
  border-radius: 0.5rem;
  overflow: hidden;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.3);
}

.stall-book-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.stall-book-info {
  flex: 1;
  min-width: 0;
}

.stall-book-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stall-book-author {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  margin: 0 0 0.5rem;
}

.stall-book-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stall-book-condition {
  font-size: 0.7rem;
  color: var(--text-secondary);
  padding: 0.125rem 0.5rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 999px;
}

.stall-book-price {
  font-size: 1rem;
  font-weight: 800;
  color: var(--lavender-accent);
}

/* ===== 售出记录列表 ===== */
.stall-order-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.stall-order-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  background: rgba(243, 239, 255, 0.4);
  border-radius: 1rem;
  border: 1px solid rgba(220, 208, 255, 0.12);
  transition: all 0.2s;
}

.stall-order-item:hover {
  background: rgba(243, 239, 255, 0.6);
  border-color: rgba(220, 208, 255, 0.25);
}

.stall-order-left {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.stall-order-icon {
  width: 2.5rem;
  height: 2.5rem;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stall-order-info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.stall-order-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}

.stall-order-buyer {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  display: flex;
  align-items: center;
}

.stall-order-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.125rem;
}

.stall-order-price {
  font-size: 1rem;
  font-weight: 700;
  color: var(--lavender-accent);
}

.stall-order-date {
  font-size: 0.7rem;
  color: var(--text-tertiary);
  display: flex;
  align-items: center;
}
</style>
