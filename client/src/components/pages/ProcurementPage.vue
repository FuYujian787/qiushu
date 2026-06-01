<template>
  <div class="procurement-page">
    <div class="filter-bar">
      <span class="filter-label">
        <span class="iconify" data-icon="solar:filter-outline" data-width="16"></span>
        分类
      </span>
      <div class="filter-chips">
        <span
          v-for="chip in filterChips"
          :key="chip"
          class="filter-chip"
          :class="{ active: store.procurementFilter.value === chip }"
          @click="setFilter(chip)"
        >
          <span class="iconify" :data-icon="getChipIcon(chip)" data-width="14"></span>
          {{ chip }}
        </span>
      </div>
    </div>
    <div class="book-grid">
      <div v-for="book in pagedBooks" :key="book.id" class="book-card" @click="openDetail(book.id)">
        <div class="book-img-wrap">
          <img :src="book.img" :alt="book.title" class="book-img" />
          <span class="book-condition-tag">{{ book.condition }}</span>
        </div>
        <div class="book-card-info">
          <div class="book-card-header">
            <h4 class="book-card-title">{{ book.title }}</h4>
            <span class="book-card-price">
              <span class="iconify" data-icon="solar:dollar-minimalistic-outline" data-width="12"></span>
              {{ book.price }}
            </span>
          </div>
          <p class="book-card-seller">
            <span class="iconify" data-icon="solar:user-outline" data-width="12"></span>
            {{ book.seller }}
            <button
              v-if="store.isLoggedIn.value && book.seller !== store.currentUser.value?.name"
              class="chat-btn-mini"
              @click.stop="startChat(book.seller)"
              title="私聊卖家"
            >
              <span class="iconify" data-icon="solar:chat-dots-outline" data-width="14"></span>
            </button>
          </p>
          <div class="book-card-actions" @click.stop>
            <div class="add-cart-btn" @click="addToCart(book)">
              <span class="iconify" data-icon="solar:cart-plus-outline" data-width="15"></span>
              加入购物车
            </div>
          </div>
        </div>
      </div>
      <div v-if="pagedBooks.length === 0" class="empty-state">
        <span class="iconify empty-state-icon" data-icon="solar:document-search-outline" data-width="48"></span>
        <p>没有找到相关书籍</p>
      </div>
    </div>
    <div v-if="totalPages > 1" class="pagination">
      <div class="pagination-buttons">
        <button class="page-btn" :disabled="page <= 1" @click="goPage(page - 1)">
          <span class="iconify" data-icon="solar:alt-arrow-left-outline" data-width="18"></span>
        </button>
        <template v-for="p in pageNumbers" :key="p">
          <button v-if="p === '...'" class="page-btn page-ellipsis" disabled>…</button>
          <button v-else class="page-btn" :class="{ active: p === page }" @click="goPage(p)">{{ p }}</button>
        </template>
        <button class="page-btn" :disabled="page >= totalPages" @click="goPage(page + 1)">
          <span class="iconify" data-icon="solar:alt-arrow-right-outline" data-width="18"></span>
        </button>
      </div>
      <div class="jump-area">
        <span class="jump-text">跳至</span>
        <input v-model.number="jumpVal" type="number" :min="1" :max="totalPages" class="jump-input" :placeholder="String(page)" />
        <span class="jump-text">页</span>
        <button class="jump-btn">GO</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useStore } from '../../stores/useStore'

const store = useStore()
const pageSize = 20
const jumpVal = ref(1)

const filterChips = computed(() => store.categoriesData.value?.filterChips || ['全部', '教材', '考研', '选修'])

const filteredBooks = computed(() => {
  let result = store.productCache.value
  const filter = store.procurementFilter.value
  const query = store.searchQuery.value?.trim().toLowerCase() || ''
  if (filter !== '全部') {
    result = result.filter(p => p.category === filter)
  }
  if (query) {
    result = result.filter(p => p.title.toLowerCase().includes(query) || p.author.toLowerCase().includes(query))
  }
  return result
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredBooks.value.length / pageSize)))

const page = computed(() => {
  const p = store.procurementPage.value
  if (p > totalPages.value) {
    store.procurementPage.value = totalPages.value
    return totalPages.value
  }
  return p
})

const pagedBooks = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredBooks.value.slice(start, start + pageSize)
})

const pageNumbers = computed(() => {
  const tp = totalPages.value
  const cp = page.value
  const maxVisible = 5
  const result = []
  let start = Math.max(1, cp - Math.floor(maxVisible / 2))
  let end = Math.min(tp, start + maxVisible - 1)
  if (end - start < maxVisible - 1) {
    start = Math.max(1, end - maxVisible + 1)
  }
  if (start > 1) {
    result.push(1)
    if (start > 2) result.push('...')
  }
  for (let i = start; i <= end; i++) result.push(i)
  if (end < tp) {
    if (end < tp - 1) result.push('...')
    result.push(tp)
  }
  return result
})

function setFilter(cat) {
  store.procurementFilter.value = cat
  store.procurementPage.value = 1
}

const CHIP_ICON_MAP = {
  '全部': 'solar:layers-outline',
  '教材': 'solar:book-2-outline',
  '考研': 'solar:document-text-outline',
  '选修': 'solar:bookmark-outline',
}

function getChipIcon(chip) {
  return CHIP_ICON_MAP[chip] || 'solar:tag-outline'
}

function goPage(p) {
  if (p < 1) p = 1
  if (p > totalPages.value) p = totalPages.value
  store.procurementPage.value = p
}

function jumpPage() {
  const v = jumpVal.value
  if (v && v >= 1 && v <= totalPages.value) {
    store.procurementPage.value = v
  }
}

function addToCart(book) {
  store.addToCart(book)
  alert('已加入购物车')
}

function openDetail(id) {
  store.navigateTo('bookDetail', id)
}

/** 私聊卖家 */
function startChat(sellerName) {
  if (!store.isLoggedIn.value) {
    alert('请先登录')
    return
  }
  sessionStorage.setItem('chat_target_user', sellerName)
  store.navigateTo('chat')
}
</script>

<style scoped>
.procurement-page { display: flex; flex-direction: column; gap: 2rem; }
.filter-bar { display: flex; align-items: center; gap: 1rem; }
.filter-label {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.filter-chips { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.375rem 1rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  color: var(--text-secondary);
  cursor: pointer;
  backdrop-filter: blur(8px);
  transition: all 0.2s var(--ease-out);
}
.filter-chip:hover { border-color: var(--lavender-primary); color: var(--lavender-accent); }
.filter-chip.active {
  background: var(--gradient-brand);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 2px 10px rgba(108,63,192,0.25);
}
.book-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; }
.book-card {
  background: var(--glass-bg-card);
  backdrop-filter: blur(28px) saturate(1.4);
  -webkit-backdrop-filter: blur(28px) saturate(1.4);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1rem;
  box-shadow: var(--shadow-md), var(--shadow-glow), inset 0 1px 0 rgba(255,255,255,0.55);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16,1,0.3,1);
}
.book-card:hover {
  box-shadow: var(--shadow-lg), 0 0 40px rgba(100,140,220,0.12);
  border-color: var(--glass-border-hover);
  transform: translateY(-3px);
}
.book-img-wrap {
  position: relative;
  aspect-ratio: 3 / 4;
  background: linear-gradient(135deg, rgba(255,255,255,0.4), rgba(220,210,240,0.3));
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.75rem;
}
.book-img { width: 100%; height: 100%; object-fit: cover; }
.book-condition-tag {
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  padding: 0.2rem 0.65rem;
  background: rgba(0,0,0,0.45);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  color: #fff;
  font-size: 0.625rem;
  font-weight: 500;
  border-radius: 9999px;
  letter-spacing: 0.02em;
}
.book-card-info {}
.book-card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.375rem; }
.book-card-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.875rem;
  margin: 0;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.book-card-price {
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 0.875rem;
  margin-left: 0.5rem;
  white-space: nowrap;
  letter-spacing: -0.02em;
  display: flex;
  align-items: center;
  gap: 0.15rem;
}
.book-card-seller {
  font-size: 0.75rem;
  color: var(--text-caption);
  margin: 0 0 0.75rem 0;
  font-weight: 400;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}
.chat-btn-mini {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  background: rgba(108,63,192,0.08);
  border: 1px solid rgba(108,63,192,0.15);
  border-radius: 6px;
  cursor: pointer;
  padding: 0;
  color: var(--lavender-accent);
  transition: all 0.2s;
}
.chat-btn-mini:hover { background: rgba(108,63,192,0.15); border-color: rgba(108,63,192,0.3); }
.book-card-actions {}
.add-cart-btn {
  width: 100%;
  padding: 0.625rem;
  background: linear-gradient(135deg, #6c3fc0 0%, #9b59b6 40%, #af52de 100%);
  color: #fff;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 10px;
  text-align: center;
  cursor: pointer;
  border: none;
  box-shadow: 0 3px 12px rgba(108, 63, 192, 0.3);
  transition: all 0.2s cubic-bezier(0.16,1,0.3,1);
  letter-spacing: 0.01em;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
}
.add-cart-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 5px 18px rgba(108, 63, 192, 0.4);
  filter: brightness(1.08);
}
.add-cart-btn:active { transform: scale(0.97); }
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 5rem 0;
  color: var(--text-tertiary);
  font-size: 1.125rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}
.empty-state-icon { opacity: 0.35; color: var(--text-tertiary); }
.pagination { display: flex; flex-direction: column; align-items: center; gap: 1rem; margin-top: 1rem; }
.pagination-buttons { display: flex; align-items: center; gap: 0.5rem; }
.page-btn {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 10px;
  border: 1px solid var(--glass-border);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: var(--text-secondary);
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.2s var(--ease-out);
}
.page-btn:hover:not(:disabled):not(.active) { border-color: var(--lavender-primary); color: var(--lavender-accent); background: var(--glass-bg-hover); }
.page-btn.active {
  background: var(--gradient-brand);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 2px 8px rgba(108,63,192,0.25);
}
.page-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.page-ellipsis { border: none; background: none; cursor: default; }
.jump-area { display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; color: var(--text-secondary); }
.jump-input { width: 4rem; padding: 0.25rem 0.5rem; border: 1px solid var(--glass-border); border-radius: 0.5rem; text-align: center; font-size: 0.875rem; outline: none; background: var(--glass-bg-input); }
.jump-btn { padding: 0.25rem 0.75rem; background: rgba(108,63,192,0.1); color: var(--lavender-accent); border: 1px solid rgba(108,63,192,0.15); border-radius: 0.5rem; font-size: 0.875rem; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.jump-btn:hover { background: rgba(108,63,192,0.18); border-color: rgba(108,63,192,0.3); }
</style>
