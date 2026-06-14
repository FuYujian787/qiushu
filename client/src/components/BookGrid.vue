<script setup>
import { computed } from 'vue'
import BookCard from '@/components/BookCard.vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['book-click'])

const skeletons = computed(() => Array(8).fill(null))
</script>

<template>
  <div class="book-grid">
    <!-- Loading -->
    <template v-if="loading">
      <div v-for="i in 8" :key="i" class="skeleton-card">
        <div class="skeleton skeleton-img"></div>
        <div class="skeleton-info">
          <div class="skeleton skeleton-title"></div>
          <div class="skeleton skeleton-author"></div>
          <div class="skeleton skeleton-price"></div>
        </div>
      </div>
    </template>

    <!-- Items -->
    <template v-else>
      <div
        v-for="book in items"
        :key="book.id"
        class="grid-item"
        @click="$emit('book-click', book)"
      >
        <slot name="item" :book="book">
          <BookCard :book="book" />
        </slot>
      </div>
    </template>
  </div>
</template>

<style scoped>
.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 20px;
}

.grid-item {
  cursor: pointer;
}

/* Skeleton */
.skeleton-card {
  background: var(--surface-secondary);
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border-default);
}

.skeleton-img {
  aspect-ratio: 3/4;
}

.skeleton-info {
  padding: 12px 14px 14px;
}

.skeleton-title {
  height: 16px;
  width: 80%;
  margin-bottom: 8px;
}

.skeleton-author {
  height: 12px;
  width: 50%;
  margin-bottom: 12px;
}

.skeleton-price {
  height: 18px;
  width: 40%;
}

.skeleton {
  background: linear-gradient(
    90deg,
    var(--surface-tertiary) 25%,
    rgba(255, 255, 255, 0.15) 50%,
    var(--surface-tertiary) 75%
  );
  background-size: 200px 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: 4px;
}

@keyframes shimmer {
  0% { background-position: -200px 0; }
  100% { background-position: calc(200px + 100%) 0; }
}

@media (max-width: 480px) {
  .book-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
}
</style>
