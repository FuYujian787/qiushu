<template>
  <div class="detail-page">
    <div v-if="!book" class="empty-state">书籍未找到</div>
    <div v-else class="detail-layout">
      <div class="detail-image">
        <div class="detail-img-wrap"><img :src="book.img" class="detail-img" /></div>
      </div>
      <div class="detail-info">
        <h1 class="detail-title">{{ book.title }}</h1>
        <p class="detail-author">{{ book.author }} · {{ book.seller }}</p>
        <div class="detail-price">
          <span class="current-price">¥{{ book.price }}</span>
          <span class="old-price">原价 ¥{{ book.oldPrice }}</span>
        </div>
        <div class="detail-actions">
          <div class="detail-btn primary" @click="addAndGo">加入购物车</div>
          <div class="detail-btn dark" @click="buyNow">立即购买</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from '../../stores/useStore'

const store = useStore()

const book = computed(() => {
  return store.productCache.value.find(p => p.id === store.bookDetailId.value)
})

function addAndGo() {
  if (book.value) {
    store.addToCart(book.value)
    alert('已加入购物车')
  }
}

function buyNow() {
  if (book.value) {
    store.addToCart(book.value)
    store.navigateTo('cart')
  }
}
</script>

<style scoped>
.detail-page {}
.empty-state { text-align: center; padding: 3rem; color: #9ca3af; }
.detail-layout { display: grid; grid-template-columns: repeat(12, 1fr); gap: 2.5rem; max-width: 72rem; margin: 0 auto; }
.detail-image { grid-column: span 4; }
.detail-img-wrap { background: white; padding: 1.5rem; border-radius: 2.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.detail-img { aspect-ratio: 3/4; border-radius: 1.5rem; overflow: hidden; width: 100%; object-fit: cover; }
.detail-info { grid-column: span 8; background: white; border-radius: 2.5rem; padding: 2.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.detail-title { font-size: 1.875rem; font-weight: 700; margin: 0; }
.detail-author { color: #9ca3af; margin-top: 0.5rem; font-size: 0.875rem; }
.detail-price { margin-top: 1.5rem; display: flex; align-items: center; gap: 1rem; }
.current-price { font-size: 2.25rem; font-weight: 900; color: #7c3aed; }
.old-price { font-size: 0.875rem; color: #9ca3af; text-decoration: line-through; }
.detail-actions { margin-top: 2rem; display: flex; gap: 1rem; }
.detail-btn { flex: 1; padding: 1rem; border-radius: 1rem; font-weight: 700; text-align: center; cursor: pointer; }
.detail-btn.primary { background: #7c3aed; color: white; }
.detail-btn.primary:hover { background: #6d28d9; }
.detail-btn.dark { background: #374151; color: white; }
.detail-btn.dark:hover { background: #1f2937; }
</style>
