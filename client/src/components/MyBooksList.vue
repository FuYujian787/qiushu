<script setup>
defineProps({
  books: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['book-click'])

function getStatusClass(status) {
  return status || ''
}
</script>

<template>
  <div class="my-books-list">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="books.length === 0" class="empty">暂无发布</div>
    <div v-else class="book-list">
      <div
        v-for="book in books"
        :key="book.id"
        class="book-item"
        @click="emit('book-click', book)"
      >
        <span class="item-title">{{ book.title }}</span>
        <span class="item-price">¥{{ book.price }}</span>
        <span :class="['item-status', getStatusClass(book.status)]">{{ book.status }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.book-list { display: flex; flex-direction: column; gap: 8px; }

.book-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 16px;
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.book-item:hover { border-color: var(--accent-primary); }

.item-title { flex: 1; font-size: 14px; color: var(--text-primary); font-weight: 500; }
.item-price { font-family: var(--font-mono); font-size: 15px; color: var(--accent-primary); }

.item-status {
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.item-status.在售 { background: #E8F5E9; color: #2E7D32; }
.item-status.已售 { background: #F5F5F5; color: #616161; }
.item-status.下架 { background: #FFF3E0; color: #E65100; }

[data-theme="cyber"] .item-status.在售 { background: rgba(168, 85, 247, 0.15); color: #A855F7; }
[data-theme="cyber"] .item-status.已售 { background: rgba(255,255,255,0.04); color: #8892B0; }
[data-theme="cyber"] .item-status.下架 { background: rgba(255,152,0,0.12); color: #FF9800; }

.loading, .empty { text-align: center; padding: 40px; color: var(--text-muted); font-size: 14px; }
</style>
