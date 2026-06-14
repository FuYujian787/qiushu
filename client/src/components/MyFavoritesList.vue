<script setup>
defineProps({
  favorites: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['book-click', 'remove'])
</script>

<template>
  <div class="my-favorites-list">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="favorites.length === 0" class="empty">
      <p>暂无收藏</p>
      <p class="empty-hint">浏览书籍时点击收藏，方便快速找到心仪的书</p>
    </div>
    <div v-else class="fav-list">
      <div
        v-for="book in favorites"
        :key="book.id"
        class="fav-item"
      >
        <span class="fav-title" @click="emit('book-click', book)">{{ book.title }}</span>
        <span class="fav-author" v-if="book.author">{{ book.author }}</span>
        <span class="fav-price">¥{{ book.price }}</span>
        <button class="remove-btn" @click.stop="emit('remove', book.id)">取消收藏</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.fav-list { display: flex; flex-direction: column; gap: 8px; }

.fav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
  border-radius: 8px;
}

.fav-title {
  flex: 1;
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s;
}

.fav-title:hover { color: var(--accent-primary); }

.fav-author { font-size: 12px; color: var(--text-muted); }
.fav-price { font-family: var(--font-mono); font-size: 15px; color: var(--accent-primary); font-weight: 600; }

.remove-btn {
  padding: 4px 12px;
  border: 1px solid var(--border-default);
  border-radius: 4px;
  background: none;
  color: var(--text-muted);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.remove-btn:hover { border-color: #C41E3A; color: #C41E3A; }

[data-theme="cyber"] .remove-btn:hover { border-color: #ff4d6a; color: #ff4d6a; }

.empty-hint { font-size: 12px; color: var(--text-muted); margin-top: 4px; }

.loading, .empty { text-align: center; padding: 40px; color: var(--text-muted); font-size: 14px; }
</style>
