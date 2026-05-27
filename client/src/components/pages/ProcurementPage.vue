<template>
  <div class="procurement-page">
    <div class="filter-bar">
      <span class="filter-label">分类:</span>
      <div class="filter-chips">
        <span v-for="chip in filterChips" :key="chip" class="filter-chip" :class="{ active: store.procurementFilter.value === chip }" @click="setFilter(chip)">{{ chip }}</span>
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
            <span class="book-card-price">¥{{ book.price }}</span>
          </div>
          <p class="book-card-seller">卖家: {{ book.seller }}</p>
          <div class="book-card-actions" @click.stop>
            <div class="add-cart-btn" @click="addToCart(book)">加入购物车</div>
          </div>
        </div>
      </div>
      <div v-if="pagedBooks.length === 0" class="empty-state">
        <p>没有找到相关书籍</p>
      </div>
    </div>
    <div v-if="totalPages > 1" class="pagination">
      <div class="pagination-buttons">
        <button class="page-btn" :disabled="page <= 1" @click="goPage(page - 1)">‹</button>
        <template v-for="p in pageNumbers" :key="p">
          <button v-if="p === '...'" class="page-btn page-ellipsis" disabled>…</button>
          <button v-else class="page-btn" :class="{ active: p === page }" @click="goPage(p)">{{ p }}</button>
        </template>
        <button class="page-btn" :disabled="page >= totalPages" @click="goPage(page + 1)">›</button>
      </div>
      <div class="jump-area">
        <span class="jump-text">跳至</span>
        <input v-model.number="jumpVal" type="number" :min="1" :max="totalPages" class="jump-input" :placeholder="String(page)" />
        <span class="jump-text">页</span>
        <button class="jump-btn" @click="jumpPage">GO</button>
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
</script>

<style scoped>
.procurement-page { display: flex; flex-direction: column; gap: 2rem; }
.filter-bar { display: flex; align-items: center; gap: 1rem; }
.filter-label { font-size: 0.875rem; font-weight: 700; color: var(--text-tertiary); }
.filter-chips { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.filter-chip { padding: 0.375rem 1rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 500; background: var(--glass-bg); border: 1px solid var(--glass-border); color: var(--text-secondary); cursor: pointer; backdrop-filter: blur(8px); }
.filter-chip:hover { border-color: var(--lavender-primary); }
.filter-chip.active { background: var(--gradient-brand); color: var(--text-primary); border-color: transparent; }
.book-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; }
.book-card { background: var(--glass-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid var(--glass-border); border-radius: 1.5rem; padding: 1rem; box-shadow: var(--glass-shadow); cursor: pointer; }
.book-card:hover { box-shadow: var(--glass-shadow-hover); border-color: var(--glass-border-strong); }
.book-img-wrap { position: relative; aspect-ratio: 3/4; background: rgba(255,255,255,0.3); border-radius: 1rem; overflow: hidden; margin-bottom: 1rem; }
.book-img { width: 100%; height: 100%; object-fit: cover; }
.book-condition-tag { position: absolute; top: 0.75rem; left: 0.75rem; padding: 0.25rem 0.75rem; background: rgba(0,0,0,0.5); color: white; font-size: 0.625rem; font-weight: 700; border-radius: 9999px; }
.book-card-info {}
.book-card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; }
.book-card-title { font-weight: 700; color: var(--text-primary); font-size: 0.875rem; margin: 0; line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.book-card-price { color: var(--lavender-accent); font-weight: 700; font-size: 0.875rem; margin-left: 0.5rem; white-space: nowrap; }
.book-card-seller { font-size: 0.75rem; color: var(--text-tertiary); margin: 0 0 0.75rem 0; }
.book-card-actions {}
.add-cart-btn { width: 100%; padding: 0.625rem; background: rgba(255,255,255,0.5); color: var(--text-secondary); font-size: 0.75rem; font-weight: 700; border-radius: 0.75rem; text-align: center; cursor: pointer; border: 1px solid var(--glass-border); }
.add-cart-btn:hover { background: var(--lavender-accent-mist); color: var(--lavender-accent); }
.empty-state { grid-column: 1 / -1; text-align: center; padding: 5rem 0; color: var(--text-tertiary); font-size: 1.125rem; }
.pagination { display: flex; flex-direction: column; align-items: center; gap: 1rem; margin-top: 1rem; }
.pagination-buttons { display: flex; align-items: center; gap: 0.5rem; }
.page-btn { width: 2.5rem; height: 2.5rem; border-radius: 0.75rem; border: 1px solid var(--glass-border); display: flex; align-items: center; justify-content: center; background: var(--glass-bg); color: var(--text-secondary); cursor: pointer; font-weight: 700; font-size: 1rem; backdrop-filter: blur(8px); }
.page-btn:hover:not(:disabled):not(.active) { border-color: var(--lavender-primary); color: var(--lavender-accent); }
.page-btn.active { background: var(--gradient-brand); color: var(--text-primary); border-color: transparent; }
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.page-ellipsis { border: none; background: none; cursor: default; }
.jump-area { display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; color: var(--text-secondary); }
.jump-input { width: 4rem; padding: 0.25rem 0.5rem; border: 1px solid var(--glass-border); border-radius: 0.5rem; text-align: center; font-size: 0.875rem; outline: none; background: rgba(255,255,255,0.5); }
.jump-btn { padding: 0.25rem 0.75rem; background: var(--lavender-accent-mist); color: var(--lavender-accent); border: none; border-radius: 0.5rem; font-size: 0.875rem; font-weight: 500; cursor: pointer; }
.jump-btn:hover { background: rgba(220,208,255,0.3); }
</style>
